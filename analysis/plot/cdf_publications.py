import numpy as np
from pickled.model_publication import Publication
from typing import List
import matplotlib.pyplot as plt
from models.model_data_set import DataSet



def total(axl, publications: List[Publication], label: str):
    overall_publication_durations = []
    for pub in publications:
        overall_publication_durations += [pub.duration_total_publication().total_seconds()]

    hist, bin_edges = np.histogram(
        overall_publication_durations, bins=np.arange(0, 60, 0.1),  density=True)

    dx = bin_edges[1]-bin_edges[0]
    cdf = np.cumsum(hist)*dx

    axl.plot(bin_edges[:-1], cdf, label=label)

def getting_closest_peers_phase(axl, publications: List[Publication], label: str):
    overall_publication_durations = []
    for pub in publications:
        overall_publication_durations += [pub.duration_dht_walk().total_seconds()]
    hist, bin_edges = np.histogram(
        overall_publication_durations, bins=np.arange(0, 60, 0.1),  density=True)

    dx = bin_edges[1]-bin_edges[0]
    cdf = np.cumsum(hist)*dx

    axl.plot(bin_edges[:-1], cdf, label=label)

def total_add_provider_phase(axl, publications: List[Publication], label: str):
    overall_publication_durations = []
    for pub in publications:
        overall_publication_durations += [pub.duration_total_add_provider().total_seconds()]
    hist, bin_edges = np.histogram(
        overall_publication_durations, bins=np.arange(0, 60, 0.1),  density=True)

    dx = bin_edges[1]-bin_edges[0]
    cdf = np.cumsum(hist)*dx

    axl.plot(bin_edges[:-1], cdf, label=label)

def plot_total(data_set: DataSet):
    fig, axl = plt.subplots()

    for agent,agent_events in data_set.agent_events_map.items():
        total(axl, agent_events.publications, agent.region)

    axl.set_title('Publish Total Duration by Region')
    axl.set_xlabel('Duration (sec).')
    axl.legend(loc='lower right')

def plot_getting_closest_peers(data_set: DataSet):
    fig, axl = plt.subplots()

    for agent,agent_events in data_set.agent_events_map.items():
        getting_closest_peers_phase(axl, agent_events.publications, agent.region)

    axl.set_title('Publish Getting Closest Peer Duration by Region')
    axl.set_xlabel('Duration (sec).')
    axl.legend(loc='lower right')

def plot_total_add_provider(data_set: DataSet):
    fig, axl = plt.subplots()

    for agent,agent_events in data_set.agent_events_map.items():
        total_add_provider_phase(axl, agent_events.publications, agent.region)

    axl.set_title('Publish Total Add Provider Duration by Region')
    axl.set_xlabel('Duration (sec).')
    axl.legend(loc='lower right')
