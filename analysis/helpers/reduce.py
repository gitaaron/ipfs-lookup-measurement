from models.model_retrieval import Retrieval
from typing import List

def by_slow_retrievals(retrievals: List[Retrieval]):
    return list(filter(lambda ret: (ret.duration_total().total_seconds() > 4), retrievals))
