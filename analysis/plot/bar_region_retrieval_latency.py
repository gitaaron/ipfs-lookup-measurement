import numpy as np
import matplotlib.pyplot as plt
from typing import List
from pickled.model_publication import Publication
from pickled.model_retrieval import Retrieval
from models.model_data_set import DataSet
from helpers.constants import PlayerType, RetrievalPhase
from helpers import reduce, stringify

def plot(data_set: DataSet, file_size: int, main_player: PlayerType):

    region_labels = []

    regions_average_retrieval_duration = []

    for agent, agent_events in data_set.agent_events_map.items():
        retrievals = reduce.by_file_size(agent_events.completed_retrievals, file_size)
        if main_player is not None:
            retrievals = reduce.by_main_player(retrievals, main_player)

        if len(retrievals) > 0:
            region_labels.append(agent.region)
            total_retrieval_durations = [ret.duration(RetrievalPhase.TOTAL).total_seconds() for ret in retrievals]
            regions_average_retrieval_duration.append(np.average(total_retrieval_durations))

    x_pos = np.arange(len(region_labels))

    plt.rcdefaults()
    fig1, ax1 = plt.subplots(figsize=(9,6), dpi=80)

    ax1.bar(x_pos, regions_average_retrieval_duration, align='center')
    ax1.set_xticks(x_pos, labels=region_labels)

    ax1.set_xlabel('Regions')
    ax1.set_ylabel('Average Duration (sec.)')
    ax1.set_title('Retrieval Duration by Region')

    txt = f"File Size: {stringify.file_size(file_size)}"

    if main_player is not None:
        if main_player==PlayerType.RETRIEVER:
            txt += f"\nMany Providers (~5)"
        else:
            txt += f"\nSingle Provider (=1)"

    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=8)

if __name__ == "__main__":
    plot()
