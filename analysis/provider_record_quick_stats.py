import json
from logs.model_logs_config import LogsConfig
from logs import load
from models.model_data_set import DataSet
from models.model_run import Run
from models.model_runs import Runs

from pickled.model_publication import Publication
from pickled.model_retrieval import Retrieval

from helpers import calc, breakdowns, reduce, constants

def execute(logs_config: LogsConfig) -> dict:
    #data_set: DataSet = load.latest_data_set(logs_config)
    data_set: DataSet = load.complete_data_set(logs_config)

    stats = {}

    stats['avg_provider_peers_found'] = calc.avg_provider_peers_found(data_set.total_completed_retrievals)

    mp = {}
    many_publish_retrievals = reduce.by_main_player(data_set.total_completed_retrievals, constants.PlayerType.RETRIEVER)
    mp['avg_provider_peers_found'] = calc.avg_provider_peers_found(many_publish_retrievals)

    small_retrievals = reduce.by_file_size(many_publish_retrievals, data_set.smallest_file_size)
    low_providers_found_small_retrievals = reduce.by_providers_found(small_retrievals, 3)
    stats['num_many_publish_small_retrievals'] = len(small_retrievals)
    stats['num_low_providers_found_small_retrievals'] = len(low_providers_found_small_retrievals)
    stats['low_providers_found_durations(3)'] = breakdowns.avg_phase_duration_breakdown(low_providers_found_small_retrievals)

    low_providers_in_first_referer_small_retrievals = reduce.by_first_referer_provider_peers(small_retrievals, 2)
    stats['num_low_providers_in_first_referer'] = len(low_providers_in_first_referer_small_retrievals)
    stats['low_providers_in_first_referer_durations(2)'] = breakdowns.avg_phase_duration_breakdown(low_providers_in_first_referer_small_retrievals)

    stats['many_publish'] = mp

    return stats

if __name__=='__main__':
    logs_config = LogsConfig('./log_config.json')
    stats = execute(logs_config)
    print(json.dumps(stats, indent=4, default=str))
