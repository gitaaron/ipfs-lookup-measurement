import matplotlib.pyplot as plt
import numpy as np
from helpers import calc, reduce, stringify
from models.model_data_set import DataSet
from helpers.constants import RetrievalPhase, PlayerType



def plot_percent_slow_by_file_size(data_set: DataSet, title: str):
    fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)
    file_size_labels = []
    sp_percents = []
    mp_percents = []
    sp_sample_sizes = []
    mp_sample_sizes = []


    for file_size in data_set.comparable_file_sizes:
        file_size_labels.append(f"{file_size}")

        rets = reduce.by_file_size(data_set.total_completed_retrievals, file_size)
        sp_rets = reduce.by_main_player(rets, PlayerType.PUBLISHER)
        mp_rets = reduce.by_main_player(rets, PlayerType.RETRIEVER)

        if len(sp_rets) > 0:
            sp_sample_sizes.append(len(sp_rets))
            percent_slow,_ = data_set.percent_slow(sp_rets, RetrievalPhase.TOTAL)
            sp_percents.append(percent_slow)
        else:
            sp_sample_sizes.append(0)
            sp_percents.append(0)

        if len(mp_rets) > 0:
            mp_sample_sizes.append(len(mp_rets))
            percent_slow,_ = data_set.percent_slow(mp_rets, RetrievalPhase.TOTAL)
            mp_percents.append(percent_slow)
        else:
            mp_sample_sizes.append(0)
            mp_percents.append(0)

    x_pos = np.arange(len(file_size_labels))

    width = 0.4

    sp_rects = ax1.bar(x_pos-0.2, sp_percents, width, align='center', label="single provider(=1)")
    mp_rects = ax1.bar(x_pos+0.2, mp_percents, width, align='center', label="many providers(~5)")

    for idx, rect in enumerate(sp_rects):
        plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'total:{sp_sample_sizes[idx]}', ha='center', va='bottom')

    for idx, rect in enumerate(mp_rects):
        plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'total:{mp_sample_sizes[idx]}', ha='center', va='bottom')

    ax1.legend(loc='upper left')
    ax1.set_xticks(x_pos, labels=file_size_labels)
    ax1.set_ylabel(f"Percent Slow")
    ax1.set_title(title)

    txt = f"Sample Size: {np.sum(sp_sample_sizes)+np.sum(mp_sample_sizes)}"

    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=8)

def plot_percent_slow_by_phase(data_set: DataSet, title: str):
    fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)
    phase_labels = []
    sp_percents = []
    mp_percents = []
    sp_sample_sizes = []
    mp_sample_sizes = []

    rets = data_set.total_completed_retrievals

    for phase in RetrievalPhase:
        phase_labels.append(f"{phase}")


        sp_rets = reduce.by_main_player(rets, PlayerType.PUBLISHER)
        mp_rets = reduce.by_main_player(rets, PlayerType.RETRIEVER)

        if len(sp_rets) > 0:
            sp_sample_sizes.append(len(sp_rets))
            percent_slow,_ = data_set.percent_slow(sp_rets, phase)
            sp_percents.append(percent_slow)
        else:
            sp_sample_sizes.append(0)
            sp_percents.append(0)

        if len(mp_rets) > 0:
            mp_sample_sizes.append(len(mp_rets))
            percent_slow,_ = data_set.percent_slow(mp_rets, phase)
            mp_percents.append(percent_slow)
        else:
            mp_sample_sizes.append(0)
            mp_percents.append(0)

    x_pos = np.arange(len(phase_labels))

    width = 0.4

    sp_rects = ax1.bar(x_pos-0.2, sp_percents, width, align='center', label="single provider(=1)")
    mp_rects = ax1.bar(x_pos+0.2, mp_percents, width, align='center', label="many providers(~5)")

    for idx, rect in enumerate(sp_rects):
        plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'total:{sp_sample_sizes[idx]}', ha='center', va='bottom')

    for idx, rect in enumerate(mp_rects):
        plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'total:{mp_sample_sizes[idx]}', ha='center', va='bottom')

    ax1.legend(loc='upper right')
    ax1.set_xticks(x_pos, labels=phase_labels)
    ax1.set_ylabel(f"Percent Slow")
    ax1.set_title(title)

    txt = f"Sample Size: {np.sum(sp_sample_sizes)+np.sum(mp_sample_sizes)}"

    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=8)

def plot_duration_by_phase(data_set: DataSet, title: str, file_size: int):
    fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)
    phase_labels = []
    sp_durations = []
    mp_durations = []
    sp_sample_sizes = []
    mp_sample_sizes = []

    rets = reduce.by_file_size(data_set.total_completed_retrievals, file_size)

    for phase in RetrievalPhase:

        sp_rets = reduce.by_main_player(rets, PlayerType.PUBLISHER)
        mp_rets = reduce.by_main_player(rets, PlayerType.RETRIEVER)

        if len(sp_rets) > 0:
            sp_sample_sizes.append(len(sp_rets))
            sp_duration = calc.avg_duration(sp_rets, phase)
        else:
            sp_sample_sizes.append(0)
            sp_duration = 0

        if len(mp_rets) > 0:
            mp_sample_sizes.append(len(mp_rets))
            mp_duration = calc.avg_duration(mp_rets, phase)
        else:
            mp_sample_sizes.append(0)
            mp_duration = 0

        sp_durations.append(sp_duration)
        mp_durations.append(mp_duration)

        phase_labels.append(f"{phase} ({round(sp_duration/mp_duration,1)})")

    x_pos = np.arange(len(phase_labels))

    width = 0.4

    sp_rects = ax1.bar(x_pos-0.2, sp_durations, width, align='center', label="single provider(=1)")
    mp_rects = ax1.bar(x_pos+0.2, mp_durations, width, align='center', label="many providers(~5)")

    for idx, rect in enumerate(sp_rects):
        plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'total:{sp_sample_sizes[idx]}', ha='center', va='bottom')

    for idx, rect in enumerate(mp_rects):
        plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'total:{mp_sample_sizes[idx]}', ha='center', va='bottom')

    ax1.legend(loc='upper right')
    ax1.set_xticks(x_pos, labels=phase_labels)
    ax1.set_ylabel(f"Average Duration (sec.)")
    ax1.set_title(title)

    txt = f"Sample Size: {np.sum(sp_sample_sizes)+np.sum(mp_sample_sizes)}, File Size: {stringify.file_size(file_size)}"

    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=8)

def plot_duration_by_file_size(data_set: DataSet, title: str):
    fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)
    file_size_labels = []
    sp_durations = []
    mp_durations = []
    sp_sample_sizes = []
    mp_sample_sizes = []


    for file_size in data_set.comparable_file_sizes:

        rets = reduce.by_file_size(data_set.total_completed_retrievals, file_size)
        sp_rets = reduce.by_main_player(rets, PlayerType.PUBLISHER)
        mp_rets = reduce.by_main_player(rets, PlayerType.RETRIEVER)

        if len(sp_rets) > 0:
            sp_sample_sizes.append(len(sp_rets))
            sp_duration  = calc.avg_duration(sp_rets, RetrievalPhase.TOTAL)
        else:
            sp_sample_sizes.append(0)
            sp_duration = 0

        if len(mp_rets) > 0:
            mp_sample_sizes.append(len(mp_rets))
            mp_duration = calc.avg_duration(mp_rets, RetrievalPhase.TOTAL)
        else:
            mp_sample_sizes.append(0)
            mp_duration = 0

        sp_durations.append(sp_duration)
        mp_durations.append(mp_duration)

        file_size_labels.append(f"{file_size} ({round(sp_duration/mp_duration,1)})")

    x_pos = np.arange(len(file_size_labels))

    width = 0.4

    sp_rects = ax1.bar(x_pos-0.2, sp_durations, width, align='center', label="single provider(=1)")
    mp_rects = ax1.bar(x_pos+0.2, mp_durations, width, align='center', label="many providers(~5)")

    for idx, rect in enumerate(sp_rects):
        plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'total:{sp_sample_sizes[idx]}', ha='center', va='bottom')

    for idx, rect in enumerate(mp_rects):
        plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(), f'total:{mp_sample_sizes[idx]}', ha='center', va='bottom')

    ax1.legend(loc='upper left')
    ax1.set_xticks(x_pos, labels=file_size_labels)
    ax1.set_ylabel(f"Average {RetrievalPhase.TOTAL} Duration (sec.)")
    ax1.set_title(title)

    txt = f"Sample Size: {np.sum(sp_sample_sizes)+np.sum(mp_sample_sizes)}"

    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=8)
