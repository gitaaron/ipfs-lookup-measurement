import matplotlib.pyplot as plt
from helpers import reduce
from models.model_data_set import DataSet
from helpers.constants import PlayerType


def plot_first_referer_agents_not_in_target_add_list(data_set: DataSet):
    fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)
    retrievals = reduce.by_main_player(data_set.total_completed_retrievals, PlayerType.RETRIEVER)
    retrievals = reduce.by_referer_in_successful_add_list(retrievals, data_set.runs, False)

    agent_counts = {}
    for ret in retrievals:
        av = ret.first_referer_to_fp.agent_version.split('/')[0]
        if av not in agent_counts:
            agent_counts[av] = 1
        else:
            agent_counts[av] += 1

    ax1.bar(list(agent_counts.keys()), list(agent_counts.values()))

    ax1.set_ylabel('Count')
    ax1.set_title(f"First Referer Agent Distribution where First Referer is not in Publishers Add Target List")

    txt = f"Sample Size: {len(retrievals)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)
