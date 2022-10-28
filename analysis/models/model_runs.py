from datetime import datetime
from models.model_run import Run
from pickled.model_publication import Publication

class Runs:
    def __init__(self, publications: list[Publication]):
        self.cid_run_map: dict[str, Run] = {}
        for pub in publications:
            if pub.cid not in self.cid_run_map:
                self.cid_run_map[pub.cid] = Run(pub)
            else:
                self.cid_run_map[pub.cid].add_publication(pub)

    def first_publish_at(self, cid: str) -> datetime:
        if cid in self.cid_run_map:
            return self.cid_run_map[cid].first_publication.get_providers_ended_at
        else:
            return None