"""Standard controlled execution service for the EIOS Vertical MVP.

This module assembles already-authorized capability outcomes/invokers into the
closed E2E execution boundary. It does not calculate business results, create a
decision, or add capability authority.
"""
from __future__ import annotations

from collections.abc import Callable

from .execution_boundary import ExecutionOutcome, ExecutionPlan, execute_plan
from .models import DecisionContext, PurchaseOperation
from .orchestration import CapabilityExecution


CapabilityInvoker = Callable[[PurchaseOperation, DecisionContext], CapabilityExecution]

MVP_CAPABILITY_ORDER = (
    "QTG",
    "PRICE",
    "TCO",
    "C0",
    "DECISION_TWIN",
    "SCENARIO_COORDINATION",
    "NEGOTIATION_INTELLIGENCE",
    "NEGOTIATION_LADDER",
)


def run_mvp_execution(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    policy_version: str,
    price_invoker: CapabilityInvoker | None = None,
    tco_invoker: CapabilityInvoker | None = None,
    rules_invoker: CapabilityInvoker | None = None,
    decision_twin_invoker: CapabilityInvoker | None = None,
    scenario_coordination_invoker: CapabilityInvoker | None = None,
    negotiation_intelligence_invoker: CapabilityInvoker | None = None,
    negotiation_ladder_invoker: CapabilityInvoker | None = None,
) -> ExecutionOutcome:
    """Execute supplied MVP capabilities through the controlled boundary.

    PRICE, TCO, Decision Twin, Scenario Coordination, Negotiation Intelligence
    and Negotiation Ladder must arrive through explicit provenance-safe
    invokers; this service never re-labels detached raw results for those
    capabilities into the current context. QTG remains in the canonical
    architecture order but is deliberately not accepted by this generic
    boundary until a provenance-safe producer from the authorized Decision
    Input Package exists.
    """
    invokers: dict[str, CapabilityInvoker] = {}

    if price_invoker is not None:
        invokers["PRICE"] = price_invoker
    if tco_invoker is not None:
        invokers["TCO"] = tco_invoker
    if rules_invoker is not None:
        invokers["C0"] = rules_invoker
    if decision_twin_invoker is not None:
        invokers["DECISION_TWIN"] = decision_twin_invoker
    if scenario_coordination_invoker is not None:
        invokers["SCENARIO_COORDINATION"] = scenario_coordination_invoker
    if negotiation_intelligence_invoker is not None:
        invokers["NEGOTIATION_INTELLIGENCE"] = negotiation_intelligence_invoker
    if negotiation_ladder_invoker is not None:
        invokers["NEGOTIATION_LADDER"] = negotiation_ladder_invoker

    if not invokers:
        raise ValueError("run_mvp_execution requiere al menos una capacidad")

    capabilities = tuple(
        capability for capability in MVP_CAPABILITY_ORDER if capability in invokers
    )
    plan = ExecutionPlan(
        capabilities=capabilities,
        policy_version=policy_version,
    )
    return execute_plan(
        purchase,
        context,
        plan,
        invokers,
    )


__all__ = [
    "CapabilityInvoker",
    "MVP_CAPABILITY_ORDER",
    "run_mvp_execution",
]
