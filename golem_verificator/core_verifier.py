import logging
import os
import threading
from datetime import datetime
from .common.common import deadline_to_timeout
from .verifier import (StateVerifier, SubtaskVerificationState, Verifier)

logger = logging.getLogger("golem_verificator.core_verifier")


class CoreVerifier(StateVerifier):

    def start_verification(self, subtask_info: dict, reference_data: list,
                           resources: list, results: list):
        self.time_started = datetime.utcnow()
        self._verify_imgs(subtask_info, results, reference_data, resources)

    def simple_verification(self, subtask_info, results):
        if not results:
            self.state = SubtaskVerificationState.WRONG_ANSWER
            return False
        
        for result in results:
            if not os.path.isfile(result) or not\
                    self._verify_result(subtask_info, result):
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
    def _verify_result(self, subtask_info: dict, result: str):
        """ Override this to change verification method
        """
        return True

    def _verify_imgs(self, subtask_info, results, reference_data,
        resources):
        """ Override this to change verification method
        """
        self.state = SubtaskVerificationState.VERIFIED
        return True
        