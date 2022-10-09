import pickle
from datetime import datetime
from logs.model_logs_config import LogsConfig
from models.model_data_set import DataSet
from logs.model_node_log_spec import NodeLogSpec, NodeLogSpecs
from pickled.model_log_file import LogFile

def _load_parsed_log_files(log_specs: list[NodeLogSpec]) -> list[LogFile]:
    parsed_logs: list[LogFile] = []
    for log_spec in log_specs:
        start = datetime.now()
        with open(log_spec.parsed_log_path,  "rb") as f:
            print("Loading ", log_spec)
            lf: LogFile = pickle.load(f)
            print(f"Took {datetime.now() - start}")
            parsed_logs += [lf]
    return parsed_logs


def latest_data_set(logs_config: LogsConfig)-> DataSet:
    log_files = NodeLogSpecs(logs_config).latest
    log_files = filter(lambda rlf: rlf.has_parsed_log, log_files)
    return DataSet(_load_parsed_log_files(log_files))

def complete_data_set(logs_config: LogsConfig)-> DataSet:
    log_files = NodeLogSpecs(logs_config).all
    log_files = filter(lambda rlf: rlf.has_parsed_log, log_files)
    return DataSet(_load_parsed_log_files(log_files))