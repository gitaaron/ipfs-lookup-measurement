import pickle
from datetime import datetime
from typing import List

from models.model_log_file import LogFile
from models.model_publication import Publication
from models.model_retrieval import Retrieval


class ParsedLogFile:
    def __init__(
            self,
            publications: List[Publication],
            retrievals: List[Retrieval],
            unattempted_retrieval_cids: List[str]):
        self.publications: List[Publication] = publications
        self.retrievals: List[Retrieval] = retrievals
        self.unattempted_retrieval_cids: List[str] = unattempted_retrieval_cids


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
        plf = ParsedLogFile(list(parsed[0].values()), list(
            parsed[1].values()), parsed[2])
        with open(log_file + ".p", "wb") as f:
            pickle.dump(plf, f)


if __name__ == '__main__':
    logs = [
        "./2022-01-16-data/af_south_1.log",
        "./2022-01-16-data/ap_southeast_2.log",
        "./2022-01-16-data/eu_central_1.log",
        "./2022-01-16-data/me_south_1.log",
        "./2022-01-16-data/sa_east_1.log",
        "./2022-01-16-data/us_west_1.log",
    ]
    parse(logs)
