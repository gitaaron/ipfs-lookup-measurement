import matplotlib.pyplot as plt
import numpy as np
from models.model_data_set import DataSet
from helpers.constants import RetrievalPhase
from helpers import calc, stringify

def plot_duration(data_set: DataSet, file_size: int, phase: RetrievalPhase, title: str):
    bins, sorted_avgs, width, sample_size = calc.agent_uptime_duration_bins(data_set, file_size, phase )
    fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)
    ax1.bar(bins, height=sorted_avgs,
        width=width, align='edge')
    plt.xticks(bins)
    ax1.set_xlabel('Agent Uptime (sec.)')
    ax1.set_ylabel('Average Duration (sec.)')
    ax1.set_title(title)
    txt = f"File Size: {stringify.file_size(file_size)}, Sample Size: {sample_size}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)

def plot_percent_slow(data_set: DataSet, phase: RetrievalPhase, title: str):
    bins, sorted_avgs, width, sample_sizes = calc.agent_uptime_percent_slow_bins(data_set, phase)
    fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)
    rects = ax1.bar(bins, height=sorted_avgs,
        width=width, align='edge')

    for idx, rect in enumerate(rects):
        plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'count:{sample_sizes[idx]}', ha='center', va='bottom')

    plt.xticks(bins)
    ax1.set_xlabel('Agent Uptime (sec.)')
    ax1.set_ylabel('Percent Slow')
    ax1.set_title(title)
    txt = f"Sample Size: {np.sum(sample_sizes)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)
