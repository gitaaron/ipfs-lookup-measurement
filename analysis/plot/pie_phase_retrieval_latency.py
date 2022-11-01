import matplotlib.pyplot as plt
from typing import List
from pickled.model_retrieval import Retrieval
from helpers.constants import RetrievalPhase
from helpers import reduce
from helpers import stringify


def plot(retrievals: List[Retrieval], file_size: int):

    total_initiated_duration = 0
    total_getting_closest_peers_duration = 0
    total_dialing_duration = 0
    total_fetching_duration = 0

    retrievals = reduce.by_file_size(retrievals, file_size)

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
    ax1.set_title('Retrieval Phase Duration Comparison')
    txt = f"File Size: {stringify.file_size(file_size)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)
