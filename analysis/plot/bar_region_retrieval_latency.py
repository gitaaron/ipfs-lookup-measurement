import numpy as np
import matplotlib.pyplot as plt
from typing import List
from pickled.model_publication import Publication
from pickled.model_retrieval import Retrieval
from models.model_data_set import DataSet

def plot(data_set: DataSet):

    region_labels = []

    regions_average_retrieval_duration = []

    for agent, agent_events in data_set.agent_events_map.items():
        region_labels.append(agent.region)
        retrievals = agent_events.completed_retrievals
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