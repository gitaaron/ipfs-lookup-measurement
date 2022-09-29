from models.model_retrieval import Retrieval
from typing import List
from helpers import constants

def by_slow_retrievals(retrievals: List[Retrieval]):
    return list(filter(lambda ret: (ret.duration_total().total_seconds() > constants.SLOW_THRESHOLD), retrievals))
