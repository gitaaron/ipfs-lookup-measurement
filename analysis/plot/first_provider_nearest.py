import matplotlib.pyplot as plt
import numpy as np
from helpers import calc, reduce, stringify
from models.model_data_set import DataSet
from helpers.constants import RetrievalPhase

def plot_percent_slow_by_phase(data_set: DataSet) -> bool:

    phase_labels = []
    fpn_phases = []
    non_fpn_phases = []
    fpn_rs = data_set.first_provider_nearest_retrievals
    non_fpn_rs = data_set.non_first_provider_nearest_retrievals

    if len(fpn_rs) > 0 and len(non_fpn_rs) >  0:
        fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)
        for phase in RetrievalPhase:
            fpn_percent_slow,fpn_sample_size = data_set.percent_slow(fpn_rs, phase)
            non_fpn_percent_slow,non_fpn_sample_size = data_set.percent_slow(non_fpn_rs, phase)
            if fpn_percent_slow > 0:
                label = f"{phase.name} ({round(non_fpn_percent_slow/fpn_percent_slow,1)})"
            else:
                label = f"{phase.name}"

            phase_labels.append(label)

            fpn_phases.append(fpn_percent_slow)
            non_fpn_phases.append(non_fpn_percent_slow)

        b1 = ax1.bar(phase_labels, fpn_phases)
        b2 = ax1.bar(phase_labels, non_fpn_phases, bottom=fpn_phases)

        plt.legend([b1, b2], ['fpn', 'non_fpn'], loc="upper right")

        ax1.set_ylabel('Percent Slow')
        ax1.set_title('First Provider Nearest effects on Duration by Phase')
        txt = f"Sample Size: [fpn={fpn_sample_size},non_fpn={non_fpn_sample_size}]"
        plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)
        return True

    return False


def plot_durations_by_phase(data_set: DataSet, file_size: int) -> bool:

    phase_labels = []
    fpn_durations = []
    non_fpn_durations = []
    fpn_rs = reduce.by_file_size(data_set.first_provider_nearest_retrievals, file_size)
    non_fpn_rs = reduce.by_file_size(data_set.non_first_provider_nearest_retrievals, file_size)

    if len(fpn_rs) > 0 and len(non_fpn_rs) >  0:
        fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)
        for phase in RetrievalPhase:
            fpn_duration = calc.avg_duration(fpn_rs, phase)
            non_fpn_duration = calc.avg_duration(non_fpn_rs, phase)
            phase_labels.append(f"{phase.name} ({round(non_fpn_duration/fpn_duration,1)})")

            fpn_durations.append(fpn_duration)
            non_fpn_durations.append(non_fpn_duration)

        b1 = ax1.bar(phase_labels, fpn_durations)
        b2 = ax1.bar(phase_labels, non_fpn_durations, bottom=fpn_durations)

        plt.legend([b1, b2], ['fpn', 'non_fpn'], loc="upper right")

        ax1.set_ylabel('Average Durations (sec.)')
        ax1.set_title('First Provider Nearest effects on Duration by Phase')
        txt = f"File Size: {stringify.file_size(file_size)}, Sample Size: [fpn={len(fpn_rs)},non_fpn={len(non_fpn_rs)}]"
        plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)
        return True

    return False


def plot_likelihood(data_set: DataSet):
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
    txt = f"Sample Size: {num_fpn + num_non_fpn}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)


def plot_fpn_likelihood_by_region(data_set: DataSet):
    plt.rcdefaults()
    fig1, ax1 = plt.subplots(figsize=(9,6), dpi=80)
    sample_size = 0

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
    txt = f"Sample Size: {sum(regions_num_fpns)+sum(regions_num_non_fpns)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)
