"""Public provenance-safe Stage-2 completion backed by the minimal VF producer."""
from __future__ import annotations

from copy import deepcopy
from collections.abc import Callable, Sequence

from pydantic import BaseModel, ConfigDict, Field

from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.orchestration import CapabilityExecution
from eios.core.orchestration_support_integration import (
    build_o2_support_from_orchestration,
)
from eios.core.scenario_coordination_adapter import adapt_scenario_coordination
from eios.core.o4_o2_o3_orchestration import (
    AuthorizedScenarioAnalytics,
    O4O2O3OrchestrationResult,
    O4O2O3Preparation,
    _complete_o4_o2_o3_orchestration,
)
from eios.core.scenario_engine import ScenarioStatus
from eios.core.scenario_evaluation import ScenarioEvaluationStatus
from eios.core.viability_scenario_integration import (
    _build_context_bound_analytics_from_viability,
)

from .provenance import AssessmentTraceBinding
from .viability_provenance import evaluate_provenanced_viability


class ProvenancedScenarioAnalyticsInput(BaseModel):
    """Scenario-specific provenanced input; it never accepts a detached VF result."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario_id: str = Field(min_length=1, max_length=64)
    purchase: PurchaseOperation
    assessment_bindings: tuple[AssessmentTraceBinding, ...]
    status: ScenarioEvaluationStatus = ScenarioEvaluationStatus.COMPLETED
    limitations: tuple[str, ...] = ()
    failure_reason: str | None = None


def _scenario_context(
    preparation: O4O2O3Preparation,
    scenario_id: str,
) -> DecisionContext:
    context = preparation.context
    return context.model_copy(update={"scenario_id": scenario_id}, deep=True)


def build_authorized_scenario_analytics_from_provenanced_assessments(
    *,
    preparation: O4O2O3Preparation,
    input_material: ProvenancedScenarioAnalyticsInput,
) -> AuthorizedScenarioAnalytics:
    """Build internal Stage-2 transport only after C0+VF provenance is re-established."""
    preparation_snapshot = preparation.model_copy(deep=True)
    material = input_material.model_copy(deep=True)

    matches = tuple(
        scenario
        for scenario in preparation_snapshot.materialization.scenarios
        if scenario.scenario_id == material.scenario_id
    )
    if len(matches) != 1:
        raise ValueError("scenario_id debe identificar exactamente un escenario O2")
    if matches[0].status != ScenarioStatus.VALID:
        raise ValueError("Stage 2 requiere un ScenarioVersion VALID")

    context = _scenario_context(preparation_snapshot, material.scenario_id)
    purchase = material.purchase.model_copy(deep=True)
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation.decision_id incompatible con escenario")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation.scenario_id incompatible con escenario")

    bindings = tuple(item.model_copy(deep=True) for item in material.assessment_bindings)
    if not bindings:
        raise ValueError("Stage 2 requiere AssessmentTraceBinding explícito y no vacío")

    viability = evaluate_provenanced_viability(
        purchase=purchase,
        context=context,
        bindings=bindings,
    )
    assessments = tuple(deepcopy(item.assessment) for item in bindings)
    trace_references = tuple(item.trace.trace_id for item in bindings)

    return _build_context_bound_analytics_from_viability(
        preparation=preparation_snapshot,
        scenario_id=material.scenario_id,
        assessments=assessments,
        viability_result=viability,
        status=material.status,
        limitations=tuple(material.limitations),
        trace_references=trace_references,
        failure_reason=material.failure_reason,
    )


def complete_provenanced_o4_o2_o3_orchestration(
    *,
    preparation: O4O2O3Preparation,
    inputs: Sequence[ProvenancedScenarioAnalyticsInput],
) -> O4O2O3OrchestrationResult:
    """Complete Stage 2 only from provenanced per-scenario C0 material and internal VF production."""
    preparation_snapshot = preparation.model_copy(deep=True)
    input_snapshots = tuple(item.model_copy(deep=True) for item in inputs)

    scenario_ids = tuple(item.scenario_id for item in input_snapshots)
    if len(scenario_ids) != len(set(scenario_ids)):
        raise ValueError("scenario_id duplicado en Stage 2 provenance-safe")

    analytics = tuple(
        build_authorized_scenario_analytics_from_provenanced_assessments(
            preparation=preparation_snapshot,
            input_material=item,
        )
        for item in input_snapshots
    )
    return _complete_o4_o2_o3_orchestration(
        preparation=preparation_snapshot,
        analytics=analytics,
    )


ScenarioCoordinationInvoker = Callable[
    [PurchaseOperation, DecisionContext],
    CapabilityExecution,
]


def _validate_root_runtime(
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
            raise ValueError(
                f"DecisionContext.{field} incompatible con preparation.context"
            )
    if purchase.decision_id != context.decision_id:
        raise ValueError(
            "PurchaseOperation.decision_id incompatible con DecisionContext"
        )
    if purchase.scenario_id != context.scenario_id:
        raise ValueError(
            "PurchaseOperation.scenario_id incompatible con DecisionContext"
        )


def build_provenanced_scenario_coordination_invoker(
    *,
    preparation: O4O2O3Preparation,
    inputs: Sequence[ProvenancedScenarioAnalyticsInput],
) -> ScenarioCoordinationInvoker:
    """Freeze provenanced Stage-2 sources and rebuild coordination at runtime.

    The returned invoker never accepts a detached orchestration or O2 support
    package. Each invocation re-establishes C0/VF provenance through the
    public provenance-safe Stage-2 completion before adapting the resulting
    support package to SCENARIO_COORDINATION.
    """
    preparation_snapshot = preparation.model_copy(deep=True)
    input_snapshots = tuple(item.model_copy(deep=True) for item in inputs)

    if not input_snapshots:
        raise ValueError(
            "SCENARIO_COORDINATION provenance-safe requiere inputs no vacíos"
        )
    scenario_ids = tuple(item.scenario_id for item in input_snapshots)
    if len(scenario_ids) != len(set(scenario_ids)):
        raise ValueError(
            "scenario_id duplicado en SCENARIO_COORDINATION provenance-safe"
        )

    def invoke(
        purchase: PurchaseOperation,
        context: DecisionContext,
    ) -> CapabilityExecution:
        purchase_snapshot = purchase.model_copy(deep=True)
        context_snapshot = context.model_copy(deep=True)
        preparation_runtime = preparation_snapshot.model_copy(deep=True)
        inputs_runtime = tuple(
            item.model_copy(deep=True) for item in input_snapshots
        )

        _validate_root_runtime(
            purchase=purchase_snapshot,
            context=context_snapshot,
            preparation=preparation_runtime,
        )
        orchestration = complete_provenanced_o4_o2_o3_orchestration(
            preparation=preparation_runtime,
            inputs=inputs_runtime,
        )
        support = build_o2_support_from_orchestration(
            purchase_operation=purchase_snapshot,
            orchestration_result=orchestration,
        )
        return adapt_scenario_coordination(support)

    return invoke


__all__ = [
    "ProvenancedScenarioAnalyticsInput",
    "ScenarioCoordinationInvoker",
    "build_authorized_scenario_analytics_from_provenanced_assessments",
    "build_provenanced_scenario_coordination_invoker",
    "complete_provenanced_o4_o2_o3_orchestration",
]
