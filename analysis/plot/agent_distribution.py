import matplotlib.pyplot as plt
from models.model_data_set import DataSet
from helpers.constants import PlayerType
from pickled.model_retrieval import Retrieval

def plot(retrievals: list[Retrieval], title: str):
    fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)

    agent_counts = {}
    for ret in retrievals:
        av = ret.first_referer_to_fp.agent_version.split('/')[0]
        if av not in agent_counts:
            agent_counts[av] = 1
        else:
            agent_counts[av] += 1

    ax1.bar(list(agent_counts.keys()), list(agent_counts.values()))

    ax1.set_ylabel('Count')
    ax1.set_title(title)

    txt = f"Sample Size: {len(retrievals)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)
