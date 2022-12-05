from pickled.model_retrieval import Retrieval
from models.model_data_set import DataSet
from models.model_time_interval import TimeInterval
from helpers.constants import RetrievalPhase, PlayerType, SLOW_THRESHOLD
from models.model_runs import Runs

def by_slow_retrievals(data_set: DataSet, retrievals: list[Retrieval], phase: RetrievalPhase) -> list[Retrieval]:
    return list(filter(lambda ret: data_set.is_slow(ret, phase), retrievals))

def by_fast_retrievals(data_set: DataSet, retrievals: list[Retrieval], phase: RetrievalPhase) -> list[Retrieval]:
    return list(filter(lambda ret: data_set.is_fast(ret, phase), retrievals))

def by_has_file_size(retrievals: list[Retrieval]) -> list[Retrieval]:
    return list(filter(lambda ret: (ret.file_size is not None), retrievals))

def by_file_size(retrievals: list[Retrieval], file_size: int) -> list[Retrieval]:
    return list(filter(lambda ret: (ret.file_size is not None and int(ret.file_size)==file_size), retrievals))

def by_comparable_file_sizes(retrievals: list[Retrieval]) -> list[Retrieval]:
    return list(filter(lambda ret: (ret.file_size is not None and int(ret.file_size)!=52439), retrievals))

def by_main_player(retrievals: list[Retrieval], player: PlayerType):
    if player==PlayerType.RETRIEVER:
        return list(filter(lambda ret: len(ret.provider_peers) > 1, retrievals))
    elif player==PlayerType.PUBLISHER:
        return list(filter(lambda ret: len(ret.provider_peers) == 1, retrievals))
    else:
        raise Exception('Invalid player type: %s' % player)

def by_first_referer(retrievals: list[Retrieval], agent_name: str):
    return list(filter(lambda ret: (agent_name in ret.first_referer_to_fp.agent_version), retrievals))

def by_least_num_providers(retrievals: list[Retrieval], num_providers: int):
    return list(filter(lambda ret: len(ret.provider_peers) >= num_providers, retrievals))


def _publish_age_within_bounds(data_set: DataSet, retrieval: Retrieval, publish_age_interval: TimeInterval):
    publish_age = data_set.publish_age(retrieval)
    if publish_age is None:
        return False

    return publish_age > publish_age_interval.start and publish_age < publish_age_interval.end

def by_publish_age_interval(data_set: DataSet, retrievals: list[Retrieval], publish_age_interval: TimeInterval):
    return list(filter(lambda ret: _publish_age_within_bounds(data_set, ret, publish_age_interval), retrievals))

def by_referer_in_successful_add_list(rets: list[Retrieval], runs: Runs, test: bool = True) -> list[Retrieval]:
    return list(filter(lambda ret: runs.from_cid(ret.cid).first_referer_in_successful_add_target_peer_list(ret) == False, rets))

def by_providers_found(rets: list[Retrieval], threshold_providers_found: int) -> list[Retrieval]:
    return list(filter(lambda ret: ret.num_provider_peers_found <= threshold_providers_found, rets))

def by_first_referer_provider_peers(rets: list[Retrieval], threshold_provider_peers: int) -> list[Retrieval]:
    return list(filter(lambda ret: ret.first_referal_providers_count <= threshold_provider_peers, rets))
