import os, glob
from logs.model_logs_config import LogsConfig
from models import model_region

class NodeLogSpec:
    _region: model_region.Region
    log_dir: str

    _has_ipfs_log_test: bool = None
    _has_agent_log_test: bool = None
    _has_parsed_log_test: bool = None

    def __init__(self, region_name: str, log_dir: str):
        self._region = model_region.from_name(region_name)
        self.log_dir = log_dir
        self._has_ipfs_log_test: bool = None

    def __str__(self):
        return self.parsed_log_path

    @property
    def region(self):
        return self._region

    @property
    def ipfs_path(self):
        return f"{self.log_dir}/ipfs-{self._region.name}.log"

    @property
    def has_ipfs_log(self):
        if self._has_ipfs_log_test is None:
            self._has_ipfs_log_test = os.path.exists(self.ipfs_path)
        return self._has_ipfs_log_test

    @property
    def agent_path(self):
        return f"{self.log_dir}/agent-{self._region.name}.log"

    @property
    def has_agent_log(self):
        if self._has_agent_log_test is None:
            self._has_agent_log_test = os.path.exists(self.agent_path)
        return self._has_agent_log_test


    @property
    def parsed_log_path(self):
        return os.path.join(self.log_dir, f"{self._region.name}.log.p")

    @property
    def has_parsed_log(self):
        if self._has_parsed_log_test is None:
            self._has_parsed_log_test = os.path.exists(self.parsed_log_path)
        return self._has_parsed_log_test


def _get_region_names_from_dir(log_dir: str) -> dict[str, bool]:
    log_file_pat = f"{log_dir}/*.log"
    region_names = {}
    paths = glob.glob(log_file_pat)
    for p in paths:
        base = os.path.basename(p)
        if '-' in base:
            rn = base.split('-')[1].split('.')[0]
        else:
            rn = base.split('/')[-1].split('.')[0]

        region_names[rn] = True

    return region_names

def _get_log_node_files_from_dir(log_dir: str) -> list[NodeLogSpec]:
    return [NodeLogSpec(rn, log_dir) for rn in _get_region_names_from_dir(log_dir)]


class NodeLogSpecs:
    config: LogsConfig
    def __init__(self, logs_config: LogsConfig):
        self.config = logs_config

    @property
    def all(self):
        all = []
        for log_dir in self.config.all_dir_paths:
            all += _get_log_node_files_from_dir(log_dir)
        return all

    @property
    def latest(self):
        return _get_log_node_files_from_dir(self.config.latest_dir_path)
