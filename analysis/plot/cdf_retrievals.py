import numpy as np
from pickled.model_retrieval import Retrieval
from typing import List
import matplotlib.pyplot as plt
from models.model_data_set import DataSet
from helpers.constants import RetrievalPhase
from helpers import reduce, stringify

def plot_duration_line(axl, phase: RetrievalPhase, file_size: int, retrievals: List[Retrieval], label: str):
    retrievals = reduce.by_file_size(retrievals, file_size)
    overall_retrieval_durations = []
    highest_duration = 0

    if len(retrievals) == 0:
        return

    for ret in retrievals:
        duration = ret.duration(phase).total_seconds()
        if duration > highest_duration:
            highest_duration = duration
        overall_retrieval_durations += [duration]

    if highest_duration < 1:
        highest_duration = 1

    hist, bin_edges = np.histogram(
        overall_retrieval_durations, bins=np.arange(0, int(round(highest_duration, 0)+1), 0.1),  density=True)

    dx = bin_edges[1]-bin_edges[0]
    cdf = np.cumsum(hist)*dx

    axl.plot(bin_edges[:-1], cdf, label=label)

def plot_duration_by_region(file_size: int, phase: RetrievalPhase, data_set: DataSet):
    fig, axl = plt.subplots()
    for agent,agent_events in data_set.agent_events_map.items():
        plot_duration_line(axl, phase, file_size, agent_events.completed_retrievals, agent.region)

    axl.set_title(f"Retrieval {phase.name} Duration by Region")
    axl.set_xlabel('Duration (sec.)')
    axl.legend(loc='lower right')
    txt = f"File Size: {stringify.file_size(file_size)}"
    fig.subplots_adjust(bottom=0.15)
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)


def plot_phase_comparison(file_size: int, retrievals: list[Retrieval]):
    fig, axl = plt.subplots()
    for phase in RetrievalPhase:
        plot_duration_line(axl, phase, file_size, retrievals, phase.name)
    axl.set_title('Retrieval Phase Duration Distribution')
    axl.set_xlabel('Duration (sec.)')
    axl.legend(loc='lower right')
    txt = f"File Size: {stringify.file_size(file_size)}"
    fig.subplots_adjust(bottom=0.15)
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)
