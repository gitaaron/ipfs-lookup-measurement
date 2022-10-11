from pickled.model_log_file import LogFile
from pickled.model_retrieval import Retrieval
from pickled.model_publication import Publication
from models.model_region import Region
from helpers import proximity, chronologist, map, constants
from pickled.model_agent import Agent
from pickled.model_peer import Peer
from datetime import datetime, timedelta
from models.model_agent_events import AgentEvents
from models.model_duration import Duration
import numpy as np

class DataSet:
    _agents: list[Agent] = []
    _total_retrievals: list[Retrieval]
    _total_completed_retrievals: list[Retrieval]
    _has_first_provider_retrievals: list[Retrieval]
    _first_provider_nearest_retrievals: list[Retrieval]
    _non_first_provider_nearest_retrievals: list[Retrieval]
    _retrievals_has_uptime: list[Retrieval]
    _total_publications: list[Publication]
    _peer_agent_map: dict[Peer,Agent]
    _agent_events_map: dict[Agent, AgentEvents] = {}
    _unique_file_sizes: dict[int, int] = None
    _phase_durations: dict = None
    _uptime_durations: dict = None

    def __init__(self, logs: list[LogFile]):
        self._total_retrievals = None
        self._total_completed_retrievals = None
        self._total_publications = None
        self._has_first_provider_retrievals = None
        self._first_provider_nearest_retrievals = None
        self._non_first_provider_nearest_retrievals = None
        self._retrievals_has_uptime = None

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

    def _set_completed_stats(self):

        if self._unique_file_sizes is None or self._phase_durations is None or self._uptime_durations:
            self._unique_file_sizes = {}
            self._phase_durations = {}
            self._uptime_durations = { 'count': 0, 'total': 0 }
            for phase in constants.RetrievalPhase:
                self._phase_durations[phase] = 0
        
            for ret in self.total_completed_retrievals:
                if ret.file_size not in self._unique_file_sizes:
                    self._unique_file_sizes[ret.file_size] = { 'count' : 1, 'durations': ret.all_durations}
                else:
                    self._unique_file_sizes[ret.file_size]['count'] += 1
                    self._unique_file_sizes[ret.file_size]['durations'] = map.add_keys(self._unique_file_sizes[ret.file_size]['durations'], ret.all_durations)

                self._phase_durations = map.add_keys(self._phase_durations, ret.all_durations)

                if ret.agent_uptime is not None:
                    self._uptime_durations['count'] += 1
                    if('max' not in self._uptime_durations or self._uptime_durations['max'] < ret.agent_uptime):
                        self._uptime_durations['max'] = ret.agent_uptime
                    if('min' not in self._uptime_durations or self._uptime_durations['min'] > ret.agent_uptime):
                        self._uptime_durations['min'] = ret.agent_uptime
                    self._uptime_durations['total'] += ret.agent_uptime.total_seconds()


            if self._uptime_durations['count'] > 0:
                self._uptime_durations['max'] = Duration(self._uptime_durations['max'].total_seconds())
                self._uptime_durations['min'] = Duration(self._uptime_durations['min'].total_seconds())
                self._uptime_durations['avg_uptime'] = Duration(self._uptime_durations['total'] / self._uptime_durations['count'])


    @property
    def agent_uptime_durations(self) -> dict[str, timedelta]:
        self._set_completed_stats()
        return self._uptime_durations

    @property
    def phase_durations(self):
        self._set_completed_stats()
        return self._phase_durations


    @property
    def unique_file_sizes(self):
        self._set_completed_stats()
        return self._unique_file_sizes

    @property

    def retrievals_has_uptime(self):
        if self._retrievals_has_uptime is None:
            self._retrievals_has_uptime = list(filter(lambda ret: ret.agent_uptime is not None, self.total_completed_retrievals))

        return self._retrievals_has_uptime



    def _set_fpns(self):
        if(self._first_provider_nearest_retrievals is None or self._non_first_provider_nearest_retrievals is None):
            self._first_provider_nearest_retrievals = []
            self._non_first_provider_nearest_retrievals = []

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