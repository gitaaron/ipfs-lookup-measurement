from enum import Enum
from datetime import datetime, timedelta
from pickled.model_get_providers_query import GetProvidersQuery
from pickled.model_peer import Peer
from models.model_region import Region
from typing import Optional, List, Dict, Set
from helpers.constants import RetrievalPhase


class Retrieval:
    class State(Enum):
        INITIATED = 1
        GETTING_CLOSEST_PEERS = 2
        DIALING = 3
        FETCHING = 4
        DONE = 5
        DONE_WITHOUT_ASKING_PEERS = 6

    _state: State

    origin: Region
    cid: str

    retrieval_started_at: datetime
    get_providers_queries_started_at: Optional[datetime]
    found_first_provider_at: Optional[datetime]
    dial_started_at: Optional[datetime]
    connected_at: Optional[datetime]
    stream_opened_at: Optional[datetime]
    last_stream_opened_at: Optional[datetime]
    # there could be more than one provider
    received_first_HAVE_at: Optional[datetime]
    done_retrieving_at: Optional[datetime]
    finished_searching_providers_at: Optional[datetime]
    agent_initiated_retrieve_at: Optional[datetime]
    file_size: Optional[int] # bytes
    agent_uptime: Optional[int] # milliseconds

    provider_peers: Set[Peer]
    provider_peers_found: Set[Peer]
    first_provider_peer: Peer
    first_referer_to_fp: Peer
    provider_record_storing_peers: Set[Peer]
    get_providers_queries: Dict[Peer, GetProvidersQuery]
    done_retrieving_error: Optional[str]
    finish_searching_providers_ctx_error: Optional[str]
    _first_referal_providers_count: Optional[int]

    marked_as_incomplete: bool
    marked_for_removal: bool

    def __init__(self, origin: Region, cid: str, retrieval_started_at: datetime) -> None:
        self.origin = origin
        self.cid = cid
        self.file_size = None
        self.agent_uptime = None
        self.retrieval_started_at = retrieval_started_at
        self._state = Retrieval.State.INITIATED
        self.get_providers_queries = {}
        self.provider_peers = set({})
        self.provider_peers_found = set({})
        self.first_provider_peer = None
        self.first_referer_to_fp = None
        self.provider_record_storing_peers = set({})
        self.marked_for_removal = False
        self.marked_as_incomplete = False
        self.get_providers_queries_started_at = None
        self.found_first_provider_at = None
        self.dial_started_at = None
        self.stream_opened_at = None
        self.last_stream_opened_at = None
        self.connected_at = None
        self.received_first_HAVE_at = None
        self.done_retrieving_at = None
        self.finished_searching_providers_at = None
        self.done_retrieving_error = None
        self.finish_searching_providers_ctx_error = None
        self.agent_initiated_retrieval_at = None
        self._first_referal_providers_count = None


    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state: State):
        if self._state == state or state == Retrieval.State.DONE_WITHOUT_ASKING_PEERS:
            self._state = state
        elif self._state == Retrieval.State.INITIATED and state == Retrieval.State.GETTING_CLOSEST_PEERS:
            self._state = state
        elif self._state == Retrieval.State.GETTING_CLOSEST_PEERS and state == Retrieval.State.DIALING:
            self._state = state
        elif self._state == Retrieval.State.DIALING and state == Retrieval.State.FETCHING:
            self._state = state
        elif self._state == Retrieval.State.FETCHING and state == Retrieval.State.DONE:
            self._state = state
        else:
            raise Exception(
                f"Illegal state transition from {self._state} to {state}")

    def duration(self, phase: RetrievalPhase) -> timedelta:
        if(phase==RetrievalPhase.TOTAL):
            return self.done_retrieving_at - self.retrieval_started_at
        elif(phase==RetrievalPhase.INITIATED):
            return self.get_providers_queries_started_at - self.retrieval_started_at
        elif(phase==RetrievalPhase.GETTING_CLOSEST_PEERS):
            return self.dial_started_at - self.get_providers_queries_started_at
        elif(phase==RetrievalPhase.DIALING):
            return self.stream_opened_at - self.dial_started_at
        elif(phase==RetrievalPhase.FETCHING):
            return self.done_retrieving_at - self.stream_opened_at
        else:
            raise Exception(f"Failed to calculate duration: {phase.name} is not recognized")

    @property
    def all_durations(self) -> dict[RetrievalPhase, timedelta]:
        r = {}
        for phase in RetrievalPhase:
            r[phase] = self.duration(phase).total_seconds()

        return r


    def getting_provider_peers_started(self, timestamp: datetime):
        try:
            self.state = Retrieval.State.GETTING_CLOSEST_PEERS
            self.get_providers_queries_started_at = timestamp
        except Exception as exc:
            if self.state == Retrieval.State.DONE_WITHOUT_ASKING_PEERS:
                print(f"Resetting retrieval for {self.cid}")
                self._state = Retrieval.State.GETTING_CLOSEST_PEERS
                self.get_providers_queries_started_at = timestamp
                self.finished_searching_providers_at = None
                self.finish_searching_providers_ctx_error = None
                self.marked_for_removal = False

    def getting_providers_from(self, target_peer: Peer, timestamp: datetime):
        if target_peer in self.get_providers_queries:
            return

        hops = None
        for provider_peer,query in self.get_providers_queries.items():
            if query.closer_peers is not None and target_peer in query.closer_peers:
                if hops == None or (query.hops_to_query + 1) < hops:
                    hops = query.hops_to_query+1

        query = GetProvidersQuery(target_peer, self.cid, timestamp, hops or 1)
        self.get_providers_queries[target_peer] = query

    @property
    def hops_to_first_provider(self):
        return self.get_providers_queries[self.first_referer_to_fp].hops_to_query

    @property
    def first_referal_providers_count(self):
        return self.get_providers_queries[self.first_referer_to_fp].providers_count

    def found_providers_from(self, target_peer: Peer, timestamp: datetime, providers_count: int):
        if target_peer not in self.get_providers_queries:
            raise Exception(
                f"Unstarted query ended CID: {self.cid} target peer: {target_peer.id}")
        self.get_providers_queries[target_peer].succeeded(
            timestamp, [], providers_count)

    def got_closer_peers_from(self, target_peer: Peer, timestamp: datetime, closer_peers: List[Peer]):
        if target_peer not in self.get_providers_queries:
            raise Exception(
                f"Unstarted query ended CID: {self.cid} target peer: {target_peer.id}")
        self.get_providers_queries[target_peer].succeeded(
            timestamp, closer_peers, 0)

    def start_dialing_provider(self, provider: Peer, timestamp: datetime):
        if self.state.value >= Retrieval.State.DONE.value:
            return
        if provider not in self.provider_peers:
            raise Exception(
                f"Received provider {self.cid} from unknown provider {provider}")
        if self.state.value >= Retrieval.State.DIALING.value:
            return
        self.dial_started_at = timestamp
        self.state = Retrieval.State.DIALING

    def bitswap_connected(self, provider: Peer, timestamp: datetime):
        if self.state.value >= Retrieval.State.DONE.value:
            return
        if provider not in self.provider_peers:
            raise Exception(
                f"Received provider {self.cid} from unknown provider {provider}")
        if self.state == Retrieval.State.DIALING:
            self.stream_opened_at = self.last_stream_opened_at = timestamp
            self.state = Retrieval.State.FETCHING
        else:
            self.last_stream_opened_at = timestamp


    def connected_to_provider(self, provider: Peer, pointer: Peer, timestamp: datetime):
        if self.state.value >= Retrieval.State.DONE.value:
            return
        if pointer not in self.get_providers_queries:
            raise Exception(
                f"Received provider record for {self.cid} from unqueried peer {pointer}")
        self.provider_peers.add(provider)
        self.connected_at = timestamp

    def received_HAVE_from_provider(self, provider: Peer, timestamp: datetime):
        self.provider_peers.add(provider)
        if self.received_first_HAVE_at is None or self.received_first_HAVE_at > timestamp:
            self.received_first_HAVE_at = timestamp
            self.first_provider_peer = provider

    def done_retrieving_first_block(self, timestamp: datetime, error_str: Optional[str]):
        self.done_retrieving_error = error_str
        self.done_retrieving_first_block_at = timestamp

    def done_retrieving(self, timestamp: datetime, file_size: int):
        self.done_retrieving_at = timestamp

        if self.file_size is not None and file_size != self.file_size:
            raise Exception(f"Actual file size {file_size} does not match expected {self.file_size} in region {self.origin}")

        try:
            self.state = Retrieval.State.DONE
        except Exception as exc:
            if len(self.get_providers_queries) == 0:
                self.state = Retrieval.State.DONE_WITHOUT_ASKING_PEERS
            else:
                self.marked_as_incomplete = True


    def finish_searching_providers(self, timestamp: datetime, error_str: Optional[str]):
        self.finish_searching_providers_ctx_error = error_str
        self.finished_searching_providers_at = timestamp

    def agent_initiated(self, timestamp: datetime, file_size: int, agent_uptime: int ):
        self.agent_initated_retrieval_at = timestamp
        self.file_size = file_size
        self.agent_uptime = agent_uptime

    @property
    def num_provider_peers_found(self):
        return len(self.provider_peers_found)
