from typing import List, Set

from models.model_retrieval import Retrieval
from models.model_peer import Peer
from models.model_region import Region
from models.model_agent import Agents


def is_nearest_neighbor(agents: Agents, origin_region: Region, first_provider_peer: Peer, all_provider_peers: Set[Peer]):
    first_provider_region = agents.agent_from_peer_id(first_provider_peer.id).region()
    dist = origin_region.distance(first_provider_region)
    for provider_peer in all_provider_peers:
        if(provider_peer.id==first_provider_peer.id):
            continue
        try:
            provider_region = agents.agent_from_peer_id(provider_peer.id).region()

            comp_dist = origin_region.distance(provider_region)

            if comp_dist < dist:
                return False

        except Exception as e:
            print('skipping other candidate provider in nearest comp: %s' % e)

    return True
