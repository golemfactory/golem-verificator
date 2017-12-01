from enum import Enum

class SubtaskVerificationState(Enum):
    UNKNOWN = 0
    WAITING = 1
    PARTIALLY_VERIFIED = 2
    VERIFIED = 3
    WRONG_ANSWER = 4
