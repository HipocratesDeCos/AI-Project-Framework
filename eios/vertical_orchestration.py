"""Compose a completed scenario orchestration into the Vertical MVP boundary.

This facade is intentionally narrow. It does not execute O4, O2 materialization,
O3 or analytical capabilities. It derives the authorized DecisionContext from
the orchestration preparation, builds closed O2 presentation support, and
provides an explicit SCENARIO_COORDINATION invoker to the E2E boundary.
"""
from __future__ import annotations

from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.mvp_execution import CapabilityInvoker, run_mvp_execution
from eios.core.o4_o2_o3_orchestration import O4O2O3OrchestrationResult
from eios.core.orchestration_support_integration import (
    build_o2_support_from_orchestration,
)
from eios.core.scenario_coordination_adapter import adapt_scenario_coordination
from eios.mvp import VerticalMVPSupportResult


def _scenario_coordination_invoker_from_orchestration(
    orchestration_result: O4O2O3OrchestrationResult,
) -> CapabilityInvoker:
    """Build a runtime-bound Scenario Coordination invoker.

    This quarantine boundary does not certify the provenance of the supplied
    orchestration object. It only prevents the Vertical composition layer from
    re-labeling a detached O2 support result through a snapshot invoker.
    """
    orchestration_snapshot = orchestration_result.model_copy(deep=True)
    expected_context = orchestration_snapshot.preparation.context.model_copy(deep=True)

    def invoke(
        purchase: PurchaseOperation,
        context: DecisionContext,
    ):
        if context != expected_context:
            raise ValueError(
                "DecisionContext runtime incoherente con la preparación de escenarios"
            )
        support = build_o2_support_from_orchestration(
            purchase_operation=purchase.model_copy(deep=True),
            orchestration_result=orchestration_snapshot.model_copy(deep=True),
        )
        return adapt_scenario_coordination(support)

    return invoke


def run_vertical_mvp_from_orchestration(
    *,
    purchase: PurchaseOperation,
    orchestration_result: O4O2O3OrchestrationResult,
    policy_version: str,
) -> VerticalMVPSupportResult:
    """Represent one completed scenario orchestration in the Vertical MVP.

    No detached ``DecisionContext`` or O3 result sequence is accepted. The
    context frozen in ``orchestration_result.preparation`` is authoritative.
    Terminal O4/DRAFT-only results remain fail-closed through the existing
    orchestration-to-O2-support bridge.
    """
    purchase_snapshot = purchase.model_copy(deep=True)
    orchestration_snapshot = orchestration_result.model_copy(deep=True)
    context_snapshot = orchestration_snapshot.preparation.context.model_copy(deep=True)

    scenario_support = build_o2_support_from_orchestration(
        purchase_operation=purchase_snapshot.model_copy(deep=True),
        orchestration_result=orchestration_snapshot.model_copy(deep=True),
    )
    scenario_coordination_invoker = _scenario_coordination_invoker_from_orchestration(
        orchestration_snapshot
    )

    execution = run_mvp_execution(
        purchase=purchase_snapshot.model_copy(deep=True),
        context=context_snapshot,
        policy_version=policy_version,
        scenario_coordination_invoker=scenario_coordination_invoker,
    )

    return VerticalMVPSupportResult(
        execution=execution,
        rules=None,
        scenario_support=scenario_support.model_copy(deep=True),
    )


__all__ = ["run_vertical_mvp_from_orchestration"]
