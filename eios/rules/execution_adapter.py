"""Adapters from Rules execution to the controlled E2E C0 capability."""
from __future__ import annotations

from collections.abc import Callable, Sequence
from copy import deepcopy

from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.orchestration import CapabilityExecution

from .orchestrator import (
    DeliveryRuleInputs,
    FinanceCapacityRuleInputs,
    FinanceSafetyMarginRuleInputs,
    HistorySufficiencyRuleInputs,
    StockAbsorptionRuleInputs,
    StockExcessRuleInputs,
    run_domain_rules,
)
from .provenance import (
    AssessmentTraceBinding,
    build_provenanced_rules_engine_c0_invoker,
)
from .runtime import ConsolidatedBaseResult


RulesEngineC0Invoker = Callable[[PurchaseOperation, DecisionContext], CapabilityExecution]
DomainRulesC0Invoker = Callable[[PurchaseOperation, DecisionContext], CapabilityExecution]


def build_rules_engine_c0_invoker(
    *,
    bindings: Sequence[AssessmentTraceBinding],
    base_result: ConsolidatedBaseResult,
) -> RulesEngineC0Invoker:
    """Build the generic E2E C0 invoker from provenance-safe bindings only."""
    return build_provenanced_rules_engine_c0_invoker(
        bindings=tuple(binding.model_copy(deep=True) for binding in bindings),
        base_result=base_result,
    )


def build_domain_rules_c0_invoker(
    *,
    base_result: ConsolidatedBaseResult,
    delivery: DeliveryRuleInputs | None = None,
    stock_excess: StockExcessRuleInputs | None = None,
    stock_absorption: StockAbsorptionRuleInputs | None = None,
    finance_capacity: FinanceCapacityRuleInputs | None = None,
    finance_safety_margin: FinanceSafetyMarginRuleInputs | None = None,
    history_sufficiency: HistorySufficiencyRuleInputs | None = None,
) -> DomainRulesC0Invoker:
    """Build an E2E C0 invoker that evaluates supplied domain-rule bundles.

    Domain bundles are snapshotted at construction and copied per invocation so
    later caller mutation cannot change the controlled execution input.
    """
    snapshot = deepcopy(
        {
            "delivery": delivery,
            "stock_excess": stock_excess,
            "stock_absorption": stock_absorption,
            "finance_capacity": finance_capacity,
            "finance_safety_margin": finance_safety_margin,
            "history_sufficiency": history_sufficiency,
        }
    )

    def invoke(
        purchase: PurchaseOperation,
        context: DecisionContext,
    ) -> CapabilityExecution:
        result = run_domain_rules(
            purchase=purchase,
            context=context,
            base_result=base_result,
            **deepcopy(snapshot),
        )
        return result.c0_capability

    return invoke


__all__ = [
    "DomainRulesC0Invoker",
    "RulesEngineC0Invoker",
    "build_domain_rules_c0_invoker",
    "build_rules_engine_c0_invoker",
]
