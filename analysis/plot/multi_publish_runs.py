import matplotlib.pyplot as plt
from helpers import reduce
from models.model_data_set import DataSet
from helpers.constants import PlayerType
from . import agent_distribution


def plot_first_referer_agents_not_in_target_add_list(data_set: DataSet):
    retrievals = reduce.by_main_player(data_set.total_completed_retrievals, PlayerType.RETRIEVER)
    retrievals = reduce.by_referer_in_successful_add_list(retrievals, data_set.runs, False)
    agent_distribution.plot(retrievals, f"First Referer Agent Distribution where First Referer is not in Publishers Add Target List")
