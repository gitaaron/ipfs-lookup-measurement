import numpy as np
import matplotlib.pyplot as plt
from log_parse import load_parsed_logs, ParsedLogFile
from typing import List
from models.model_publication import Publication
from models.model_retrieval import Retrieval


def plot():

    region_labels = ['af_south_1', 'ap_southeast_2', 'eu_central_1', 'me_south_1', 'sa_east_1', 'us_west_1']

    regions_average_retrieval_duration = []

    logs = [ './2022-01-16-data/%s.log' % rl for rl in region_labels]

    for log in logs:

        parsed_logs = load_parsed_logs([log])

        #retrievals: List[Retrieval] = []

        retrievals = parsed_logs[0].retrievals

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

        total_retrieval_durations = [(ret.done_retrieving_at - ret.retrieval_started_at).total_seconds() for ret in retrievals]
        for ret in retrievals:
            print('tot duration : %s' % (ret.done_retrieving_at - ret.retrieval_started_at).total_seconds())

        print('log : %s total_retrieval_durations %s' % (log, np.average(total_retrieval_durations)))

        regions_average_retrieval_duration.append(np.average(total_retrieval_durations))

    x_pos = np.arange(len(region_labels))

    plt.rcdefaults()
    fig1, ax1 = plt.subplots()

    print(x_pos)
    print(regions_average_retrieval_duration)

    ax1.bar(x_pos, regions_average_retrieval_duration, align='center')
    ax1.set_xticks(x_pos, labels=region_labels)

    ax1.set_xlabel('Regions')

    plt.show()


if __name__ == "__main__":
    plot()
