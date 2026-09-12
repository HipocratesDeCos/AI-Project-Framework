"""Canonical public execution facade for the EIOS Rules Engine v0.2.

The public boundary accepts only already-produced Assessment+Trace bindings
whose provenance can be verified against the exact purchase and execution
context. Business conditions remain owned by rule-specific bridges.
"""
from __future__ import annotations

from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, model_validator

from eios.core.models import DecisionContext, PurchaseOperation

from .provenance import AssessmentTraceBinding, run_provenanced_assessments_vertical
from .runtime import ConsolidatedBaseResult, RuleSetVerticalResult


class RulesEngineInput(BaseModel):
    """Public provenance-safe boundary for already-produced rule results."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    purchase: PurchaseOperation
    context: DecisionContext
    bindings: tuple[AssessmentTraceBinding, ...] = ()
    base_result: ConsolidatedBaseResult

    @model_validator(mode="after")
    def validate_identity(self) -> "RulesEngineInput":
        if self.purchase.decision_id != self.context.decision_id:
            raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
        if self.purchase.scenario_id != self.context.scenario_id:
            raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
        return self


RulesEngineResult: TypeAlias = RuleSetVerticalResult


def run_rules_engine(payload: RulesEngineInput) -> RulesEngineResult:
    """Execute the public Rules Engine only after complete provenance checks."""
    return run_provenanced_assessments_vertical(
        purchase=payload.purchase,
        context=payload.context,
        bindings=payload.bindings,
        base_result=payload.base_result,
    )


__all__ = ["RulesEngineInput", "RulesEngineResult", "run_rules_engine"]
