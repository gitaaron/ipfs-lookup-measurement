import numpy as np
from models.model_publication import Publication
from typing import List
import matplotlib.pyplot as plt
from models.model_parsed_log_file import ParsedLogFiles



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

def plot_total(parsed_logs: ParsedLogFiles):
    fig, axl = plt.subplots()

    for parsed_log in parsed_logs.all:
        total(axl, parsed_log.publications, parsed_log.region_log_file.region)

    axl.set_title('Publish Total Latency by Region (fig. a)')
    axl.legend(loc='lower right')

def plot_getting_closest_peers(parsed_logs: ParsedLogFiles):
    fig, axl = plt.subplots()

    for parsed_log in parsed_logs.all:
        getting_closest_peers_phase(axl, parsed_log.publications, parsed_log.region_log_file.region)

    axl.set_title('Publish Getting Closest Peer Latency by Region (fig. b)')
    axl.legend(loc='lower right')

def plot_total_add_provider(parsed_logs: ParsedLogFiles):
    fig, axl = plt.subplots()

    for parsed_log in parsed_logs.all:
        total_add_provider_phase(axl, parsed_log.publications, parsed_log.region_log_file.region)

    axl.set_title('Publish Total Add Provider Latency by Region (fig. c)')
    axl.legend(loc='lower right')
