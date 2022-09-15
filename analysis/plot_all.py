import os
import json
from typing import List
import matplotlib.pyplot as plt
from pathlib import Path
from plot import cdf_retrievals, cdf_publications, bar_region_retrieval_latency, pie_phase_retrieval_latency
from log_parse import load_parsed_logs, ParsedLogFile
from models.model_publication import Publication
from models.model_retrieval import Retrieval

# Set outDir to `None` to display the graphs with the GUI
#outDir = None
outDir = './figs'

def doPlot(containerDir):
    parsed_logs = load_parsed_logs(logs)


    publications: List[Publication] = []
    retrievals: List[Retrieval] = []

    for parsed_log in parsed_logs:
        publications += parsed_log.publications
        retrievals += parsed_log.completed_retrievals()


    if outDir is not None:
        containedDir = os.path.join(outDir, containerDir)
        Path(containedDir).mkdir(exist_ok=True, parents=True)

    cdf_publications.plot_total(parsed_logs)
    if outDir is not None:
        plt.savefig(os.path.join(containedDir, 'pvd_total.png'))
        plt.clf()

    cdf_publications.plot_getting_closest_peers(parsed_logs)
    if outDir is not None:
        plt.savefig(os.path.join(containedDir, 'pvd_getting_closest_peers.png'))
        plt.clf()

    cdf_publications.plot_total_add_provider(parsed_logs)
    if outDir is not None:
        plt.savefig(os.path.join(containedDir, 'pvd_total_add_provider.png'))
        plt.clf()

    cdf_retrievals.plot_total(parsed_logs)
    if outDir is not None:
        plt.savefig(os.path.join(containedDir, 'ret_total.png'))
        plt.clf()

    cdf_retrievals.plot_getting_closest_peers(parsed_logs)
    if outDir is not None:
        plt.savefig(os.path.join(containedDir, 'ret_getting_closest_peers.png'))
        plt.clf()

    cdf_retrievals.plot_fetch(parsed_logs)
    if outDir is not None:
        plt.savefig(os.path.join(containedDir, 'ret_fetch.png'))
        plt.clf()

    cdf_retrievals.plot_phase_comparison(retrievals)
    if outDir is not None:
        plt.savefig(os.path.join(containedDir, 'ret_phase_comparison_cdf.png'))
        plt.clf()

    pie_phase_retrieval_latency.plot(retrievals)
    if outDir is not None:
        plt.savefig(os.path.join(containedDir, 'ret_phase_comparison_pie.png'))
        plt.clf()


    bar_region_retrieval_latency.plot(parsed_logs)
    if outDir is not None:
        plt.savefig(os.path.join(containedDir, 'ret_region_comparison_bar.png'))
        plt.clf()

    if outDir is None:
        plt.show()

if __name__=='__main__':
    logs = json.load(open('./log_config.json'))
    doPlot(logs[0].split('/')[-2])
