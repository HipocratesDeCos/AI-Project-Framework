"""EIOS Profitability Core public surface."""
from .engine import calculate_profitability
from .models import (
    AuthorizedCostBasis,
    AuthorizedSaleBasis,
    EconomicBasisState,
    ProfitabilityCalculationState,
    ProfitabilityInput,
    ProfitabilityResult,
)

__all__ = [
    "AuthorizedCostBasis",
    "AuthorizedSaleBasis",
    "EconomicBasisState",
    "ProfitabilityCalculationState",
    "ProfitabilityInput",
    "ProfitabilityResult",
    "calculate_profitability",
]
