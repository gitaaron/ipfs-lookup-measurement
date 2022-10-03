import numpy as np
import matplotlib.pyplot as plt
from models.model_parsed_log_file import ParsedLogFile
from typing import List
from models.model_publication import Publication
from models.model_retrieval import Retrieval


def plot(retrievals: List[Retrieval]):

    total_initiated_duration = 0
    total_getting_closest_peers_duration = 0
    total_dialing_duration = 0
    total_fetching_duration = 0

    for ret in retrievals:
        total_initiated_duration += (ret.get_providers_queries_started_at - ret.retrieval_started_at).total_seconds()
        total_getting_closest_peers_duration += (ret.dial_started_at - ret.get_providers_queries_started_at).total_seconds()
        total_dialing_duration += (ret.connected_at - ret.dial_started_at).total_seconds()
        total_fetching_duration += (ret.done_retrieving_at - ret.connected_at).total_seconds()

    labels = ['initiated', 'getting_closest_peers', 'dialing', 'fetching']
    phases = [total_initiated_duration, total_getting_closest_peers_duration, total_dialing_duration, total_fetching_duration]

    fig1, ax1 = plt.subplots()
    ax1.pie(phases, labels=labels, autopct='%1.1f%%')
    ax1.axis('equal')
    ax1.set_title('Retrieval Phase Latency Comparison')
