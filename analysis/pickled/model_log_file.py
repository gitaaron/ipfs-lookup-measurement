from logs.model_node_log_spec import NodeLogSpec
from pickled.model_retrieval import Retrieval
from pickled.model_publication import Publication
from pickled.model_agent import Agent
from pickled.model_sys_health import SysHealth
from datetime import datetime

class LogFile:

    started_at: datetime
    ended_at: datetime

    @property
    def region(self):
        return self.agent.region

    def __init__(
            self,
            started_at: datetime,
            ended_at: datetime,
            publications: list[Publication],
            retrievals: list[Retrieval],
            unattempted_retrieval_cids: list[str],
            agent: Agent,
            sys_health_events: list[SysHealth]):
        self.started_at = started_at
        self.ended_at = ended_at
        self.publications: list[Publication] = publications
        self.retrievals: list[Retrieval] = retrievals
        self.unattempted_retrieval_cids: list[str] = unattempted_retrieval_cids
        self.agent = agent
        self.sys_health_events = sys_health_events

    def __str__(self):
        return 'region: %s : %s ended_at: %s' % (self.region, self.started_at, self.ended_at)
