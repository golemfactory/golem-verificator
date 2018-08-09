from golem_verificator.core_verifier import CoreVerifier
from golem_verificator.verifier import SubtaskVerificationState
from tests.test_utils.assertlogs import LogTestCase
from tests.test_utils.temp_dir_fixture import TempDirFixture


class TestCoreVerifier(TempDirFixture, LogTestCase):

    def test_start_verification(self):

        def callback(*args, **kwargs):
            pass

        core_verifier = CoreVerifier(callback)
        subtask_info = {'subtask_id': 5}
        files = self.additional_dir_content([1])

        verification_data = dict()
        verification_data["results"] = files
        verification_data["subtask_info"] = subtask_info

        core_verifier.start_verification(verification_data)

        assert core_verifier.state == SubtaskVerificationState.VERIFIED

    def test_simple_verification(self):
        def callback(subtask_id, verdict, result):
            pass

        core_verifier = CoreVerifier(callback)
        subtask_info = {"subtask_id": "2432423"}
        core_verifier.subtask_info = subtask_info
        verification_data = dict()
        verification_data["results"] = []
        core_verifier.simple_verification(verification_data)
        assert core_verifier.state == SubtaskVerificationState.WRONG_ANSWER

        files = self.additional_dir_content([3])
        verification_data["results"] = files
        core_verifier.simple_verification(verification_data)
        assert core_verifier.state == SubtaskVerificationState.VERIFIED

        verification_data["results"] = [files[0]]
        core_verifier.simple_verification(verification_data)
        assert core_verifier.state == SubtaskVerificationState.VERIFIED

        verification_data["results"] = ["not a file"]
        core_verifier.simple_verification(verification_data)
        assert core_verifier.state == SubtaskVerificationState.WRONG_ANSWER
