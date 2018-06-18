from golem_verificator.common.assertlogs import LogTestCase
from golem_verificator.verifier import SubtaskVerificationState
from golem_verificator.core_verifier import CoreVerifier
from tests.testutils import TempDirFixture


class TestCoreVerifierr(TempDirFixture, LogTestCase):

    def test_start_verification(self):
        # given
        def callback(*args, **kwargs):
            pass

        cv = CoreVerifier(callback)
        subtask_info = {'subtask_id': 5}
        files = self.additional_dir_content([1])

        verification_data = dict()
        verification_data["results"] = files

        # when
        cv.start_verification(verification_data)

        # then
        assert cv.state == SubtaskVerificationState.VERIFIED

    def test_simple_verification(self):
        def callback(subtask_id, verdict, result):
            pass

        cv = CoreVerifier(callback)
        subtask_info = {"subtask_id": "2432423"}
        cv.subtask_info = subtask_info
        verification_data = dict()
        verification_data["results"] = []
        cv.simple_verification(verification_data)
        assert cv.state == SubtaskVerificationState.WRONG_ANSWER

        files = self.additional_dir_content([3])
        verification_data["results"] = files
        cv.simple_verification(verification_data)
        assert cv.state == SubtaskVerificationState.VERIFIED

        verification_data["results"] = [files[0]]
        files = self.additional_dir_content([3])
        cv.simple_verification(verification_data)
        assert cv.state == SubtaskVerificationState.VERIFIED

        verification_data["results"] = ["not a file"]
        cv.simple_verification(verification_data)
        assert cv.state == SubtaskVerificationState.WRONG_ANSWER
