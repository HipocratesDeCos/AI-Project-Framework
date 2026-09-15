"""Provenance-safe execution boundary for Finance Basic.

The low-level Finance Basic engine remains deterministic and non-decisional.
This module closes the reuse boundary by binding the projection horizon to the
resolved P-FIN-001 configuration and by revalidating/recomputing the analytical
result before it can cross into Rules.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from eios.parameters import ResolvedConfiguration

from .engine import calculate_finance_basic
from .models import FinanceBasicInput, FinanceBasicResult


P_FIN_001 = "P-FIN-001"
P_FIN_001_UNIT = "días"


class FinanceHorizonProvenanceError(ValueError):
    """Technical contract failure for the Finance Basic horizon boundary."""


@dataclass(frozen=True)
class ProvenancedFinanceBasicExecution:
    """Finance Basic execution bound to the resolved P-FIN-001 configuration."""

    finance_input: FinanceBasicInput
    finance_result: FinanceBasicResult
    horizon_resolution: ResolvedConfiguration

    @property
    def horizon_configuration_ref(self) -> str:
        return self.horizon_resolution.configuration_ref


def _provenance_error(message: str) -> FinanceHorizonProvenanceError:
    return FinanceHorizonProvenanceError(message)


def _validate_horizon_resolution(
    finance_input: FinanceBasicInput,
    horizon_resolution: ResolvedConfiguration,
) -> int:
    if not isinstance(finance_input, FinanceBasicInput):
        raise TypeError("finance_input debe ser FinanceBasicInput")
    if not isinstance(horizon_resolution, ResolvedConfiguration):
        raise TypeError("horizon_resolution debe ser ResolvedConfiguration")

    if horizon_resolution.parameter_id != P_FIN_001:
        raise _provenance_error("El horizonte Finance Basic requiere P-FIN-001")
    if horizon_resolution.parameters_version != finance_input.context.parameters_version:
        raise _provenance_error(
            "P-FIN-001 está vinculada a otra DecisionContext.parameters_version"
        )
    if horizon_resolution.company_id != finance_input.snapshot.company_scope:
        raise _provenance_error("P-FIN-001 pertenece a otro company_scope")
    if horizon_resolution.effective_at.date() != finance_input.snapshot.as_of_date:
        raise _provenance_error(
            "P-FIN-001 debe resolverse para la fecha del snapshot financiero"
        )

    configuration = horizon_resolution.configuration
    try:
        active = configuration.valid_from <= horizon_resolution.effective_at and (
            configuration.valid_to is None
            or horizon_resolution.effective_at < configuration.valid_to
        )
    except TypeError as exc:
        raise _provenance_error(
            "P-FIN-001 y effective_at usan semántica temporal incompatible"
        ) from exc
    if not active:
        raise _provenance_error("P-FIN-001 no está vigente en effective_at")

    if horizon_resolution.unit != P_FIN_001_UNIT:
        raise _provenance_error("P-FIN-001 debe usar la unidad canónica 'días'")

    try:
        value = Decimal(horizon_resolution.value)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise _provenance_error("P-FIN-001 debe contener un número entero de días") from exc

    if not value.is_finite() or value <= 0 or value != value.to_integral_value():
        raise _provenance_error("P-FIN-001 debe ser un entero finito y positivo")

    horizon_days = int(value)
    if horizon_days != finance_input.horizon_days:
        raise _provenance_error(
            "FinanceBasicInput.horizon_days no coincide con la P-FIN-001 resuelta"
        )
    return horizon_days


def run_provenanced_finance_basic(
    finance_input: FinanceBasicInput,
    horizon_resolution: ResolvedConfiguration,
) -> ProvenancedFinanceBasicExecution:
    """Freeze, validate and execute Finance Basic from a resolved P-FIN-001."""
    if not isinstance(finance_input, FinanceBasicInput):
        raise TypeError("finance_input debe ser FinanceBasicInput")
    if not isinstance(horizon_resolution, ResolvedConfiguration):
        raise TypeError("horizon_resolution debe ser ResolvedConfiguration")

    input_snapshot = finance_input.model_copy(deep=True)
    resolution_snapshot = deepcopy(horizon_resolution)
    _validate_horizon_resolution(input_snapshot, resolution_snapshot)
    result = calculate_finance_basic(input_snapshot)
    return ProvenancedFinanceBasicExecution(
        finance_input=input_snapshot,
        finance_result=result,
        horizon_resolution=resolution_snapshot,
    )


def validate_provenanced_finance_basic_execution(
    execution: ProvenancedFinanceBasicExecution,
) -> None:
    """Reject detached or forged Finance Basic executions before Rules."""
    if not isinstance(execution, ProvenancedFinanceBasicExecution):
        raise TypeError("execution debe ser ProvenancedFinanceBasicExecution")

    _validate_horizon_resolution(
        execution.finance_input,
        execution.horizon_resolution,
    )
    expected_result = calculate_finance_basic(execution.finance_input)
    if expected_result != execution.finance_result:
        raise _provenance_error(
            "FinanceBasicResult no coincide con la recomputación del input provenance-safe"
        )


__all__ = [
    "FinanceHorizonProvenanceError",
    "P_FIN_001",
    "P_FIN_001_UNIT",
    "ProvenancedFinanceBasicExecution",
    "run_provenanced_finance_basic",
    "validate_provenanced_finance_basic_execution",
]
