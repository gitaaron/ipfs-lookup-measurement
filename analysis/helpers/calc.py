from models.model_data_set import DataSet
from helpers import reduce
from pickled.model_retrieval import Retrieval
from helpers.constants import RetrievalPhase


def _avg_duration(retrievals: list[Retrieval]):
    num: float = len(retrievals)
    _total_duration: int = 0
    for ret in retrievals:
        _total_duration += ret.duration(RetrievalPhase.TOTAL).total_seconds()

    return _total_duration / num

def avg_duration_non_first_provider_nearest(data_set: DataSet) -> float:
    non_fpn_retrievals = data_set.non_first_provider_nearest_retrievals
    return _avg_duration(non_fpn_retrievals)

def avg_duration_first_provider_nearest(data_set: DataSet) -> float:
    fpn_retrievals = data_set.first_provider_nearest_retrievals
    return _avg_duration(fpn_retrievals)


def percent_fpn_slow(data_set: DataSet) -> float:
    fpn_retrievals = data_set.first_provider_nearest_retrievals
    slow_fpn_retrievals = reduce.by_slow_retrievals(fpn_retrievals)
    return len(slow_fpn_retrievals) / len(fpn_retrievals) * 100

def percent_non_fpn_slow(data_set: DataSet) -> float:
    non_fpn_retrievals = data_set.non_first_provider_nearest_retrievals
    slow_non_fpn_retrievals = reduce.by_slow_retrievals(non_fpn_retrievals)
    return len(slow_non_fpn_retrievals) / len(non_fpn_retrievals) * 100

def percent_nearest_neighbor_first_provider(data_set: DataSet) -> float:
    hfp_retrievals = data_set.has_first_provider_retrievals
    fpn_retrievals = data_set.first_provider_nearest_retrievals
    return len(fpn_retrievals) / len(hfp_retrievals) * 100

# returns a count of (many providers, single providers, average providers / retrieval)
def provider_count(retrievals: list[Retrieval]) -> tuple[int, int, float]:
    many_providers_count = 0
    single_provider_count = 0
    total_providers = 0

    for r in retrievals:
        if len(r.provider_peers) > 1:
            many_providers_count += 1
        else:
            single_provider_count += 1
        total_providers += len(r.provider_peers)

    return (many_providers_count, single_provider_count, total_providers / len(retrievals))
