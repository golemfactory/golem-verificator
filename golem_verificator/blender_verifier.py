import logging
import math
import os
import posixpath
import json
import numpy
from collections import Callable
from threading import Lock
from shutil import copy
from functools import partial

from .rendering_verifier import FrameRenderingVerifier
from .imgcompare import check_size
from .docker.job import DockerJob
from .docker.image import DockerImage
from .common.common import get_golem_path

logger = logging.getLogger("apps.blender")


# FIXME #2086
# pylint: disable=R0902
class BlenderVerifier(FrameRenderingVerifier):
    DOCKER_NAME = "golemfactory/image_metrics"
    DOCKER_TAG = '1.4'

    def __init__(self, callback: Callable, verification_data) -> None:
        super().__init__(callback, verification_data)
        self.lock = Lock()
        self.verified_crops_counter = 0
        self.success = None
        self.failure = None
        self.current_results_files = None
        self.program_file = os.path.join(
            get_golem_path(), 'docker', 'blender', 'images', 'scripts',
            'runner.py')
        self.wasFailure = False
        self.cropper = verification_data["reference_generator"]
        self.metrics = dict()
        self.subtask_info = None
        self.crops_size = ()
        self.additional_test = False

    def _get_part_img_size(self, subtask_info):
        x, y = self._get_part_size(subtask_info)
        return 0, 0, x, y

    def _get_part_size(self, subtask_info):
        if subtask_info['use_frames'] and len(subtask_info['all_frames']) \
          >= subtask_info['total_tasks']:
            res_y = subtask_info['res_y']
        else:
            res_y = int(round(numpy.float32(
                numpy.float32(subtask_info['crop_window'][2])
                * numpy.float32(subtask_info['res_y']))))
        return subtask_info['res_x'], res_y

    @staticmethod
    def _get_part_size_from_subtask_number(subtask_info):

        if subtask_info['res_y'] % subtask_info['total_tasks'] == 0:
            res_y = int(subtask_info['res_y'] / subtask_info['total_tasks'])
        else:
            # in this case task will be divided into not equal parts:
            # floor or ceil of (res_y/total_tasks)
            # ceiling will be height of subtasks with smaller num
            ceiling_height = int(math.ceil(subtask_info['res_y'] /
                                           subtask_info['total_tasks']))
            additional_height = ceiling_height * subtask_info['total_tasks']
            additional_pixels = additional_height - subtask_info['res_y']
            ceiling_subtasks = subtask_info['total_tasks'] - additional_pixels

            if subtask_info['start_task'] > ceiling_subtasks:
                res_y = ceiling_height - 1
            else:
                res_y = ceiling_height
        return res_y

    def _check_size(self, file_, res_x, res_y):
        return check_size(file_, res_x, res_y)

    # pylint: disable-msg=too-many-arguments
    def _verify_with_reference(self, verification_data):
        self.current_results_files = results
        self.subtask_info = subtask_info

        def success():
            self.state = SubtaskVerificationState.VERIFIED
            self.verification_completed()

        def failure():
            self.state = SubtaskVerificationState.WRONG_ANSWER
            self.verification_completed()

        try:
            from twisted.internet import reactor
            self.success = partial(reactor.callFromThread, success_)
            self.failure = partial(reactor.callFromThread, failure)
            self.cropper.render_crops(
                self.computer,
                self.resources,
                self._crop_rendered,
                self._crop_render_failure,
                subtask_info)

        # pylint: disable=W0703
        except Exception as e:
            logger.error("Crop generation failed %r", e)
            import traceback
            traceback.print_exc()
            failure()

    # The verification function will generate three random crops, from results
    #  only after all three will be generated, we can start verification process
    # pylint: disable=R0914
    def _crop_rendered(self, results, time_spend, verification_context,
                       crop_number):
        logger.info("Crop for verification rendered. Time spent: %r, "
                    "results: %r", time_spend, results)

        filtered_results = list(filter(lambda x:
                                       not os.path.basename(x).endswith(
                                           ".log"), results['data']))

        with self.lock:
            if self.wasFailure:
                return

        work_dir = verification_context.get_crop_path(
            crop_number+self.cropper.crop_counter)
        di = DockerImage(BlenderVerifier.DOCKER_NAME,
                         tag=BlenderVerifier.DOCKER_TAG)

        output_dir = os.path.join(work_dir, "output")
        logs_dir = os.path.join(work_dir, "logs")
        resource_dir = os.path.join(work_dir, "resources")

        if not os.path.exists(resource_dir):
            os.mkdir(resource_dir)
        if not os.path.exists(logs_dir):
            os.mkdir(logs_dir)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        verification_pairs = dict()
        for result in self.current_results_files:
            copy(result, resource_dir)
            for ref_result in filtered_results:
                if os.path.basename(result) == os.path.basename(ref_result)[4:]:
                    verification_pairs[posixpath.join(
                        "/golem/resources",
                        os.path.basename(result))] = posixpath.join(
                        "/golem/work/tmp/output", os.path.basename(ref_result))

        # This is failsafe in 99% cases there will be only one result file
        # in subtask, so match it even if outfilebasename doesnt match pattern
        if not verification_pairs:
            verification_pairs[posixpath.join(
                "/golem/resources",
                os.path.basename(
                    self.current_results_files[0]))] = posixpath.join(
                "/golem/work/tmp/output", os.path.basename(filtered_results[0]))

        params = dict()

        params['verification_files'] = verification_pairs
        params['xres'] = verification_context.crop_pixels[crop_number][0]
        params['yres'] = verification_context.crop_pixels[crop_number][1]

        # pylint: disable=W0703
        try:
            with open(self.program_file, "r") as src_file:
                src_code = src_file.read()
        except FileNotFoundError as err:
            logger.warning("Wrong main program file: %r", err)
            src_code = ""

        with DockerJob(di, src_code, params,
                       resource_dir, work_dir, output_dir,
                       host_config=None) as job:
            job.start()
            was_failure = job.wait()
            stdout_file = os.path.join(logs_dir, "stdout.log")
            stderr_file = os.path.join(logs_dir, "stderr.log")
            job.dump_logs(stdout_file, stderr_file)
            self.metrics[crop_number] = dict()
            for root, dir, files in os.walk(output_dir):
                for i, file in enumerate(files):
                    try:
                        with open(os.path.join(output_dir, file)) as json_data:
                            self.metrics[crop_number][i] = json.load(
                                    json_data)
                    except EnvironmentError as exc:
                        logger.error("Metrics not calculated %r", exc)
                        was_failure = -1

        with self.lock:
            if was_failure == -1:
                self.wasFailure = True
                self.failure()
            else:
                self.verified_crops_counter += 1
                if self.verified_crops_counter == 3:
                    self.crops_size = verification_context.crop_size
                    self.make_verdict()

    # One failure is enough to stop verification process, although this might
    #  change in future
    def _crop_render_failure(self, error):
        logger.warning("Crop for verification render failure %r", error)
        with self.lock:
            self.wasFailure = True
            self.failure()

    def make_verdict(self):
        # These are empirically measured, render on different machines can
        # cause single pixels to change its intensity and cause deviation.
        # We observe that in majority cases 0.990 is enough to count for this
        # deviation, but there are exceptions, scenes like BMW which deviates
        # more drops to 0.970.
        w_ssim = 0.920
        w_ssim_min = 0.900
        avg_ssims = []
        for metrics_frames in range(len(self.metrics[0])):
            avg_histograms_correlation = 0
            avg_ssim = 0
            for _, metric in self.metrics.items():
                avg_histograms_correlation += \
                    metric[metrics_frames]['histograms_correlation']
                avg_ssim += metric[metrics_frames]['SSIM_normal']
            avg_histograms_correlation /= 3
            avg_ssim /= 3
            avg_ssims.append(avg_ssim)

            if avg_ssim < w_ssim_min:
                logger.warning("Subtask %r NOT verified with %r",
                               self.subtask_info['subtask_id'], avg_ssim)
                self.failure()
                return
            elif avg_ssim > w_ssim_min and avg_ssim < w_ssim and not \
                    self.additional_test:
                self.verified_crops_counter = 0
                self.metrics.clear()
                self.additional_test = True
                logger.info(
                    "Performing additional verification for subtask %r ",
                    self.subtask_info['subtask_id'])
                self.cropper.crop_counter = 3
                self.cropper.render_crops(self.computer, self.resources,
                                          self._crop_rendered,
                                          self._crop_render_failure,
                                          self.subtask_info,
                                          3,
                                          (self.crops_size[0] + 0.01,
                                           self.crops_size[1] + 0.01))
                return

        if all(ssim > w_ssim for ssim in avg_ssims):
            logger.info("Subtask %r verified with %r",
                        self.subtask_info['subtask_id'], avg_ssims)
            self.success()
        else:
            logger.warning("Unexpected verification output for subtask %r,"
                           " histograms_correlation = %r, ssim = %r",
                           self.subtask_info['subtask_id'],
                           avg_histograms_correlation, avg_ssim)
            self.failure()
