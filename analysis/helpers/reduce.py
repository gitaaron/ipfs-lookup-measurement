from pickled.model_retrieval import Retrieval
from helpers.constants import RetrievalPhase, PlayerType

def by_slow_retrievals(retrievals: list[Retrieval]) -> list[Retrieval]:
    return list(filter(lambda ret: (ret.duration(RetrievalPhase.TOTAL).total_seconds() > constants.SLOW_THRESHOLD), retrievals))

def by_has_file_size(retrievals: list[Retrieval]) -> list[Retrieval]:
    return list(filter(lambda ret: (ret.file_size is not None), retrievals))

def by_file_size(retrievals: list[Retrieval], file_size: int) -> list[Retrieval]:
    return list(filter(lambda ret: (ret.file_size is not None and int(ret.file_size)==file_size), retrievals))

def by_main_player(retrievals: list[Retrieval], player: PlayerType):
    if player==PlayerType.RETRIEVER:
        return list(filter(lambda ret: len(ret.provider_peers) > 1, retrievals))
    elif player==PlayerType.PUBLISHER:
        return list(filter(lambda ret: len(ret.provider_peers) == 1, retrievals))
    else:
        raise Exception('Invalid player type: %s' % player)
