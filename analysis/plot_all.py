from plot import cdf_retrievals, bar_region_retrieval_latency, pie_phase_retrieval_latency
from log_parse import load_parsed_logs, ParsedLogFile
from models.model_publication import Publication
from models.model_retrieval import Retrieval
from typing import List
import matplotlib.pyplot as plt


def plot_cdf(retrievals):
    fig, axl = plt.subplots()
    cdf_retrievals.total(axl, retrievals)
    cdf_retrievals.initiated_phase(axl, retrievals)
    cdf_retrievals.getting_closest_peers_phase(axl, retrievals)
    cdf_retrievals.dialing_phase(axl, retrievals)
    cdf_retrievals.fetching_phase(axl, retrievals)
    axl.set_title('Retrieval Phase Latency Distribution')
    axl.legend(loc='lower right')

if __name__=='__main__':
    logs = [
        "./2022-01-16-data/af_south_1.log",
        "./2022-01-16-data/ap_southeast_2.log",
        "./2022-01-16-data/eu_central_1.log",
        "./2022-01-16-data/me_south_1.log",
        "./2022-01-16-data/sa_east_1.log",
        "./2022-01-16-data/us_west_1.log",
    ]

    parsed_logs = load_parsed_logs(logs)


    publications: List[Publication] = []
    retrievals: List[Retrieval] = []

    for parsed_log in parsed_logs:
        publications += parsed_log.publications
        retrievals += parsed_log.completed_retrievals()

    plot_cdf(retrievals)
    pie_phase_retrieval_latency.plot(retrievals)
    bar_region_retrieval_latency.plot(parsed_logs)

    plt.show()
