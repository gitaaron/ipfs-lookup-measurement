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


    total_initiated_duration = 0
    total_getting_closest_peers_duration = 0
    total_dialing_duration = 0
    total_fetching_duration = 0

    for ret in retrievals:
        total_initiated_duration += (ret.get_providers_queries_started_at - ret.retrieval_started_at).total_seconds()
        total_getting_closest_peers_duration += (ret.dial_started_at - ret.get_providers_queries_started_at).total_seconds()
        total_dialing_duration += (ret.connected_at - ret.dial_started_at).total_seconds()
        total_fetching_duration += (ret.done_retrieving_at - ret.connected_at).total_seconds()

    labels = ['initiated', 'getting_closest_peers', 'dialing', 'fetching']
    phases = [total_initiated_duration, total_getting_closest_peers_duration, total_dialing_duration, total_fetching_duration]

    fig1, ax1 = plt.subplots()
    ax1.pie(phases, labels=labels, autopct='%1.1f%%')
    ax1.axis('equal')

    plt.show()


if __name__ == "__main__":
    plot()
