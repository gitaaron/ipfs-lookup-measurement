from models.model_region import Region
from pickled.model_peer import Peer
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

class Agent:
    node_num: int
    region: Region
    peer_ids: list[Peer]

    def __init__(self, node_num: int, region: Region):
        self.node_num = node_num
        self.region = region
        self.peer_ids = []
        self.start_times = []

    def add_peer(self, peer):
        if peer not in self.peer_ids:
            self.peer_ids.append(peer)

    def __hash__(self):
        return hash(self.node_num)

    def __eq__(self, other):
        return hasattr(other, 'node_num') and self.node_num == other.node_num
