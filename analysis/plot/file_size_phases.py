import matplotlib.pyplot as plt
import numpy as np
from helpers import calc, reduce, stringify
from models.model_data_set import DataSet
from helpers.constants import RetrievalPhase, PlayerType

def plot_percent_slow(data_set: DataSet, title: str):
    phase = RetrievalPhase.TOTAL
    fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)
    file_size_labels = []

    phase_percents = {}
    phase_sample_sizes = {}

    retrievals = data_set.total_completed_retrievals

    sorted_fs = data_set.comparable_file_sizes

    phases = list(filter(lambda phase: phase != RetrievalPhase.TOTAL, RetrievalPhase))
    sample_sizes = []

    for phase in phases:
        phase_percents[phase] = []

    for file_size in sorted_fs:
        file_size_labels.append(str(file_size))
        f_rets = reduce.by_file_size(retrievals, file_size)
        sample_sizes.append(len(f_rets))
        for phase in phases:
            if len(f_rets) > 0:
                percent_slow,_ = data_set.percent_slow(f_rets, phase)
                phase_percents[phase].append(percent_slow)
            else:
                phase_percents[phase].append(0)

    x_pos = np.arange(len(file_size_labels))

    width = 0.1

    rects_by_phase = {}

    for idx, phase in enumerate(phases):
        idx_x_pos = x_pos - width*len(phases)/2 + (idx*width)
        rects_by_phase[phase] = ax1.bar(idx_x_pos, phase_percents[phase], width, align='center', label=f"{phase}")

    fs_rects = [{'x':None, 'y':None} for i in range(len(sorted_fs))]

    for phase,rects in rects_by_phase.items():
        for idx, rect in enumerate(rects):
            if fs_rects[idx]['x'] is None:
                fs_rects[idx]['x'] = rect.get_x()

            if fs_rects[idx]['y'] is None or fs_rects[idx]['y'] < rect.get_height():
                fs_rects[idx]['y'] = rect.get_height()

    for idx, rect in enumerate(fs_rects):
        plt.text(rect['x'] + width * len(phases) / 2.0, rect['y'], f'total:{sample_sizes[idx]}', ha='center', va='bottom')


    ax1.set_ylabel(f"Percent Slow")
    ax1.set_title(title)
    ax1.set_xticks(x_pos, labels=file_size_labels)
    ax1.legend(loc='upper left')


    txt = f"Sample Size: {np.sum(sample_sizes)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=8)

def plot_duration(data_set: DataSet, title: str):
    phase = RetrievalPhase.TOTAL
    fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)
    file_size_labels = []

    phase_durations = {}
    phase_sample_sizes = {}

    retrievals = data_set.total_completed_retrievals

    sorted_fs = data_set.comparable_file_sizes

    phases = list(filter(lambda phase: phase != RetrievalPhase.TOTAL, RetrievalPhase))
    sample_sizes = []

    for phase in phases:
        phase_durations[phase] = []

    for file_size in sorted_fs:
        file_size_labels.append(str(file_size))
        f_rets = reduce.by_file_size(retrievals, file_size)
        sample_sizes.append(len(f_rets))
        for phase in phases:
            if len(f_rets) > 0:
                phase_durations[phase].append(calc.avg_duration(f_rets, phase))
            else:
                phase_durations[phase].append(0)

    x_pos = np.arange(len(file_size_labels))

    width = 0.1

    rects_by_phase = {}

    for idx, phase in enumerate(phases):
        idx_x_pos = x_pos - width*len(phases)/2 + (idx*width)
        rects_by_phase[phase] = ax1.bar(idx_x_pos, phase_durations[phase], width, align='center', label=f"{phase}")

    fs_rects = [{'x':None, 'y':None} for i in range(len(sorted_fs))]

    for phase,rects in rects_by_phase.items():
        for idx, rect in enumerate(rects):
            if fs_rects[idx]['x'] is None:
                fs_rects[idx]['x'] = rect.get_x()

            if fs_rects[idx]['y'] is None or fs_rects[idx]['y'] < rect.get_height():
                fs_rects[idx]['y'] = rect.get_height()

    for idx, rect in enumerate(fs_rects):
        plt.text(rect['x'] + width * len(phases) / 2.0, rect['y'], f'total:{sample_sizes[idx]}', ha='center', va='bottom')


    ax1.set_ylabel(f"Average Duration (sec.)")
    ax1.set_title(title)
    ax1.set_xticks(x_pos, labels=file_size_labels)
    ax1.legend(loc='upper left')


    txt = f"Sample Size: {np.sum(sample_sizes)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=8)


def plot_scatter(data_set: DataSet, phase_x: RetrievalPhase,  phase_y: RetrievalPhase, file_size: int):
    plt.rcdefaults()
    fig1, ax1 = plt.subplots(figsize=(9,6), dpi=80)

    retrievals = data_set.comparable_file_size_retrievals[file_size]
    durations_x = [ret.duration(phase_x).total_seconds() for ret in retrievals]
    durations_y = [ret.duration(phase_y).total_seconds() for ret in retrievals]


    ax1.scatter(durations_x, durations_y)
    ax1.set_xlabel(f"{phase_x} durations (sec.)")
    ax1.set_ylabel(f"{phase_y} durations (sec.)")

    txt = f"File Size: {stringify.file_size(file_size)}, Sample Size: {len(retrievals)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)
    ax1.set_title(f"Comparing {phase_y} vs {phase_x} durations")
