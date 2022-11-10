import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime,timedelta
from pickled.model_retrieval import Retrieval
from helpers.constants import RetrievalPhase
from helpers import reduce, stringify, calc
from models.model_region import Region
from models.model_data_set import DataSet

# `freq` is specified by Pandas `date_range`
# https://pandas.pydata.org/docs/reference/api/pandas.date_range.html
def plot_interval_duration_each_region(file_size: int, phase: RetrievalPhase, data_set: DataSet, title: str, freq: str):
    retrievals = reduce.by_file_size(data_set.total_completed_retrievals, file_size)
    start_dates = [pd.to_datetime(ret.retrieval_started_at) for ret in retrievals]
    ts_start_dates = [ts.value for ts in start_dates]

    start = None
    end = None
    for ts in start_dates:
        if start is None or ts < start:
            start = ts
        if end is None or ts > end:
            end = ts


    edges = [pd.to_datetime(v) for v in pd.date_range(start=start, end=end+timedelta(seconds=1), freq=freq).values]
    ts_edges = [ts.value for ts in edges]

    bucket_locations = np.digitize(ts_start_dates, ts_edges)

    bucket_retrievals = {}

    region_bucket_retrievals = {}
    region_bucket_durations = {}


    for agent in data_set.agent_events_map.keys():
        region_bucket_retrievals[agent.region] = {}
        for bl in range(len(edges)):
            region_bucket_retrievals[agent.region][bl] = []
        region_bucket_durations[agent.region] = {}

    for idx, ret in enumerate(retrievals):
        bl = bucket_locations[idx]
        region_bucket_retrievals[ret.origin][bl-1].append(ret)

    for region,bucket_retrievals in region_bucket_retrievals.items():
        for b,rets in bucket_retrievals.items():
            if len(rets) > 0:
                region_bucket_durations[region][b] = calc.avg_duration(rets, phase)


    region_sorted_durations = {}

    for region,bucket_durations in region_bucket_durations.items():
        region_sorted_durations[region] = [bucket_durations.get(i, np.nan) for i in range(len(edges))]


    DF = pd.DataFrame(region_sorted_durations, index=edges).bfill()
    ax = DF.plot(x_compat=True, rot=90, figsize=(16, 5),)
    ax.set_ylabel('Duration (sec.)')
    ax.set_title(title)
    txt = f"File Size: {stringify.file_size(file_size)}, Sample Size: {len(retrievals)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)


def plot_each_phase_all_regions(file_size: int, retrievals:list[Retrieval], title: str):
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

# `freq` is specified by Pandas `date_range`
# https://pandas.pydata.org/docs/reference/api/pandas.date_range.html
def plot_interval_each_phase_all_regions(file_size: int, data_set:DataSet, title: str, freq: str):
    retrievals = reduce.by_file_size(data_set.total_completed_retrievals, file_size)

    start_dates = [pd.to_datetime(ret.retrieval_started_at) for ret in retrievals]
    ts_start_dates = [ts.value for ts in start_dates]

    start = None
    end = None
    for ts in start_dates:
        if start is None or ts < start:
            start = ts
        if end is None or ts > end:
            end = ts

    edges = [pd.to_datetime(v) for v in pd.date_range(start=start, end=end+timedelta(seconds=1), freq=freq).values]
    ts_edges = [ts.value for ts in edges]

    bucket_locations = np.digitize(ts_start_dates, ts_edges)

    bucket_retrievals = {}
    for bl in range(len(edges)):
        bucket_retrievals[bl] = []

    for idx, ret in enumerate(retrievals):
        bl = bucket_locations[idx]
        bucket_retrievals[bl-1].append(ret)

    phase_bucket_durations = {}
    for phase in RetrievalPhase:
        phase_bucket_durations[phase] = {}

    for b,rets in bucket_retrievals.items():
        if len(rets) > 0:
            for phase in RetrievalPhase:
                phase_bucket_durations[phase][b] = calc.avg_duration(rets, phase)

    phase_sorted_durations = {}

    for phase in RetrievalPhase:
        phase_sorted_durations[phase.name] = [phase_bucket_durations[phase].get(i, np.nan) for i in range(len(edges))]

    DF = pd.DataFrame(phase_sorted_durations, index=edges).bfill()
    ax = DF.plot(x_compat=True, rot=90, figsize=(16, 5),)
    ax.set_ylabel('Duration (sec.)')
    ax.set_title(title)
    txt = f"File Size: {stringify.file_size(file_size)}, Sample Size: {len(retrievals)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)

def plot_each_phase_all_regions(file_size: int, data_set:DataSet, title: str):
    retrievals = reduce.by_file_size(data_set.total_completed_retrievals, file_size)
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
