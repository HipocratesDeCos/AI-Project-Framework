"""Bridge completed O4 -> O2 -> O3 orchestration into closed O2 support.

This integration does not execute generation, scenario materialization,
evaluation, analytics, or business decision logic. It only delegates already-
produced O3 evaluations to the existing O3 -> O2 support bridge using the
DecisionContext frozen inside the orchestration preparation.
"""
from __future__ import annotations

from .models import PurchaseOperation
from .o2 import O2SupportPackage
from .o2_o3_integration import build_o2_support_from_o3
from .o4_o2_o3_orchestration import O4O2O3OrchestrationResult
from .scenario_coordination_adapter import validate_scenario_coordination_context


def build_o2_support_from_orchestration(
    *,
    purchase_operation: PurchaseOperation,
    orchestration_result: O4O2O3OrchestrationResult,
) -> O2SupportPackage:
    """Build the authorized O2 support package from a completed orchestration.

    The orchestration's own prepared context is authoritative. No detached
    context argument is accepted. Results without O3 evaluations fail closed
    because no authorized mapping exists from O4/DRAFT terminal states to O2
    scenario-support states.
    """
    purchase_snapshot = purchase_operation.model_copy(deep=True)
    orchestration_snapshot = orchestration_result.model_copy(deep=True)

    if not orchestration_snapshot.evaluations:
        raise ValueError(
            "O4/O2/O3 -> O2 Support requiere al menos una evaluación O3; "
            "no se traducen estados O4 o DRAFT sin evaluación"
        )

    context_snapshot = orchestration_snapshot.preparation.context.model_copy(deep=True)
    evaluations_snapshot = tuple(
        item.model_copy(deep=True) for item in orchestration_snapshot.evaluations
    )

    support = build_o2_support_from_o3(
        purchase_snapshot,
        context_snapshot,
        evaluations_snapshot,
    )
    validate_scenario_coordination_context(support, context_snapshot)
    return support.model_copy(deep=True)


__all__ = ["build_o2_support_from_orchestration"]
