import numpy as np
import matplotlib.pyplot as plt
from log_parse import load_parsed_logs, ParsedLogFile
from typing import List
from models.model_publication import Publication
from models.model_retrieval import Retrieval


def plot(parsed_logs: List[ParsedLogFile]):

    region_labels = []

    regions_average_retrieval_duration = []

    for log in parsed_logs:

        region_labels.append(log.region())

        retrievals = log.retrievals

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

        total_retrieval_durations = [(ret.done_retrieving_at - ret.retrieval_started_at).total_seconds() for ret in retrievals]

        regions_average_retrieval_duration.append(np.average(total_retrieval_durations))

    x_pos = np.arange(len(region_labels))

    plt.rcdefaults()
    fig1, ax1 = plt.subplots()

    ax1.bar(x_pos, regions_average_retrieval_duration, align='center')
    ax1.set_xticks(x_pos, labels=region_labels)

    ax1.set_xlabel('Regions')

    plt.show()


if __name__ == "__main__":
    plot()
