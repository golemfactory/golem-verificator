# pylint: disable=protected-access
import os
import unittest.mock as mock
from golem_verificator.common.assertlogs import LogTestCase
from golem_verificator.verifier import SubtaskVerificationState
from golem_verificator.lux_verifier import LuxRenderVerifier, logger
from golem_verificator.common.rendering_task_utils import (
    AdvanceRenderingVerificationOptions)
from tests.testutils import PEP8MixIn, TempDirFixture


class TestLuxRenderVerifier(TempDirFixture, LogTestCase, PEP8MixIn):
    PEP8_FILES = [
        'lux_verifier.py',
    ]

    def test_merge_flm_files_failure(self):
        subtask_info = {"tmp_dir": self.path,
                        'merge_ctd': {'extra_data': {'flm_files': []}},
                        'root_path': self.path}
        lrv = LuxRenderVerifier(AdvanceRenderingVerificationOptions,
            subtask_info, [], [], [])
        lrv.test_flm = "test_flm"
        assert not lrv.merge_flm_files("flm_file", subtask_info, "flm_output")
        assert lrv.state == SubtaskVerificationState.NOT_SURE
        lrv.computer = mock.Mock()
        lrv.computer.wait.return_value = None
        assert not lrv.merge_flm_files("flm_file", subtask_info, "flm_output")
        lrv.computer.wait.return_value = mock.Mock()
        lrv.verification_error = True
        assert not lrv.merge_flm_files("flm_file", subtask_info, "flm_output")
        lrv.verification_error = False
        lrv.computer.get_result.return_value = {
            'data': self.additional_dir_content([3])}
        assert not lrv.merge_flm_files("flm_file", subtask_info, "flm_output")
        flm_file = os.path.join(self.path, "bla.flm")
        open(flm_file, 'w').close()
        lrv.computer.get_result.return_value = {
            'data': self.additional_dir_content([1]) + [flm_file]}
        assert not lrv.merge_flm_files("flm_file", subtask_info, "flm_output")
        stderr_file = os.path.join(self.path, "stderr.log")
        lrv.computer.get_result.return_value = {'data': [flm_file, stderr_file]}
        assert not lrv.merge_flm_files("flm_file", subtask_info, "flm_output")
        open(stderr_file, 'w').close()
        assert lrv.merge_flm_files("flm_file", subtask_info, "flm_output")
        with open(stderr_file, 'w') as f:
            f.write("ERROR at merging files")

        assert not lrv.merge_flm_files("flm_file", subtask_info, "flm_output")

    def test_flm_verify_failure(self):
        lrv = LuxRenderVerifier(AdvanceRenderingVerificationOptions,
            {}, [], [], [])
        with self.assertLogs(logger, level="INFO"):
            lrv._verify_flm_failure("Error in something")
        assert lrv.verification_error
