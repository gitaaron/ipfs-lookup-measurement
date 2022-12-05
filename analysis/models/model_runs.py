from datetime import datetime
from models.model_run import Run
from pickled.model_publication import Publication
from pickled.model_retrieval import Retrieval

class Runs:
    def __init__(self, publications: list[Publication], retrievals: list[Retrieval]):
        self.cid_run_map: dict[str, Run] = {}
        self._many_publish_runs: dict[str, Run] = None
        for pub in publications:
            if pub.cid not in self.cid_run_map:
                self.cid_run_map[pub.cid] = Run(pub.cid)
            self.cid_run_map[pub.cid].add_publication(pub)

        for ret in retrievals:
            if ret.cid not in self.cid_run_map:
                self.cid_run_map[ret.cid] = Run(ret.cid)
            self.cid_run_map[ret.cid].add_retrieval(ret)

    def from_cid(self, cid: str) -> Run:
        if cid in self.cid_run_map:
            return self.cid_run_map[cid]
        else:
            return None


    def first_publish_at(self, cid: str) -> datetime:
        if cid in self.cid_run_map and self.cid_run_map[cid].first_publication is not None:
            return self.cid_run_map[cid].first_publication.get_providers_ended_at
        else:
            return None

    @property
    def many_publish_runs(self) -> dict[str, Run]:
        if self._many_publish_runs is None:
            self._many_publish_runs = {cid:run for cid,run in self.cid_run_map.items() if len(run.publications) > 1 and len(run.retrievals) == 1}

        return self._many_publish_runs
