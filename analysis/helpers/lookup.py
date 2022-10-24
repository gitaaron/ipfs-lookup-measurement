from models.model_region import Region

_region_num_map : dict[str,int]= {
    'me_south_1': 0,
    'ap_southeast_2': 1,
    'af_south_1': 2,
    'us_west_1': 3,
    'eu_central_1': 4,
    'sa_east_1': 5,

    # for docker generated logs
    'node0': 0,
    'node1': 1,
    'node2': 2,
}
# A temporary hardcoded mapping of regions to node_nums (should be in the log file)
def node_num_from_region(region: Region) -> int:
    return _region_num_map[region.name]
