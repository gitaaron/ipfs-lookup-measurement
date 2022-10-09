from pickled.model_retrieval import Retrieval
from pickled.model_publication import Publication
from pickled.model_agent import Agent

class AgentEvents:
    agent: Agent
    retrievals: list[Retrieval]
    publications: list[Publication]
    _completed_retrievals: list[Retrieval]
    def __init__(self, agent, retrievals: list[Retrieval], publications: list[Publication]):
        self.agent = agent
        self.retrievals = retrievals
        self.publications = publications
        self._completed_retrievals = None

    def add_events(self, retrievals: list[Retrieval], publications: list[Publication]):
        self.retrievals += retrievals
        self.publications += publications

    @property
    def completed_retrievals(self):
        if self._completed_retrievals is None:
            # Remove all retrievals that are marked as invalid
            before = len(self.retrievals)
            self._completed_retrievals = list(
                filter(lambda ret: not ret.marked_as_incomplete, self.retrievals))

            print(
                f"Removed {before - len(self._completed_retrievals)} of {before} retrievals because they were incomplete for region {self.agent.region.name}")

            before = len(self._completed_retrievals)

            self._completed_retrievals = list(filter(lambda ret: ret.state !=
                            Retrieval.State.DONE_WITHOUT_ASKING_PEERS, self._completed_retrievals))

            print(
                f"Removed {before - len(self._completed_retrievals)} of {before} retrievals because they were not started for region {self.agent.region.name}")  # error in our measurement setup

        return self._completed_retrievals