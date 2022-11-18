import numpy as np
import matplotlib.pyplot as plt
from typing import List
from pickled.model_publication import Publication
from pickled.model_retrieval import Retrieval
from models.model_data_set import DataSet
from helpers.constants import PlayerType, RetrievalPhase
from helpers import reduce, stringify


def plot_histo_percent_slow(data_set: DataSet, phase):

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
            sp_percent_slow, sp_sample_size = data_set.percent_slow(sp_retrievals, phase)
            sp_regions_percent_slow.append(sp_percent_slow)
            sp_regions_sample_size.append(sp_sample_size)
        else:
            sp_regions_percent_slow.append(0)
            sp_regions_sample_size.append(0)

        if len(mp_retrievals) > 0:
            mp_percent_slow, mp_sample_size = data_set.percent_slow(mp_retrievals, phase)
            mp_regions_percent_slow.append(mp_percent_slow)
            mp_regions_sample_size.append(mp_sample_size)
        else:
            mp_regions_percent_slow.append(0)
            mp_regions_sample_size.append(0)


    x_pos = np.arange(len(region_labels))

    plt.rcdefaults()
    fig1, ax1 = plt.subplots(figsize=(18,6), dpi=80)

    width = 0.4
    sp_rects = ax1.bar(x_pos-0.2, sp_regions_percent_slow, width, align='center', label='single provider(=1)')
    mp_rects = ax1.bar(x_pos+0.2, mp_regions_percent_slow, width, align='center', label='many providers(~5)')

    for idx, rect in enumerate(sp_rects):
        plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'total:{sp_regions_sample_size[idx]}', ha='center', va='bottom')

    for idx, rect in enumerate(mp_rects):
        plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'total:{mp_regions_sample_size[idx]}', ha='center', va='bottom')

    ax1.set_xticks(x_pos, labels=region_labels)
    ax1.legend(loc='upper left')

    ax1.set_xlabel('Retriever Regions')
    ax1.set_ylabel('Percent Slow')
    ax1.set_title(f"Retrieval {phase.name} Percent Slow Retrievals by Region")

    txt = f"Sample Size: {np.sum(sp_regions_sample_size)+np.sum(mp_regions_sample_size)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=8)


def plot_histo_duration(data_set: DataSet, file_size: int, phase):

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
            sp_regions_sample_size.append(len(sp_retrievals))
            sp_total_retrieval_durations = [ret.duration(phase).total_seconds() for ret in sp_retrievals]
            sp_regions_average_retrieval_duration.append(np.average(sp_total_retrieval_durations))
        else:
            sp_regions_sample_size.append(0)
            sp_regions_average_retrieval_duration.append(0)

        if len(mp_retrievals) > 0:
            mp_regions_sample_size.append(len(mp_retrievals))
            mp_total_retrieval_durations = [ret.duration(phase).total_seconds() for ret in mp_retrievals]
            mp_regions_average_retrieval_duration.append(np.average(mp_total_retrieval_durations))
        else:
            mp_regions_sample_size.append(0)
            mp_regions_average_retrieval_duration.append(0)

    x_pos = np.arange(len(region_labels))

    plt.rcdefaults()
    fig1, ax1 = plt.subplots(figsize=(18,6), dpi=80)

    width = 0.4
    sp_rects = ax1.bar(x_pos-0.2, sp_regions_average_retrieval_duration, width, align='center', label='single provider(=1)')
    mp_rects = ax1.bar(x_pos+0.2, mp_regions_average_retrieval_duration, width, align='center', label='many providers(~5)')

    for idx, rect in enumerate(sp_rects):
        plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'total:{sp_regions_sample_size[idx]}', ha='center', va='bottom')

    for idx, rect in enumerate(mp_rects):
        plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'total:{mp_regions_sample_size[idx]}', ha='center', va='bottom')


    ax1.set_xticks(x_pos, labels=region_labels)

    ax1.set_xlabel('Regions')
    ax1.set_ylabel('Average Duration (sec.)')
    ax1.set_title(f"Retrieval {phase.name} Duration by Region")
    ax1.legend(loc='upper left')


    txt = f"File Size: {stringify.file_size(file_size)}, Sample Size: {np.sum(sp_regions_sample_size)+np.sum(mp_regions_sample_size)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=8)

def plot_avg_hops_to_first_provider(data_set: DataSet):
    fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)

    avg_hops_by_region = {}
    region_sample_size = {}
    for agent, agent_events in data_set.agent_events_map.items():
        num_hops = []
        for ret in agent_events.completed_retrievals:
            num_hops.append(ret.hops_to_first_provider)

        if len(num_hops) > 0:
            avg_hops_by_region[agent.region] = np.mean(num_hops)
            region_sample_size[agent.region] = len(num_hops)

    region_labels = list(avg_hops_by_region.keys())
    sorted_region_values = [avg_hops_by_region[region] for region in region_labels]
    sorted_sample_sizes = [region_sample_size[region] for region in region_labels]


    rects = ax1.bar([region.name for region in region_labels], sorted_region_values)

    for idx, rect in enumerate(rects):
        plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'tot:{sorted_sample_sizes[idx]}', ha='center', va='bottom')


    ax1.set_ylabel('Average Hops')
    ax1.set_title(f"Number of hops to first provider by Region")

    txt = f"Sample Size: {np.sum(sorted_sample_sizes)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)

def plot_percent_hydras_first_referers(data_set):
    fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)
    percent_hydras_by_region = {}
    region_sample_size = {}
    for agent, agent_events in data_set.agent_events_map.items():
        total_rets = agent_events.completed_retrievals
        hydra_rets = reduce.by_first_referer(total_rets, 'hydra')
        percent_hydras_by_region[agent.region] = round(len(hydra_rets)/len(total_rets)*100, 1)
        region_sample_size[agent.region] = len(total_rets)

    region_labels = list(percent_hydras_by_region.keys())
    sorted_region_percents = [percent_hydras_by_region[region] for region in region_labels]
    sorted_sample_sizes = [region_sample_size[region] for region in region_labels]

    rects = ax1.bar([region.name for region in region_labels], sorted_region_percents)

    for idx, rect in enumerate(rects):
        plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'tot:{sorted_sample_sizes[idx]}', ha='center', va='bottom')

    ax1.set_ylabel('% Hydras')
    ax1.set_title('Percent Hydras as First Referers to First Provider by Region')

    txt = f"Sample Size: {np.sum(sorted_sample_sizes)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)


def plot_fail_success_rate(data_set):
    fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)
    success_rate_by_region = {}
    fail_rate_by_region = {}
    for agent, agent_events in data_set.agent_events_map.items():
        success_rate_by_region[agent.region] = agent_events.num_succeeded_retrievals
        fail_rate_by_region[agent.region] = agent_events.num_failed_retrievals

    region_labels = list(success_rate_by_region.keys())
    sorted_region_success_rate = [success_rate_by_region[region] for region in region_labels]
    sorted_region_fail_rate = [fail_rate_by_region[region] for region in region_labels]
    sorted_sample_sizes = [success_rate_by_region[region] + fail_rate_by_region[region] for region in region_labels]

    x_pos = np.arange(len(region_labels))

    width = 0.4
    ax1.bar(x_pos-0.2, sorted_region_fail_rate, width, align='center', label='failed')
    ax1.bar(x_pos+0.2, sorted_region_success_rate, width, align='center', label='succeeded')

    ax1.set_xticks(x_pos, labels=region_labels)
    ax1.legend(loc='upper left')
    ax1.set_xlabel('Retriever Regions')
    ax1.set_ylabel('Number of Retrievals')
    ax1.set_title(f"Retrieval Success and Failure Rate by Region")
    txt = f"Sample Size: {np.sum(sorted_sample_sizes)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=8)



if __name__ == "__main__":
    plot()
