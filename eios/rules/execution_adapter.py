"""Adapter from the Rules Engine facade to the controlled E2E C0 capability.

The adapter captures an immutable snapshot of already-produced Assessments and
returns a callable compatible with ``eios.core.execution_boundary.execute_plan``.
It does not evaluate business conditions or create a new capability identity.
"""
from __future__ import annotations

from collections.abc import Callable, Sequence

from eios.core.models import Assessment, DecisionContext, PurchaseOperation
from eios.core.orchestration import CapabilityExecution

from .engine import RulesEngineInput, run_rules_engine
from .runtime import ConsolidatedBaseResult


RulesEngineC0Invoker = Callable[[PurchaseOperation, DecisionContext], CapabilityExecution]


def build_rules_engine_c0_invoker(
    *,
    assessments: Sequence[Assessment],
    base_result: ConsolidatedBaseResult,
) -> RulesEngineC0Invoker:
    """Build a stable C0 invoker for the controlled E2E execution boundary.

    Assessment values are deep-copied at construction time and again per
    invocation so caller mutation cannot alter the execution snapshot.
    """
    assessment_snapshot = tuple(item.model_copy(deep=True) for item in assessments)

    def invoke(
        purchase: PurchaseOperation,
        context: DecisionContext,
    ) -> CapabilityExecution:
        result = run_rules_engine(
            RulesEngineInput(
                purchase=purchase,
                context=context,
                assessments=tuple(
                    item.model_copy(deep=True) for item in assessment_snapshot
                ),
                base_result=base_result,
            )
        )
        return result.c0_capability

    return invoke


__all__ = ["RulesEngineC0Invoker", "build_rules_engine_c0_invoker"]
