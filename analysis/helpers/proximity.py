from typing import List, Set

from pickled.model_retrieval import Retrieval
from models.model_region import Region

def is_nearest_neighbor(origin_region: Region, first_provider_region: Region, other_provider_regions: list[Region]):
    dist = origin_region.distance(first_provider_region)
    for provider_region in other_provider_regions:
        try:
            comp_dist = origin_region.distance(provider_region)

            if comp_dist < dist:
                return False

        except Exception as e:
            print('skipping other candidate provider in nearest comp: %s' % e)

    return True
