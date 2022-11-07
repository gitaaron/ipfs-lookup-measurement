import matplotlib.pyplot as plt
from models.model_data_set import DataSet
from helpers.constants import RetrievalPhase



def plot_phases(data_set: DataSet, phase_x: RetrievalPhase,  phase_y: RetrievalPhase, file_size: int):
    plt.rcdefaults()
    fig1, ax1 = plt.subplots(figsize=(9,6), dpi=80)

    retrievals = data_set.comparable_file_size_retrievals[file_size]
    durations_x = [ret.duration(phase_x).total_seconds() for ret in retrievals]
    durations_y = [ret.duration(phase_y).total_seconds() for ret in retrievals]


    ax1.scatter(durations_x, durations_y)
    ax1.set_xlabel(f"{phase_x} durations (sec.)")
    ax1.set_ylabel(f"{phase_y} durations (sec.)")

    txt = f"Sample Size: {len(retrievals)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)
    ax1.set_title(f"Comparing {phase_y} vs {phase_x} durations")
