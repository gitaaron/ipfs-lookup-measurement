import matplotlib.pyplot as plt
import numpy as np
from models.model_data_set import DataSet
from helpers.constants import RetrievalPhase
from helpers import calc, reduce, stringify


def plot_histo_percent_slow(data_set: DataSet, phase: RetrievalPhase, title: str):
    bins, sorted_percents, width, delay_file_size, sample_sizes = calc.publish_age_percent_slow_bins(data_set, phase)
    fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)
    rects = ax1.bar(bins, height=sorted_percents,
        width=width, align='edge')
    for idx, rect in enumerate(rects):
        plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'count:{sample_sizes[idx]}', ha='center', va='bottom')
    plt.xticks(bins)
    ax1.set_xlabel('Publish Age (sec.)')
    ax1.set_ylabel('Percent Slow')
    ax1.set_title(title)
    txt = f"File Size: {round(delay_file_size/1024, 3)} KB, Sample Size: {np.sum(sample_sizes)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)

def plot_histo_duration(data_set: DataSet, phase: RetrievalPhase, title: str):
    bins, sorted_avgs, width, delay_file_size, sample_sizes = calc.publish_age_duration_bins(data_set, phase)
    fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)
    rects = ax1.bar(bins, height=sorted_avgs,
        width=width, align='edge')
    for idx, rect in enumerate(rects):
        plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'count:{sample_sizes[idx]}', ha='center', va='bottom')
    plt.xticks(bins)
    ax1.set_xlabel('Publish Age (sec.)')
    ax1.set_ylabel('Average Duration (sec.)')
    ax1.set_title(title)
    txt = f"File Size: {round(delay_file_size/1024, 3)} KB, Sample Size: {np.sum(sample_sizes)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)

def plot_scatter_duration(data_set: DataSet, file_size: int, phase: RetrievalPhase):
    fig1, ax1 = plt.subplots(figsize=(9,6), dpi=80)
    retrievals = reduce.by_file_size(data_set.has_publish_age_retrievals, file_size)
    durations_y = [ret.duration(phase).total_seconds() for ret in retrievals]
    publish_ages_x = [round(data_set.publish_age(ret).total_seconds(), 2) for ret in retrievals]

    ax1.scatter(publish_ages_x, durations_y)
    ax1.set_xlabel('Publish Age (sec.)')
    ax1.set_ylabel(f"Duration (sec.)")
    txt = f"File Size: {round(file_size/1024, 3)} KB, Sample Size: {len(retrievals)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)
    ax1.set_title(f"Comparing {phase} Durations vs Publish Age")
