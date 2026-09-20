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
    "ProfitabilityProvenanceError",
    "ProvenancedProfitabilityExecution",
    "calculate_profitability",
    "run_provenanced_profitability",
    "validate_provenanced_profitability_execution",
]

from .provenance import (
    ProfitabilityProvenanceError,
    ProvenancedProfitabilityExecution,
    run_provenanced_profitability,
    validate_provenanced_profitability_execution,
)
