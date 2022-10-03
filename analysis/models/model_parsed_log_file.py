from typing import List
from models.model_retrieval import Retrieval
from models.model_publication import Publication
from models.model_region_log_file import RegionLogFile
from models.model_agent import Agent, Agents
from helpers import proximity



class ParsedLogFile:

    @property
    def _region(self):
        return self.region_log_file.region

    _completed_retrievals: List[Retrieval] = None

    def completed_retrievals(self):
        if(self._completed_retrievals==None):
            self._completed_retrievals = []
            # Remove all retrievals that are marked as invalid
            before = len(self.retrievals)
            self._completed_retrievals = list(
                filter(lambda ret: not ret.marked_as_incomplete, self.retrievals))
            print(
                f"Removed {before - len(self._completed_retrievals)} of {before} retrievals because they were incomplete for region {self._region.name}")

            before = len(self._completed_retrievals)

            self._completed_retrievals = list(filter(lambda ret: ret.state !=
                            Retrieval.State.DONE_WITHOUT_ASKING_PEERS, self._completed_retrievals))
            print(
                f"Removed {before - len(self._completed_retrievals)} of {before} retrievals because they were not started for region {self._region.name}")  # error in our measurement setup

        return self._completed_retrievals


    def __init__(
            self,
            region_log_file: RegionLogFile,
            publications: List[Publication],
            retrievals: List[Retrieval],
            unattempted_retrieval_cids: List[str]):
        self.region_log_file: RegionLogFile = region_log_file
        self.publications: List[Publication] = publications
        self.retrievals: List[Retrieval] = retrievals
        self.unattempted_retrieval_cids: List[str] = unattempted_retrieval_cids


class ParsedLogFiles:
    _logs: List[ParsedLogFile]
    _total_retrievals: List[Retrieval]
    _total_completed_retrievals: List[Retrieval]
    _has_first_provider_retrievals: List[Retrieval]
    _first_provider_nearest_retrievals: List[Retrieval]
    _non_first_provider_nearest_retrievals: List[Retrieval]
    _total_publications: List[Publication]
    _agents: Agents

    def __init__(self, agents: Agents, logs: List[ParsedLogFile]):
        self._agents = agents
        self._logs = logs
        self._total_retrievals = None
        self._total_completed_retrievals = None
        self._total_publications = None
        self._has_first_provider_retrievals = None
        self._first_provider_nearest_retrievals = None
        self._non_first_provider_nearest_retrievals = None

    @property
    def all(self):
        return self._logs

    @property
    def total_retrievals(self):
        if(self._total_retrievals is None):
            self._total_retrievals = []
            for log in self._logs:
                self._total_retrievals += log.retrievals

        return self._total_retrievals

    @property
    def total_completed_retrievals(self):
        if(self._total_completed_retrievals is None):
            self._total_completed_retrievals = []
            for log in self._logs:
                self._total_completed_retrievals += log.completed_retrievals()

        return self._total_completed_retrievals

    @property
    def has_first_provider_retrievals(self):
        if(self._has_first_provider_retrievals is None):
            self._has_first_provider_retrievals = list(
                    filter(lambda ret: ret.first_provider_peer is not None, self.total_completed_retrievals))

        return self._has_first_provider_retrievals

    def set_fpns(self):
        if(self._first_provider_nearest_retrievals is None or self._non_first_provider_nearest_retrievals is None):
            self._first_provider_nearest_retrievals = []
            self._non_first_provider_nearest_retrievals = []

            print('num has_first: %s' % len(self.has_first_provider_retrievals))
            for ret in self.has_first_provider_retrievals:
                try:
                    if(proximity.is_nearest_neighbor(
                            self._agents,
                            ret.origin,
                            ret.first_provider_peer,
                            ret.provider_peers) == True):
                        self._first_provider_nearest_retrievals.append(ret)
                    else:
                        self._non_first_provider_nearest_retrievals.append(ret)

                except Exception as e:
                    print("skipping cid: %s is_nearest_neighbor can not be calculated: %s" % (ret.cid, e))


    @property
    def first_provider_nearest_retrievals(self):
        self.set_fpns()
        return self._first_provider_nearest_retrievals

    @property
    def non_first_provider_nearest_retrievals(self):
        self.set_fpns()
        return self._non_first_provider_nearest_retrievals


    @property
    def total_publications(self):
        if(self._total_publications is None):
            self._total_publications = []
            for log in self._logs:
                self._total_publications += log.publications

        return self._total_publications
