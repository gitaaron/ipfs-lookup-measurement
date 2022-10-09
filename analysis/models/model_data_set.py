from pickled.model_log_file import LogFile
from pickled.model_retrieval import Retrieval
from pickled.model_publication import Publication
from models.model_region import Region
from helpers import proximity, chronologist
from pickled.model_agent import Agent
from pickled.model_peer import Peer
from datetime import datetime
from models.model_agent_events import AgentEvents

class DataSet:
    _agents: list[Agent] = []
    _total_retrievals: list[Retrieval]
    _total_completed_retrievals: list[Retrieval]
    _has_first_provider_retrievals: list[Retrieval]
    _first_provider_nearest_retrievals: list[Retrieval]
    _non_first_provider_nearest_retrievals: list[Retrieval]
    _total_publications: list[Publication]
    _peer_agent_map: dict[Peer,Agent]
    _agent_events_map: dict[Agent, AgentEvents] = {}

    def __init__(self, logs: list[LogFile]):
        self._total_retrievals = None
        self._total_completed_retrievals = None
        self._total_publications = None
        self._has_first_provider_retrievals = None
        self._first_provider_nearest_retrievals = None
        self._non_first_provider_nearest_retrievals = None

        self.regions = []
        self._peer_agent_map = {}
        for log in logs:
            if log.agent not in self._agents:
                self._agents.append(log.agent)

            if log.agent not in self._agent_events_map:
                self._agent_events_map[log.agent] = AgentEvents(log.agent, log.retrievals, log.publications)
            else:
                self._agent_events_map[log.agent].add_events(log.retrievals, log.publications)

            for peer in log.agent.peer_ids:
                self._peer_agent_map[peer] = log.agent

    @property
    def agent_events_map(self) -> dict[Agent, AgentEvents]:
        return self._agent_events_map

    @property
    def total_retrievals(self):
        if(self._total_retrievals is None):
            self._total_retrievals = []
            for _,agent_events in self._agent_events_map.items():
                self._total_retrievals += agent_events.retrievals

        return self._total_retrievals

    @property
    def total_publications(self):
        if(self._total_publications is None):
            self._total_publications = []
            for _,agent_events in self._agent_events_map.items():
                self._total_publications += agent_events.publications

        return self._total_publications


    @property
    def total_completed_retrievals(self):
        if(self._total_completed_retrievals is None):
            self._total_completed_retrievals = []
            for _,agent_events in self._agent_events_map.items():
                self._total_completed_retrievals += agent_events.completed_retrievals

        return self._total_completed_retrievals

    @property
    def has_first_provider_retrievals(self):
        if(self._has_first_provider_retrievals is None):
            self._has_first_provider_retrievals = list(
                    filter(lambda ret: ret.first_provider_peer is not None, self.total_completed_retrievals))

        return self._has_first_provider_retrievals

    def _set_fpns(self):
        if(self._first_provider_nearest_retrievals is None or self._non_first_provider_nearest_retrievals is None):
            self._first_provider_nearest_retrievals = []
            self._non_first_provider_nearest_retrievals = []

            print('num has_first: %s' % len(self.has_first_provider_retrievals))
            for ret in self.has_first_provider_retrievals:
                try:
                    first_provider_region = self.agent_from_peer_id(ret.first_provider_peer).region
                    other_provider_regions = []
                    for peer in ret.provider_peers:
                        if ret.first_provider_peer == peer:
                            continue
                        other_provider_regions.append(self.agent_from_peer_id(peer).region)
                    if(proximity.is_nearest_neighbor(
                            ret.origin,
                            first_provider_region,
                            other_provider_regions) == True):
                        self._first_provider_nearest_retrievals.append(ret)
                    else:
                        self._non_first_provider_nearest_retrievals.append(ret)

                except Exception as e:
                    print("skipping cid: %s is_nearest_neighbor can not be calculated: %s" % (ret.cid, e))

    @property
    def first_provider_nearest_retrievals(self):
        self._set_fpns()
        return self._first_provider_nearest_retrievals

    @property
    def non_first_provider_nearest_retrievals(self):
        self._set_fpns()
        return self._non_first_provider_nearest_retrievals


    def agent_from_peer_id(self, peer):
        return self._peer_agent_map[peer]

    @property
    def started_ended_at(self) -> tuple[datetime, datetime]:
        _started_at: datetime = None
        _ended_at: datetime = None
        for log in self._logs:
            _started_at, _ended_at = chronologist.get_start_end(_started_at, _ended_at, log.started_at, log.ended_at)

        return (_started_at, _ended_at)