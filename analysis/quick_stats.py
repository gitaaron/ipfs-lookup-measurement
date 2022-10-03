import os
import json
import glob
from typing import List
from models.model_parsed_log_file import ParsedLogFile
from models.model_publication import Publication
from models.model_retrieval import Retrieval
from helpers import proximity, calc, reduce, constants, logs
from models.model_logs_config import LogsConfig

if __name__=='__main__':
    logs_config = LogsConfig('./log_config.json')
    parsed_logs = logs.load_latest_parsed_log_files(logs_config)

    publications: List[Publication] = parsed_logs.total_publications
    completed_retrievals: List[Retrieval] = parsed_logs.total_completed_retrievals


    many_providers_count = 0
    single_provider_count = 0
    total_providers = 0

    for r in completed_retrievals:
        if len(r.provider_peers) > 1:
            many_providers_count += 1
        else:
            single_provider_count += 1

        total_providers += len(r.provider_peers)

    slow = reduce.by_slow_retrievals(completed_retrievals)

    num_slow_many_providers = 0
    num_slow_one_provider = 0
    for sr in slow:
        if(len(sr.provider_peers)) > 1:
            num_slow_many_providers += 1
        else:
            num_slow_one_provider += 1

    stats = {}
    stats['num_retrievals'] = len(completed_retrievals)
    stats[f"slow_retrievals (>{constants.SLOW_THRESHOLD} sec.)"] = len(slow)
    stats['percent_retrievals_are_slow'] = f"{round(len(slow)/len(completed_retrievals)*100,3)}%"
    stats['many_providers_count'] = many_providers_count
    stats['single_provider_count'] = single_provider_count
    stats['avg_providers_per_retrieval'] = round(total_providers / len(completed_retrievals),3)
    stats['slow_many_providers'] = f"{round(num_slow_many_providers/len(slow),3)*100}%"
    stats['slow_one_provider'] = f"{round(num_slow_one_provider/len(slow),3)*100}%"
    stats['many_providers_slow_likelihood'] = f"{round(num_slow_many_providers/many_providers_count,3)*100}%"
    stats['one_provider_slow_likelihood'] = f"{round(num_slow_one_provider/single_provider_count,3)*100}%"
    stats['percent_first_provider_nearest[fpn]'] = f"{round(calc.percent_nearest_neighbor_first_provider(parsed_logs),3)}%"
    stats['num_fpn'] = len(parsed_logs.first_provider_nearest_retrievals)
    stats['num_non_fpn'] = len(parsed_logs.non_first_provider_nearest_retrievals)
    stats['avg_duration_fpn'] = f"{round(calc.avg_duration_first_provider_nearest(parsed_logs),3)} sec."
    stats['avg_duration_non_fpn'] = f"{round(calc.avg_duration_non_first_provider_nearest(parsed_logs),3)} sec."
    stats['fpn_slow_likelihood'] = f"{round(calc.percent_fpn_slow(parsed_logs),3)}%"
    stats['non_fpn_slow_likelihood'] = f"{round(calc.percent_non_fpn_slow(parsed_logs),3)}%"


    print(json.dumps(stats, indent=4))
