import os
import json
import pickle
from typing import List
import matplotlib.pyplot as plt
from pathlib import Path
from plot import cdf_retrievals, cdf_publications, bar_region_retrieval_latency, pie_phase_retrieval_latency
from log_parse import load_parsed_logs, ParsedLogFile
from models.model_publication import Publication
from models.model_retrieval import Retrieval

# Set OUT_DIR to `None` to display the graphs with the GUI
#OUT_DIR = None
OUT_DIR = './figs'

def dateStarted(parsed_logs: List[ParsedLogFile]):
    started_at = None

    for parsed_log in parsed_logs:

        for pub in parsed_log.publications:
            if(started_at is None or pub.provide_started_at < started_at):
                started_at = pub.provide_started_at

        for ret in parsed_log.retrievals:
            if(started_at is None or ret.retrieval_started_at < started_at):
                started_at = ret.retrieval_started_at
    print(f"started_at: {started_at}")
    return started_at

def dateEnded(parsed_logs: List[ParsedLogFile]):
    ended_at = None

    for parsed_log in parsed_logs:

        for pub in parsed_log.publications:
            if(ended_at is None or pub.provide_ended_at > ended_at):
                ended_at = pub.provide_ended_at

        for ret in parsed_log.completed_retrievals():
            if(ended_at is None or ret.done_retrieving_at > ended_at):
                ended_at = ret.done_retrieving_at

    print(f"ended_at: {ended_at}")
    return ended_at


def writeMeta(contained_dir: str, parsed_logs: List[ParsedLogFile]):
    fpt = open(f"{contained_dir}/meta.p", 'wb')
    meta = {
        'started_at': dateStarted(parsed_logs),
        'ended_at': dateEnded(parsed_logs)
    }
    pickle.dump(meta, fpt)
    fpt.close()

def doPlot(container_dir):
    parsed_logs = load_parsed_logs(logs)

    publications: List[Publication] = []
    retrievals: List[Retrieval] = []

    for parsed_log in parsed_logs:
        publications += parsed_log.publications
        retrievals += parsed_log.completed_retrievals()

    if OUT_DIR is not None:
        contained_dir = os.path.join(OUT_DIR, container_dir)
        Path(contained_dir).mkdir(exist_ok=True, parents=True)

    cdf_publications.plot_total(parsed_logs)
    if OUT_DIR is not None:
        plt.savefig(os.path.join(contained_dir, 'pvd_total.png'))
        plt.clf()

    cdf_publications.plot_getting_closest_peers(parsed_logs)
    if OUT_DIR is not None:
        plt.savefig(os.path.join(contained_dir, 'pvd_getting_closest_peers.png'))
        plt.clf()

    cdf_publications.plot_total_add_provider(parsed_logs)
    if OUT_DIR is not None:
        plt.savefig(os.path.join(contained_dir, 'pvd_total_add_provider.png'))
        plt.clf()

    cdf_retrievals.plot_total(parsed_logs)
    if OUT_DIR is not None:
        plt.savefig(os.path.join(contained_dir, 'ret_total.png'))
        plt.clf()

    cdf_retrievals.plot_getting_closest_peers(parsed_logs)
    if OUT_DIR is not None:
        plt.savefig(os.path.join(contained_dir, 'ret_getting_closest_peers.png'))
        plt.clf()

    cdf_retrievals.plot_fetch(parsed_logs)
    if OUT_DIR is not None:
        plt.savefig(os.path.join(contained_dir, 'ret_fetch.png'))
        plt.clf()

    cdf_retrievals.plot_phase_comparison(retrievals)
    if OUT_DIR is not None:
        plt.savefig(os.path.join(contained_dir, 'ret_phase_comparison_cdf.png'))
        plt.clf()

    pie_phase_retrieval_latency.plot(retrievals)
    if OUT_DIR is not None:
        plt.savefig(os.path.join(contained_dir, 'ret_phase_comparison_pie.png'))
        plt.clf()


    bar_region_retrieval_latency.plot(parsed_logs)
    if OUT_DIR is not None:
        plt.savefig(os.path.join(contained_dir, 'ret_region_comparison_bar.png'))
        plt.clf()

    if OUT_DIR is None:
        plt.show()

    writeMeta(contained_dir, parsed_logs)

if __name__=='__main__':
    logs = json.load(open('./log_config.json'))
    doPlot(logs[0].split('/')[-2])
