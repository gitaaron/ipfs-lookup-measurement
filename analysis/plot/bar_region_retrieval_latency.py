import numpy as np
import matplotlib.pyplot as plt
from log_parse import ParsedLogFile
from typing import List
from models.model_publication import Publication
from models.model_retrieval import Retrieval


def plot(parsed_logs: List[ParsedLogFile]):

    region_labels = []

    regions_average_retrieval_duration = []

    for log in parsed_logs:

        region_labels.append(log.region())

        retrievals = log.completed_retrievals()

        total_retrieval_durations = [(ret.done_retrieving_at - ret.retrieval_started_at).total_seconds() for ret in retrievals]

        regions_average_retrieval_duration.append(np.average(total_retrieval_durations))

    x_pos = np.arange(len(region_labels))

    plt.rcdefaults()
    fig1, ax1 = plt.subplots(figsize=(9,6), dpi=80)

    ax1.bar(x_pos, regions_average_retrieval_duration, align='center')
    ax1.set_xticks(x_pos, labels=region_labels)

    ax1.set_xlabel('Regions')
    ax1.set_title('Retrieval Latency by Region')


if __name__ == "__main__":
    plot()
