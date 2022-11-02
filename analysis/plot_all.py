import os
import pickle
from typing import List
import matplotlib.pyplot as plt
from pathlib import Path
from plot import cdf_retrievals, cdf_publications, bar_region_retrieval_latency,\
                 pie_phase_retrieval_latency, timeseries_retrievals, histo_agent_uptime,\
                 histo_publish_age, first_provider_nearest, file_size_comparison
from pickled.model_publication import Publication
from pickled.model_retrieval import Retrieval
from helpers.constants import RetrievalPhase, PlayerType
from logs.model_logs_config import LogsConfig
from logs import load
from models.model_data_set import DataSet

# Set OUT_DIR to `None` to display the graphs with the GUI
#OUT_DIR = None
OUT_DIR = './figs'


def writeMeta(out_target_dir: str, data_set: DataSet):
    fpt = open(f"{out_target_dir}/meta.p", 'wb')
    started_at, ended_at = data_set.started_ended_at
    meta = {
        'started_at': started_at,
        'ended_at': ended_at
    }
    pickle.dump(meta, fpt)
    fpt.close()


def doPlotFromDataSet(out_target_dir, data_set: DataSet):

    publications = data_set.total_publications
    retrievals = data_set.total_completed_retrievals

    for phase in RetrievalPhase:
        file_size_comparison.plot_duration(data_set, phase, f"Retreival {phase.name} duration by file size", PlayerType.PUBLISHER)
        if out_target_dir is not None:
            plt.savefig(os.path.join(out_target_dir, f"file_size_{phase.name}_durations_single_provider.png"))
            plt.close()

        file_size_comparison.plot_duration(data_set, phase, f"Retreival {phase.name} duration by file size", PlayerType.RETRIEVER)
        if out_target_dir is not None:
            plt.savefig(os.path.join(out_target_dir, f"file_size_{phase.name}_durations_multi_provider.png"))
            plt.close()

        file_size_comparison.plot_duration(data_set, phase, f"Retreival {phase.name} duration by file size", None)
        if out_target_dir is not None:
            plt.savefig(os.path.join(out_target_dir, f"file_size_{phase.name}_durations.png"))
            plt.close()


    for file_size in data_set.comparable_file_sizes:
        did_plot = first_provider_nearest.plot_fpn_durations(data_set, file_size)
        if did_plot and out_target_dir is not None:
            plt.savefig(os.path.join(out_target_dir, f"fpn_durations_fs_{file_size}.png"))
            plt.close()

        did_plot = first_provider_nearest.plot_fpn_durations_by_phase(data_set, file_size)
        if did_plot and out_target_dir is not None:
            plt.savefig(os.path.join(out_target_dir, f"fpn_durations_by_phase_fs_{file_size}.png"))
            plt.close()

    first_provider_nearest.plot_fpn_likelihood(data_set)
    if out_target_dir is not None:
        plt.savefig(os.path.join(out_target_dir, f"fpn_likelihood.png"))
        plt.close()

    first_provider_nearest.plot_fpn_likelihood_by_region(data_set)
    if out_target_dir is not None:
        plt.savefig(os.path.join(out_target_dir, f"fpn_likelihood_by_region.png"))
        plt.close()

    for phase in RetrievalPhase:
        histo_publish_age.plot(data_set, phase, f"Retrieval {phase.name} Duration by Publish Age")
        if out_target_dir is not None:
            plt.savefig(os.path.join(out_target_dir, f"publish_age_ret_{phase.name}_duration_comp_bar.png"))
            plt.close()

    for phase in RetrievalPhase:
        histo_agent_uptime.plot(data_set, data_set.smallest_file_size, phase, f"Retrieval {phase.name} Duration by Agent Uptime")
        if out_target_dir is not None:
            plt.savefig(os.path.join(out_target_dir, f"agent_uptime_ret_{phase.name}_comp_bar.png"))
            plt.close()


    cdf_publications.plot_total(data_set)
    if out_target_dir is not None:
        plt.savefig(os.path.join(out_target_dir, 'pvd_total.png'))
        plt.close()

    cdf_publications.plot_getting_closest_peers(data_set)
    if out_target_dir is not None:
        plt.savefig(os.path.join(out_target_dir, 'pvd_getting_closest_peers.png'))
        plt.close()

    cdf_publications.plot_total_add_provider(data_set)
    if out_target_dir is not None:
        plt.savefig(os.path.join(out_target_dir, 'pvd_total_add_provider.png'))
        plt.close()

    for file_size in data_set.comparable_file_sizes:
        for phase in RetrievalPhase:
            cdf_retrievals.plot_duration_by_region(file_size, phase, data_set)
            if out_target_dir is not None:
                plt.savefig(os.path.join(out_target_dir, f"ret_{phase.name}_fs_{file_size}_cdf.png"))
                plt.close()

        cdf_retrievals.plot_phase_comparison(file_size, retrievals)
        if out_target_dir is not None:
            plt.savefig(os.path.join(out_target_dir, 'ret_phase_comparison_fs_{file_size}_cdf.png'))
        plt.close()

        pie_phase_retrieval_latency.plot(retrievals, file_size)
        if out_target_dir is not None:
            plt.savefig(os.path.join(out_target_dir, f"ret_phase_comparison_pie_fs_{file_size}.png"))
            plt.close()

    bar_region_retrieval_latency.plot(data_set)
    if out_target_dir is not None:
        plt.savefig(os.path.join(out_target_dir, 'ret_region_comparison_bar.png'))
        plt.close()


    for file_size in data_set.comparable_file_sizes:
        timeseries_retrievals.plot_each_phase_all_regions(file_size, data_set.total_completed_retrievals, 'Retrieval Duration by Phase')
        if out_target_dir is not None:
            plt.savefig(os.path.join(out_target_dir, 'trend_ret_phase_breakdown.png'))
            plt.close()

        for phase in RetrievalPhase:
            timeseries_retrievals.plot_duration_each_region(file_size, phase, data_set, f"Retrieval {phase.name} Duration by Region")
            if out_target_dir is not None:
                plt.savefig(os.path.join(out_target_dir, f"trend_ret_{phase.name}_region_breakdown.png"))
                plt.close()

    timeseries_retrievals.plot_num_providers(retrievals, 'Retrieval Number Providers')
    if out_target_dir is not None:
        plt.savefig(os.path.join(out_target_dir, 'ret_num_providers.png'))
        plt.close()

    if out_target_dir is not None:
        writeMeta(out_target_dir, data_set)


def doPlotFromConfig(out_target_dir, logs_config: LogsConfig):
    if OUT_DIR is not None:
        out_target_dir = os.path.join(OUT_DIR, out_target_dir)
        Path(out_target_dir).mkdir(exist_ok=True, parents=True)
    else:
        out_target_dir = None

    #doPlotFromDataSet(out_target_dir, load.latest_data_set(logs_config))
    doPlotFromDataSet(out_target_dir, load.complete_data_set(logs_config))

    if OUT_DIR is None:
        plt.show()


if __name__=='__main__':
    logs_config = LogsConfig('./log_config.json')
    doPlotFromConfig(logs_config.latest_dir_name, logs_config)
