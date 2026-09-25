"""Public provenance-safe Decision Twin wrapper backed by safe Stage 2 completion."""
from __future__ import annotations

from copy import deepcopy
from collections.abc import Callable
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field, model_validator

from eios.core.capability_adapters import adapt_twin
from eios.core.decision_twin import AlternativeRepresentation, DecisionTwinComparison, DecisionTwinComparisonInput
from eios.core.decision_twin_engine import compare_alternatives
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.o4_o2_o3_orchestration import O4O2O3Preparation
from eios.core.orchestration import CapabilityExecution
from eios.core.observed_invocation import SingleUseObservedInvoker

from .scenario_integration import (
    ProvenancedScenarioAnalyticsInput,
    complete_provenanced_o4_o2_o3_orchestration,
)


DecisionTwinInvoker = Callable[[PurchaseOperation, DecisionContext], CapabilityExecution]


@dataclass(frozen=True)
class DecisionTwinInvocationCapture:
    result: DecisionTwinComparison
    capability: CapabilityExecution


class ProvenancedDecisionTwinAlternativeInput(BaseModel):
    """One Twin alternative bound to provenance-safe Stage-2 input."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    representation_ref: str = Field(min_length=1, max_length=256)
    scenario_input: ProvenancedScenarioAnalyticsInput

    @model_validator(mode="after")
    def validate_representation(self) -> "ProvenancedDecisionTwinAlternativeInput":
        if not self.representation_ref.strip():
            raise ValueError("representation_ref no puede estar vacía")
        return self


def _validate_root_binding(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    preparation: O4O2O3Preparation,
) -> None:
    prepared = preparation.context
    for field in (
        "decision_id",
        "scenario_id",
        "rules_version",
        "parameters_version",
        "data_snapshot_id",
    ):
        if getattr(context, field) != getattr(prepared, field):
            raise ValueError(f"DecisionContext.{field} incompatible con preparation.context")
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation.decision_id incompatible con DecisionContext")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation.scenario_id incompatible con DecisionContext")


def build_provenanced_decision_twin_comparison(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    preparation: O4O2O3Preparation,
    alternatives: tuple[ProvenancedDecisionTwinAlternativeInput, ...],
) -> DecisionTwinComparison:
    """Rebuild Stage 2 and compare two or more alternatives without detached results."""

    purchase_snapshot = purchase.model_copy(deep=True)
    context_snapshot = context.model_copy(deep=True)
    preparation_snapshot = preparation.model_copy(deep=True)
    alternative_snapshots = tuple(item.model_copy(deep=True) for item in alternatives)

    _validate_root_binding(
        purchase=purchase_snapshot,
        context=context_snapshot,
        preparation=preparation_snapshot,
    )

    if len(alternative_snapshots) < 2:
        raise ValueError("Decision Twin requiere al menos dos alternativas")

    refs = tuple(item.representation_ref for item in alternative_snapshots)
    if len(refs) != len(set(refs)):
        raise ValueError("representation_ref duplicada")

    scenario_ids = tuple(item.scenario_input.scenario_id for item in alternative_snapshots)
    if len(scenario_ids) != len(set(scenario_ids)):
        raise ValueError("scenario_id analítico duplicado")

    stage2 = complete_provenanced_o4_o2_o3_orchestration(
        preparation=preparation_snapshot,
        inputs=tuple(item.scenario_input for item in alternative_snapshots),
    )
    evaluations_by_scenario = {item.scenario_id: item for item in stage2.evaluations}

    representations: list[AlternativeRepresentation] = []
    for item in alternative_snapshots:
        evaluation = evaluations_by_scenario.get(item.scenario_input.scenario_id)
        if evaluation is None:
            raise ValueError("Falta ScenarioEvaluationResult para una alternativa")

        viability_payload = evaluation.viability_result
        if not isinstance(viability_payload, dict):
            raise ValueError("ScenarioEvaluationResult.viability_result debe ser payload canónico")
        viability = viability_payload.get("status")
        if viability not in {
            "VIABLE",
            "VIABLE_CON_CONDICIONES",
            "NOT_VIABLE",
            "NOT_EVALUABLE",
        }:
            raise ValueError("Viability status no soportado por Decision Twin")

        representations.append(
            AlternativeRepresentation(
                representation_ref=item.representation_ref,
                scenario_id=evaluation.scenario_id,
                viability=viability,
                results={
                    "status": evaluation.status.value,
                    "assessments": tuple(deepcopy(evaluation.assessments)),
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
        DecisionTwinComparisonInput(alternatives=tuple(representations))
    )


def build_provenanced_decision_twin_invoker(
    *,
    preparation: O4O2O3Preparation,
    alternatives: tuple[ProvenancedDecisionTwinAlternativeInput, ...],
) -> DecisionTwinInvoker:
    """Freeze source material and return the O1-compatible Decision Twin invoker."""

    preparation_snapshot = preparation.model_copy(deep=True)
    alternative_snapshots = tuple(item.model_copy(deep=True) for item in alternatives)

    if len(alternative_snapshots) < 2:
        raise ValueError("Decision Twin requiere al menos dos alternativas")

    refs = tuple(item.representation_ref for item in alternative_snapshots)
    if len(refs) != len(set(refs)):
        raise ValueError("representation_ref duplicada")

    def invoke(purchase: PurchaseOperation, context: DecisionContext) -> CapabilityExecution:
        comparison = build_provenanced_decision_twin_comparison(
            purchase=purchase.model_copy(deep=True),
            context=context.model_copy(deep=True),
            preparation=preparation_snapshot.model_copy(deep=True),
            alternatives=tuple(item.model_copy(deep=True) for item in alternative_snapshots),
        )
        return adapt_twin(comparison)

    return invoke


class ObservedDecisionTwinInvoker(SingleUseObservedInvoker[
    DecisionTwinComparison, DecisionTwinInvocationCapture
]):
    """One-shot comparison tied to the complete synthetic root purchase."""

    def __init__(self, *, purchase: PurchaseOperation,
                 preparation: O4O2O3Preparation,
                 alternatives: tuple[ProvenancedDecisionTwinAlternativeInput, ...],
                 reference_case_id: str) -> None:
        self._purchase = purchase.model_copy(deep=True)
        self._preparation = preparation.model_copy(deep=True)
        self._alternatives = tuple(item.model_copy(deep=True) for item in alternatives)
        if len(self._alternatives) < 2:
            raise ValueError("Decision Twin requiere al menos dos alternativas")
        refs = tuple(item.representation_ref for item in self._alternatives)
        if len(refs) != len(set(refs)):
            raise ValueError("representation_ref duplicada")
        super().__init__(
            label="DECISION_TWIN", reference_case_id=reference_case_id,
            producer=self._produce, adapter=adapt_twin,
            capture_factory=DecisionTwinInvocationCapture,
        )

    def _produce(self, purchase: PurchaseOperation,
                 context: DecisionContext) -> DecisionTwinComparison:
        mismatches = tuple(field for field in PurchaseOperation.model_fields
                           if getattr(self._purchase, field) != getattr(purchase, field))
        if mismatches:
            raise ValueError("Observed Decision Twin purchase mismatch: "
                             + ", ".join(mismatches))
        return build_provenanced_decision_twin_comparison(
            purchase=purchase, context=context, preparation=self._preparation,
            alternatives=self._alternatives,
        )

    def source_payload(self) -> dict:
        return {
            "purchase": self._purchase.model_dump(mode="json"),
            "preparation": self._preparation.model_dump(mode="json"),
            "alternatives": [item.model_dump(mode="json") for item in self._alternatives],
        }


def build_reference_observed_decision_twin_invoker(
    *, purchase: PurchaseOperation, preparation: O4O2O3Preparation,
    alternatives: tuple[ProvenancedDecisionTwinAlternativeInput, ...],
    reference_case_id: str,
) -> ObservedDecisionTwinInvoker:
    return ObservedDecisionTwinInvoker(
        purchase=purchase, preparation=preparation,
        alternatives=alternatives, reference_case_id=reference_case_id,
    )


__all__ = [
    "DecisionTwinInvoker",
    "ProvenancedDecisionTwinAlternativeInput",
    "build_provenanced_decision_twin_comparison",
    "build_provenanced_decision_twin_invoker",
]
