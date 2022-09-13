from plot import cdf_retrievals
from log_parse import load_parsed_logs, ParsedLogFile
from models.model_publication import Publication
from models.model_retrieval import Retrieval
from typing import List
import matplotlib.pyplot as plt


if __name__=='__main__':
    logs = [
        "./2022-01-16-data/af_south_1.log",
        "./2022-01-16-data/ap_southeast_2.log",
        "./2022-01-16-data/eu_central_1.log",
        "./2022-01-16-data/me_south_1.log",
        "./2022-01-16-data/sa_east_1.log",
        "./2022-01-16-data/us_west_1.log",
    ]

    parsed_logs = load_parsed_logs(logs)


    publications: List[Publication] = []

    retrievals: List[Retrieval] = []
    for parsed_log in parsed_logs:
        publications += parsed_log.publications
        retrievals += parsed_log.retrievals

    # Remove all retrievals that are marked as invalid
    before = len(retrievals)
    retrievals = list(
        filter(lambda ret: not ret.marked_as_incomplete, retrievals))
    print(
        f"Removed {before - len(retrievals)} of {before} retrievals because they were incomplete")

    retrievals = list(filter(lambda ret: ret.state !=
                      Retrieval.State.DONE_WITHOUT_ASKING_PEERS, retrievals))
    print(
        f"Removed {before - len(retrievals)} of {before} retrievals because they were not started")  # error in our measurement setup

    cdf_retrievals.total(retrievals)
    cdf_retrievals.initiated_phase(retrievals)
    cdf_retrievals.getting_closest_peers_phase(retrievals)
    cdf_retrievals.dialing_phase(retrievals)
    cdf_retrievals.fetching_phase(retrievals)
    plt.legend(loc='lower right')
    plt.show()
