from log_parse import ParsedLogFiles
from helpers import reduce
from typing import List
from models.model_retrieval import Retrieval
from helpers.constants import RetrievalPhase


def _avg_duration(retrievals: List[Retrieval]):
    num: float = len(retrievals)
    _total_duration: int = 0
    for ret in retrievals:
        _total_duration += ret.duration(RetrievalPhase.TOTAL).total_seconds()

    return _total_duration / num

def avg_duration_non_first_provider_nearest(parsed_logs: ParsedLogFiles) -> float:
    non_fpn_retrievals = parsed_logs.non_first_provider_nearest_retrievals
    return _avg_duration(non_fpn_retrievals)

def avg_duration_first_provider_nearest(parsed_logs: ParsedLogFiles) -> float:
    fpn_retrievals = parsed_logs.first_provider_nearest_retrievals
    return _avg_duration(fpn_retrievals)


def percent_fpn_slow(parsed_logs: ParsedLogFiles) -> float:
    fpn_retrievals = parsed_logs.first_provider_nearest_retrievals
    slow_fpn_retrievals = reduce.by_slow_retrievals(fpn_retrievals)

    return len(slow_fpn_retrievals) / len(fpn_retrievals) * 100

def percent_non_fpn_slow(parsed_logs: ParsedLogFiles) -> float:
    non_fpn_retrievals = parsed_logs.non_first_provider_nearest_retrievals
    slow_non_fpn_retrievals = reduce.by_slow_retrievals(non_fpn_retrievals)

    return len(slow_non_fpn_retrievals) / len(non_fpn_retrievals) * 100


def percent_nearest_neighbor_first_provider(parsed_logs: ParsedLogFiles) -> float:
    hfp_retrievals = parsed_logs.has_first_provider_retrievals
    fpn_retrievals = parsed_logs.first_provider_nearest_retrievals

    return len(fpn_retrievals) / len(hfp_retrievals) * 100
