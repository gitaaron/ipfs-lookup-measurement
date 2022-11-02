import matplotlib.pyplot as plt
from helpers import calc, reduce
from models.model_data_set import DataSet
from helpers.constants import RetrievalPhase, PlayerType


def plot_duration(data_set: DataSet, phase: RetrievalPhase, title: str, main_player: PlayerType):
    fig1, ax1 = plt.subplots(figsize=(9,6), dpi=80)
    file_size_labels = []
    durations = []

    retrievals = data_set.total_completed_retrievals

    sorted_fs = list(data_set.unique_file_sizes.keys())
    # ignore delayed retrievals and missing file_size
    sorted_fs = list(filter(lambda fs: fs is not None and fs != 52439, sorted_fs))
    sorted_fs.sort()

    for file_size in sorted_fs:
        f_rets = reduce.by_file_size(retrievals, file_size)
        if main_player is not None:
            f_rets = reduce.by_main_player(f_rets, main_player)
        if len(f_rets) > 0:
            file_size_labels.append(str(file_size))
            durations.append(calc.avg_duration(f_rets, phase))

    ax1.bar(file_size_labels, durations)

    ax1.set_ylabel(f"{phase.name} duration (sec.)")
    ax1.set_title(title)

    if main_player is not None:
        if main_player==PlayerType.RETRIEVER:
            txt = f"Many Providers (~5)"
        else:
            txt = f"Single Provider (=1)"
        plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=8)
