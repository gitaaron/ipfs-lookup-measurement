import json
from logs.model_logs_config import LogsConfig
from logs import load
from models.model_data_set import DataSet

from pickled.model_publication import Publication
from pickled.model_retrieval import Retrieval

from helpers import calc, breakdowns, reduce, constants

def execute(logs_config: LogsConfig) -> dict:
    #data_set: DataSet = load.latest_data_set(logs_config)
    data_set: DataSet = load.complete_data_set(logs_config)

    publications: list[Publication] = data_set.total_publications
    completed_retrievals: list[Retrieval] = data_set.total_completed_retrievals

    stats = {}
    stats['num_retrievals'] = len(completed_retrievals)

    many_providers_count, single_provider_count, avg_providers = calc.provider_count(data_set, False)
    stats['num_has_first_provider'] = len(data_set.has_first_provider_retrievals)
    stats['num_many_providers'] = many_providers_count
    stats['num_single_provider'] = single_provider_count
    stats['average_providers_per_retrieval'] = avg_providers
    stats['phase_avg_duration'] = breakdowns.avg_duration_from_breakdown({'count': len(data_set.total_completed_retrievals), 'durations':data_set.phase_durations})

    if many_providers_count > 0 and len(data_set.first_provider_nearest_retrievals) > 0:
        stats['first_provider_nearest[fpn]'] = calc.first_provider_nearest_stats(data_set)
        if len(data_set.first_provider_nearest_retrievals) > 0:
            stats['avg_duration_fpn'] = f"{round(calc.avg_duration_first_provider_nearest(data_set),3)} sec."
        if len(data_set.non_first_provider_nearest_retrievals) > 0:
            stats['avg_duration_non_fpn'] = f"{round(calc.avg_duration_non_first_provider_nearest(data_set),3)} sec."

    slow = reduce.by_slow_retrievals(completed_retrievals)

    if len(slow) > 0:
        slow_stats = {}
        num_slow_many_providers, num_slow_one_provider,_ = calc.provider_count(data_set, True)
        slow_stats[f"slow_retrievals (>{constants.SLOW_THRESHOLD} sec.)"] = len(slow)
        slow_stats['slow_likelihood'] = f"{round(len(slow) / len(completed_retrievals),3)*100}%"
        slow_stats['slow_many_providers_likelihood'] = f"{round(num_slow_many_providers/len(slow),3)*100}%"
        slow_stats['slow_one_provider_likelihood'] = f"{round(num_slow_one_provider/len(slow),3)*100}%"
        if many_providers_count > 0:
            slow_stats['many_providers_slow_likelihood'] = f"{round(num_slow_many_providers/many_providers_count,3)*100}%"
            slow_stats['one_provider_slow_likelihood'] = f"{round(num_slow_one_provider/single_provider_count,3)*100}%"
            slow_stats['fpn_slow_likelihood'] = f"{round(calc.percent_fpn_slow(data_set),3)}%"
            slow_stats['non_fpn_slow_likelihood'] = f"{round(calc.percent_non_fpn_slow(data_set),3)}%"

        stats['slow'] = slow_stats
    stats['uptime'] = data_set.agent_uptime_durations



    hfs = reduce.by_has_file_size(completed_retrievals)

    if len(hfs) > 0:
        fstats = {}
        fstats['has_file_size'] = len(hfs)
        fstats['counts'] = breakdowns.count_from_breakdown(data_set.comparable_file_size_retrievals)
        fstats['avg_phase_durations'] = breakdowns.avg_phase_duration_from_breakdown(data_set.comparable_file_size_retrievals)
        fstats['standard_deviations'] = breakdowns.std_from_breakdown(data_set.comparable_file_size_retrievals)
        fstats['percent_slow'] = breakdowns.percent_slow_phase_breakdown_from_breakdown(data_set.comparable_file_size_retrievals)
        stats['file_size'] = fstats


    has_publish_age = data_set.has_publish_age_retrievals
    count = 0
    stats['num_has_publish_age'] = len(has_publish_age)
    stats['publish_age(retrieval_started-first_publish_ended)'],_,_ = data_set.publish_age_stats


    return stats

if __name__=='__main__':
    logs_config = LogsConfig('./log_config.json')
    stats = execute(logs_config)
    print(json.dumps(stats, indent=4, default=str))
