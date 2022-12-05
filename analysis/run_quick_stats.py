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

    stats['num_runs'] = len(data_set.runs.cid_run_map.values())
    stats['num_total_pubs'] = len(data_set.total_publications)

    '''
    for cid, run in data_set.runs.cid_run_map.items():
        print(f'pubs: {len(run.publications)}')

    for cid, run in data_set.runs.many_publish_runs.items():
        print('--start--')
        print('cid:%s rets:%d pubs:%d' % (cid, len(run.retrievals), len(run.publications)))
        print(f'unique add provider target peers:{run.num_add_provider_target_peers}')
        for ret in run.retrievals:
            print(f'first_referal_providers_count:{ret.first_referal_providers_count} first_provider_peer:{str(ret.first_provider_peer)} first_referal_peer:{str(ret.first_referer_to_fp)}')

        for pub in run.publications:
            print(f'success add queries num:{pub.num_successful_add_provider_queries} peers:{[p.id for p  in pub.successful_add_provider_target_peers]}')

        print('')
        print('--end--')
        print('')
    '''

    stats['avg_add_query_publish_success_peers'] = calc.avg_add_query_publish_success(data_set.total_publications)
    mp = {}
    mp['avg_unique_add_query_peers_per_run'] = calc.avg_unique_add_query_peers_per_run(data_set.runs.many_publish_runs)
    multi_publish_retrievals = reduce.by_main_player(data_set.total_completed_retrievals, constants.PlayerType.RETRIEVER)
    mp['percent_first_referer_in_add_query_list'] = calc.percent_retrievals_with_first_referer_in_add_query_list(multi_publish_retrievals, data_set.runs)
    mp['percent_hydra_referer_not_in_add_query_list'] = calc.percent_agent_not_in_add_query_list(multi_publish_retrievals, data_set.runs, 'hydra')
    stats['multi_publish'] = mp

    return stats

if __name__=='__main__':
    logs_config = LogsConfig('./log_config.json')
    stats = execute(logs_config)
    print(json.dumps(stats, indent=4, default=str))
