import json
from typing import Dict

from models.model_region import Region

agents = json.load(open('./agent_info.json'))

peer_id_agent_map = {}

def from_peer_id(peer_id: str):
    if peer_id in peer_id_agent_map:
        return peer_id_agent_map[peer_id]
    else:
        for agent in agents:
            if(agent['Peer_ID']==peer_id):
                peer_id_agent_map[peer_id] = Agent(agent)
                return peer_id_agent_map[peer_id]

        raise Exception('Peer_ID %s not found in agent list' % peer_id)

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
