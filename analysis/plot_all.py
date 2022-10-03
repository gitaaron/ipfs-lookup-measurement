import os
import json
import pickle
import glob
from typing import List
import matplotlib.pyplot as plt
from pathlib import Path
from plot import cdf_retrievals, cdf_publications, bar_region_retrieval_latency, pie_phase_retrieval_latency, timeseries_retrievals
from models.model_parsed_log_file import ParsedLogFile, ParsedLogFiles
from models.model_publication import Publication
from models.model_retrieval import Retrieval
from helpers.constants import RetrievalPhase
from helpers import logs
from models.model_logs_config import LogsConfig

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


def writeMeta(out_target_dir: str, parsed_logs: List[ParsedLogFile]):
    fpt = open(f"{out_target_dir}/meta.p", 'wb')
    meta = {
        'started_at': dateStarted(parsed_logs),
        'ended_at': dateEnded(parsed_logs)
    }
    pickle.dump(meta, fpt)
    fpt.close()

def doPlotSinceTimeStarted(out_target_dir, parsed_logs: ParsedLogFiles):

    publications: List[Publication] = []
    retrievals: List[Retrieval] = []

    for parsed_log in parsed_logs.all:
        publications += parsed_log.publications
        retrievals += parsed_log.completed_retrievals()

    timeseries_retrievals.plot_each_phase_all_regions(retrievals, 'Retrieval Duration by Phase (since beginning)')
    if out_target_dir is not None:
        plt.savefig(os.path.join(out_target_dir, 'trend_ret_phase_breakdown_all_time.png'))
        plt.close()

    for phase in RetrievalPhase:
        timeseries_retrievals.plot_duration_each_region(phase, retrievals, parsed_logs, f"Retrieval {phase.name} Duration by Region (since beginning)")
        if out_target_dir is not None:
            plt.savefig(os.path.join(out_target_dir, f"trend_ret_{phase.name}_region_breakdown_all_time.png"))
            plt.close()


def doPlotLatest(out_target_dir, parsed_logs: ParsedLogFiles):
    print('latest dir : %s' % out_target_dir)

    publications = parsed_logs.total_publications
    retrievals = parsed_logs.total_completed_retrievals


    cdf_publications.plot_total(parsed_logs)
    if out_target_dir is not None:
        plt.savefig(os.path.join(out_target_dir, 'pvd_total.png'))
        plt.close()

    cdf_publications.plot_getting_closest_peers(parsed_logs)
    if out_target_dir is not None:
        plt.savefig(os.path.join(out_target_dir, 'pvd_getting_closest_peers.png'))
        plt.close()

    cdf_publications.plot_total_add_provider(parsed_logs)
    if out_target_dir is not None:
        plt.savefig(os.path.join(out_target_dir, 'pvd_total_add_provider.png'))
        plt.close()

    cdf_retrievals.plot_total(parsed_logs)
    if out_target_dir is not None:
        plt.savefig(os.path.join(out_target_dir, 'ret_total.png'))
        plt.close()

    cdf_retrievals.plot_getting_closest_peers(parsed_logs)
    if out_target_dir is not None:
        plt.savefig(os.path.join(out_target_dir, 'ret_getting_closest_peers.png'))
        plt.close()

    cdf_retrievals.plot_fetch(parsed_logs)
    if out_target_dir is not None:
        plt.savefig(os.path.join(out_target_dir, 'ret_fetch.png'))
        plt.close()

    cdf_retrievals.plot_phase_comparison(retrievals)
    if out_target_dir is not None:
        plt.savefig(os.path.join(out_target_dir, 'ret_phase_comparison_cdf.png'))
        plt.close()

    pie_phase_retrieval_latency.plot(retrievals)
    if out_target_dir is not None:
        plt.savefig(os.path.join(out_target_dir, 'ret_phase_comparison_pie.png'))
        plt.close()

    bar_region_retrieval_latency.plot(parsed_logs)

    if out_target_dir is not None:
        plt.savefig(os.path.join(out_target_dir, 'ret_region_comparison_bar.png'))
        plt.close()


    timeseries_retrievals.plot_each_phase_all_regions(retrievals, 'Retrieval Duration by Phase (last 4 hours)')
    if out_target_dir is not None:
        plt.savefig(os.path.join(out_target_dir, 'trend_ret_phase_breakdown_recent.png'))
        plt.close()

    for phase in RetrievalPhase:
        timeseries_retrievals.plot_duration_each_region(phase, retrievals, parsed_logs, f"Retrieval {phase.name} Duration by Region (last 4 hours)")
        if out_target_dir is not None:
            plt.savefig(os.path.join(out_target_dir, f"trend_ret_{phase.name}_region_breakdown_recent.png"))
            plt.close()

    timeseries_retrievals.plot_num_providers(retrievals, 'Retrieval Number Providers (last 4 hours)')
    if out_target_dir is not None:
        plt.savefig(os.path.join(out_target_dir, 'ret_num_providers_recent.png'))
        plt.close()

    if out_target_dir is not None:
        writeMeta(out_target_dir, parsed_logs.all)


def doPlot(out_target_dir, latest_parsed_log_files: ParsedLogFiles, all_parsed_log_files: ParsedLogFiles):
    if OUT_DIR is not None:
        out_target_dir = os.path.join(OUT_DIR, out_target_dir)
        Path(out_target_dir).mkdir(exist_ok=True, parents=True)
    else:
        out_target_dir = None

    doPlotLatest(out_target_dir, latest_parsed_log_files)
    doPlotSinceTimeStarted(out_target_dir, all_parsed_log_files)

    if OUT_DIR is None:
        plt.show()


if __name__=='__main__':
    logs_config = LogsConfig('./log_config.json')
    doPlot(logs_config.latest_dir_name, logs.load_latest_parsed_log_files(logs_config), logs.load_all_parsed_log_files(logs_config))
