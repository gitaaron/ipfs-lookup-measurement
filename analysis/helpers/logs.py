import glob, os, json
import pickle
from typing import List, Dict
from models.model_log_file import LogFile
from models.model_logs_config import LogsConfig
from models.model_region_log_file import RegionLogFile
from models.model_parsed_log_file import ParsedLogFile, ParsedLogFiles
from models.model_agent import Agents
from datetime import datetime



def _get_log_dir_region_names(log_dir) -> Dict:
    region_names = {}
    log_file_pat = f"{log_dir}/*.log"
    paths = glob.glob(log_file_pat)
    for p in paths:
        rn = os.path.basename(p).split('-')[1].split('.')[0]
        region_names[rn] = True

    return region_names

def _get_log_region_files(log_dir: str) -> List[RegionLogFile]:
    return [RegionLogFile(rn, log_dir) for rn in _get_log_dir_region_names(log_dir)]

def get_latest_log_region_files(logs_config: LogsConfig) -> List[RegionLogFile]:
    return _get_log_region_files(logs_config.latest_log_dir)

def _get_all_log_region_files(logs_config: LogsConfig) -> List[RegionLogFile]:
    all_log_file_paths = []
    for log_dir in os.listdir(logs_config.root_dir_path):
        all_log_region_files += _get_log_region_files(os.path.join(logs_config['root_dir_path'], log_dir))
    return all_log_region_files

def _load_region_log_files(log_files: List[RegionLogFile]) -> List[ParsedLogFile]:
    parsed_logs: List[ParsedLogFile] = []
    for log_file in log_files:
        start = datetime.now()
        with open(log_file.parsed_log_path,  "rb") as f:
            print("Loading ", log_file)
            plf: ParsedLogFile = pickle.load(f)
            print(f"Took {datetime.now() - start}")
            parsed_logs += [plf]
    return parsed_logs



def load_latest_parsed_log_files(logs_config: LogsConfig) -> ParsedLogFiles:
    agents = json.load(open('./agent_info.json'))
    log_files = get_latest_log_region_files(logs_config)
    log_files = filter(lambda rlf: rlf.has_parsed_log, log_files)
    return ParsedLogFiles(Agents(agents), _load_region_log_files(log_files))

def load_all_parsed_log_files(logs_config: LogsConfig) -> ParsedLogFiles:
    agents = json.load(open('./agent_info.json'))
    log_files = get_latest_log_region_files(logs_config)
    log_files = filter(lambda rlf: rlf.has_parsed_log, log_files)
    return ParsedLogFiles(Agents(agents), _load_region_log_files(log_files))

def generate_parsed_log_files(log_files: List[RegionLogFile]):
    for log_file in log_files:
        if not log_file.has_ipfs_log:
            print('Skipping : %s because it does not have a corresponding ipfs log' % log_file.region_name)
            continue

        if not log_file.has_agent_log:
            print('Skipping : %s because it does not have a corresponding agent log' % log_file.region_name)
            continue

        parsed = LogFile.parse(log_file)
        plf = ParsedLogFile(log_file, list(parsed[0].values()), list(
            parsed[1].values()), parsed[2])

        with open(log_file.parsed_log_path, "wb") as f:
            pickle.dump(plf, f)


