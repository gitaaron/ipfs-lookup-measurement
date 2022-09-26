import os
import json
import glob
from typing import List
from log_parse import load_parsed_logs, ParsedLogFile
from models.model_publication import Publication
from models.model_retrieval import Retrieval

def get_log_file_paths(log_dir):
    log_file_pat = f"{log_dir}/*.log"
    return glob.glob(log_file_pat)


def slow_retrievals(retrievals):
    return list(filter(lambda ret: (ret.duration_total().total_seconds() > 3), retrievals))

if __name__=='__main__':
    logs_config = json.load(open('./log_config.json'))
    latest_log_dir = os.path.join(logs_config['root_dir_path'], logs_config['latest_dir_name'])
    log_file_paths = get_log_file_paths(latest_log_dir)
    parsed_logs = load_parsed_logs(log_file_paths)

    publications: List[Publication] = []
    retrievals: List[Retrieval] = []

    for parsed_log in parsed_logs:
        publications += parsed_log.publications
        retrievals += parsed_log.completed_retrievals()

    many_providers_count = 0
    single_provider_count = 0
    total_providers = 0

    for r in retrievals:
        if len(r.provider_peers) > 1:
            many_providers_count += 1
        else:
            single_provider_count += 1

        total_providers += len(r.provider_peers)

    slow = slow_retrievals(retrievals)

    num_slow_many_providers = 0
    num_slow_one_provider = 0
    for sr in slow:
        if(len(sr.provider_peers)) > 1:
            num_slow_many_providers += 1
        else:
            num_slow_one_provider += 1

    stats = {}
    stats['num_retrievals'] = len(retrievals)
    stats['slow_retrievals (>3s)'] = len(slow)
    stats['percent_retrievals_are_slow'] = len(slow)/len(retrievals) * 100
    stats['many_providers_count'] = many_providers_count
    stats['single_provider_count'] = single_provider_count
    stats['avg_providers_per_retrieval'] = total_providers / len(retrievals)
    stats['slow_many_providers'] = f"{round(num_slow_many_providers/len(slow),3)*100}%"
    stats['slow_one_provider'] = f"{round(num_slow_one_provider/len(slow),3)*100}%"
    stats['many_providers_slow_likelyhood'] = f"{round(num_slow_many_providers/many_providers_count,3)*100}%"
    stats['one_provider_slow_likelyhood'] = f"{round(num_slow_one_provider/single_provider_count,3)*100}%"


    print(json.dumps(stats, indent=4))
