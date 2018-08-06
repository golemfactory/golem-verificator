import logging
from typing import Type

import math
import os
import posixpath
import json
import numpy
from collections import Callable
from threading import Lock
from shutil import copy
from functools import partial
from golem_verificator.verifier import SubtaskVerificationState

from .rendering_verifier import FrameRenderingVerifier
from .common.common import get_golem_path

logger = logging.getLogger("apps.blender")


# FIXME #2086
# pylint: disable=R0902
class BlenderVerifier(FrameRenderingVerifier):
    DOCKER_NAME = "golemfactory/image_metrics"
    DOCKER_TAG = '1.5'

    def __init__(self, callback: Callable, verification_data,
                 cropper_cls: Type, docker_task_cls: Type) -> None:
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
        self.cropper = cropper_cls()
        self.docker_task_cls = docker_task_cls
        self.metrics = dict()
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

    # pylint: disable-msg=too-many-arguments
    def _verify_with_reference(self, verification_data):
        self.current_results_files = verification_data["results"]
        self.subtask_info = verification_data["subtask_info"]

        def success():
            self.state = SubtaskVerificationState.VERIFIED
            self.verification_completed()

        def failure():
            self.state = SubtaskVerificationState.WRONG_ANSWER
            self.verification_completed()

        try:
            from twisted.internet import reactor
            self.success = partial(reactor.callFromThread, success)
            self.failure = partial(reactor.callFromThread, failure)
            self.cropper.render_crops(
                self.resources,
                self._crop_rendered,
                self._crop_render_failure,
                verification_data["subtask_info"])

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

        with self.lock:
            if self.wasFailure:
                return

        # pylint: disable=W0703
        try:
            with open(self.program_file, "r") as src_file:
                src_code = src_file.read()
        except FileNotFoundError as err:
            logger.warning("Wrong main program file: %r", err)
            src_code = ""

        work_dir = verification_context.get_crop_path(
            crop_number + self.cropper.crop_counter)

        dir_mapping = self.docker_task_cls.specify_dir_mapping(
            resources=os.path.join(work_dir, "resources"),
            temporary=os.path.dirname(work_dir),
            work=work_dir,
            output=os.path.join(work_dir, "output"),
            logs=os.path.join(work_dir, "logs"),
        )

        extra_data = self.create_extra_data(
            results, verification_context,
            crop_number, dir_mapping)

        docker_task = self.docker_task_cls(
            subtask_id=self.subtask_info['subtask_id'],
            docker_images=[(self.DOCKER_NAME, self.DOCKER_TAG)],
            orig_script_dir=work_dir,
            src_code=src_code,
            extra_data=extra_data,
            short_desc="BlenderVerifier",
            dir_mapping=dir_mapping,
            timeout=0)

        docker_task.run()
        was_failure = docker_task.error

        self.metrics[crop_number] = dict()
        for root, _, files in os.walk(str(dir_mapping.output)):
            for i, file in enumerate(files):
                try:
                    with open(dir_mapping.output / file) as json_data:
                        self.metrics[crop_number][i] = json.load(json_data)
                except EnvironmentError as exc:
                    logger.error("Metrics not calculated %r", exc)
                    was_failure = -1

        with self.lock:
            if was_failure == -1:
                self.wasFailure = True
                self.failure()
            else:
                self.verified_crops_counter += 1
                if self.verified_crops_counter == self.cropper.CROPS_NO_FIRST:
                    self.crops_size = verification_context.crop_size
                    self.make_verdict()

    # One failure is enough to stop verification process, although this might
    #  change in future
    def _crop_render_failure(self, error):
        logger.warning("Crop for verification render failure %r", error)
        with self.lock:
            self.wasFailure = True
            self.failure()

    def create_extra_data(self, results, verification_context, crop_number,
                          dir_mapping):
        filtered_results = list(filter(
            lambda x: not os.path.basename(x).endswith(".log"), results['data']
        ))

        dir_mapping.mkdirs()
        verification_pairs = dict()

        for result in self.current_results_files:
            copy(result, dir_mapping.resources)
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

        return dict(
            verification_files=verification_pairs,
            xres=verification_context.crop_pixels[crop_number][0],
            yres=verification_context.crop_pixels[crop_number][1],
        )

    def make_verdict(self):
        labels = []
        for crop_idx in range(len(self.metrics.keys())):
            for frame_idx, metric in self.metrics[crop_idx].items():
                labels.append(metric['Label'])
                logger.info(
                    "METRIC: Subtask: %r crop no: %r, frame %r SSIM %r,"
                    " PSNR: %r \n"
                    "Scene %s \n"
                    "requestor %r\n"
                    "provider %r",
                    self.subtask_info['subtask_id'],
                    crop_idx,
                    frame_idx,
                    metric['ssim'],
                    metric['psnr'],
                    self.subtask_info['scene_file'],
                    self.subtask_info['owner'],
                    self.subtask_info['node_id'])

                if metric['Label'] == "FALSE":
                    logger.warning("Subtask %r NOT verified with %r",
                                   self.subtask_info['subtask_id'],
                                   metric['ssim'])
                    self.failure()
                    return
                elif metric['Label'] == "DONT_KNOW" and not \
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

        if labels and all(label == "TRUE" for label in labels):
            logger.info("Subtask %r verified",
                        self.subtask_info['subtask_id'])
            self.success()
        else:
            logger.warning("Unexpected verification output for subtask %r,",
                           self.subtask_info['subtask_id'])
            self.failure()
