from typing import List, Set

from models.model_retrieval import Retrieval
from models.model_peer import Peer
from models.model_region import Region
from models import model_agent


def is_nearest_neighbor(origin_region: Region, first_provider_peer: Peer, all_provider_peers: Set[Peer]):
    first_provider_region = model_agent.from_peer_id(first_provider_peer.id).region()
    dist = origin_region.distance(first_provider_region)
    for provider_peer in all_provider_peers:
        if(provider_peer.id==first_provider_peer.id):
            continue
        provider_region = model_agent.from_peer_id(provider_peer.id).region()

        comp_dist = origin_region.distance(provider_region)

        if comp_dist < dist:
            return False

    return True




def percent_nearest_neighbor_first_provider(retrievals: List[Retrieval]):
    total = len(retrievals)

    num_has_first_provider = 0
    num_nearest_fetches = 0

    for ret in retrievals:
        if(ret.first_provider_peer is not None):
            num_has_first_provider += 1

            try:
                if(is_nearest_neighbor(ret.region_of_origin(), ret.first_provider_peer, ret.provider_peers) == True):
                    num_nearest_fetches += 1
            except Exception as e:
                print("skipping is_nearest_neighbor calculation: %s" % e)


    print('num_has_first_provider %s' % num_has_first_provider)

    return num_nearest_fetches / num_has_first_provider * 100
