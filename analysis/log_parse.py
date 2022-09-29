import os
import glob
import pickle
from datetime import datetime
from typing import List
import json

from models.model_log_file import LogFile
from models.model_publication import Publication
from models.model_retrieval import Retrieval

class ParsedLogFile:

    def region(self):
        return self.filename.split('/')[-1].split('.')[0]

    _completed_retrievals: List[Retrieval] = None

    def completed_retrievals(self):
        if(self._completed_retrievals==None):
            self._completed_retrievals = []
            # Remove all retrievals that are marked as invalid
            before = len(self.retrievals)
            self._completed_retrievals = list(
                filter(lambda ret: not ret.marked_as_incomplete, self.retrievals))
            print(
                f"Removed {before - len(self._completed_retrievals)} of {before} retrievals because they were incomplete for region {self.region()}")

            before = len(self._completed_retrievals)

            self._completed_retrievals = list(filter(lambda ret: ret.state !=
                            Retrieval.State.DONE_WITHOUT_ASKING_PEERS, self._completed_retrievals))
            print(
                f"Removed {before - len(self._completed_retrievals)} of {before} retrievals because they were not started for region {self.region()}")  # error in our measurement setup

        return self._completed_retrievals


    def __init__(
            self,
            filename: str,
            publications: List[Publication],
            retrievals: List[Retrieval],
            unattempted_retrieval_cids: List[str]):
        self.filename: str = filename
        self.publications: List[Publication] = publications
        self.retrievals: List[Retrieval] = retrievals
        self.unattempted_retrieval_cids: List[str] = unattempted_retrieval_cids


class ParsedLogFiles:
    _logs: List[ParsedLogFile]
    _total_retrievals: List[Retrieval]
    _total_completed_retrievals: List[Retrieval]
    _total_publications: List[Publication]

    def __init__(self, logs: List[ParsedLogFile]):
        self._logs = logs
        self._total_retrievals = None
        self._total_completed_retrievals = None
        self._total_publications = None

    @property
    def total_retrievals(self):
        if(self._total_retrievals is None):
            self._total_retrievals = []
            for log in self._logs:
                self._total_retrievals += log.retrievals

        return self._total_retrievals

    @property
    def total_completed_retrievals(self):
        if(self._total_completed_retrievals is None):
            self._total_completed_retrievals = []
            for log in self._logs:
                self._total_completed_retrievals += log.completed_retrievals()

        return self._total_completed_retrievals

    @property
    def total_publications(self):
        if(self._total_publications is None):
            self._total_publications = []
            for log in self._logs:
                self._total_publications += log.publications

        return self._total_publications


def load_ParsedLogFiles(log_files: List[str]) -> ParsedLogFiles:
    return ParsedLogFiles(load_parsed_logs(log_files))

def load_parsed_logs(log_files: List[str]) -> List[ParsedLogFile]:
    parsed_logs: List[ParsedLogFile] = []
    for log_file in log_files:
        start = datetime.now()
        with open(log_file + ".p", "rb") as f:
            print("Loading ", log_file)
            plf: ParsedLogFile = pickle.load(f)
            print(f"Took {datetime.now() - start}")
            parsed_logs += [plf]
    return parsed_logs



def parse(log_files: List[str]):
    for log_file in log_files:
        parsed = LogFile.parse(log_file)
        plf = ParsedLogFile(log_file, list(parsed[0].values()), list(
            parsed[1].values()), parsed[2])
        with open(log_file + ".p", "wb") as f:
            pickle.dump(plf, f)


def get_log_file_paths(log_dir):
    log_file_pat = f"{log_dir}/*.log"
    return glob.glob(log_file_pat)


if __name__ == '__main__':
    logs_config = json.load(open('./log_config.json'))
    latest_log_dir = os.path.join(logs_config['root_dir_path'], logs_config['latest_dir_name'])
    parse(get_log_file_paths(latest_log_dir))
