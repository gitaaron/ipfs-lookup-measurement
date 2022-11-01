import matplotlib.pyplot as plt
from helpers import calc
from models.model_data_set import DataSet
from helpers.constants import RetrievalPhase


def plot_duration(data_set: DataSet, phase: RetrievalPhase, title: str):
    fig1, ax1 = plt.subplots(figsize=(9,6), dpi=80)
    file_size_labels = []
    durations = []

    stats = calc.avg_duration_from_breakdowns(data_set.unique_file_sizes)

    sorted_fs = list(data_set.unique_file_sizes.keys())
    # ignore delayed retrievals and missing file_size
    sorted_fs = list(filter(lambda fs: fs is not None and fs != 52439, sorted_fs))
    sorted_fs.sort()

    for file_size in sorted_fs:
        file_size_labels.append(str(file_size))
        durations.append(stats[file_size][phase.name].duration)


    ax1.bar(file_size_labels, durations)

    ax1.set_ylabel(f"{phase.name} duration (sec.)")
    ax1.set_title(title)
