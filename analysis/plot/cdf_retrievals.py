import numpy as np
from pickled.model_retrieval import Retrieval
from typing import List
import matplotlib.pyplot as plt
from models.model_data_set import DataSet


def initiated_phase(axl, retrievals: List[Retrieval]):
    overall_retrieval_durations = []
    for ret in retrievals:
        overall_retrieval_durations += [
            (ret.get_providers_queries_started_at - ret.retrieval_started_at).total_seconds()]

    hist, bin_edges = np.histogram(
        overall_retrieval_durations, bins=np.arange(0, 5, 0.1),  density=True)

    dx = bin_edges[1]-bin_edges[0]
    cdf = np.cumsum(hist)*dx

    axl.plot(bin_edges[:-1], cdf, label='initiated')


def getting_closest_peers_phase(axl, retrievals: List[Retrieval], label: str):
    overall_retrieval_durations = []
    for ret in retrievals:
        overall_retrieval_durations += [
            (ret.dial_started_at - ret.get_providers_queries_started_at).total_seconds()]

    hist, bin_edges = np.histogram(
        overall_retrieval_durations, bins=np.arange(0, 5, 0.1),  density=True)

    dx = bin_edges[1]-bin_edges[0]
    cdf = np.cumsum(hist)*dx

    axl.plot(bin_edges[:-1], cdf, label=label)


def dialing_phase(axl, retrievals: List[Retrieval]):
    overall_retrieval_durations = []
    for ret in retrievals:
        overall_retrieval_durations += [
            (ret.connected_at - ret.dial_started_at).total_seconds()]

    hist, bin_edges = np.histogram(
        overall_retrieval_durations, bins=np.arange(0, 5, 0.1),  density=True)

    dx = bin_edges[1]-bin_edges[0]
    cdf = np.cumsum(hist)*dx

    axl.plot(bin_edges[:-1], cdf, label='dialing')

def fetching_phase(axl, retrievals: List[Retrieval], label: str):
    overall_retrieval_durations = []
    for ret in retrievals:
        overall_retrieval_durations += [
            (ret.done_retrieving_at - ret.connected_at).total_seconds()]

    hist, bin_edges = np.histogram(
        overall_retrieval_durations, bins=np.arange(0, 5, 0.1),  density=True)

    dx = bin_edges[1]-bin_edges[0]
    cdf = np.cumsum(hist)*dx

    axl.plot(bin_edges[:-1], cdf, label=label)



def total(axl, retrievals: List[Retrieval], label: str):

    overall_retrieval_durations = []
    for ret in retrievals:
        overall_retrieval_durations += [
            (ret.done_retrieving_at - ret.retrieval_started_at).total_seconds()]

    hist, bin_edges = np.histogram(
        overall_retrieval_durations, bins=np.arange(0, 5, 0.1),  density=True)

    dx = bin_edges[1]-bin_edges[0]
    cdf = np.cumsum(hist)*dx

    axl.plot(bin_edges[:-1], cdf, label=label)

def plot_total(data_set: DataSet):
    fig, axl = plt.subplots()

    for agent,agent_events in data_set.agent_events_map.items():
        total(axl, agent_events.completed_retrievals, agent.region)

    axl.set_title('Retrieval Total Latency by Region (fig. d)')
    axl.legend(loc='lower right')


def plot_getting_closest_peers(data_set: DataSet):
    fig, axl = plt.subplots()

    for agent,agent_events in data_set.agent_events_map.items():
        getting_closest_peers_phase(axl, agent_events.completed_retrievals, agent.region)

    axl.set_title('Retrieval Getting Closest Peer Latency by Region (fig. e)')
    axl.legend(loc='lower right')

def plot_fetch(data_set: DataSet):
    fig, axl = plt.subplots()

    for agent,agent_events in data_set.agent_events_map.items():
        fetching_phase(axl, agent_events.completed_retrievals, agent.region)

    axl.set_title('Retrieval Fetch Latency by Region (fig. f)')
    axl.legend(loc='lower right')


def plot_phase_comparison(retrievals):
    fig, axl = plt.subplots()
    total(axl, retrievals, 'total')
    initiated_phase(axl, retrievals)
    getting_closest_peers_phase(axl, retrievals, 'getting_closest_peers')
    dialing_phase(axl, retrievals)
    fetching_phase(axl, retrievals, 'fetch')
    axl.set_title('Retrieval Phase Latency Distribution')
    axl.legend(loc='lower right')