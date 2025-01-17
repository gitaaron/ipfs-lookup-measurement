import dateutil.parser
import re
from datetime import datetime
from dateutil.parser import isoparse
from typing import Any, Optional, List

from pickled.model_peer import Peer


class ParsedLogLine:
    cid: str
    timestamp: datetime
    peer: Optional[Peer]
    remote_peer: Optional[Peer]
    other_peer: Optional[Peer]
    closest_peers: Optional[List[Peer]]
    file_size: Optional[int] # bytes
    agent_uptime: Optional[int] # milliseconds
    error_str: Optional[str]
    count: Optional[int]
    available_mem: Optional[int]
    load_avg_last_min: Optional[float]


    def __init__(self, cid: str, timestamp_str: str):
        self.cid = cid
        self.timestamp = isoparse(timestamp_str)
        self.remote_peer = None
        self.other_peer = None
        self.closest_peers = None
        self.error_str = None
        self.count = None


class _LogLine:
    line: str
    def __init__(self, line: str, timestamp: datetime) -> None:
        self.line = line


class IPFSLogLine(_LogLine):

    def is_start_providing(self) -> Optional[ParsedLogLine]:
        if "Start providing cid" not in self.line:
            return None
        match = re.search(r"([^\s]+): Start providing cid (\w+)", self.line)
        return None if match is None else ParsedLogLine(match.group(2), match.group(1))

    def is_start_getting_closest_peers(self) -> Optional[ParsedLogLine]:
        if "Start getting closest peers to cid" not in self.line:
            return None
        match = re.search(
            r"([^\s]+): Start getting closest peers to cid ([^\s]+)", self.line)
        return None if match is None else ParsedLogLine(match.group(2), match.group(1))

    def is_getting_closest_peers(self) -> Optional[ParsedLogLine]:
        if "Getting closest peers for cid" not in self.line:
            return None
        match = re.search(
            r"([^\s]+): Getting closest peers for cid (\w+) from (\w+)\((.*)\)$", self.line)
        if match is None:
            return None
        parsed = ParsedLogLine(match.group(2), match.group(1))
        parsed.remote_peer = Peer(match.group(3), match.group(4))
        return parsed

    def is_got_closest_peers(self) -> Optional[ParsedLogLine]:
        if "closest peers to cid" not in self.line:
            return None
        match = re.search(
            r"([^\s]+): Got (\d+) closest peers to cid (\w+) from (\w+)\((.*)\): \s?([\w\s]+)$", self.line)
        if match is None:
            return None

        parsed = ParsedLogLine(match.group(3), match.group(1))
        parsed.remote_peer = Peer(match.group(4), match.group(5))

        peers: List[Peer] = []
        for peer_str in match.group(6).split(" "):
            if peer_str == "":
                continue
            peers.append(Peer(peer_str, "n.a."))
        parsed.closest_peers = peers
        return parsed

    def is_error_getting_closest_peers(self) -> Optional[ParsedLogLine]:
        if "Error getting closest peers for cid" not in self.line:
            return None
        match = re.search(
            r"([^\s]+): Error getting closest peers for cid (\w+) from (\w+)\((.*)\): (.*)", self.line)
        if match is None:
            return None
        parsed = ParsedLogLine(match.group(2), match.group(1))
        parsed.remote_peer = Peer(match.group(3), match.group(4))
        parsed.error_str = match.group(5)
        return parsed

    def is_pvd_dht_walk_end(self) -> Optional[ParsedLogLine]:
        if "In total, got " not in self.line:
            return None
        match = re.search(
            r"([^\s]+): In total, got \d+ closest peers to cid ([^\s]+).*: (.*)\s$", self.line)
        if match is None:
            return None

        peers: List[Peer] = []

        matches = re.findall(
            r"\w+\([^)]+\)", match.group(3))

        # peer agent may not be specified by log
        if len(matches) == 0:
            matches = match.group(3).split(' ')

        for peer_str in matches:
            sub_match = re.search(r"(\w+)\((.*)\)", peer_str)
            if sub_match is None:
                raise Exception(f"could not parse peer {peer_str} in {match.group(1)}")
            peers.append(Peer(sub_match.group(1), sub_match.group(2)))
        parsed = ParsedLogLine(match.group(2), match.group(1))
        parsed.closest_peers = peers
        return parsed

    def is_add_provider_success(self) -> Optional[ParsedLogLine]:
        if "Succeed in putting provider record for cid" not in self.line:
            return None
        match = re.search(
            r"([^\s]+): Succeed in putting provider record for cid ([^\s]+) to (\w+)\((.+)\)",
            self.line)
        if match is None:
            return None
        parsed = ParsedLogLine(match.group(2), match.group(1))
        parsed.remote_peer = Peer(match.group(3), match.group(4))
        return parsed

    def is_add_provider_started(self) -> Optional[ParsedLogLine]:
        if "Start putting provider record for cid" not in self.line:
            return None
        match = re.search(
            r"([^\s]+): Start putting provider record for cid ([^\s]+) to (\w+)\((.+)\)",
            self.line)
        if match is None:
            return None
        parsed = ParsedLogLine(match.group(2), match.group(1))
        parsed.remote_peer = Peer(match.group(3), match.group(4))
        return parsed

    def is_add_provider_error(self) -> Optional[ParsedLogLine]:
        if "Error putting provider record for cid" not in self.line:
            return None
        match = re.search(r"([^\s]+): Error putting provider record for cid (\w+) to (\w+)\((.+)\) \[(.*)\]$",
                          self.line)
        if match is None:
            return None

        parsed = ParsedLogLine(match.group(2), match.group(1))
        parsed.remote_peer = Peer(match.group(3), match.group(4))
        parsed.error_str = match.group(5)
        return parsed

    def is_get_provider_success(self) -> Optional[ParsedLogLine]:
        if "provider records back from " not in self.line:
            return None
        match = re.search(
            r"([^\s]+): Got \d+ provider records back from (\w+)\((.+)\).*", self.line)
        if match is None:
            return None

        parsed = ParsedLogLine("", match.group(1))
        parsed.remote_peer = Peer(match.group(2), match.group(3))
        return parsed

    def is_get_provider_error(self) -> Optional[ParsedLogLine]:
        if "Error getting provider record for cid" not in self.line:
            return None
        match = re.search(
            r"([^\s]+): Error getting provider record for cid (\w+) from (\w+)\((.+)\) after a successful put (.+)$",
            self.line)
        if match is None:
            return None

        parsed = ParsedLogLine(match.group(2), match.group(1))
        parsed.remote_peer = Peer(match.group(3), match.group(4))
        parsed.error_str = match.group(5)
        return parsed

    def is_finish_providing(self) -> Optional[ParsedLogLine]:
        if "Finish providing cid " not in self.line:
            return None
        match = re.search(
            r"([^\s]+): Finish providing cid ([^\s]+)", self.line)
        if match is None:
            return None
        return ParsedLogLine(match.group(2), match.group(1))

    # Retrieval
    def is_start_retrieving(self) -> Optional[ParsedLogLine]:
        if "Start retrieving content for" not in self.line:
            return None
        match = re.search(
            r"([^\s]+): Start retrieving content for ([^\s]+)", self.line)
        if match is None:
            return None
        return ParsedLogLine(match.group(2), match.group(1))

    def is_start_searching_pvd(self) -> Optional[ParsedLogLine]:
        if "Start searching providers for cid" not in self.line:
            return None
        match = re.search(
            r"([^\s]+): Start searching providers for cid (\w+)", self.line)
        if match is None:
            return None
        return ParsedLogLine(match.group(2), match.group(1))

    def is_start_getting_providers(self) -> Optional[ParsedLogLine]:
        if "Getting providers for cid" not in self.line:
            return None
        match = re.search(
            r"([^\s]+): Getting providers for cid (\w+) from (\w+)\((.+)\)", self.line)
        if match is None:
            return None

        parsed = ParsedLogLine(match.group(2), match.group(1))
        parsed.remote_peer = Peer(match.group(3), match.group(4))
        return parsed

    def is_found_provider_entries(self) -> Optional[ParsedLogLine]:
        if "provider entries for cid " not in self.line:
            return None
        match = re.search(
            r"([^\s]+): Found (\d+) provider entries for cid (\w+) from (\w+)\((.+)\): (.+)?", self.line)
        if match is None:
            return None

        parsed = ParsedLogLine(match.group(3), match.group(1))
        parsed.remote_peer = Peer(match.group(4), match.group(5))
        parsed.error_str = match.group(6)
        parsed.count = int(match.group(2))
        return parsed

    def is_pvd_found(self) -> Optional[ParsedLogLine]:
        if "Found provider " not in self.line:
            return None
        match = re.search(
            r"([^\s]+): Found provider (\w+) for cid ([^\s]+) from (\w+)\((.+)\)", self.line)
        if match is None:
            return None

        parsed = ParsedLogLine(match.group(3), match.group(1))
        parsed.remote_peer = Peer(match.group(4), match.group(5))
        parsed.other_peer = Peer(match.group(2), "n.a.")
        return parsed

    def is_bitswap_connect(self) -> Optional[ParsedLogLine]:
        if ": Bitswap connect to peer " not in self.line:
            return None
        match = re.search(
            r"([^\s]+): Bitswap connect to peer (\w+)", self.line)
        if match is None:
            return None

        parsed = ParsedLogLine("", match.group(1))
        parsed.remote_peer = Peer(match.group(2), "n.a.")
        return parsed

    def is_bitswap_connected(self) -> Optional[ParsedLogLine]:
        if ": Bitswap connected to peer " not in self.line:
            return None
        match = re.search(
            r"([^\s]+): Bitswap connected to peer (\w+)", self.line)
        if match is None:
            return None

        parsed = ParsedLogLine("", match.group(1))
        parsed.remote_peer = Peer(match.group(2), "n.a.")
        return parsed

    def is_done_retrieving_first_block(self) -> Optional[ParsedLogLine]:
        if "Done retrieving content for" not in self.line:
            return None
        match = re.search(
            r"([^\s]+): Done retrieving content for (\w+) error: (.+)?", self.line)
        if match is None:
            return None

        parsed = ParsedLogLine(match.group(2), match.group(1))
        parsed.error_str = match.group(3)
        return parsed

    def is_got_provider(self) -> Optional[ParsedLogLine]:
        if ": Got provider " not in self.line:
            return None
        match = re.search(
            r"([^\s]+): Got provider (\w+) for content (\w+)", self.line)
        if match is None:
            return None

        parsed = ParsedLogLine(match.group(3), match.group(1))
        parsed.remote_peer = Peer(match.group(2), "n.a.")
        return parsed

    def is_connected_to_pvd(self) -> Optional[ParsedLogLine]:
        if ": Connected to provider " not in self.line:
            return None
        match = re.search(
            r"([^\s]+): Connected to provider (\w+)\((.+)\) for cid ([^\s]+) from (\w+)\((.+)\)", self.line)
        if match is None:
            return None

        parsed = ParsedLogLine(match.group(4), match.group(1))
        parsed.remote_peer = Peer(match.group(2), match.group(3))
        parsed.other_peer = Peer(match.group(5), match.group(6))
        return parsed

    def is_finish_searching_pvd(self) -> Optional[ParsedLogLine]:
        if "Finished searching providers for cid" not in self.line:
            return None
        match = re.search(
            r"([^\s]+): Finished searching providers for cid (\w+)( ctx error: )?(.+)?", self.line)
        if match is None:
            return None

        parsed = ParsedLogLine(match.group(2), match.group(1))
        parsed.error_str = match.group(4)
        return parsed

    @staticmethod
    def from_dict(obj: Any) -> 'IPFSLogLine':
        assert isinstance(obj, dict)
        line = obj.get("line")
        timestamp = dateutil.parser.parse(obj.get("timestamp"))
        return IPFSLogLine(line, timestamp)

class AgentLogLine(_LogLine):

    def is_start_retrieving(self) -> Optional[ParsedLogLine]:
        if "Start retrieve for CID:" not in self.line:
            return None
        if "expected content length:" not in self.line:
            return None

        match = re.search(
            r"([^\s]+): Start retrieve for CID:([^\s]+) expected content length:([1-9][0-9]*) agent uptime:([1-9][0-9]*)", self.line)

        if match is None:
            raise Exception("Failed to parse line: ", self.line)

        parsed = ParsedLogLine(match.group(2), match.group(1))
        parsed.file_size = int(match.group(3))
        parsed.agent_uptime = int(match.group(4))
        return parsed

    def is_finished_retrieving(self) -> Optional[ParsedLogLine]:
        if "Finished retrieve for CID:" not in self.line:
            return None
        if "actual content length:" not in self.line:
            return None

        match = re.search(
            r"([^\s]+): Finished retrieve for CID:(\w+) actual content length:([1-9][0-9]*)", self.line)

        if match is None:
            raise Exception("Failed to parse line: ", self.line)

        parsed = ParsedLogLine(match.group(2), match.group(1))
        parsed.file_size = int(match.group(3))
        return parsed


    def is_get_id(self) -> Optional[ParsedLogLine]:
        if "Get PeerID:" not in self.line:
            return None
        match = re.search(
            r"([^\s]+): Get PeerID:([^\s]+)", self.line
        )
        if match is None:
            raise Exception("Failed to parse line: ", self.line)
        parsed = ParsedLogLine(None, match.group(1))
        parsed.peer = Peer(match.group(2), "n.a.")
        return parsed

    # 2022-11-06T09:00:14.774145594Z: available_mem:1045240 load_avg_last_min:0.31","timestamp":"2022-11-06T04:00:14.958219682-05:00
    def is_sys_health(self) -> Optional[ParsedLogLine]:
        if "available_mem:" not in self.line or "load_avg_last_min:" not in self.line:
            return None

        match = re.search(
                r"([^\s]+): available_mem:([1-9][0-9]*) load_avg_last_min:([0-9\.])", self.line
        )

        if match is None:
            raise Exception("Failed to parse line: ", self.line)

        parsed = ParsedLogLine(None, match.group(1))
        parsed.available_mem = int(match.group(2))
        parsed.load_avg_last_min = float(match.group(3))
        return parsed

    @staticmethod
    def from_dict(obj: Any) -> 'AgentLogLine':
        assert isinstance(obj, dict)
        line = obj.get("line")
        timestamp = dateutil.parser.parse(obj.get("timestamp"))
        return AgentLogLine(line, timestamp)

