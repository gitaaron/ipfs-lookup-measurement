import numpy as np
import matplotlib.pyplot as plt
from typing import List
from pickled.model_publication import Publication
from pickled.model_retrieval import Retrieval
from models.model_data_set import DataSet
from helpers.constants import PlayerType, RetrievalPhase
from helpers import reduce, stringify


def plot_histo_percent_slow(data_set: DataSet):

    region_labels = []

    sp_regions_percent_slow = []
    sp_regions_sample_size = []

    mp_regions_percent_slow = []
    mp_regions_sample_size = []

    for agent, agent_events in data_set.agent_events_map.items():
        retrievals = agent_events.completed_retrievals
        sp_retrievals = reduce.by_main_player(retrievals, PlayerType.PUBLISHER)
        mp_retrievals = reduce.by_main_player(retrievals, PlayerType.RETRIEVER)

        region_labels.append(agent.region)
        if len(sp_retrievals) > 0:
            sp_percent_slow, sp_sample_size = data_set.percent_slow(sp_retrievals, RetrievalPhase.TOTAL)
            sp_regions_percent_slow.append(sp_percent_slow)
            sp_regions_sample_size.append(sp_sample_size)
        else:
            sp_regions_percent_slow.append(0)
            sp_regions_sample_size.append(0)

        if len(mp_retrievals) > 0:
            mp_percent_slow, mp_sample_size = data_set.percent_slow(mp_retrievals, RetrievalPhase.TOTAL)
            mp_regions_percent_slow.append(mp_percent_slow)
            mp_regions_sample_size.append(mp_sample_size)
        else:
            mp_regions_percent_slow.append(0)
            mp_regions_sample_size.append(0)


    x_pos = np.arange(len(region_labels))

    plt.rcdefaults()
    fig1, ax1 = plt.subplots(figsize=(18,6), dpi=80)

    width = 0.4
    sp_rects = ax1.bar(x_pos-0.2, sp_regions_percent_slow, width, align='center', color='green', label='single provider(=1)')
    mp_rects = ax1.bar(x_pos+0.2, mp_regions_percent_slow, width, align='center', color='red', label='many providers(~5)')

    for idx, rect in enumerate(sp_rects):
        plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'total:{sp_regions_sample_size[idx]}', ha='center', va='bottom')

    for idx, rect in enumerate(mp_rects):
        plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'total:{mp_regions_sample_size[idx]}', ha='center', va='bottom')

    ax1.set_xticks(x_pos, labels=region_labels)
    ax1.legend(loc='upper left')

    ax1.set_xlabel('Regions')
    ax1.set_ylabel('Percent Slow')
    ax1.set_title('Percent Slow Retrievals by Region')

    txt = f"Sample Size: {np.sum(sp_regions_sample_size)+np.sum(mp_regions_sample_size)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=8)


def plot_histo_duration(data_set: DataSet, file_size: int):

    region_labels = []

    sp_regions_average_retrieval_duration = []
    sp_regions_sample_size = []

    mp_regions_average_retrieval_duration = []
    mp_regions_sample_size = []

    for agent, agent_events in data_set.agent_events_map.items():
        retrievals = reduce.by_file_size(agent_events.completed_retrievals, file_size)
        sp_retrievals = reduce.by_main_player(retrievals, PlayerType.PUBLISHER)
        mp_retrievals = reduce.by_main_player(retrievals, PlayerType.RETRIEVER)

        region_labels.append(agent.region)

        if len(sp_retrievals) > 0:
            sp_regions_sample_size.append(len(retrievals))
            sp_total_retrieval_durations = [ret.duration(RetrievalPhase.TOTAL).total_seconds() for ret in sp_retrievals]
            sp_regions_average_retrieval_duration.append(np.average(sp_total_retrieval_durations))
        else:
            sp_regions_sample_size.append(0)
            sp_regions_average_retrieval_duration.append(0)

        if len(mp_retrievals) > 0:
            mp_regions_sample_size.append(len(retrievals))
            mp_total_retrieval_durations = [ret.duration(RetrievalPhase.TOTAL).total_seconds() for ret in mp_retrievals]
            mp_regions_average_retrieval_duration.append(np.average(mp_total_retrieval_durations))
        else:
            mp_regions_sample_size.append(0)
            mp_regions_average_retrieval_duration.append(0)

    x_pos = np.arange(len(region_labels))

    plt.rcdefaults()
    fig1, ax1 = plt.subplots(figsize=(18,6), dpi=80)

    width = 0.4
    sp_rects = ax1.bar(x_pos-0.2, sp_regions_average_retrieval_duration, width, color='green', align='center', label='single provider(=1)')
    mp_rects = ax1.bar(x_pos+0.2, mp_regions_average_retrieval_duration, width, color='red', align='center', label='many providers(~5)')

    for idx, rect in enumerate(sp_rects):
        plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'total:{sp_regions_sample_size[idx]}', ha='center', va='bottom')

    for idx, rect in enumerate(mp_rects):
        plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'total:{mp_regions_sample_size[idx]}', ha='center', va='bottom')


    ax1.set_xticks(x_pos, labels=region_labels)

    ax1.set_xlabel('Regions')
    ax1.set_ylabel('Average Duration (sec.)')
    ax1.set_title('Retrieval Duration by Region')

    txt = f"File Size: {stringify.file_size(file_size)}, Sample Size: {np.sum(sp_regions_sample_size)+np.sum(mp_regions_sample_size)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=8)

if __name__ == "__main__":
    plot()
