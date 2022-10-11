import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import List
from pickled.model_retrieval import Retrieval
from helpers.constants import RetrievalPhase
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

def plot_duration_each_region(phase: RetrievalPhase, data_set: DataSet, title: str):

    start_dates = [ret.retrieval_started_at for ret in data_set.total_completed_retrievals]
    start_dates.sort()

    region_durations = {}

    for agent,agent_events in data_set.agent_events_map.items():
        region_durations[agent.region] = []
        for start_date in start_dates:
            region_durations[agent.region].append(np.nan)

        for ret in agent_events.completed_retrievals:
            start_index = start_dates.index(ret.retrieval_started_at)
            region_durations[agent.region][start_index] = (ret.duration(phase)).total_seconds()


    DF = pd.DataFrame(region_durations, index=start_dates).bfill()
    ax = DF.plot(x_compat=True, rot=90, figsize=(16, 5),)
    ax.set_ylabel('Duration (sec.)')
    ax.set_title(title)

def plot_each_phase_all_regions(retrievals:List[Retrieval], title: str):
    overall_durations = []
    initiated_durations = []
    getting_closest_peers_durations = []
    dialing_durations = []
    fetching_durations = []

    for ret in retrievals:
        overall_durations += [
            (ret.duration(RetrievalPhase.TOTAL)).total_seconds()]

        initiated_durations += [
            (ret.get_providers_queries_started_at - ret.retrieval_started_at).total_seconds()]

        getting_closest_peers_durations += [
            (ret.dial_started_at - ret.get_providers_queries_started_at).total_seconds()]

        dialing_durations += [
            (ret.connected_at - ret.dial_started_at).total_seconds()]

        fetching_durations += [
            (ret.done_retrieving_at - ret.connected_at).total_seconds()]


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
