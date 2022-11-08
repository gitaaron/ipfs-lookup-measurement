from pickled.model_retrieval import Retrieval
from models.model_duration import Duration
from helpers.constants import RetrievalPhase
import numpy as np

def avg_duration(retrievals: list[Retrieval], phase: RetrievalPhase):
    num: float = len(retrievals)
    _total_duration: int = 0
    for ret in retrievals:
        _total_duration += ret.duration(phase).total_seconds()

    return round(_total_duration / num, 3)


# calculate percentage of retrievals that are more than one std slower than mean
def percent_slow(retrievals: list[Retrieval], phase: RetrievalPhase):
    durations = [ret.duration(phase).total_seconds() for ret in retrievals]
    std = np.std(durations)
    mean = np.mean(durations)
    slow = mean+std
    count = 0
    for ret in retrievals:
        if ret.duration(phase).total_seconds() > slow:
            count += 1

    return round(count / len(retrievals) * 100, 3)


def avg_duration_from_breakdown(breakdown: dict[str, float]):
    avg_duration = {}
    avg_duration['count'] = breakdown['count']
    for d_key,d_val in breakdown['durations'].items():
        avg_duration[d_key] = Duration(d_val / breakdown['count'])

    return avg_duration


def count_from_breakdown(breakdown: dict[int, list[Retrieval]]):
    counts = {}
    for b_key, b_val in breakdown.items():
        counts[b_key] = len(b_val)

    return counts

def avg_phase_duration_breakdown(retrievals: list[Retrieval]):
    b = {}
    for phase in RetrievalPhase:
        b[phase] = Duration(avg_duration(retrievals, phase))
    return b

def avg_phase_duration_from_breakdown(breakdown: dict[int,  list[Retrieval]]):
    avg_durations = {}
    for b_key, b_val in breakdown.items():
        avg_durations[b_key] = avg_phase_duration_breakdown(b_val)

    return avg_durations

def std_breakdown(retrievals: list[Retrieval]):
    phases = {}
    for phase in RetrievalPhase:
        durations = [ret.duration(phase).total_seconds() for ret in retrievals]
        phases[phase] = Duration(round(np.std(durations), 3))

    return phases

def std_from_breakdown(breakdown: dict[int, list[Retrieval]]):
    stds = {}
    for b_key, rets in breakdown.items():
        stds[b_key] = std_breakdown(rets)

    return stds


def percent_slow_breakdown(retrievals: list[Retrieval]):
    percents = {}
    for phase in RetrievalPhase:
        percents[phase] = percent_slow(retrievals, phase)

    return percents

def percent_slow_phase_breakdown_from_breakdown(breakdown: dict[int, list[Retrieval]]):
    percents = {}
    for b_key, rets in breakdown.items():
        percents[b_key] =  percent_slow_breakdown(rets)

    return percents
