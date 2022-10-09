from models.model_region import Region
from pickled.model_peer import Peer
from dataclasses import dataclass
from typing import Optional

class Agent:
    node_num: int
    region: Region
    peer_ids: list[Peer]

    def __init__(self, node_num: int, region: Region, peer: Optional[Peer]):
        self.node_num = node_num
        self.region = region
        if peer is None:
            self.peer_ids = []
        else:
            self.peer_ids = [peer]

    def add_peer(self, peer):
        if peer not in self.peer_ids:
            self.peer_ids.append(peer)

    def __hash__(self):
        return hash(self.node_num)

    def __eq__(self, other):
        return hasattr(other, 'node_num') and self.node_num == other.node_num