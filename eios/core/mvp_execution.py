"""Standard controlled execution service for the EIOS Vertical MVP.

This module assembles already-authorized capability outcomes/invokers into the
closed E2E execution boundary. It does not calculate business results, create a
decision, or add capability authority.
"""
from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from typing import Any

from .capability_adapters import (
    adapt_ni,
    adapt_nl,
)
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


def _validate_negotiation_intelligence_context(
    result: NegotiationIntelligenceResult,
    context: DecisionContext,
) -> None:
    refs = result.context_references
    mismatches: list[str] = []

    if refs.decision_id != context.decision_id:
        mismatches.append("decision_id")

    for field in (
        "scenario_id",
        "rules_version",
        "parameters_version",
        "data_snapshot_id",
    ):
        value = getattr(refs, field)
        if value is not None and value != getattr(context, field):
            mismatches.append(field)

    if mismatches:
        raise ValueError(
            "NegotiationIntelligenceResult no coincide con DecisionContext: "
            + ", ".join(mismatches)
        )


def _validate_negotiation_ladder_context(
    result: NegotiationLadderResult,
    context: DecisionContext,
    negotiation_intelligence_result: NegotiationIntelligenceResult | None,
) -> None:
    refs = result.context_references
    mismatches: list[str] = []

    if refs.decision_id != context.decision_id:
        mismatches.append("decision_id")
    if refs.scenario_id is not None and refs.scenario_id != context.scenario_id:
        mismatches.append("scenario_id")
    if (
        negotiation_intelligence_result is not None
        and refs.negotiation_result_id
        != negotiation_intelligence_result.negotiation_result_id
    ):
        mismatches.append("negotiation_result_id")

    if mismatches:
        raise ValueError(
            "NegotiationLadderResult no coincide con su contexto autorizado: "
            + ", ".join(mismatches)
        )


def run_mvp_execution(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    policy_version: str,
    quality_invoker: CapabilityInvoker | None = None,
    price_invoker: CapabilityInvoker | None = None,
    tco_invoker: CapabilityInvoker | None = None,
    rules_invoker: CapabilityInvoker | None = None,
    decision_twin_invoker: CapabilityInvoker | None = None,
    scenario_coordination_result: O2SupportPackage | None = None,
    negotiation_intelligence_result: NegotiationIntelligenceResult | None = None,
    negotiation_ladder_result: NegotiationLadderResult | None = None,
) -> ExecutionOutcome:
    """Execute supplied MVP capabilities through the controlled boundary.

    QTG, PRICE, TCO and Decision Twin outputs must arrive through explicit
    invokers; this service never re-labels detached raw results into the current
    context. Remaining context-verifiable result objects are validated and
    snapshotted when the execution catalog is built.
    """
    invokers: dict[str, CapabilityInvoker] = {}

    if quality_invoker is not None:
        invokers["QTG"] = quality_invoker
    if price_invoker is not None:
        invokers["PRICE"] = price_invoker
    if tco_invoker is not None:
        invokers["TCO"] = tco_invoker
    if rules_invoker is not None:
        invokers["C0"] = rules_invoker
    if decision_twin_invoker is not None:
        invokers["DECISION_TWIN"] = decision_twin_invoker
    if scenario_coordination_result is not None:
        validate_scenario_coordination_context(scenario_coordination_result, context)
        invokers["SCENARIO_COORDINATION"] = _snapshot_invoker(
            scenario_coordination_result, adapt_scenario_coordination
        )
    if negotiation_intelligence_result is not None:
        _validate_negotiation_intelligence_context(
            negotiation_intelligence_result, context
        )
        invokers["NEGOTIATION_INTELLIGENCE"] = _snapshot_invoker(
            negotiation_intelligence_result, adapt_ni
        )
    if negotiation_ladder_result is not None:
        _validate_negotiation_ladder_context(
            negotiation_ladder_result,
            context,
            negotiation_intelligence_result,
        )
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
