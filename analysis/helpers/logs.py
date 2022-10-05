import glob, os, json
import pickle
from typing import List, Dict
from models.model_log_file import LogFile
from models.model_logs_config import LogsConfig
from models.model_region_log_file import RegionLogFile
from models.model_parsed_log_file import ParsedLogFile, ParsedLogFiles
from models.model_agent import Agents
from datetime import datetime
from pathlib import Path

def _get_region_names_from_dir(log_dir: str) -> Dict:
    log_file_pat = f"{log_dir}/*.log"
    region_names = {}
    paths = glob.glob(log_file_pat)
    for p in paths:
        base = os.path.basename(p)
        print('base: ', base)
        if '-' in base:
            rn = base.split('-')[1].split('.')[0]
        # is old style rename to new
        else:
            rn = base.split('/')[-1].split('.')[0]
            newPath = f"{Path(p).parent.as_posix()}/ipfs-{rn}.log"
            os.rename(p, newPath)

        region_names[rn] = True

    return region_names

def _get_log_region_files(log_dir: str) -> List[RegionLogFile]:
    return [RegionLogFile(rn, log_dir) for rn in _get_region_names_from_dir(log_dir)]

def _load_parsed_log_files(log_files: List[RegionLogFile]) -> List[ParsedLogFile]:
    parsed_logs: List[ParsedLogFile] = []
    for log_file in log_files:
        start = datetime.now()
        with open(log_file.parsed_log_path,  "rb") as f:
            print("Loading ", log_file)
            plf: ParsedLogFile = pickle.load(f)
            print(f"Took {datetime.now() - start}")
            parsed_logs += [plf]
    return parsed_logs

def _get_log_region_files_latest(logs_config: LogsConfig) -> List[RegionLogFile]:
    return _get_log_region_files(logs_config.latest_log_dir)

def load_latest_parsed_log_files(logs_config: LogsConfig) -> ParsedLogFiles:
    agents = json.load(open('./agent_info.json'))
    log_files = _get_log_region_files_latest(logs_config)
    log_files = filter(lambda rlf: rlf.has_parsed_log, log_files)
    return ParsedLogFiles(Agents(agents), _load_parsed_log_files(log_files))

def _get_region_files_since_beginning(logs_config: LogsConfig) -> List[RegionLogFile]:
    all_log_region_files = []
    for log_dir in os.listdir(logs_config.root_dir_path):
        all_log_region_files += _get_log_region_files(os.path.join(logs_config.root_dir_path, log_dir))
    return all_log_region_files


def load_all_parsed_log_files(logs_config: LogsConfig) -> ParsedLogFiles:
    agents = json.load(open('./agent_info.json'))
    log_files = _get_region_files_since_beginning(logs_config)
    log_files = filter(lambda rlf: rlf.has_parsed_log, log_files)
    return ParsedLogFiles(Agents(agents), _load_parsed_log_files(log_files))


def _get_all_log_region_files(logs_config) -> List[RegionLogFile]:
    all_log_region_files = []
    for log_dir in os.listdir(logs_config.root_dir_path):
        all_log_region_files += _get_region_files_since_beginning(logs_config)
    return all_log_region_files

def _get_latest_log_region_files(logs_config: LogsConfig) -> List[RegionLogFile]:
    log_dir = logs_config.latest_log_dir
    return _get_log_region_files(log_dir)



def _generate_parsed_log_files(log_files: List[RegionLogFile], _skip_old: bool):
    for log_file in log_files:
        if _skip_old:
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



def generate_all_parsed_log_files_since_beginning(logs_config: LogsConfig):
    log_files: List[RegionLogFile] = _get_all_log_region_files(logs_config)
    _generate_parsed_log_files(log_files, False)

def generate_latest_parsed_log_files(logs_config: LogsConfig):
    log_files: List[RegionLogFile] = _get_latest_log_region_files(logs_config)
    _generate_parsed_log_files(log_files, True)
