import matplotlib.pyplot as plt
from models.model_data_set import DataSet
from helpers.constants import RetrievalPhase
from helpers import calc

def plot(data_set: DataSet):
    bins, sorted_avgs, width = calc.agent_uptime_duration_bins(data_set)
    fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)
    ax1.bar(bins, height=sorted_avgs,
        width=width, align='edge')
    plt.xticks(bins)
    ax1.set_xlabel('Agent Uptime (sec.)')
    ax1.set_ylabel('Average Duration (sec.)')
    ax1.set_title('Retrieval Total Duration by Agent Uptime')
