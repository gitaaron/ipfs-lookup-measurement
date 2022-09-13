import numpy as np
import matplotlib.pyplot as plt
from models.model_retrieval import Retrieval
from typing import List

def initiated_phase(retrievals: List[Retrieval]):
    overall_retrieval_durations = []
    for ret in retrievals:
        overall_retrieval_durations += [
            (ret.get_providers_queries_started_at - ret.retrieval_started_at).total_seconds()]

    hist, bin_edges = np.histogram(
        overall_retrieval_durations, bins=np.arange(0, 5, 0.1),  density=True)

    dx = bin_edges[1]-bin_edges[0]
    cdf = np.cumsum(hist)*dx

    plt.plot(bin_edges[:-1], cdf, label='initiated')


def getting_closest_peers_phase(retrievals: List[Retrieval]):
    overall_retrieval_durations = []
    for ret in retrievals:
        overall_retrieval_durations += [
            (ret.dial_started_at - ret.get_providers_queries_started_at).total_seconds()]

    hist, bin_edges = np.histogram(
        overall_retrieval_durations, bins=np.arange(0, 5, 0.1),  density=True)

    dx = bin_edges[1]-bin_edges[0]
    cdf = np.cumsum(hist)*dx

    plt.plot(bin_edges[:-1], cdf, label='getting_closest_peers')


def dialing_phase(retrievals: List[Retrieval]):
    overall_retrieval_durations = []
    for ret in retrievals:
        overall_retrieval_durations += [
            (ret.connected_at - ret.dial_started_at).total_seconds()]

    hist, bin_edges = np.histogram(
        overall_retrieval_durations, bins=np.arange(0, 5, 0.1),  density=True)

    dx = bin_edges[1]-bin_edges[0]
    cdf = np.cumsum(hist)*dx

    plt.plot(bin_edges[:-1], cdf, label='dialing')

def fetching_phase(retrievals: List[Retrieval]):
    overall_retrieval_durations = []
    for ret in retrievals:
        overall_retrieval_durations += [
            (ret.done_retrieving_at - ret.connected_at).total_seconds()]

    hist, bin_edges = np.histogram(
        overall_retrieval_durations, bins=np.arange(0, 5, 0.1),  density=True)

    dx = bin_edges[1]-bin_edges[0]
    cdf = np.cumsum(hist)*dx

    plt.plot(bin_edges[:-1], cdf, label='fetching')



def total(retrievals: List[Retrieval]):

    overall_retrieval_durations = []
    for ret in retrievals:
        overall_retrieval_durations += [
            (ret.done_retrieving_at - ret.retrieval_started_at).total_seconds()]

    hist, bin_edges = np.histogram(
        overall_retrieval_durations, bins=np.arange(0, 5, 0.1),  density=True)

    dx = bin_edges[1]-bin_edges[0]
    cdf = np.cumsum(hist)*dx

    plt.plot(bin_edges[:-1], cdf, label='total')
