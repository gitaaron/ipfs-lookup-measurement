import json
from typing import List, Dict

from models.model_region import Region


class Agent:
    public_ip: str
    region_key: str
    node_num: int
    peer_id: str

    def __init__(self, agent: Dict):
        self.public_ip = agent['Public_ip']
        self.region_key = agent['Region_key']
        self.node_num = agent['Node_num']
        self.peer_id = agent['Peer_ID']

    def region(self):
        return Region(self.region_key)

class Agents:
    _peer_agents_map: List[Agent]

    def __init__(self, agents: List[Dict]):
        self._peer_agents_map = {}
        for a in agents:
            agent = Agent(a)
            self._peer_agents_map[agent.peer_id] = agent

    def agent_from_peer_id(self, peer_id: str,):

        if (peer_id not in self._peer_agents_map):
            raise Exception('Peer_ID %s not found in agent list' % peer_id)
        else:
            return self._peer_agents_map[peer_id]
