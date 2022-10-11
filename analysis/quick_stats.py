import json
from logs.model_logs_config import LogsConfig
from logs import load
from models.model_data_set import DataSet

from pickled.model_publication import Publication
from pickled.model_retrieval import Retrieval

from helpers import calc, reduce, constants

if __name__=='__main__':
    logs_config = LogsConfig('./log_config.json')
    #data_set: DataSet = load.latest_data_set(logs_config)
    data_set: DataSet = load.complete_data_set(logs_config)

    publications: list[Publication] = data_set.total_publications
    completed_retrievals: list[Retrieval] = data_set.total_completed_retrievals

    slow = reduce.by_slow_retrievals(completed_retrievals)

    many_providers_count, single_provider_count, avg_providers = calc.provider_count(completed_retrievals)

    slow = reduce.by_slow_retrievals(completed_retrievals)
    hfs = reduce.by_has_file_size(completed_retrievals)
    num_slow_many_providers, num_slow_one_provider,_ = calc.provider_count(slow)

    stats = {}
    stats['num_retrievals'] = len(completed_retrievals)
    stats['has_file_size'] = len(hfs)
    stats[f"slow_retrievals (>{constants.SLOW_THRESHOLD} sec.)"] = len(slow)
    stats['percent_retrievals_are_slow'] = f"{round(len(slow)/len(completed_retrievals)*100,3)}%"
    stats['many_providers_count'] = many_providers_count
    stats['single_provider_count'] = single_provider_count
    stats['average_providers_per_retrieval'] = avg_providers
    stats['slow_many_providers'] = f"{round(num_slow_many_providers/len(slow),3)*100}%"
    stats['slow_one_provider'] = f"{round(num_slow_one_provider/len(slow),3)*100}%"
    stats['many_providers_slow_likelihood'] = f"{round(num_slow_many_providers/many_providers_count,3)*100}%"
    stats['one_provider_slow_likelihood'] = f"{round(num_slow_one_provider/single_provider_count,3)*100}%"
    stats['num_fpn'] = len(data_set.first_provider_nearest_retrievals)
    stats['num_non_fpn'] = len(data_set.non_first_provider_nearest_retrievals)
    stats['avg_duration_fpn'] = f"{round(calc.avg_duration_first_provider_nearest(data_set),3)} sec."
    stats['avg_duration_non_fpn'] = f"{round(calc.avg_duration_non_first_provider_nearest(data_set),3)} sec."
    stats['fpn_slow_likelihood'] = f"{round(calc.percent_fpn_slow(data_set),3)}%"
    stats['non_fpn_slow_likelihood'] = f"{round(calc.percent_non_fpn_slow(data_set),3)}%"
    stats['phase_avg_duration'] = calc.avg_duration_from_breakdown({'count': len(data_set.total_completed_retrievals), 'durations':data_set.phase_durations})
    stats['file_size_avg_duration'] = calc.avg_duration_from_breakdowns(data_set.unique_file_sizes)
    stats['uptime'] = data_set.agent_uptime_durations


    print(json.dumps(stats, indent=4, default=str))
