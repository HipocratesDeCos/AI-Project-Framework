"""Canonical public execution facade for the EIOS Rules Engine v0.1.

The facade does not evaluate business conditions. Rule-specific bridges produce
Assessment objects; this boundary validates execution identity and delegates
catalog binding, Trace generation, CRC consolidation and O1 packaging to the
authorized rules runtime.
"""
from __future__ import annotations

from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, model_validator

from eios.core.models import Assessment, DecisionContext, PurchaseOperation

from .runtime import (
    ConsolidatedBaseResult,
    RuleSetVerticalResult,
    run_authorized_assessments_vertical,
)


class RulesEngineInput(BaseModel):
    """Public input boundary for already-produced individual rule Assessments."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    purchase: PurchaseOperation
    context: DecisionContext
    assessments: tuple[Assessment, ...] = ()
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
    """Execute the authorized rules runtime through one stable public boundary."""
    return run_authorized_assessments_vertical(
        purchase=payload.purchase,
        context=payload.context,
        assessments=payload.assessments,
        base_result=payload.base_result,
    )


__all__ = ["RulesEngineInput", "RulesEngineResult", "run_rules_engine"]
