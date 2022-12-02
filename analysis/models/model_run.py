from pickled.model_peer import Peer
from pickled.model_publication import Publication
from pickled.model_retrieval import Retrieval

class Run:
    def __init__(self, cid):
        self.cid: str = cid
        self.publications: list[Publication] = []
        self.retrievals: list[Retrieval] = []
        self.first_publication: Publication = None
        self._unique_add_provider_target_peers: list[Peer] = None


    def add_publication(self, pub: Publication):
        if self.first_publication == None or pub.get_providers_ended_at < self.first_publication.get_providers_ended_at:
            self.first_publication = pub
        self.publications.append(pub)

    def add_retrieval(self, ret: Retrieval):
        self.retrievals.append(ret)

    @property
    def num_add_provider_target_peers(self):
        if self._unique_add_provider_target_peers is None:
            u = {}
            for pub in self.publications:
                for ap in pub.successful_add_provider_target_peers:
                    u[ap] = True

            self._unique_add_provider_target_peers = u.keys()

        return len(self._unique_add_provider_target_peers)