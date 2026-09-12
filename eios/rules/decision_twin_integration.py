"""Provenance-safe integration from verified scenario analytics into Decision Twin.

The integration never accepts a detached DecisionTwinComparison or arbitrary
AlternativeRepresentation as a reusable public boundary. It reconstructs Stage
2 through the existing provenance-safe scenario boundary, then transports only
already-produced values into the closed Decision Twin comparison engine.
"""
from __future__ import annotations

from collections.abc import Callable, Sequence
from copy import deepcopy
from dataclasses import dataclass

from eios.core.capability_adapters import adapt_twin
from eios.core.decision_twin import AlternativeRepresentation, DecisionTwinComparison, DecisionTwinComparisonInput
from eios.core.decision_twin_engine import compare_alternatives
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.o4_o2_o3_orchestration import O4O2O3Preparation
from eios.core.orchestration import CapabilityExecution

from .scenario_integration import (
    ProvenancedScenarioAnalyticsInput,
    complete_provenanced_o4_o2_o3_orchestration,
)


DecisionTwinInvoker = Callable[[PurchaseOperation, DecisionContext], CapabilityExecution]


@dataclass(frozen=True)
class ProvenancedDecisionTwinAlternativeInput:
    """Transient representation reference bound to verifiable scenario analytics."""

    representation_ref: str
    analytics: ProvenancedScenarioAnalyticsInput


def _snapshot_alternatives(
    alternatives: Sequence[ProvenancedDecisionTwinAlternativeInput],
) -> tuple[ProvenancedDecisionTwinAlternativeInput, ...]:
    snapshots = tuple(deepcopy(item) for item in alternatives)
    if len(snapshots) < 2:
        raise ValueError("Decision Twin requiere al menos dos alternativas provenanced")

    for item in snapshots:
        if not isinstance(item, ProvenancedDecisionTwinAlternativeInput):
            raise TypeError("Decision Twin requiere ProvenancedDecisionTwinAlternativeInput")
        if not isinstance(item.analytics, ProvenancedScenarioAnalyticsInput):
            raise TypeError("analytics debe ser ProvenancedScenarioAnalyticsInput")
        if not item.representation_ref.strip():
            raise ValueError("representation_ref no puede estar vacía")
        if len(item.representation_ref) > 256:
            raise ValueError("representation_ref excede la longitud autorizada")

    refs = tuple(item.representation_ref for item in snapshots)
    if len(refs) != len(set(refs)):
        raise ValueError("representation_ref debe ser única dentro de la comparación")

    scenario_ids = tuple(item.analytics.scenario_id for item in snapshots)
    if len(scenario_ids) != len(set(scenario_ids)):
        raise ValueError("scenario_id analítico duplicado en Decision Twin")

    return snapshots


def _validate_root_context(
    preparation: O4O2O3Preparation,
    purchase: PurchaseOperation,
    context: DecisionContext,
) -> None:
    mismatches = tuple(
        field
        for field in (
            "decision_id",
            "scenario_id",
            "rules_version",
            "parameters_version",
            "data_snapshot_id",
        )
        if getattr(preparation.context, field) != getattr(context, field)
    )
    if mismatches:
        raise ValueError(
            "DecisionContext no coincide con la preparación Decision Twin: "
            + ", ".join(mismatches)
        )

    purchase_mismatches = tuple(
        field
        for field in ("decision_id", "scenario_id")
        if getattr(purchase, field) != getattr(context, field)
    )
    if purchase_mismatches:
        raise ValueError(
            "PurchaseOperation no coincide con DecisionContext: "
            + ", ".join(purchase_mismatches)
        )


def build_provenanced_decision_twin_comparison(
    *,
    preparation: O4O2O3Preparation,
    alternatives: Sequence[ProvenancedDecisionTwinAlternativeInput],
    purchase: PurchaseOperation,
    context: DecisionContext,
) -> DecisionTwinComparison:
    """Rebuild verified Stage 2 and compare its alternatives descriptively."""
    preparation_snapshot = preparation.model_copy(deep=True)
    purchase_snapshot = purchase.model_copy(deep=True)
    context_snapshot = context.model_copy(deep=True)
    alternative_snapshots = _snapshot_alternatives(alternatives)

    _validate_root_context(
        preparation_snapshot,
        purchase_snapshot,
        context_snapshot,
    )

    orchestration = complete_provenanced_o4_o2_o3_orchestration(
        preparation=preparation_snapshot,
        analytics=tuple(item.analytics for item in alternative_snapshots),
    )

    by_scenario = {
        item.analytics.scenario_id: item for item in alternative_snapshots
    }
    represented: list[AlternativeRepresentation] = []
    for evaluation in orchestration.evaluations:
        source = by_scenario[evaluation.scenario_id]
        viability_status = source.analytics.viability_result.status.value

        viability_payload = evaluation.viability_result
        if not isinstance(viability_payload, dict):
            raise TypeError("O3 viability_result debe conservar el payload canónico de VF")
        if viability_payload.get("status") != viability_status:
            raise ValueError("O3 viability_result no coincide con el ViabilityResult provenanced")

        represented.append(
            AlternativeRepresentation(
                representation_ref=source.representation_ref,
                scenario_id=evaluation.scenario_id,
                viability=viability_status,
                results={
                    "scenario_evaluation_status": evaluation.status.value,
                    "assessments": deepcopy(tuple(evaluation.assessments)),
                    "limitations": tuple(evaluation.limitations),
                    "failure_reason": evaluation.failure_reason,
                },
                conditions={},
                consequences={},
                risk_refs=(),
                trace_refs=tuple(evaluation.trace_references),
            )
        )

    return compare_alternatives(
        DecisionTwinComparisonInput(alternatives=tuple(represented))
    )


def build_provenanced_decision_twin_invoker(
    *,
    preparation: O4O2O3Preparation,
    alternatives: Sequence[ProvenancedDecisionTwinAlternativeInput],
) -> DecisionTwinInvoker:
    """Freeze verifiable inputs and expose the Vertical MVP invoker contract."""
    preparation_snapshot = preparation.model_copy(deep=True)
    alternative_snapshots = _snapshot_alternatives(alternatives)

    def invoke(
        purchase: PurchaseOperation,
        context: DecisionContext,
    ) -> CapabilityExecution:
        comparison = build_provenanced_decision_twin_comparison(
            preparation=preparation_snapshot.model_copy(deep=True),
            alternatives=tuple(deepcopy(item) for item in alternative_snapshots),
            purchase=purchase.model_copy(deep=True),
            context=context.model_copy(deep=True),
        )
        return adapt_twin(comparison)

    return invoke


__all__ = [
    "DecisionTwinInvoker",
    "ProvenancedDecisionTwinAlternativeInput",
    "build_provenanced_decision_twin_comparison",
    "build_provenanced_decision_twin_invoker",
]
