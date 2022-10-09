import pickle
from logs.model_logs_config import LogsConfig
from logs.model_node_log_spec import NodeLogSpec, NodeLogSpecs
from pickled.model_log_file import LogFile

from parse import read

def _generate_parsed_log_files(log_files: list[NodeLogSpec], _skip_old: bool):
    for log_file in log_files:
        if _skip_old:
            if not log_file.has_ipfs_log:
                print('Skipping : %s because it does not have a corresponding ipfs log' % log_file.region_name)
                continue

            if not log_file.has_agent_log:
                print('Skipping : %s because it does not have a corresponding agent log' % log_file.region_name)
                continue

        lf: LogFile = read.from_log_file_spec(log_file)

        with open(log_file.parsed_log_path, "wb") as f:
            pickle.dump(lf, f)

def all(logs_config: LogsConfig):
    log_files: list[NodeLogSpec] = NodeLogSpecs(logs_config).all
    print('generate all')
    _generate_parsed_log_files(log_files, False)

def latest(logs_config: LogsConfig):
    log_files: list[NodeLogSpec] = NodeLogSpecs(logs_config).latest
    print('generate latest')
    _generate_parsed_log_files(log_files, True)
