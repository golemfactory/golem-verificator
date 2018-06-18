import logging
import os
import threading
from datetime import datetime
from .common.common import deadline_to_timeout
from .verifier import (StateVerifier, SubtaskVerificationState, Verifier)

logger = logging.getLogger("golem_verificator.core_verifier")


class CoreVerifier(StateVerifier):

    def start_verification(self, verification_data):
        self.time_started = datetime.utcnow()
        if self._verify_result(verification_data):
            self.state = SubtaskVerificationState.VERIFIED

    def simple_verification(self, verification_data):
        results = verification_data["results"]
        if not results:
            self.state = SubtaskVerificationState.WRONG_ANSWER
            return False
        
        for result in results:
            if not os.path.isfile(result) or not\
                    self._verify_result(verification_data):
                self.message = "No proper task result found"
                self.state = SubtaskVerificationState.WRONG_ANSWER
                return False

        self.state = SubtaskVerificationState.VERIFIED
        return True

    def verification_completed(self):
        self.time_ended = datetime.utcnow()
        self.extra_data['results'] = self.results
        self.callback(subtask_id=self.subtask_info['subtask_id'],
                      verdict=self.state,
                      result=self._get_answer())

    # pylint: disable=unused-argument
    def _verify_result(self, results):
        """ Override this to change verification method
        """
        return True

