from pickled.model_retrieval import Retrieval
from helpers import constants

def by_slow_retrievals(retrievals: list[Retrieval]) -> list[Retrieval]:
    return list(filter(lambda ret: (ret.duration(constants.RetrievalPhase.TOTAL).total_seconds() > constants.SLOW_THRESHOLD), retrievals))

def by_has_file_size(retrievals: list[Retrieval]) -> list[Retrieval]:
    return list(filter(lambda ret: (ret.file_size is not None), retrievals))
