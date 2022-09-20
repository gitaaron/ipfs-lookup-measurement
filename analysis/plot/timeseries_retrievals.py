import pandas as pd
import matplotlib.pyplot as plt
from typing import List
from models.model_retrieval import Retrieval

def plot_total_phase(retrievals:List[Retrieval], title: str):
    overall_durations = []
    initiated_durations = []
    getting_closest_peers_durations = []
    dialing_durations = []
    fetching_durations = []

    for ret in retrievals:
        overall_durations += [
            (ret.done_retrieving_at - ret.retrieval_started_at).total_seconds()]

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
    ax.set_title(title)
