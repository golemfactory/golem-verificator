from golem_verificator.common.assertlogs import LogTestCase
from golem_verificator.verifier import SubtaskVerificationState
from golem_verificator.core_verifier import CoreVerifier
from tests.testutils import TempDirFixture


class TestCoreVerifierr(TempDirFixture, LogTestCase):

    def test_start_verification(self):
        # given
        def callback(*args, **kwargs):
            pass

        cv = CoreVerifier(callback, {}, [], [], [])
        subtask_info = {'subtask_id': 5}
        files = self.additional_dir_content([1])

        # when
        cv.start_verification(subtask_info, [], [], files)

        # then
        assert cv.state == SubtaskVerificationState.VERIFIED

    def test_simple_verification(self):
        def callback(subtask_id, verdict, result):
            pass

        cv = CoreVerifier(callback, {}, [], [], [])
        subtask_info = {"subtask_id": "2432423"}
        cv.subtask_info = subtask_info
        cv.simple_verification(dict(), [])
        assert cv.state == SubtaskVerificationState.WRONG_ANSWER

        files = self.additional_dir_content([3])
        cv.simple_verification(dict(), files)
        assert cv.state == SubtaskVerificationState.VERIFIED

        files = self.additional_dir_content([3])
        cv.simple_verification(dict(), [files[0]])
        assert cv.state == SubtaskVerificationState.VERIFIED

        cv.simple_verification(dict(), ["not a file"])
        assert cv.state == SubtaskVerificationState.WRONG_ANSWER
