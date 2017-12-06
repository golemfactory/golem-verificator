from enum import Enum

class SubtaskVerificationState(Enum):
    """
    Copy-pasted Enum from golem core.
    Pitfall: its works better to return the value of enum
    (not name, not whole enum state),
    and then remap it in core.
    """

    UNKNOWN = 0
    WAITING = 1
    PARTIALLY_VERIFIED = 2
    VERIFIED = 3
    WRONG_ANSWER = 4
