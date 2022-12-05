from pickled.model_peer import Peer
from pickled.model_publication import Publication
from pickled.model_retrieval import Retrieval

class Run:
    def __init__(self, cid):
        self.cid: str = cid
        self.publications: list[Publication] = []
        self.retrievals: list[Retrieval] = []
        self.first_publication: Publication = None
        self._unique_successful_add_provider_target_peers: list[Peer] = None


    def add_publication(self, pub: Publication):
        if self.first_publication == None or pub.get_providers_ended_at < self.first_publication.get_providers_ended_at:
            self.first_publication = pub
        self.publications.append(pub)

    @property
    def unique_successful_add_provider_target_peers(self) -> list[Peer]:
        if self._unique_successful_add_provider_target_peers is None:
            unique_peers = {}
            for pub in self.publications:
                for p in pub.successful_add_provider_target_peers:
                    unique_peers[p] = 1

            self._unique_successful_add_provider_target_peers = list(unique_peers.keys())

        return self._unique_successful_add_provider_target_peers

    @property
    def num_unique_successful_add_target_peers(self) -> int:
        return len(self.unique_successful_add_provider_target_peers)

    def add_retrieval(self, ret: Retrieval):
        self.retrievals.append(ret)

    def first_referer_in_successful_add_target_peer_list(self, ret: Retrieval) -> bool:
        return ret.first_referer_to_fp in self.unique_successful_add_provider_target_peers
