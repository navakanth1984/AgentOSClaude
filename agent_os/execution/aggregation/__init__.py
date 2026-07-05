from .base import Aggregator, AggregationResult
from .fast import FastAggregator
from .standard import StandardAggregator
from .verified import VerifiedAggregator

_AGGREGATORS = {
    "fast": FastAggregator,
    "standard": StandardAggregator,
    "verified": VerifiedAggregator,
}


def get_aggregator(name: str) -> Aggregator:
    try:
        return _AGGREGATORS[name]()
    except KeyError:
        raise ValueError(f"Unknown aggregation strategy '{name}'. Choose one of {list(_AGGREGATORS)}.")
