import os, shutil
import pickle
from typing import List
import matplotlib.pyplot as plt
from pathlib import Path
from plot import cdf_retrievals, cdf_publications, bar_region_retrieval_latency,\
                 pie_phase_retrieval_latency, timeseries_retrievals, histo_agent_uptime,\
                 histo_publish_age, first_provider_nearest, file_size_comparison, scatter
from pickled.model_publication import Publication
from pickled.model_retrieval import Retrieval
from helpers.constants import RetrievalPhase, PlayerType
from logs.model_logs_config import LogsConfig
from logs import load
from models.model_data_set import DataSet

# Set OUT_DIR to `None` to display the graphs with the GUI
#OUT_DIR = None
OUT_DIR = './figs'

sections = {}

def writeMeta(out_target_dir: str, data_set: DataSet):
    fpt = open(f"{out_target_dir}/meta.p", 'wb')
    started_at, ended_at = data_set.started_ended_at
    meta = {
        'started_at': started_at,
        'ended_at': ended_at
    }
    meta['sections'] = sections
    pickle.dump(meta, fpt)
    fpt.close()


def saveFig(out_target_dir, section_name, file_name):
    if out_target_dir is not None:
        if section_name in sections:
            sections[section_name].append(file_name)
        else:
            sections[section_name] = [file_name]
        plt.savefig(os.path.join(out_target_dir, file_name))
        plt.close()

def doPlotFromDataSet(out_target_dir, data_set: DataSet):

    publications = data_set.total_publications
    retrievals = data_set.total_completed_retrievals

    section_name = 'Retrieval Phase Duration Comparisons'

    scatter.plot_phases(data_set, RetrievalPhase.GETTING_CLOSEST_PEERS, RetrievalPhase.DIALING, data_set.smallest_file_size)
    saveFig(out_target_dir, section_name, f"phase_correlation_{RetrievalPhase.GETTING_CLOSEST_PEERS.name}_vs_{RetrievalPhase.DIALING}_fs_{data_set.smallest_file_size}.png")


    scatter.plot_phases(data_set, RetrievalPhase.GETTING_CLOSEST_PEERS, RetrievalPhase.FETCHING, data_set.smallest_file_size)
    saveFig(out_target_dir, section_name, f"phase_correlation_{RetrievalPhase.GETTING_CLOSEST_PEERS.name}_vs_{RetrievalPhase.FETCHING}_fs_{data_set.smallest_file_size}.png")

    scatter.plot_phases(data_set, RetrievalPhase.DIALING, RetrievalPhase.FETCHING, data_set.smallest_file_size)
    saveFig(out_target_dir, section_name, f"phase_correlation_{RetrievalPhase.DIALING.name}_vs_{RetrievalPhase.FETCHING}_fs_{data_set.smallest_file_size}.png")

    section_name = 'File Size Comparisons for each Phase'
    for phase in RetrievalPhase:
        file_size_comparison.plot_duration(data_set, phase, f"Retrieval {phase.name} duration by File Size", PlayerType.PUBLISHER)
        saveFig(out_target_dir, section_name, f"file_size_{phase.name}_durations_single_provider.png")

        file_size_comparison.plot_duration(data_set, phase, f"Retrieval {phase.name} duration by File Size", PlayerType.RETRIEVER)
        saveFig(out_target_dir, section_name, f"file_size_{phase.name}_durations_multi_provider.png")

        file_size_comparison.plot_duration(data_set, phase, f"Retrieval {phase.name} duration by File Size", None)
        saveFig(out_target_dir, section_name, f"file_size_{phase.name}_durations.png")

    section_name = 'First Provider Nearest Percent Slow'
    did_plot = first_provider_nearest.plot_percent_slow_by_phase(data_set)
    if did_plot:
        saveFig(out_target_dir, section_name, f"fpn_percent_slow_by_phase.png")

    section_name = 'First Provider Nearest Durations'
    for file_size in data_set.comparable_file_sizes:
        did_plot = first_provider_nearest.plot_durations_by_phase(data_set, file_size)
        if did_plot:
            saveFig(out_target_dir, section_name, f"fpn_durations_by_phase_fs_{file_size}.png")

    section_name = 'First Provider Nearest Likelihood'

    first_provider_nearest.plot_likelihood(data_set)
    saveFig(out_target_dir, section_name, f"fpn_likelihood.png")

    first_provider_nearest.plot_fpn_likelihood_by_region(data_set)
    saveFig(out_target_dir, section_name, f"fpn_likelihood_by_region.png")

    section_name = 'Publish Age'

    for phase in RetrievalPhase:
        histo_publish_age.plot(data_set, phase, f"Retrieval {phase.name} Duration by Publish Age")
        saveFig(out_target_dir, section_name, f"publish_age_ret_{phase.name}_duration_comp_bar.png")

    section_name = 'Agent Uptime'

    for phase in RetrievalPhase:
        histo_agent_uptime.plot(data_set, data_set.smallest_file_size, phase, f"Retrieval {phase.name} Duration by Agent Uptime")
        saveFig(out_target_dir, section_name, f"agent_uptime_ret_{phase.name}_fs_{data_set.smallest_file_size}_comp_bar.png")

    section_name = 'CDF Publications'

    cdf_publications.plot_total(data_set)
    saveFig(out_target_dir, section_name, 'pvd_total.png')

    cdf_publications.plot_getting_closest_peers(data_set)
    saveFig(out_target_dir, section_name, 'pvd_getting_closest_peers.png')

    cdf_publications.plot_total_add_provider(data_set)
    saveFig(out_target_dir, section_name, 'pvd_total_add_provider.png')

    for file_size in data_set.comparable_file_sizes:
        section_name = 'CDF Retrievals by Region'
        for phase in RetrievalPhase:
            cdf_retrievals.plot_duration_by_region(file_size, phase, data_set)
            saveFig(out_target_dir, section_name, f"ret_{phase.name}_fs_{file_size}_cdf.png")

        section_name = 'CDF Retrievals by Phase'
        cdf_retrievals.plot_phase_comparison(file_size, retrievals)
        saveFig(out_target_dir, section_name, f"ret_phase_comparison_fs_{file_size}_cdf.png")

        section_name = 'Phase Comparisons'
        pie_phase_retrieval_latency.plot(retrievals, file_size)
        saveFig(out_target_dir, section_name, f"ret_phase_comparison_pie_fs_{file_size}.png")


    section_name = 'Region Comparisons'
    file_size = data_set.smallest_file_size
    bar_region_retrieval_latency.plot(data_set, file_size, PlayerType.PUBLISHER)
    saveFig(out_target_dir, section_name, f"ret_region_comparison_bar_fs_{file_size}_single_provider.png")

    bar_region_retrieval_latency.plot(data_set, file_size, PlayerType.RETRIEVER)
    saveFig(out_target_dir, section_name, f"ret_region_comparison_bar_fs_{file_size}_multi_provider.png")

    bar_region_retrieval_latency.plot(data_set, file_size, None)
    saveFig(out_target_dir, section_name, f"ret_region_comparison_bar_fs_{file_size}.png")

    section_name = 'Trends'

    for file_size in data_set.comparable_file_sizes:
        timeseries_retrievals.plot_each_phase_all_regions(file_size, data_set.total_completed_retrievals, 'Retrieval Duration by Phase')
        saveFig(out_target_dir, section_name, f"trend_ret_phase_breakdown_fs_{file_size}.png")

        for phase in RetrievalPhase:
            timeseries_retrievals.plot_duration_each_region(file_size, phase, data_set, f"Retrieval {phase.name} Duration by Region")
            saveFig(out_target_dir, section_name, f"trend_ret_{phase.name}_region_breakdown_fs_{file_size}.png")

    timeseries_retrievals.plot_num_providers(retrievals, 'Retrieval Number Providers')
    saveFig(out_target_dir, section_name, 'ret_num_providers.png')

    if out_target_dir is not None:
        writeMeta(out_target_dir, data_set)


def doPlotFromConfig(out_target_dir, logs_config: LogsConfig):
    if OUT_DIR is not None:
        out_target_dir = os.path.join(OUT_DIR, out_target_dir)
        # remove target if it exists
        if os.path.exists(out_target_dir) and os.path.isdir(out_target_dir):
            shutil.rmtree(out_target_dir)
        Path(out_target_dir).mkdir(parents=True)
    else:
        out_target_dir = None

    #doPlotFromDataSet(out_target_dir, load.latest_data_set(logs_config))
    doPlotFromDataSet(out_target_dir, load.complete_data_set(logs_config))

    if OUT_DIR is None:
        plt.show()


if __name__=='__main__':
    logs_config = LogsConfig('./log_config.json')
    doPlotFromConfig(logs_config.latest_dir_name, logs_config)
