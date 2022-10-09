import geopy.distance
from typing import Tuple

# These lat/longs are based on the general region where the AWS datacenter is located in google maps since AWS does not provide official locations of their data centers.
#
# For the purposes of this experiment (determining which nodes in different cities are closer)
# this approximation should suffice.

name_coords_map = {
    'me_south_1': (26.046356864775923, 50.538634198559535), # Bahrain
    'ap_southeast_2': (-33.802116359682906, 151.13801505087193), # Sydney
    'af_south_1': (-33.864048786014315, 18.487253558675054), # Cape Town
    'us_west_1': (38.615248104516496, -121.51858586578618), # N. California / Sacramento
    'eu_central_1': (50.13890029070833, 8.736546836001605), # Frankfurt
    'sa_east_1': (-23.497812701529366, -46.679286631987864), # Sao Paulo
}


class Region:
    name: str
    latitude: float
    longitude: float

    def __init__(self, name: str):
        self.name = name
        self.coords = name_coords_map[name]

    @property
    def coords(self) -> Tuple[float, float]:
        return (self.latitude, self.longitude)

    @coords.setter
    def coords(self, coords: Tuple[float, float]):
        self.latitude = coords[0]
        self.longitude = coords[1]

    # Returns distance (km) between from_region and self
    def distance(self, from_region):
        return geopy.distance.geodesic(self.coords, from_region.coords).km

    def __repr__(self):
        return self.name

_cached_regions = {}

def from_name(name):
    if name not in _cached_regions:
        print('creating new region: %s' % name)
        _cached_regions[name] = Region(name)

    return _cached_regions[name]
