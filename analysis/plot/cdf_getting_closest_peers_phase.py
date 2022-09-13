import numpy as np
import matplotlib.pyplot as plt
from log_parse import load_parsed_logs, ParsedLogFile
from typing import List
from models.model_publication import Publication
from models.model_retrieval import Retrieval


def plot():
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

    overall_retrieval_durations = []
    for ret in retrievals:
        overall_retrieval_durations += [
            (ret.dial_started_at - ret.get_providers_queries_started_at).total_seconds()]

    hist, bin_edges = np.histogram(
        overall_retrieval_durations, bins=np.arange(0, 5, 0.1),  density=True)

    dx = bin_edges[1]-bin_edges[0]
    cdf = np.cumsum(hist)*dx

    plt.plot(bin_edges[:-1], cdf,)
    plt.show()


if __name__ == "__main__":
    plot()
