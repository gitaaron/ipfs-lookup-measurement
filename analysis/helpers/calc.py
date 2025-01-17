import math
import numpy as np
from models.model_data_set import DataSet
from helpers import reduce
from pickled.model_retrieval import Retrieval
from pickled.model_publication import Publication
from helpers.constants import RetrievalPhase
from models.model_duration import Duration
from models.model_run import Run
from models.model_runs import Runs


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
    slow_fpn_retrievals = reduce.by_slow_retrievals(data_set, fpn_retrievals, RetrievalPhase.TOTAL)
    if len(fpn_retrievals) > 0:
        return len(slow_fpn_retrievals) / len(fpn_retrievals) * 100
    else:
        return np.NaN

def percent_non_fpn_slow(data_set: DataSet) -> float:
    non_fpn_retrievals = data_set.non_first_provider_nearest_retrievals
    slow_non_fpn_retrievals = reduce.by_slow_retrievals(data_set, non_fpn_retrievals, RetrievalPhase.TOTAL)
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
        if((val['num_fpns']+val['num_non_fpns']) > 0):
            regions[region]['fpn_likelihood'] = round(val['num_fpns'] / (val['num_fpns']+val['num_non_fpns']) * 100, 3)

    regions['all'] = a

    return regions

# returns a count of (many providers, single providers, average providers / retrieval)
def provider_count(data_set: DataSet, slow: bool) -> tuple[int, int, float]:
    retrievals = data_set.total_completed_retrievals
    many_provider_retrievals = data_set.many_provider_retrievals
    single_provider_retrievals = data_set.single_provider_retrievals


    if slow:
        retrievals = reduce.by_slow_retrievals(data_set, retrievals, RetrievalPhase.TOTAL)
        many_provider_retrievals = reduce.by_slow_retrievals(data_set, many_provider_retrievals, RetrievalPhase.TOTAL)
        single_provider_retrievals = reduce.by_slow_retrievals(data_set, single_provider_retrievals, RetrievalPhase.TOTAL)

    total_providers = 0

    for r in retrievals:
        total_providers += len(r.provider_peers)


    return (len(many_provider_retrievals), len(single_provider_retrievals), total_providers / len(retrievals))

def publish_age_percent_slow_bins(data_set: DataSet, phase: RetrievalPhase) -> tuple[list[float], list[float], float, list[int]]:
    stats,retrievals,delay_file_size = data_set.publish_age_stats

    publish_ages = [math.floor(data_set.publish_age(ret).total_seconds()) for ret in retrievals]
    if 'min' in stats and 'max' in stats:
        edges = np.linspace(stats['min'], stats['max'] + 1e-12, 4)
    else:
        edges = np.linspace(0, 1, 4)

    bucket_locations = np.digitize(publish_ages, edges)

    buckets = {}
    for bl in range(len(edges)):
        buckets[bl] = []

    for idx, ret in enumerate(retrievals):
        bl = bucket_locations[idx]
        buckets[bl].append(ret)

    bucket_percents = {}
    sample_sizes = {}

    for b,retrievals in buckets.items():
        if len(retrievals)>0:
            bucket_percents[b],sample_sizes[b] = data_set.percent_slow(retrievals, phase)

    sorted_percents = [bucket_percents.get(i, 0) for i in range(1, len(edges))]
    sorted_sample_sizes = [sample_sizes.get(i, 0) for i in range(1, len(edges))]


    width=(edges[1]-edges[0])*0.9
    return edges[:-1], sorted_percents, width, delay_file_size, sorted_sample_sizes

def publish_age_duration_bins(data_set: DataSet, phase: RetrievalPhase) -> tuple[list[float], list[float], float, list[int]]:
    stats,retrievals,delay_file_size = data_set.publish_age_stats

    publish_ages = [math.floor(data_set.publish_age(ret).total_seconds()) for ret in retrievals]
    if 'min' in stats and 'max' in stats:
        edges = np.linspace(stats['min'], stats['max'] + 1e-12, 4)
    else:
        edges = np.linspace(0, 1, 4)

    bucket_locations = np.digitize(publish_ages, edges)

    buckets = {}
    for bl in range(len(edges)):
        buckets[bl] = []


    for idx, ret in enumerate(retrievals):
        bl = bucket_locations[idx]
        buckets[bl].append(ret.duration(phase).total_seconds())

    bucket_avgs = {}
    sample_sizes = {}

    for b,durations in buckets.items():
        bucket_avgs[b] = np.mean(durations)
        sample_sizes[b] = len(durations)

    sorted_avgs = [bucket_avgs.get(i, 0) for i in range(1, len(edges))]
    sorted_sample_sizes = [sample_sizes.get(i, 0) for i in range(1, len(edges))]


    width=(edges[1]-edges[0])*0.9
    return edges[:-1], sorted_avgs, width, delay_file_size, sorted_sample_sizes

def agent_uptime_percent_slow_bins(data_set: DataSet, phase: RetrievalPhase) -> tuple[list[float], list[float], float, list[int]]:
    retrievals = reduce.by_comparable_file_sizes(data_set.retrievals_has_uptime)
    d = data_set.agent_uptime_durations
    agent_uptimes = [math.floor(ret.agent_uptime/1000) for ret in retrievals]
    edges = np.linspace(d['min'].duration, d['max'].duration + 1e-12, 5)
    bucket_locations = np.digitize(agent_uptimes, edges)
    buckets = {}
    for bl in range(len(edges)):
        buckets[bl] = []

    for idx,ret in enumerate(retrievals):
        bl = bucket_locations[idx]
        buckets[bl].append(ret)

    sample_sizes = {}
    buckets_percent_slow = {}
    for b,retrievals in buckets.items():
        if len(retrievals)>0:
            buckets_percent_slow[b],sample_sizes[b] = data_set.percent_slow(retrievals, phase)

    sorted_percent_slow = [buckets_percent_slow.get(i, 0) for i in range(1, len(edges))]
    sorted_sample_sizes = [sample_sizes.get(i, 0) for i in range(1, len(edges))]

    width=(edges[1] - edges[0])*0.9
    return edges[:-1], sorted_percent_slow, width, sorted_sample_sizes

def agent_uptime_duration_bins(data_set: DataSet, file_size: int, phase: RetrievalPhase) -> tuple[list[float], list[float], float, list[int]]:
    retrievals = data_set.retrievals_has_uptime
    retrievals = reduce.by_file_size(retrievals, file_size)
    d = data_set.agent_uptime_durations
    agent_uptimes = [math.floor(ret.agent_uptime/1000) for ret in retrievals]
    edges = np.linspace(d['min'].duration, d['max'].duration + 1e-12, 5)
    bucket_locations = np.digitize(agent_uptimes, edges)
    buckets = {}
    for bl in range(len(edges)):
        buckets[bl] = []
    for idx,ret in enumerate(retrievals):
        bl = bucket_locations[idx]
        buckets[bl].append(ret.duration(phase).total_seconds())

    bucket_avgs = {}

    sample_sizes = {}
    for b,durations in buckets.items():
        bucket_avgs[b] = np.mean(durations)
        sample_sizes[b] = len(durations)

    sorted_avgs = [bucket_avgs.get(i, 0) for i in range(1, len(edges))]
    sorted_sample_sizes = [sample_sizes.get(i, 0) for i in range(1, len(edges))]

    width=(edges[1] - edges[0])*0.9
    return edges[:-1], sorted_avgs, width, sorted_sample_sizes

def average_hops_to_first_provider(data_set: DataSet):
    return np.mean([ret.hops_to_first_provider for ret in data_set.has_first_provider_retrievals])

def first_referal_num_providers_in_percent(retrievals: list[Retrieval]):
    freqs = {}
    for ret in retrievals:
        num = ret.first_referal_providers_count
        if num in freqs:
            freqs[num] += 1
        else:
            freqs[num] = 1

    percents = {}
    for num,freq in freqs.items():
        percents[num] = round(freq/len(retrievals)*100, 2)
    return percents

def avg_add_query_publish_success(pubs: list[Publication]) -> float:
    add_query_success_nums = [pub.num_successful_add_provider_queries for pub in pubs]
    return round(np.mean(add_query_success_nums), 2)

def avg_unique_add_query_peers_per_run(runs: dict[str, Run]) -> float:
    unique_peers = [run.num_unique_successful_add_target_peers for cid,run in runs.items()]
    return round(np.mean(unique_peers), 2)

def percent_retrievals_with_first_referer_in_add_query_list(rets: list[Retrieval], runs: Runs) -> float:
    rets_with_referer_in_add_query_list = reduce.by_referer_in_successful_add_list(rets, runs)
    return round(len(rets_with_referer_in_add_query_list) / len(rets) * 100, 3)

def percent_agent_not_in_add_query_list(rets: list[Retrieval], runs: Runs, agent_name: str) -> float:
    rets_with_referer_not_in_add_query_list = reduce.by_referer_in_successful_add_list(rets, runs, False)
    hydra_rets = reduce.by_first_referer(rets_with_referer_not_in_add_query_list, agent_name)
    return round(len(hydra_rets)/len(rets_with_referer_not_in_add_query_list)*100, 2)

def avg_provider_peers_found(rets: list[Retrieval]) -> float:
    pvr_found = [ret.num_provider_peers_found for ret in rets]
    return round(np.mean(pvr_found), 3)
