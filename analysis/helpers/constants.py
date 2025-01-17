from enum import Enum
from pickled.model_agent import Agent
from models.model_region import Region


SLOW_THRESHOLD = 4 # in sec.

class RetrievalPhase(str, Enum):
    TOTAL = 'TOTAL'
    INITIATED = 'INITIATED'
    GETTING_CLOSEST_PEERS = 'GETTING_CLOSEST_PEERS'
    DIALING = 'DIALING'
    FETCHING = 'FETCHING'

class PlayerType(str, Enum):
    RETRIEVER = 'RETRIEVER'
    PUBLISHER = 'PUBLISHER'

class DurationType(str, Enum):
    FAST = 'FAST'
    SLOW = 'SLOW'
    ALL = 'ALL'


DELAY_FILE_SIZE = 52439

UNKNOWN_AGENT = Agent(-1, Region('unknown'))
