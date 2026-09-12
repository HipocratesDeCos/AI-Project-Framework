"""Compose a completed scenario orchestration into the Vertical MVP boundary.

This facade is intentionally narrow. It does not execute O4, O2, O3 or any
analytical capability. It derives the authorized DecisionContext exclusively
from the orchestration preparation, builds the closed O2 support package, and
represents that package through the existing SCENARIO_COORDINATION capability.
"""
from __future__ import annotations

from eios.core.models import PurchaseOperation
from eios.core.mvp_execution import run_mvp_execution
from eios.core.o4_o2_o3_orchestration import O4O2O3OrchestrationResult
from eios.core.orchestration_support_integration import (
    build_o2_support_from_orchestration,
)
from eios.mvp import VerticalMVPSupportResult


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

    execution = run_mvp_execution(
        purchase=purchase_snapshot.model_copy(deep=True),
        context=context_snapshot,
        policy_version=policy_version,
        scenario_coordination_result=scenario_support.model_copy(deep=True),
    )

    return VerticalMVPSupportResult(
        execution=execution,
        rules=None,
        scenario_support=scenario_support.model_copy(deep=True),
    )


__all__ = ["run_vertical_mvp_from_orchestration"]
