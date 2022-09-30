from enum import Enum


SLOW_THRESHOLD = 4 # in sec.

class RetrievalPhase(Enum):
    TOTAL = 1
    INITIATED = 2
    GETTING_CLOSEST_PEERS = 3
    DIALING = 4
    FETCHING = 5
