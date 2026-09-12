"""Standard controlled execution service for the EIOS Vertical MVP.

This module assembles already-authorized capability outcomes/invokers into the
closed E2E execution boundary. It does not calculate business results, create a
decision, or add capability authority.
"""
from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from typing import Any

from eios.pricing.models import PriceIntelligenceResult
from eios.quality.gate import QualityTrustResult
from eios.tco.models import TCOResult

from .capability_adapters import (
    adapt_ni,
    adapt_nl,
    adapt_price,
    adapt_qtg,
    adapt_tco,
    adapt_twin,
)
from .decision_twin import DecisionTwinComparison
from .execution_boundary import ExecutionOutcome, ExecutionPlan, execute_plan
from .models import DecisionContext, PurchaseOperation
from .negotiation_intelligence import NegotiationIntelligenceResult
from .negotiation_ladder import NegotiationLadderResult
from .o2 import O2SupportPackage
from .orchestration import CapabilityExecution
from .scenario_coordination_adapter import (
    adapt_scenario_coordination,
    validate_scenario_coordination_context,
)


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


def _snapshot_invoker(result: Any, adapter: Callable[[Any], CapabilityExecution]) -> CapabilityInvoker:
    snapshot = deepcopy(result)

    def invoke(_: PurchaseOperation, __: DecisionContext) -> CapabilityExecution:
        return adapter(deepcopy(snapshot))

    return invoke


def run_mvp_execution(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    policy_version: str,
    rules_invoker: CapabilityInvoker | None = None,
    price_result: PriceIntelligenceResult | None = None,
    tco_result: TCOResult | None = None,
    quality_result: QualityTrustResult | None = None,
    decision_twin_result: DecisionTwinComparison | None = None,
    scenario_coordination_result: O2SupportPackage | None = None,
    negotiation_intelligence_result: NegotiationIntelligenceResult | None = None,
    negotiation_ladder_result: NegotiationLadderResult | None = None,
) -> ExecutionOutcome:
    """Execute the supplied MVP capabilities through the controlled boundary.

    Result objects are snapshotted when the execution catalog is built. The C0
    invoker is expected to be a stable authorized invoker such as
    ``build_domain_rules_c0_invoker``.
    """
    invokers: dict[str, CapabilityInvoker] = {}

    if quality_result is not None:
        invokers["QTG"] = _snapshot_invoker(quality_result, adapt_qtg)
    if price_result is not None:
        invokers["PRICE"] = _snapshot_invoker(price_result, adapt_price)
    if tco_result is not None:
        invokers["TCO"] = _snapshot_invoker(tco_result, adapt_tco)
    if rules_invoker is not None:
        invokers["C0"] = rules_invoker
    if decision_twin_result is not None:
        invokers["DECISION_TWIN"] = _snapshot_invoker(
            decision_twin_result, adapt_twin
        )
    if scenario_coordination_result is not None:
        validate_scenario_coordination_context(scenario_coordination_result, context)
        invokers["SCENARIO_COORDINATION"] = _snapshot_invoker(
            scenario_coordination_result, adapt_scenario_coordination
        )
    if negotiation_intelligence_result is not None:
        invokers["NEGOTIATION_INTELLIGENCE"] = _snapshot_invoker(
            negotiation_intelligence_result, adapt_ni
        )
    if negotiation_ladder_result is not None:
        invokers["NEGOTIATION_LADDER"] = _snapshot_invoker(
            negotiation_ladder_result, adapt_nl
        )

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
