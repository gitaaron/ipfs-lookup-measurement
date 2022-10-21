import json, os
from pickled.model_log_file import LogFile
from pickled.model_publication import Publication
from pickled.model_retrieval import Retrieval
from pickled.model_agent import Agent

from logs.model_node_log_spec import NodeLogSpec
from parse.model_log_line import IPFSLogLine, AgentLogLine
from datetime import datetime
from helpers import chronologist, lookup


def from_log_file_spec(log_file_spec: NodeLogSpec) -> LogFile:

    started_at: datetime = None
    ended_at: datetime = None


    # CIDs that were not attempted to query
    unattempted_retrieval_cids: list[str] = []
    sealed_publications: dict[str, Publication] = {}
    sealed_retrievals: dict[str, Retrieval] = {}

    print("Parsing: ", log_file_spec.ipfs_path)

    with open(log_file_spec.ipfs_path, 'r') as f:
        publications: dict[str, Publication] = {}
        retrievals: dict[str, Retrieval] = {}

        for idx, line in enumerate(reversed(f.readlines())):
            try:
                log = IPFSLogLine.from_dict(json.loads(line))
                if (pll := log.is_start_providing()) is not None:
                    publications[pll.cid] = Publication(log_file_spec.region, pll.cid, pll.timestamp)
                if (pll := log.is_start_getting_closest_peers()) is not None and pll.cid in publications:
                    publications[pll.cid].getting_closest_peers_started(
                        pll.timestamp)
                elif (pll := log.is_getting_closest_peers()) is not None and pll.cid in publications:
                    publications[pll.cid].find_node_query_started(
                        pll.remote_peer, pll.timestamp)
                elif (pll := log.is_got_closest_peers()) is not None and (
                        pll.cid in publications or pll.cid in retrievals):
                    if pll.cid in publications:
                        publications[pll.cid].find_node_query_ended(
                            pll.remote_peer, pll.timestamp, pll.closest_peers)
                    else:
                        retrievals[pll.cid].got_closer_peers_from(
                            pll.remote_peer, pll.timestamp, pll.closest_peers)
                elif (pll := log.is_error_getting_closest_peers()) is not None and pll.cid in publications:
                    publications[pll.cid].find_node_query_ended(
                        pll.remote_peer, pll.timestamp, [], pll.error_str)
                elif (pll := log.is_pvd_dht_walk_end()) is not None and pll.cid in publications:
                    publications[pll.cid].dht_walk_ended(
                        pll.timestamp, pll.closest_peers)
                elif (pll := log.is_add_provider_started()) is not None and pll.cid in publications:
                    publications[pll.cid].add_provider_started(
                        pll.remote_peer, pll.timestamp)
                elif (pll := log.is_add_provider_success()) is not None and pll.cid in publications:
                    publications[pll.cid].add_provider_success(
                        pll.remote_peer, pll.timestamp)
                elif (pll := log.is_add_provider_error()) is not None and pll.cid in publications:
                    publications[pll.cid].add_provider_error(
                        pll.remote_peer, pll.timestamp, pll.error_str)
                elif pll := log.is_get_provider_success():
                    if len(publications) == 1:
                        publications[list(publications.keys())[0]].get_provider_success(
                            pll.remote_peer, pll.timestamp)
                    else:
                        for cid in publications:
                            if pll.remote_peer in publications[cid].get_provider_queries:
                                print(
                                    f"Multiple publications going on: {pll.remote_peer.id} ({pll.remote_peer.agent_version}) "
                                    f"using CID: {cid} - {' '.join(list(publications.keys()))}"
                                )
                                publications[cid].get_provider_success(
                                    pll.remote_peer, pll.timestamp)
                                break
                            print(
                                f"not using peer {pll.remote_peer} for cid {cid}")
                elif (pll := log.is_get_provider_error()) is not None and pll.cid in publications:
                    publications[pll.cid].get_provider_error(
                        pll.remote_peer, pll.timestamp, pll.error_str)
                elif (pll := log.is_finish_providing()) is not None:
                    publications[pll.cid].seal(pll.timestamp)
                    sealed_publications[pll.cid] = publications[pll.cid]
                    del publications[pll.cid]

                elif (pll := log.is_start_retrieving()) is not None:
                    retrievals[pll.cid] = Retrieval(log_file_spec.region, pll.cid, pll.timestamp)
                elif (pll := log.is_start_searching_pvd()) is not None and pll.cid in retrievals:
                    retrievals[pll.cid].getting_provider_peers_started(
                        pll.timestamp)
                elif (pll := log.is_start_getting_providers()) is not None and pll.cid in retrievals:
                    retrievals[pll.cid].getting_providers_from(
                        pll.remote_peer, pll.timestamp)
                elif (pll := log.is_found_provider_entries()) is not None:
                    for cid in retrievals:
                        if pll.remote_peer in retrievals[cid].get_providers_queries:
                            retrievals[cid].found_providers_from(
                                pll.remote_peer, pll.timestamp, pll.count)
                            break
                elif (pll := log.is_pvd_found()) is not None and pll.cid in retrievals:
                    if retrievals[pll.cid].found_first_provider_at is None or retrievals[
                            pll.cid].found_first_provider_at > pll.timestamp:
                        retrievals[pll.cid].found_first_provider_at = pll.timestamp
                    retrievals[pll.cid].provider_record_storing_peers.add(
                        pll.remote_peer)
                    retrievals[pll.cid].provider_peers.add(pll.other_peer)
                elif (pll := log.is_bitswap_connect()) is not None:
                    for cid in retrievals:
                        if pll.remote_peer in retrievals[cid].provider_peers:
                            retrievals[cid].start_dialing_provider(
                                pll.remote_peer, pll.timestamp)
                            break
                elif (pll := log.is_bitswap_connected()) is not None:
                    for cid in retrievals:
                        if pll.remote_peer in retrievals[cid].provider_peers:
                            retrievals[cid].bitswap_connected(
                                pll.remote_peer, pll.timestamp)
                            break
                elif (pll := log.is_connected_to_pvd()) is not None and pll.cid in retrievals:
                    retrievals[pll.cid].connected_to_provider(
                        pll.remote_peer, pll.other_peer, pll.timestamp)
                elif (pll := log.is_got_provider()) is not None and pll.cid in retrievals:
                    retrievals[pll.cid].received_HAVE_from_provider(
                        pll.remote_peer, pll.timestamp)
                elif (pll := log.is_done_retrieving_first_block()) is not None and pll.cid in retrievals:
                    retrievals[pll.cid].done_retrieving_first_block(
                        pll.timestamp, pll.error_str)
                    if retrievals[pll.cid].marked_for_removal:
                        sealed_retrievals[pll.cid] = retrievals[pll.cid]
                        del retrievals[pll.cid]
                    else:
                        retrievals[pll.cid].marked_for_removal = True
                elif (pll := log.is_finish_searching_pvd()) is not None and pll.cid in retrievals:
                    retrievals[pll.cid].finish_searching_providers(
                        pll.timestamp, pll.error_str)
                    if retrievals[pll.cid].state == Retrieval.State.DONE_WITHOUT_ASKING_PEERS:
                        unattempted_retrieval_cids.append(pll.cid)
                    if retrievals[pll.cid].marked_for_removal:
                        sealed_retrievals[pll.cid] = retrievals[pll.cid]
                        del retrievals[pll.cid]
                    else:
                        retrievals[pll.cid].marked_for_removal = True

            except Exception as e:
                print('Failed parsing IPFS line.')
                print('Line: %s' % log.line)
                print('Reason: %s' % str(e))


    agent: Agent = Agent(lookup.node_num_from_region(log_file_spec.region), log_file_spec.region)

    if log_file_spec.has_agent_log:
        print("Parsing: ", log_file_spec.agent_path)
        with open(log_file_spec.agent_path, 'r') as f:
            for idx, line in enumerate(reversed(f.readlines())):
                try:
                    log = AgentLogLine.from_dict(json.loads(line))
                    if (pll := log.is_start_retrieving()) and pll.cid in sealed_retrievals:
                        sealed_retrievals[pll.cid].agent_initiated(pll.timestamp, pll.file_size)
                    elif (pll := log.is_finished_retrieving()) and pll.cid in sealed_retrievals:
                        sealed_retrievals[pll.cid].done_retrieving(pll.timestamp, pll.file_size)
                    elif (pll := log.is_get_id()):
                        agent.add_peer(pll.peer)
                    elif (pll := log.is_start_listening()):
                        agent.add_start_time(pll.timestamp)

                except Exception as e:
                    print('Failed parsing Agent line.')
                    print('Line: %s' % log.line)
                    print('Reason: %s' % str(e))
    else:
        print('Skipping parse of agent as it does not exist: ', log_file_spec.agent_path)

    publications = []
    for _,publication in sealed_publications.items():
        started_at, ended_at = chronologist.get_start_end(started_at, ended_at, publication.provide_started_at, publication.provide_ended_at)
        publications.append(publication)

    retrievals = []
    for _,retrieval in sealed_retrievals.items():
        started_at, ended_at = chronologist.get_start_end(started_at, ended_at, retrieval.retrieval_started_at, retrieval.done_retrieving_at)
        most_recent = agent.most_recent_start_time(retrieval.retrieval_started_at)
        if most_recent is not None:
            retrieval.agent_started_at = most_recent

        retrievals.append(retrieval)


    return LogFile(started_at, ended_at, publications, retrievals, unattempted_retrieval_cids, agent)
