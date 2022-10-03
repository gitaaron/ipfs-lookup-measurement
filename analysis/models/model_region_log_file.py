import os
from models.model_region import Region

class RegionLogFile:
    region: Region
    log_dir: str

    _has_ipfs_log_test: bool = None
    _has_agent_log_test: bool = None
    _has_parsed_log_test: bool = None

    def __init__(self, region_name: str, log_dir: str):
        self.region = Region(region_name)
        self.log_dir = log_dir
        self._has_ipfs_log_test: bool = None

    @property
    def ipfs_path(self):
        return f"{self.log_dir}/ipfs-{self.region.name}.log"

    @property
    def has_ipfs_log(self):
        if self._has_ipfs_log_test is None:
            self._has_ipfs_log_test = os.path.exists(self.ipfs_path)
        return self._has_ipfs_log_test

    @property
    def agent_path(self):
        return f"{self.log_dir}/agent-{self.region.name}.log"

    @property
    def has_agent_log(self):
        if self._has_agent_log_test is None:
            self._has_agent_log_test = os.path.exists(self.agent_path)
        return self._has_agent_log_test


    @property
    def parsed_log_path(self):
        return os.path.join(self.log_dir, f"{self.region.name}.log.p")

    @property
    def has_parsed_log(self):
        if self._has_parsed_log_test is None:
            self._has_parsed_log_test = os.path.exists(self.parsed_log_path)
        return self._has_parsed_log_test


