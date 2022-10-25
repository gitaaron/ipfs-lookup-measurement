import matplotlib.pyplot as plt
from typing import List
from pickled.model_retrieval import Retrieval


def plot(retrievals: List[Retrieval]):

    total_initiated_duration = 0
    total_getting_closest_peers_duration = 0
    total_dialing_duration = 0
    total_fetching_duration = 0

    for ret in retrievals:
        total_initiated_duration += ret.duration(RetrievalPhase.INITIATED).total_seconds()
        total_getting_closest_peers_duration += ret.duration(RetrievalPhase.GETTING_CLOSEST_PEERS).total_seconds()
        total_dialing_duration += ret.duration(RetrievalPhase.DIALING).total_seconds()
        total_fetching_duration += ret.duration(RetrievalPhase.FETCHING).total_seconds()

    labels = ['initiated', 'getting_closest_peers', 'dialing', 'fetching']
    phases = [total_initiated_duration, total_getting_closest_peers_duration, total_dialing_duration, total_fetching_duration]

    fig1, ax1 = plt.subplots()
    ax1.pie(phases, labels=labels, autopct='%1.1f%%')
    ax1.axis('equal')
    ax1.set_title('Retrieval Phase Average Duration Comparison')
