from pickled.model_retrieval import Retrieval
from pickled.model_publication import Publication
from pickled.model_agent import Agent

class AgentEvents:
    agent: Agent
    retrievals: list[Retrieval]
    publications: list[Publication]
    _completed_retrievals: list[Retrieval]
    _num_succeeded_retrievals: int
    _num_failed_retrievals: int

    def __init__(self, agent, retrievals: list[Retrieval], publications: list[Publication]):
        self.agent = agent
        self.retrievals = retrievals
        self.publications = publications
        self._completed_retrievals = None
        self._num_succeeded_retrievals = None
        self._num_failed_retrievals = None

    def add_events(self, retrievals: list[Retrieval], publications: list[Publication]):
        self.retrievals += retrievals
        self.publications += publications

    @property
    def completed_retrievals(self):
        if self._completed_retrievals is None:
            self._set_completed_retrievals()

        return self._completed_retrievals

    def _set_completed_retrievals(self):
        total_removed = 0

        # Remove all retrievals that are marked as invalid
        before = len(self.retrievals)
        self._completed_retrievals = list(
            filter(lambda ret: not ret.marked_as_incomplete, self.retrievals))
        removed = before - len(self._completed_retrievals)
        print(
            f"Removed {removed} of {before} retrievals because they were incomplete for region {self.agent.region.name}")
        total_removed += removed

        before = len(self._completed_retrievals)
        self._completed_retrievals = list(
            filter(lambda ret: ret.done_retrieving_at is not None, self._completed_retrievals))
        removed = before - len(self._completed_retrievals)
        print(
            f"Removed {removed} of {before} retrievals because they were missing 'done_retrieving_at' for region {self.agent.region.name}")  # error in our measurement setup
        total_removed += removed

        before = len(self._completed_retrievals)
        self._completed_retrievals = list(filter(lambda ret: ret.state !=
                        Retrieval.State.DONE_WITHOUT_ASKING_PEERS, self._completed_retrievals))
        removed = before - len(self._completed_retrievals)
        print(
            f"Removed {removed} of {before} retrievals because they were not started for region {self.agent.region.name}")  # error in our measurement setup
        total_removed += removed

        self._num_succeeded_retrievals = len(self._completed_retrievals)
        self._num_failed_retrievals = total_removed

    @property
    def num_succeeded_retrievals(self):
        if self._num_succeeded_retrievals is None:
            self._set_completed_retrievals()
        return self._num_succeeded_retrievals

    @property
    def num_failed_retrievals(self):
        if self._num_failed_retrievals is None:
            self._set_completed_retrievals()
        return self._num_failed_retrievals


