import numpy as np
import matplotlib.pyplot as plt
from models.model_data_set import DataSet
from helpers.constants import RetrievalPhase

def plot(data_set: DataSet):
    retrievals = data_set.retrievals_has_uptime
    d = data_set.agent_uptime_durations
    agent_uptimes = [ret.agent_uptime.total_seconds() for ret in retrievals]
    bins = np.linspace(d['min'].duration, d['max'].duration + 1e-12, 5)
    bucket_locations = np.digitize(agent_uptimes, bins)

    buckets = {}

    for idx,ret in enumerate(retrievals):
        bl = bucket_locations[idx]
        if bl not in buckets:
            buckets[bl] = []
        buckets[bl].append(ret.duration(RetrievalPhase.TOTAL).total_seconds())
        idx+=1

    bucket_avgs = {}

    for b,durations in buckets.items():
        bucket_avgs[b] = np.mean(durations)

    sorted_avgs = [bucket_avgs.get(i, 0) for i in range(1, len(bins))]

    fig1, ax1 = plt.subplots()
    ax1.bar(bins[:-1], height=sorted_avgs, 
        width=bins[1] - bins[0], align='edge')
    plt.xticks(bins)
    ax1.set_xlabel('Agent Uptime (sec.)')
    ax1.set_ylabel('Average Duration (sec.)')
    ax1.set_title('Retrieval Total Duration by Agent Uptime')

    plt.show() 