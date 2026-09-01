"""Deterministic aggregation boundary for EIOS Price Intelligence."""
from __future__ import annotations
from decimal import Decimal
from typing import Sequence
from .models import AggregationMethod

def aggregate_median_unweighted(values: Sequence[Decimal]) -> Decimal | None:
    """Return the exact unweighted median; never selects, weights, or filters values."""
    if not values:
        return None
    ordered=sorted(values)
    n=len(ordered)
    if n % 2:
        return ordered[n//2]
    return (ordered[n//2-1]+ordered[n//2])/Decimal(2)

def aggregate_selected_prices(values: Sequence[Decimal]) -> tuple[Decimal | None, AggregationMethod]:
    return aggregate_median_unweighted(values), "MEDIAN_UNWEIGHTED"

__all__=["aggregate_median_unweighted","aggregate_selected_prices"]
