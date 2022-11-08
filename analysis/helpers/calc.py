from models.model_data_set import DataSet
from helpers import reduce
from pickled.model_retrieval import Retrieval
from helpers.constants import RetrievalPhase
from models.model_duration import Duration
import numpy as np


def avg_duration(retrievals: list[Retrieval], phase: RetrievalPhase):
    num: float = len(retrievals)
    _total_duration: int = 0
    for ret in retrievals:
        _total_duration += ret.duration(phase).total_seconds()

    return round(_total_duration / num, 3)


def avg_duration_non_first_provider_nearest(data_set: DataSet) -> float:
    non_fpn_retrievals = data_set.non_first_provider_nearest_retrievals
    return avg_duration(non_fpn_retrievals, RetrievalPhase.TOTAL)

def avg_duration_first_provider_nearest(data_set: DataSet) -> float:
    fpn_retrievals = data_set.first_provider_nearest_retrievals
    return avg_duration(fpn_retrievals, RetrievalPhase.TOTAL)

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

def first_provider_nearest_stats(data_set: DataSet) -> dict:
    non_fpn_retrievals = data_set.non_first_provider_nearest_retrievals
    fpn_retrievals = data_set.first_provider_nearest_retrievals
    a = {}
    a['num_fpn'] = len(fpn_retrievals)
    a['num_non_fpn'] =  len(non_fpn_retrievals)
    a['fpn_likelihood'] = round(len(fpn_retrievals) / len(fpn_retrievals+non_fpn_retrievals) * 100, 3)
    regions = {}
    for agent,_ in data_set.agent_events_map.items():
        if agent.region not in regions:
            regions[agent.region.name] = {'num_fpns':0, 'num_non_fpns':0}

    for ret in non_fpn_retrievals:
        if ret.origin.name in regions:
            regions[ret.origin.name]['num_non_fpns'] += 1

    for ret in fpn_retrievals:
        if ret.origin.name in regions:
            regions[ret.origin.name]['num_fpns'] += 1

    for region,val in regions.items():
        regions[region]['fpn_likelihood'] = round(val['num_fpns'] / (val['num_fpns']+val['num_non_fpns']) * 100, 3)

    regions['all'] = a

    return regions

# returns a count of (many providers, single providers, average providers / retrieval)
def provider_count(data_set: DataSet, slow: bool) -> tuple[int, int, float]:
    retrievals = data_set.total_completed_retrievals
    many_provider_retrievals = data_set.many_provider_retrievals
    single_provider_retrievals = data_set.single_provider_retrievals


    if slow:
        retrievals = reduce.by_slow_retrievals(retrievals)
        many_provider_retrievals = reduce.by_slow_retrievals(many_provider_retrievals)
        single_provider_retrievals = reduce.by_slow_retrievals(single_provider_retrievals)

    total_providers = 0

    for r in retrievals:
        total_providers += len(r.provider_peers)


    return (len(many_provider_retrievals), len(single_provider_retrievals), total_providers / len(retrievals))

def publish_age_duration_bins(data_set: DataSet, phase: RetrievalPhase) -> tuple[list[float], list[float], float]:
    stats,retrievals,delay_file_size = data_set.publish_age_stats

    publish_ages = [data_set.publish_age(ret).total_seconds() for ret in retrievals]
    if 'min' in stats and 'max' in stats:
        edges = np.linspace(stats['min'], stats['max'] + 1e-12, 4)
    else:
        edges = np.linspace(0, 1, 4)

    bucket_locations = np.digitize(publish_ages, edges)

    buckets = {}

    for idx, ret in enumerate(retrievals):
        bl = bucket_locations[idx]
        if bl not in buckets:
            buckets[bl] = []
        buckets[bl].append(ret.duration(phase).total_seconds())

    bucket_avgs = {}

    for b,durations in buckets.items():
        bucket_avgs[b] = np.mean(durations)

    sorted_avgs = [bucket_avgs.get(i, 0) for i in range(1, len(edges))]

    width=(edges[1]-edges[0])*0.9
    return edges[:-1], sorted_avgs, width, delay_file_size, len(retrievals)

def agent_uptime_duration_bins(data_set: DataSet, file_size: int, phase: RetrievalPhase) -> tuple[list[float], list[float], float, int]:
    retrievals = data_set.retrievals_has_uptime
    retrievals = reduce.by_file_size(retrievals, file_size)
    d = data_set.agent_uptime_durations
    agent_uptimes = [ret.agent_uptime/1000 for ret in retrievals]
    edges = np.linspace(d['min'].duration, d['max'].duration + 1e-12, 5)
    bucket_locations = np.digitize(agent_uptimes, edges)

    buckets = {}

    for idx,ret in enumerate(retrievals):
        bl = bucket_locations[idx]
        if bl not in buckets:
            buckets[bl] = []
        buckets[bl].append(ret.duration(phase).total_seconds())

    bucket_avgs = {}

    for b,durations in buckets.items():
        bucket_avgs[b] = np.mean(durations)

    sorted_avgs = [bucket_avgs.get(i, 0) for i in range(1, len(edges))]

    width=(edges[1] - edges[0])*0.9
    return edges[:-1], sorted_avgs, width, len(retrievals)
