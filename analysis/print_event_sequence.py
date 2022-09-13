import json
import numpy as np
import matplotlib.pyplot as plt
from log_parse import load_parsed_logs, ParsedLogFile
from typing import List
from models.model_publication import Publication
from models.model_retrieval import Retrieval


def plot():
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
        retrievals += parsed_log.retrievals

    # Remove all retrievals that are marked as invalid
    before = len(retrievals)
    retrievals = list(
        filter(lambda ret: not ret.marked_as_incomplete, retrievals))
    print(
        f"Removed {before - len(retrievals)} of {before} retrievals because they were incomplete")

    retrievals = list(filter(lambda ret: ret.state !=
                      Retrieval.State.DONE_WITHOUT_ASKING_PEERS, retrievals))
    print(
        f"Removed {before - len(retrievals)} of {before} retrievals because they were not started")  # error in our measurement setup

    cids = {}

    for r in retrievals:
        print('retrieval_started_at %s' % r.retrieval_started_at)
        print('  get_providers_queries_started_time %s' % (r.get_providers_queries_started_at - r.retrieval_started_at).total_seconds())
        print('  found_first_provider_at %s' % (r.found_first_provider_at - r.retrieval_started_at).total_seconds())
        print('  finished_searching_providers_at %s' % (r.finished_searching_providers_at - r.retrieval_started_at).total_seconds())

        #print('dial_started_at
        #print('connected_at
        #print('stream_opened_at


        #print('  found_first_provider_time %s')
        #print('  dial_started_at %s connected_at %s')

        #% retrieval.retrieval_started_at, get_providers_queries_started_at, found_first_provider_at, dial_started_at, connected_at)

if __name__ == "__main__":
    plot()
