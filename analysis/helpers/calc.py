from models.model_data_set import DataSet
from helpers import reduce
from pickled.model_retrieval import Retrieval
from helpers.constants import RetrievalPhase
from models.model_duration import Duration


def _avg_duration(retrievals: list[Retrieval]):
    num: float = len(retrievals)
    _total_duration: int = 0
    for ret in retrievals:
        _total_duration += ret.duration(RetrievalPhase.TOTAL).total_seconds()

    return _total_duration / num

def avg_duration_from_breakdown(breakdown: dict[str, float]):
    avg_duration = {}
    avg_duration['count'] = breakdown['count']
    for d_key,d_val in breakdown['durations'].items():
        avg_duration[d_key] = Duration(d_val / breakdown['count'])

    return avg_duration


def avg_duration_from_breakdowns(breakdowns: dict[int,  dict[str, float]]):
    avg_durations = {}
    for b_key, b_val in breakdowns.items():
        avg_durations[b_key] = avg_duration_from_breakdown(b_val)

    return avg_durations



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
def provider_count(data_set: DataSet) -> tuple[int, int, float]:
    retrievals = data_set.total_completed_retrievals
    total_providers = 0

    for r in retrievals:
        total_providers += len(r.provider_peers)

    return (len(data_set.many_provider_retrievals), len(data_set.single_provider_retrievals), total_providers / len(retrievals))
