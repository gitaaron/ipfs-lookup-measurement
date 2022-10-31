import matplotlib.pyplot as plt
import numpy as np
from helpers import calc
from models.model_data_set import DataSet

def plot_fpn_likelihood(data_set: DataSet):
    stats = calc.first_provider_nearest_stats(data_set)
    fig1, ax1 = plt.subplots(figsize=(9,6), dpi=80)
    num_fpn = stats['all']['num_fpn']
    num_non_fpn = stats['all']['num_non_fpn']
    b1 = ax1.barh(['all'], [num_fpn], )
    b2 = ax1.barh(['all'], [num_non_fpn], left=num_fpn,)

    plt.legend([b1, b2], ['num_fpns', 'num_non_fpns'], loc="upper right")

    ax1.set_ylabel(None)
    ax1.set_xlabel('Ratio of fpn vs non-fpn')
    ax1.set_title('First Provider Nearest Likelihood')

def plot_fpn_likelihood_by_region(data_set: DataSet):
    region_labels = []

    regions_num_fpns = []
    regions_num_non_fpns = []

    stats = calc.first_provider_nearest_stats(data_set)

    for agent, agent_events in data_set.agent_events_map.items():
        region_labels.append(agent.region)
        regions_num_fpns.append(stats[agent.region.name]['num_fpns'])
        regions_num_non_fpns.append(stats[agent.region.name]['num_non_fpns'])

    plt.rcdefaults()
    fig1, ax1 = plt.subplots(figsize=(9,6), dpi=80)

    x_pos = np.arange(len(region_labels))
    b1 = ax1.bar(x_pos, regions_num_fpns, align='center')
    b2 = ax1.bar(x_pos, regions_num_non_fpns, align='center', bottom=regions_num_fpns)

    x_pos = np.arange(len(region_labels))
    ax1.set_xticks(x_pos, labels=region_labels)
    plt.legend([b1, b2], ['num_fpns', 'num_non_fpns'], loc="upper right")

    ax1.set_xlabel('Regions')
    ax1.set_ylabel('Ratio of fpn vs non-fpn')

    ax1.set_title('First Provider Nearest Likelihood by Region')
