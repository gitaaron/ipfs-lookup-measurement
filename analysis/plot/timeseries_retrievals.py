import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import List
from pickled.model_retrieval import Retrieval
from helpers.constants import RetrievalPhase
from helpers import reduce, stringify
from models.model_region import Region
from models.model_data_set import DataSet


def plot_num_providers(retrievals:List[Retrieval], title: str):

    num_providers_in_retrievals = []

    for ret in retrievals:
        num_providers_in_retrievals.append(len(ret.provider_peers))


    start_dates = [ret.retrieval_started_at for ret in retrievals]

    DF = pd.DataFrame(
            {
                "num_providers_in_retrievals":num_providers_in_retrievals,
            }, index=start_dates)

    ax = DF.plot(x_compat=True, rot=90, figsize=(16, 5),)
    ax.set_ylabel('Number Providers found during Retrieval')
    ax.set_title(title)
    txt = f"Sample Size: {len(retrievals)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)


def plot_duration_each_region(file_size: int, phase: RetrievalPhase, data_set: DataSet, title: str):
    retrievals = reduce.by_file_size(data_set.total_completed_retrievals, file_size)
    start_dates = [ret.retrieval_started_at for ret in retrievals]
    start_dates.sort()

    region_durations = {}

    for agent,agent_events in data_set.agent_events_map.items():
        region_durations[agent.region] = []
        for start_date in start_dates:
            region_durations[agent.region].append(np.nan)

        agent_retrievals = reduce.by_file_size(agent_events.completed_retrievals, file_size)

        for ret in agent_retrievals:
            start_index = start_dates.index(ret.retrieval_started_at)
            region_durations[agent.region][start_index] = (ret.duration(phase)).total_seconds()


    DF = pd.DataFrame(region_durations, index=start_dates).bfill()
    ax = DF.plot(x_compat=True, rot=90, figsize=(16, 5),)
    ax.set_ylabel('Duration (sec.)')
    ax.set_title(title)
    txt = f"File Size: {stringify.file_size(file_size)}, Sample Size: {len(retrievals)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)

def plot_each_phase_all_regions(file_size: int, retrievals:List[Retrieval], title: str):
    retrievals = reduce.by_file_size(retrievals, file_size)
    overall_durations = []
    initiated_durations = []
    getting_closest_peers_durations = []
    dialing_durations = []
    fetching_durations = []

    for ret in retrievals:
        overall_durations += [
            (ret.duration(RetrievalPhase.TOTAL)).total_seconds()]

        initiated_durations += [
            ret.duration(RetrievalPhase.INITIATED).total_seconds()]

        getting_closest_peers_durations += [
            ret.duration(RetrievalPhase.GETTING_CLOSEST_PEERS).total_seconds()]

        dialing_durations += [
            ret.duration(RetrievalPhase.DIALING).total_seconds()]

        fetching_durations += [
            ret.duration(RetrievalPhase.FETCHING).total_seconds()]


    start_dates = [ret.retrieval_started_at for ret in retrievals]

    DF = pd.DataFrame(
            {
                "total":overall_durations,
                "initated":initiated_durations,
                "getting_closest_peers":getting_closest_peers_durations,
                "dialing":dialing_durations,
                "fetching":fetching_durations
            }, index=start_dates)

    ax = DF.plot(x_compat=True, rot=90, figsize=(16, 5),)
    ax.set_ylabel('Duration (sec.)')
    ax.set_title(title)
    txt = f"File Size: {stringify.file_size(file_size)}, Sample Size: {len(retrievals)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)
