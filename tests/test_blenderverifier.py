import os
from unittest import mock

from golem_verificator.blender_verifier import BlenderVerifier, logger
from golem_verificator.common.ci import ci_skip
from tests.test_utils.assertlogs import LogTestCase
from tests.test_utils.pep8_conformance_test import Pep8ConformanceTest
from tests.test_utils.temp_dir_fixture import TempDirFixture


class VerificationContext:
    def __init__(self, crops_data, computer,
                 subtask_data, callbacks):
        self.crops_path = crops_data['paths']
        self.crops_floating_point_coordinates = crops_data['position'][0]
        self.crops_pixel_coordinates = crops_data['position'][1]
        self.computer = computer
        self.resources = subtask_data['resources']
        self.subtask_info = subtask_data['subtask_info']
        self.success_callback = callbacks['success']
        self.error_callback = callbacks['errback']
        self.crop_size = crops_data['position'][2]

    def get_crop_path(self, crop_number):
        return os.path.join(self.crops_path, str(0))


class TestBlenderVerifier(LogTestCase, Pep8ConformanceTest, TempDirFixture):

    PEP8_FILES = ["blender_verifier.py"]

    def test_get_part_size_from_subtask_number(self):
        subtask_info = {
            "res_y": 600,
            "total_tasks": 20,
            "start_task": 3,
        }

        verification_data = {}
        verification_data['subtask_info'] = subtask_info
        verification_data['results'] = []
        verification_data['reference_data'] = []
        verification_data['resources'] = []

        blender_verifier = BlenderVerifier(verification_data,
                             cropper_cls=mock.Mock(),
                             docker_task_cls=mock.Mock())
        assert blender_verifier._get_part_size_from_subtask_number(subtask_info) == 30
        subtask_info["total_tasks"] = 13
        subtask_info["start_task"] = 2
        assert blender_verifier._get_part_size_from_subtask_number(subtask_info) == 47
        subtask_info["start_task"] = 3
        assert blender_verifier._get_part_size_from_subtask_number(subtask_info) == 46
        subtask_info["start_task"] = 13
        assert blender_verifier._get_part_size_from_subtask_number(subtask_info) == 46

    def test_get_part_size(self):
        subtask_info = {
            "subtask_id": "deadbeef",
            "use_frames": False,
            "res_x": 800,
            "res_y": 600,
            "total_tasks": 20,
            "start_task": 3,
            "crop_window": (0,1,0.05,1) 
        }

        verification_data = {}
        verification_data['subtask_info'] = subtask_info
        verification_data['results'] = []
        verification_data['reference_data'] = []
        verification_data['resources'] = []

        blender_verifier = BlenderVerifier(verification_data,
                             cropper_cls=mock.Mock(),
                             docker_task_cls=mock.Mock())
        assert blender_verifier._get_part_size(subtask_info) == (800, 30)
        subtask_info["use_frames"] = True
        subtask_info["all_frames"] = list(range(40))
        subtask_info["crop_window"] = (0,1,0,1)
        assert blender_verifier._get_part_size(subtask_info) == (800, 600)
        subtask_info["all_frames"] = list(range(10))
        subtask_info["crop_window"] = (0,1,0.5,1)
        assert blender_verifier._get_part_size(subtask_info) == (800, 300)

    def test_crop_render_failure(self):
        verification_data = {}
        verification_data['subtask_info'] = {}
        verification_data['results'] = []
        verification_data['reference_data'] = []
        verification_data['resources'] = []

        blender_verifier = BlenderVerifier(verification_data,
                             cropper_cls=mock.Mock(),
                             docker_task_cls=mock.Mock())
        blender_verifier.failure = lambda: None

        with self.assertLogs(logger, level="WARNING") as logs:
            blender_verifier._crop_render_failure("There was a problem")
        assert any("WARNING:apps.blender:Crop for verification render failure"
                   " 'There was a problem'"
                   in log for log in logs.output)

    @ci_skip
    def test_crop_rendered(self):
        crop_path = os.path.join(self.tempdir, str(0))

        verification_data = {}
        verification_data['subtask_info'] = {'subtask_id': 'deadbeef'}
        verification_data['results'] = []
        verification_data['reference_data'] = []
        verification_data['resources'] = []

        reference_generator = mock.MagicMock()
        reference_generator.crop_counter = 3

        docker_task_thread = mock.Mock()
        docker_task_thread.return_value.output_dir_path = os.path.join(
            self.tempdir, 'output')
        docker_task_thread.specify_dir_mapping.return_value = \
            mock.Mock(resources=crop_path, temporary=self.tempdir)

        bv = BlenderVerifier(verification_data,
                             cropper_cls=reference_generator,
                             docker_task_cls=docker_task_thread)
        verify_ctx = VerificationContext({'position': [[0.2, 0.4, 0.2, 0.4],
                                               [[75, 34]], 0.05],
                                  'paths': self.tempdir},
                                 mock.MagicMock(), mock.MagicMock(),
                                 mock.MagicMock())
        bv.current_results_files = [os.path.join(self.tempdir, "none.png")]
        open(bv.current_results_files[0], mode='a').close()
        if not os.path.exists(crop_path):
            os.mkdir(crop_path)
        output_dir = os.path.join(crop_path, "output")
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        f = open(os.path.join(output_dir, "result_0.txt"), mode='a')
        f.write("{")
        f.write("\"MSE_canny\": 2032.03125,")
        f.write("\"MSE_normal\": 1.171875,")
        f.write("\"MSE_wavelet\": 5080.765625,")
        f.write("\"SSIM_canny\": 0.9377418556022814,")
        f.write("\"SSIM_normal\": 0.9948028194990917,")
        f.write("\"SSIM_wavelet\": 0.7995332835184454,")
        f.write("\"crop_resolution\": \"8x8\",")
        f.write("\"imgCorr\": 0.7342643964262355")
        f.write("}")
        f.close()
        with self.assertLogs(logger, level="INFO") as logs:
            bv._crop_rendered(({"data": ["def"]}, 2913, verify_ctx, 0))
        assert any("Crop for verification rendered"
                   in log for log in logs.output)
        assert any("2913" in log for log in logs.output)
        assert any("def" in log for log in logs.output)

