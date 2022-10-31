import matplotlib.pyplot as plt
import numpy as np
from helpers import calc
from models.model_data_set import DataSet
from helpers.constants import RetrievalPhase

def plot_fpn_durations(data_set: DataSet):
    fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)

    phase_labels = []
    fpn_durations = []
    non_fpn_durations = []
    fpn_rs = data_set.first_provider_nearest_retrievals
    non_fpn_rs = data_set.non_first_provider_nearest_retrievals

    for phase in RetrievalPhase:
        if phase==RetrievalPhase.TOTAL:
            phase_labels.append(phase.name)
            fpn_durations.append(calc.avg_duration(fpn_rs, phase))
            non_fpn_durations.append(calc.avg_duration(non_fpn_rs, phase))

    b1 = ax1.barh(phase_labels, fpn_durations)
    b2 = ax1.barh(phase_labels, non_fpn_durations, left=fpn_durations)

    plt.legend([b1, b2], ['fpn', 'non_fpn'], loc="upper right")

    ax1.set_ylabel(None)
    ax1.set_xlabel('fpn vs non-fpn durations (sec.)')
    ax1.set_title('First Provider Nearest effects on Total Duration')


def plot_fpn_durations_by_phase(data_set: DataSet):
    fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)

    phase_labels = []
    fpn_durations = []
    non_fpn_durations = []
    fpn_rs = data_set.first_provider_nearest_retrievals
    non_fpn_rs = data_set.non_first_provider_nearest_retrievals

    for phase in RetrievalPhase:
        if phase != RetrievalPhase.TOTAL:
            phase_labels.append(phase.name)
            fpn_durations.append(calc.avg_duration(fpn_rs, phase))
            non_fpn_durations.append(calc.avg_duration(non_fpn_rs, phase))

    b1 = ax1.bar(phase_labels, fpn_durations)
    b2 = ax1.bar(phase_labels, non_fpn_durations, bottom=fpn_durations)

    plt.legend([b1, b2], ['fpn', 'non_fpn'], loc="upper right")

    ax1.set_ylabel('fpn vs non-fpn durations (sec.)')
    ax1.set_title('First Provider Nearest effects on Duration by Phase')

def plot_fpn_likelihood(data_set: DataSet):
    fig1, ax1 = plt.subplots(figsize=(9,6), dpi=80)

    stats = calc.first_provider_nearest_stats(data_set)
    num_fpn = stats['all']['num_fpn']
    num_non_fpn = stats['all']['num_non_fpn']
    b1 = ax1.barh(['all'], [num_fpn], )
    b2 = ax1.barh(['all'], [num_non_fpn], left=num_fpn,)

    plt.legend([b1, b2], ['num_fpns', 'num_non_fpns'], loc="upper right")

    ax1.set_ylabel(None)
    ax1.set_xlabel('Ratio of fpn vs non-fpn')
    ax1.set_title('First Provider Nearest Likelihood')

def plot_fpn_likelihood_by_region(data_set: DataSet):
    plt.rcdefaults()
    fig1, ax1 = plt.subplots(figsize=(9,6), dpi=80)

    region_labels = []

    regions_num_fpns = []
    regions_num_non_fpns = []

    stats = calc.first_provider_nearest_stats(data_set)

    for agent, agent_events in data_set.agent_events_map.items():
        region_labels.append(agent.region)
        regions_num_fpns.append(stats[agent.region.name]['num_fpns'])
        regions_num_non_fpns.append(stats[agent.region.name]['num_non_fpns'])


    x_pos = np.arange(len(region_labels))
    b1 = ax1.bar(x_pos, regions_num_fpns, align='center')
    b2 = ax1.bar(x_pos, regions_num_non_fpns, align='center', bottom=regions_num_fpns)

    x_pos = np.arange(len(region_labels))
    ax1.set_xticks(x_pos, labels=region_labels)
    plt.legend([b1, b2], ['num_fpns', 'num_non_fpns'], loc="upper right")

    ax1.set_xlabel('Regions')
    ax1.set_ylabel('Ratio of fpn vs non-fpn')

    ax1.set_title('First Provider Nearest Likelihood by Region')
