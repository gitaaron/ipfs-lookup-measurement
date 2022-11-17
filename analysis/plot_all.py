import os, shutil
import pickle
from typing import List
import matplotlib.pyplot as plt
from pathlib import Path
from plot import cdf_retrievals, cdf_publications, regions, experimental_controls,\
                 timeseries_retrievals, agent_uptime,\
                 publish_age, first_provider, file_size_phases,\
                 single_multi_provider, agent_health
from pickled.model_publication import Publication
from pickled.model_retrieval import Retrieval
from helpers.constants import RetrievalPhase, PlayerType, DELAY_FILE_SIZE, DurationType
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

_files_written = {}

def saveFig(out_target_dir, section_name, file_name):
    if out_target_dir is None:
        return

    if file_name in _files_written:
        raise Exception(f"Already wrote : {file_name}")

    _files_written[file_name] = True

    if section_name in sections:
        sections[section_name].append(file_name)
    else:
        sections[section_name] = [file_name]
    plt.savefig(os.path.join(out_target_dir, file_name))
    plt.close()

def doPlotFromDataSet(out_target_dir, data_set: DataSet):

    retrievals = data_set.total_completed_retrievals

    for file_size in data_set.comparable_file_sizes:
        section_name = 'Trends by Phase'
        timeseries_retrievals.plot_each_phase_all_regions(file_size, data_set, 'Retrieval Duration by Phase')
        saveFig(out_target_dir, section_name, f"trend_ret_phase_breakdown_fs_{file_size}.png")

        section_name = 'Trends by Phase (every 30 min.)'
        timeseries_retrievals.plot_interval_each_phase_all_regions(file_size, data_set, 'Retrieval Duration by Phase (30m)', '30min')
        saveFig(out_target_dir, section_name, f"trend_ret_phase_breakdown_fs_{file_size}_30_min.png")

        section_name = 'Trends by Phase (every 4 hours)'
        timeseries_retrievals.plot_interval_each_phase_all_regions(file_size, data_set, 'Retrieval Duration by Phase (4h)', '4H')
        saveFig(out_target_dir, section_name, f"trend_ret_phase_breakdown_fs_{file_size}_4_hour.png")


        for phase in RetrievalPhase:

            section_name = 'Trends by Region'
            timeseries_retrievals.plot_duration_each_region(file_size, phase, data_set, f"Retrieval {phase.name} Duration by Region")
            saveFig(out_target_dir, section_name, f"trend_ret_{phase.name}_region_breakdown_fs_{file_size}.png")

            section_name = 'Trends by Region (every 30 min.)'
            timeseries_retrievals.plot_interval_duration_each_region(data_set.smallest_file_size, phase, data_set, f"Retrieval {phase.name} Duration by Region (30m)", '30min')
            saveFig(out_target_dir, section_name, f"trend_ret_{phase.name}_region_breakdown_fs_{file_size}_30_min.png")

            section_name = 'Trends by Region (every 4 hours)'
            timeseries_retrievals.plot_interval_duration_each_region(data_set.smallest_file_size, phase, data_set, f"Retrieval {phase.name} Duration by Region (4h)", '4H')
            saveFig(out_target_dir, section_name, f"trend_ret_{phase.name}_region_breakdown_fs_{file_size}_4_hour.png")

    section_name = 'Phase Comparisons (scatter)'

    for file_size in data_set.comparable_file_sizes:
        file_size_phases.plot_scatter(data_set, RetrievalPhase.GETTING_CLOSEST_PEERS, RetrievalPhase.DIALING, file_size)
        saveFig(out_target_dir, section_name, f"phase_correlation_{RetrievalPhase.GETTING_CLOSEST_PEERS.name}_vs_{RetrievalPhase.DIALING}_fs_{file_size}.png")

        file_size_phases.plot_scatter(data_set, RetrievalPhase.GETTING_CLOSEST_PEERS, RetrievalPhase.FETCHING, file_size)
        saveFig(out_target_dir, section_name, f"phase_correlation_{RetrievalPhase.GETTING_CLOSEST_PEERS.name}_vs_{RetrievalPhase.FETCHING}_fs_{file_size}.png")

        file_size_phases.plot_scatter(data_set, RetrievalPhase.DIALING, RetrievalPhase.FETCHING, data_set.smallest_file_size)
        saveFig(out_target_dir, section_name, f"phase_correlation_{RetrievalPhase.DIALING.name}_vs_{RetrievalPhase.FETCHING}_fs_{file_size}.png")

    section_name = 'File Size / Phase Comparisons (histo)'

    file_size_phases.plot_percent_slow(data_set, f"Retrieval Percent Slow for each Phase by File Size")
    saveFig(out_target_dir, section_name, f"file_size_phase_percent_slow.png")

    file_size_phases.plot_duration(data_set, f"Retrieval Durations for each Phase by File Size")
    saveFig(out_target_dir, section_name, f"file_size_phase_durations.png")

    section_name = 'Single vs Multi Providers'

    for file_size in data_set.comparable_file_sizes:
        single_multi_provider.plot_duration_by_phase(data_set, f"Single vs Multi Provider Retrieval Durations by Phase", file_size)
        saveFig(out_target_dir, section_name, f"single_multi_provider_durations_by_phase_fs_{file_size}.png")

    for phase in RetrievalPhase:
        single_multi_provider.plot_duration_by_file_size(data_set, f"Single vs Multi Provider Retrieval {phase.name} Durations by File Size", phase)
        saveFig(out_target_dir, section_name, f"single_multi_provider_{phase.name}_durations_by_file_size.png")


    single_multi_provider.plot_percent_slow_by_phase(data_set, f"Single vs Multi Provider Retrieval Percent Slow by Phase")
    saveFig(out_target_dir, section_name, f"single_multi_provider_percent_slow_by_phase.png")

    single_multi_provider.plot_percent_slow_by_file_size(data_set, f"Single vs Multi Provider Retrieval Percent Slow by File Size")
    saveFig(out_target_dir, section_name, f"single_multi_provider_percent_slow_by_file_size.png")

    section_name = 'Regional Comparisons'

    regions.plot_avg_hops_to_first_provider(data_set)
    saveFig(out_target_dir, section_name, f"avg_hops_to_fp_by_region.png")

    for phase in RetrievalPhase:
        regions.plot_histo_percent_slow(data_set, phase)
        saveFig(out_target_dir, section_name, f"{phase.name}_percent_slow_region_comparison_bar.png")

        for file_size in data_set.comparable_file_sizes:
            regions.plot_histo_duration(data_set, file_size, phase)
            saveFig(out_target_dir, section_name, f"{phase.name}_duration_region_comparison_bar_fs_{file_size}.png")


    section_name = 'First Provider Distributions'
    first_provider.plot_fp_distribution_by_region(data_set)
    saveFig(out_target_dir, section_name, f"first_provider_distribution_by_region.png")


    section_name = 'First Referer Agents'

    first_provider.plot_first_referer_agents(data_set, DurationType.ALL)
    saveFig(out_target_dir, section_name, f"first_referer_agents_all.png")

    first_provider.plot_first_referer_agents(data_set, DurationType.FAST)
    saveFig(out_target_dir, section_name, f"first_referer_agents_fast.png")

    first_provider.plot_first_referer_agents(data_set, DurationType.SLOW)
    saveFig(out_target_dir, section_name, f"first_referer_agents_slow.png")

    section_name = 'First Provider Nearest Likelihood'

    first_provider.plot_likelihood(data_set)
    saveFig(out_target_dir, section_name, f"fpn_likelihood.png")

    first_provider.plot_fpn_likelihood_by_region(data_set)
    saveFig(out_target_dir, section_name, f"fpn_likelihood_by_region.png")

    section_name = 'First Provider Nearest Percent Slow'
    did_plot = first_provider.plot_percent_slow_by_phase(data_set)
    if did_plot:
        saveFig(out_target_dir, section_name, f"fpn_percent_slow_by_phase.png")

    section_name = 'First Provider Nearest Durations'
    for file_size in data_set.comparable_file_sizes:
        did_plot = first_provider.plot_durations_by_phase(data_set, file_size)
        if did_plot:
            saveFig(out_target_dir, section_name, f"fpn_durations_by_phase_fs_{file_size}.png")


    section_name = 'Publish Age Percent Slow'
    for phase in RetrievalPhase:
        publish_age.plot_histo_percent_slow(data_set, phase, f"Retrieval {phase.name} Percent Slow by Publish Age")
        saveFig(out_target_dir, section_name, f"publish_age_{phase.name}_percent_slow.png")


    section_name = 'Publish Age Durations (Bar)'
    for phase in RetrievalPhase:
        publish_age.plot_histo_duration(data_set, phase, f"Retrieval {phase.name} Duration by Publish Age")
        saveFig(out_target_dir, section_name, f"publish_age_{phase.name}_duration_comp_bar.png")

    section_name = 'Publish Age Durations (Scatter)'

    for phase in RetrievalPhase:
        publish_age.plot_scatter_duration(data_set, DELAY_FILE_SIZE, phase,)
        saveFig(out_target_dir, section_name, f"scatter_publish_age_ret_{phase.name}_duration_fs_{DELAY_FILE_SIZE}_comp_bar.png")

    section_name = 'Agent Uptime Percent Slow'
    for phase in RetrievalPhase:
        agent_uptime.plot_histo_percent_slow(data_set, phase, f"Retrieval {phase.name} Percent Slow by Agent Uptime")
        saveFig(out_target_dir, section_name, f"agent_uptime_ret_{phase.name}_percent_slow_fs_{data_set.smallest_file_size}_comp_bar.png")

    section_name = 'Agent Uptime Durations (Bar)'
    for phase in RetrievalPhase:
        agent_uptime.plot_histo_duration(data_set, data_set.smallest_file_size, phase, f"Retrieval {phase.name} Duration by Agent Uptime")
        saveFig(out_target_dir, section_name, f"histo_agent_uptime_ret_{phase.name}_duration_fs_{data_set.smallest_file_size}_comp_bar.png")

    section_name = 'Agent Uptime Durations (Scatter)'
    for file_size in data_set.comparable_file_sizes:
        for phase in RetrievalPhase:
            agent_uptime.plot_scatter_duration(data_set, file_size, phase,)
            saveFig(out_target_dir, section_name, f"scatter_agent_uptime_ret_{phase.name}_duration_fs_{file_size}_comp_bar.png")

    section_name = 'CDF Publications'

    cdf_publications.plot_total(data_set)
    saveFig(out_target_dir, section_name, 'pvd_total.png')

    cdf_publications.plot_getting_closest_peers(data_set)
    saveFig(out_target_dir, section_name, 'pvd_getting_closest_peers.png')

    cdf_publications.plot_total_add_provider(data_set)
    saveFig(out_target_dir, section_name, 'pvd_total_add_provider.png')

    section_name = 'CDF Multi Provider Retrievals by Region'
    cdf_retrievals.plot_duration_by_region(None, RetrievalPhase.TOTAL, data_set, True)
    saveFig(out_target_dir, section_name, f"ret_multi_provider_{RetrievalPhase.TOTAL.name}_cdf.png")


    for file_size in data_set.comparable_file_sizes:
        section_name = 'CDF Retrievals by Region'
        for phase in RetrievalPhase:
            cdf_retrievals.plot_duration_by_region(file_size, phase, data_set, False)
            saveFig(out_target_dir, section_name, f"ret_{phase.name}_fs_{file_size}_cdf.png")

        section_name = 'CDF Retrievals by Phase'
        cdf_retrievals.plot_phase_comparison(file_size, retrievals)
        saveFig(out_target_dir, section_name, f"ret_phase_comparison_fs_{file_size}_cdf.png")

    section_name = 'Sys Health Trends'
    agent_health.plot_interval_property(data_set, '5min', 'available_mem')
    saveFig(out_target_dir, section_name, 'available_mem_5_min.png')

    agent_health.plot_interval_property(data_set, '4H', 'available_mem')
    saveFig(out_target_dir, section_name, 'available_mem_4_h.png')

    agent_health.plot_interval_property(data_set, '5min', 'load_avg_last_min')
    saveFig(out_target_dir, section_name, 'load_avg_5_min.png')

    agent_health.plot_interval_property(data_set, '4H', 'load_avg_last_min')
    saveFig(out_target_dir, section_name, 'load_avg_4_h.png')

    section_name = 'Experimental Controls'
    experimental_controls.plot_num_providers(retrievals, 'Retrieval Number Providers')
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
