from models.model_retrieval import Retrieval
from typing import List
from helpers import constants
from helpers.constants import RetrievalPhase

def by_slow_retrievals(retrievals: List[Retrieval]) -> List[Retrieval]:
    return list(filter(lambda ret: (ret.duration(RetrievalPhase.TOTAL).total_seconds() > constants.SLOW_THRESHOLD), retrievals))

def by_has_file_size(retrievals: List[Retrieval]) -> List[Retrieval]:
    return list(filter(lambda ret: (ret.file_size is not None), retrievals))
