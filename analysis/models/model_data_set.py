from pickled.model_log_file import LogFile
from pickled.model_retrieval import Retrieval
from pickled.model_publication import Publication
from pickled.model_sys_health import SysHealth
from models.model_region import Region
from helpers import proximity, chronologist, map, constants, breakdowns
from pickled.model_agent import Agent
from pickled.model_peer import Peer
from datetime import datetime, timedelta
from models.model_agent_events import AgentEvents
from models.model_duration import Duration
from models.model_runs import Runs
import numpy as np

class DataSet:
    _logs: list[LogFile]
    _agents: list[Agent] = []
    _total_retrievals: list[Retrieval]
    _total_completed_retrievals: list[Retrieval]
    _has_first_provider_retrievals: list[Retrieval]
    _first_provider_nearest_retrievals: list[Retrieval]
    _non_first_provider_nearest_retrievals: list[Retrieval]
    _many_provider_retrievals: list[Retrieval]
    _single_provider_retrievals: list[Retrieval]
    _retrievals_has_uptime: list[Retrieval]
    _total_publications: list[Publication]
    _peer_agent_map: dict[Peer,Agent]
    _agent_events_map: dict[Agent, AgentEvents]
    _phase_durations: dict = None
    _uptime_durations: dict = None

    def __init__(self, logs: list[LogFile]):
        self._logs = logs
        self._total_retrievals = None
        self._total_completed_retrievals = None
        self._total_publications = None
        self._has_first_provider_retrievals = None
        self._first_provider_nearest_retrievals = None
        self._non_first_provider_nearest_retrievals = None
        self._many_provider_retrievals = None
        self._single_provider_retrievals = None
        self._retrievals_has_uptime = None
        self._agent_events_map = {}
        self._peer_agent_map = {}
        self._runs: Runs = None
        self._has_publish_age_retrievals: list[Retrieval] = None
        self._publish_age_stats: dict = None
        self._publish_age_retrievals: list[Retrieval] = None
        self._comparable_file_size_retrievals: dict[int, list[Retrieval]]= None
        self._file_size_retrievals: dict[int, list[Retrieval]]= None
        self._file_size_means: dict[int, dict[RetrievalPhase, Duration]] = None
        self._file_size_deviations: dict[int, dict[RetrievalPhase, Duration]] = None
        self._sys_health_events: list[SysHealth] = []

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

            self._sys_health_events += log.sys_health_events

    @property
    def agent_events_map(self) -> dict[Agent, AgentEvents]:
        return self._agent_events_map

    @property
    def sys_health_events(self) -> list[SysHealth]:
        return self._sys_health_events

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

    def exclude_file_size(self, file_size: int) -> bool:
        return file_size is None or file_size == 52439

    @property
    def file_size_retrievals(self):
        if(self._file_size_retrievals is None):
            self._file_size_retrievals = {}
            for ret in self.total_completed_retrievals:
                if ret.file_size not in self._file_size_retrievals:
                    self._file_size_retrievals[ret.file_size] = [ret]
                else:
                    self._file_size_retrievals[ret.file_size].append(ret)

        return self._file_size_retrievals


    @property
    def comparable_file_size_retrievals(self):
        if(self._comparable_file_size_retrievals is None):
            self._comparable_file_size_retrievals = {}
            for ret in self.total_completed_retrievals:
                if self.exclude_file_size(ret.file_size):
                    continue
                if ret.file_size not in self._comparable_file_size_retrievals:
                    self._comparable_file_size_retrievals[ret.file_size] = [ret]
                else:
                    self._comparable_file_size_retrievals[ret.file_size].append(ret)

        return self._comparable_file_size_retrievals

    def percent_slow(self, retrievals: list[Retrieval], phase) -> tuple[float,int]:
        slow_retrievals = list(filter(lambda ret: self.is_slow(ret, phase), retrievals))
        if len(retrievals)>0:
            return round(len(slow_retrievals)/len(retrievals)*100, 2),len(retrievals)
        else:
            return 0,len(retrievals)

    # a retrieval is considered slow if it is more than one standard deviation greater than the mean
    # for retrievals of the same file size
    def is_slow(self, ret: Retrieval, phase: constants.RetrievalPhase) -> bool:
        mean = self.file_size_means[ret.file_size][phase]
        std = self.file_size_deviations[ret.file_size][phase]
        return ret.duration(phase).total_seconds() > (mean.duration + std.duration)

    def is_fast(self, ret: Retrieval, phase: constants.RetrievalPhase) -> bool:
        mean = self.file_size_means[ret.file_size][phase]
        return ret.duration(phase).total_seconds() < mean.duration

    @property
    def file_size_means(self):
        if  self._file_size_means is None:
            self._file_size_means = breakdowns.avg_phase_duration_from_breakdown(self.file_size_retrievals)

        return self._file_size_means

    @property
    def file_size_deviations(self):
        if self._file_size_deviations is None:
            self._file_size_deviations = breakdowns.std_from_breakdown(self.file_size_retrievals)
        return self._file_size_deviations

    def _set_completed_stats(self):

        if self._phase_durations is None or self._uptime_durations:
            self._phase_durations = {}
            self._uptime_durations = { 'count': 0, }
            for phase in constants.RetrievalPhase:
                self._phase_durations[phase] = 0

            _total_uptime_duration = 0
            for ret in self.total_completed_retrievals:
                self._phase_durations = map.add_keys(self._phase_durations, ret.all_durations)

                if hasattr(ret, 'agent_uptime') and ret.agent_uptime is not None:
                    self._uptime_durations['count'] += 1
                    if('max' not in self._uptime_durations or self._uptime_durations['max'] < ret.agent_uptime):
                        self._uptime_durations['max'] = ret.agent_uptime
                    if('min' not in self._uptime_durations or self._uptime_durations['min'] > ret.agent_uptime):
                        self._uptime_durations['min'] = ret.agent_uptime
                    _total_uptime_duration += ret.agent_uptime


            if self._uptime_durations['count'] > 0:
                self._uptime_durations['max'] = Duration(self._uptime_durations['max']/1000)
                self._uptime_durations['min'] = Duration(self._uptime_durations['min']/1000)
                self._uptime_durations['avg_uptime'] = Duration(_total_uptime_duration / self._uptime_durations['count']/1000)


    @property
    def agent_uptime_durations(self) -> dict[str, timedelta]:
        self._set_completed_stats()
        return self._uptime_durations

    @property
    def phase_durations(self):
        self._set_completed_stats()
        return self._phase_durations


    @property
    def comparable_file_sizes(self):
        cpy = list(self.comparable_file_size_retrievals.keys())
        cpy.sort()
        return cpy

    @property
    def smallest_file_size(self):
        smallest = None
        for fs in self.comparable_file_sizes:
            if smallest is None or fs < smallest:
                smallest = fs

        return smallest

    @property
    def retrievals_has_uptime(self):
        if self._retrievals_has_uptime is None:
            self._retrievals_has_uptime = list(filter(lambda ret: hasattr(ret, 'agent_uptime') and ret.agent_uptime is not None, self.total_completed_retrievals))

        return self._retrievals_has_uptime


    def _set_has_many_providers(self):
        if(self._many_provider_retrievals is None or self._single_provider_retrievals is None):
            self._many_provider_retrievals = []
            self._single_provider_retrievals = []

            for ret in self.has_first_provider_retrievals:
                if(len(ret.provider_peers) > 1):
                    self._many_provider_retrievals.append(ret)
                else:
                    self._single_provider_retrievals.append(ret)

    @property
    def many_provider_retrievals(self):
        self._set_has_many_providers()
        return self._many_provider_retrievals


    @property
    def single_provider_retrievals(self):
        self._set_has_many_providers()
        return self._single_provider_retrievals


    def _set_fpns(self):
        if(self._first_provider_nearest_retrievals is None or self._non_first_provider_nearest_retrievals is None):
            self._first_provider_nearest_retrievals = []
            self._non_first_provider_nearest_retrievals = []

            for ret in self.many_provider_retrievals:
                fp = self.agent_from_peer_id(ret.first_provider_peer)
                if fp == None:
                    print(f"skipping cid: {ret.cid} because first provider peer: {ret.first_provider_peer} is not in agent list")
                    continue

                first_provider_region = fp.region
                other_provider_regions = []
                found_unknown = False
                for peer in ret.provider_peers:
                    if ret.first_provider_peer == peer:
                        continue
                    op = self.agent_from_peer_id(peer)
                    if op == None:
                        print(f"skipping cid: {ret.cid} because other provider peer: {peer} is not in agent list")
                        found_unknown = True
                        continue
                    other_provider_regions.append(op.region)
                if found_unknown:
                    continue
                if(proximity.is_nearest_neighbor(
                        ret.origin,
                        first_provider_region,
                        other_provider_regions) == True):
                    self._first_provider_nearest_retrievals.append(ret)
                else:
                    self._non_first_provider_nearest_retrievals.append(ret)

    @property
    def first_provider_nearest_retrievals(self):
        self._set_fpns()
        return self._first_provider_nearest_retrievals

    @property
    def non_first_provider_nearest_retrievals(self):
        self._set_fpns()
        return self._non_first_provider_nearest_retrievals


    def agent_from_peer_id(self, peer) -> Agent:
        if peer in self._peer_agent_map:
            return self._peer_agent_map[peer]
        else:
            return None

    @property
    def started_ended_at(self) -> tuple[datetime, datetime]:
        _started_at: datetime = None
        _ended_at: datetime = None
        for log in self._logs:
            _started_at, _ended_at = chronologist.get_start_end(_started_at, _ended_at, log.started_at, log.ended_at)

        return (_started_at, _ended_at)

    @property
    def runs(self) -> Runs:
        if self._runs == None:
            self._runs = Runs(self.total_publications)

        return self._runs

    @property
    def has_publish_age_retrievals(self):
        if self._has_publish_age_retrievals is None:
            self._has_publish_age_retrievals = list(
                filter(lambda ret: self.publish_age(ret) is not None, self.total_completed_retrievals))
        return self._has_publish_age_retrievals

    def publish_age(self, retrieval: Retrieval) -> timedelta:
        published_at = self.runs.first_publish_at(retrieval.cid)
        if published_at != None:
            return retrieval.retrieval_started_at - published_at
        else:
            return None

    @property
    def publish_age_stats(self) -> tuple[dict, list[Retrieval], int]:
        if self._publish_age_stats is None or self._publish_age_retrievals is None:
            self._publish_age_stats = {}
            # filtering by 52439 since there is not even distribution of publish/retrieval delays and filesizes
            self._publish_age_retrievals = list(
                    filter(lambda ret: ret.file_size is not None and int(ret.file_size) == constants.DELAY_FILE_SIZE, self.has_publish_age_retrievals))
            self._publish_age_stats['count'] = len(self._publish_age_retrievals)
            total = 0
            min = None
            max = None

            for ret in self._publish_age_retrievals:
                pub_age = self.publish_age(ret).total_seconds()
                if max is None or max < pub_age:
                    max = pub_age
                if min is None or min > pub_age:
                    min = pub_age
                total +=  pub_age

            self._publish_age_stats['min'] = round(min,3)
            self._publish_age_stats['max'] = round(max,1)
            self._publish_age_stats['average'] = round(total/len(self._publish_age_retrievals),1)

        return (self._publish_age_stats, self._publish_age_retrievals, constants.DELAY_FILE_SIZE)
