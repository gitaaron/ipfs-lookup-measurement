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
    total_providers = 0

    for r in retrievals:
        if len(r.provider_peers) > 1:
            many_providers_count += 1
        total_providers += len(r.provider_peers)

    stats = {}
    stats['num_retrievals'] = len(retrievals)
    stats['many_providers_count'] = many_providers_count
    stats['avg_providers_per_retrieval'] = total_providers / len(retrievals)

    print(json.dumps(stats, indent=4))
