from models.model_data_set import DataSet
from helpers import reduce
from pickled.model_retrieval import Retrieval
from helpers.constants import RetrievalPhase
from models.model_duration import Duration
import numpy as np


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
    if len(fpn_retrievals) > 0:
        return len(slow_fpn_retrievals) / len(fpn_retrievals) * 100
    else:
        return np.NaN

def percent_non_fpn_slow(data_set: DataSet) -> float:
    non_fpn_retrievals = data_set.non_first_provider_nearest_retrievals
    slow_non_fpn_retrievals = reduce.by_slow_retrievals(non_fpn_retrievals)
    if len(non_fpn_retrievals) > 0:
        return len(slow_non_fpn_retrievals) / len(non_fpn_retrievals) * 100
    else:
        return np.NaN

def percent_nearest_neighbor_first_provider(data_set: DataSet) -> float:
    hfp_retrievals = data_set.has_first_provider_retrievals
    fpn_retrievals = data_set.first_provider_nearest_retrievals
    return len(fpn_retrievals) / len(hfp_retrievals) * 100

# returns a count of (many providers, single providers, average providers / retrieval)
def provider_count(data_set: DataSet, slow: bool) -> tuple[int, int, float]:
    retrievals = data_set.total_completed_retrievals
    many_provider_retrievals = data_set.many_provider_retrievals
    single_provider_retrievals = data_set.single_provider_retrievals


    if slow:
        retrievals = reduce.by_slow_retrievals(retrievals)
        many_provider_retrievals = reduce.by_slow_retrievals(retrievals)
        single_provider_retrievals = reduce.by_slow_retrievals(retrievals)

    total_providers = 0

    for r in retrievals:
        total_providers += len(r.provider_peers)


    return (len(many_provider_retrievals), len(single_provider_retrievals), total_providers / len(retrievals))

def publish_age_duration_bins(data_set: DataSet) -> tuple[list[float], list[float], float]:
    retrievals = data_set.has_publish_age_retrievals
    stats = data_set.publish_age_stats
    publish_ages = [data_set.publish_age(ret).total_seconds() for ret in retrievals]
    edges = np.linspace(stats['min'], stats['max'] + 1e-12, 4)
    bucket_locations = np.digitize(publish_ages, edges)

    buckets = {}

    for idx, ret in enumerate(retrievals):
        bl = bucket_locations[idx]
        if bl not in buckets:
            buckets[bl] = []
        buckets[bl].append(ret.duration(RetrievalPhase.TOTAL).total_seconds())

    bucket_avgs = {}

    for b,durations in buckets.items():
        bucket_avgs[b] = np.mean(durations)

    sorted_avgs = [bucket_avgs.get(i, 0) for i in range(1, len(edges))]

    width=(edges[1]-edges[0])*0.9
    return edges[:-1], sorted_avgs, width

def agent_uptime_duration_bins(data_set: DataSet) -> tuple[list[float], list[float], float]:
    retrievals = data_set.retrievals_has_uptime
    d = data_set.agent_uptime_durations
    agent_uptimes = [ret.agent_uptime/1000 for ret in retrievals]
    edges = np.linspace(d['min'].duration, d['max'].duration + 1e-12, 5)
    bucket_locations = np.digitize(agent_uptimes, edges)

    buckets = {}

    for idx,ret in enumerate(retrievals):
        bl = bucket_locations[idx]
        if bl not in buckets:
            buckets[bl] = []
        buckets[bl].append(ret.duration(RetrievalPhase.TOTAL).total_seconds())
        idx+=1

    bucket_avgs = {}

    for b,durations in buckets.items():
        bucket_avgs[b] = np.mean(durations)

    sorted_avgs = [bucket_avgs.get(i, 0) for i in range(1, len(edges))]

    width=(edges[1] - edges[0])*0.9
    return edges[:-1], sorted_avgs, width
