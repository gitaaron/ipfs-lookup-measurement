from plot import cdf_retrievals, bar_region_retrieval_latency, pie_phase_retrieval_latency
from log_parse import load_parsed_logs, ParsedLogFile
from models.model_publication import Publication
from models.model_retrieval import Retrieval
from typing import List
import matplotlib.pyplot as plt


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

    cdf_retrievals.plot_cumulative_regions(retrievals)
    cdf_retrievals.plot_total(parsed_logs)
    cdf_retrievals.plot_getting_closest_peers(parsed_logs)
    cdf_retrievals.plot_fetch(parsed_logs)
    pie_phase_retrieval_latency.plot(retrievals)
    bar_region_retrieval_latency.plot(parsed_logs)

    plt.show()
