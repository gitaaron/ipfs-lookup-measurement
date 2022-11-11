from pickled.model_agent import Agent
from datetime import datetime

class SysHealth:

    def __init__(
            self,
            agent: Agent,
            occurred: datetime,
            available_mem: int,
            load_avg_last_min: float):
        self.agent = agent
        self.occurred = occurred
        self.available_mem = available_mem
        self.load_avg_last_min = load_avg_last_min

    def __getitem__(self, i):
        if i == 'available_mem':
            return self.available_mem
        elif i == 'load_avg_last_min':
            return self.load_avg_last_min
