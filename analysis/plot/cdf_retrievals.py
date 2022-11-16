import numpy as np
from pickled.model_retrieval import Retrieval
from typing import List
import matplotlib.pyplot as plt
from models.model_data_set import DataSet
from helpers.constants import RetrievalPhase, PlayerType
from helpers import reduce, stringify

def plot_duration_line(axl, phase: RetrievalPhase, file_size: int, retrievals: List[Retrieval], label: str, include_size: bool, many_providers_only: bool) -> int:
    if file_size is not None:
        retrievals = reduce.by_file_size(retrievals, file_size)
    if many_providers_only:
        retrievals = reduce.by_main_player(retrievals, PlayerType.RETRIEVER)

    overall_retrieval_durations = []
    highest_duration = 0

    if len(retrievals) == 0:
        return 0

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

    if include_size:
        label = f"{label} ({len(retrievals)})"

    axl.plot(bin_edges[:-1], cdf, label=label)

    return len(retrievals)

def plot_duration_by_region(file_size: int, phase: RetrievalPhase, data_set: DataSet, multi_only: bool):
    fig, axl = plt.subplots()
    sample_size = 0
    for agent,agent_events in data_set.agent_events_map.items():
        sample_size += plot_duration_line(axl, phase, file_size, agent_events.completed_retrievals, agent.region, True, multi_only)

    if multi_only:
        axl.set_title(f"CDF of multi provider {phase.name} Duration by Region")
    else:
        axl.set_title(f"CDF of {phase.name} Duration by Region")

    axl.set_ylabel('Number of Retrievals in %')
    axl.set_xlabel('Duration (sec.)')
    axl.legend(loc='lower right')
    txt = f"Sample Size: {sample_size}"
    if file_size is not None:
        txt += f", File Size: {stringify.file_size(file_size)}"

    fig.subplots_adjust(bottom=0.15)
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)


def plot_phase_comparison(file_size: int, retrievals: list[Retrieval]):
    fig, axl = plt.subplots()
    sample_size = 0
    for phase in RetrievalPhase:
        sample_size = plot_duration_line(axl, phase, file_size, retrievals, phase.name, False, False)
    axl.set_title('CDF of Duration by Phase')
    axl.set_ylabel('Number of Retrievals in %')
    axl.set_xlabel('Duration (sec.)')
    axl.legend(loc='lower right')
    txt = f"File Size: {stringify.file_size(file_size)}, Sample Size: {sample_size}"
    fig.subplots_adjust(bottom=0.15)
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)
