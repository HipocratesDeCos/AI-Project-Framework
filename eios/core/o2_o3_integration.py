"""Narrow integration bridge from O3 scenario results into closed O2 models.

The bridge copies already-produced information only. It does not execute or
reinterpret scenario evaluation, rules, viability, or business decisions.
"""
from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from typing import Any

from .models import DecisionContext, PurchaseOperation
from .o2 import O2ScenarioResult, O2ScenarioStatus, O2SupportPackage, build_support_package
from .scenario_evaluation import ScenarioEvaluationResult


def _validate_context(result: ScenarioEvaluationResult, context: DecisionContext) -> None:
    if result.decision_id != context.decision_id:
        raise ValueError("O3 decision_id incoherente con DecisionContext")
    if result.rules_version != context.rules_version:
        raise ValueError("O3 rules_version incoherente con DecisionContext")
    if result.parameters_version != context.parameters_version:
        raise ValueError("O3 parameters_version incoherente con DecisionContext")
    if result.data_snapshot_id != context.data_snapshot_id:
        raise ValueError("O3 data_snapshot_id incoherente con DecisionContext")


def adapt_o3_result_for_o2(
    result: ScenarioEvaluationResult,
    context: DecisionContext,
) -> O2ScenarioResult:
    """Copy one already-produced O3 result into the existing O2 envelope."""
    _validate_context(result, context)
    try:
        status = O2ScenarioStatus(result.status.value)
    except ValueError as exc:
        raise ValueError(
            f"El estado O3 {result.status.value} no tiene equivalencia O2 literal autorizada"
        ) from exc

    values: dict[str, Any] = {}
    if result.assessments:
        values["assessments"] = deepcopy(tuple(result.assessments))
    if result.viability_result is not None:
        values["viability_result"] = deepcopy(result.viability_result)

    return O2ScenarioResult(
        scenario_id=result.scenario_id,
        status=status,
        values=values,
        trace_references=tuple(result.trace_references),
        unresolved_items=tuple(result.limitations),
        failure_reason=result.failure_reason,
    )


def build_o2_support_from_o3(
    purchase_operation: PurchaseOperation,
    context: DecisionContext,
    results: Sequence[ScenarioEvaluationResult],
) -> O2SupportPackage:
    """Build O2 support from O3 results without running either component."""
    if purchase_operation.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase_operation.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    if not results:
        raise ValueError("La integración O2/O3 requiere al menos un resultado O3")

    adapted = tuple(adapt_o3_result_for_o2(result, context) for result in results)
    return build_support_package(purchase_operation, context, adapted)


__all__ = ["adapt_o3_result_for_o2", "build_o2_support_from_o3"]
