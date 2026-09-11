"""Executable vertical slice for the authorized R-ENT-001 rule."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from eios.core.crc_mvp import CRCResult, RuleMetadata
from eios.core.models import Assessment, DecisionContext, Evidence, PurchaseOperation, Rule, Trace
from eios.core.orchestration import CapabilityExecution, DecisionSupportPackage
from eios.delivery import DeliveryStockoutAnalysisInput, DeliveryStockoutAnalysisResult, analyze_delivery_stockout

from .delivery import R_ENT_001, evaluate_r_ent_001
from .runtime import ConsolidatedBaseResult, run_assessment_vertical


class REnt001VerticalResult(BaseModel):
    """Traceable output of the isolated R-ENT-001 vertical execution."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    analysis: DeliveryStockoutAnalysisResult
    assessment: Assessment
    trace: Trace
    c0_capability: CapabilityExecution
    crc_result: CRCResult
    support_package: DecisionSupportPackage


def _validate_rule_metadata(rule: Rule, metadata: RuleMetadata) -> None:
    if metadata.rule_id != R_ENT_001 or metadata.rule_id != rule.rule_id:
        raise ValueError("RuleMetadata debe corresponder exactamente a R-ENT-001")
    if metadata.version != rule.version:
        raise ValueError("RuleMetadata.version debe coincidir con Rule.version")
    if metadata.effect != "R2" or metadata.severity != "ALTA":
        raise ValueError("R-ENT-001 requiere metadatos normativos R2 / ALTA")


def run_r_ent_001_vertical(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    analysis_input: DeliveryStockoutAnalysisInput,
    baseline_evidence: Evidence,
    delivery_evidence: Evidence,
    base_result: ConsolidatedBaseResult,
    rule_metadata: RuleMetadata,
) -> REnt001VerticalResult:
    """Execute ENT analysis and delegate the generic vertical rule pipeline."""

    _validate_rule_metadata(rule, rule_metadata)
    analysis = analyze_delivery_stockout(analysis_input)
    assessment = evaluate_r_ent_001(
        purchase,
        context,
        rule,
        analysis_input,
        analysis,
        baseline_evidence,
        delivery_evidence,
    )
    vertical = run_assessment_vertical(
        purchase=purchase,
        context=context,
        rule=rule,
        assessment=assessment,
        base_result=base_result,
        rule_metadata=rule_metadata,
    )
    return REnt001VerticalResult(
        analysis=analysis,
        assessment=vertical.assessment,
        trace=vertical.trace,
        c0_capability=vertical.c0_capability,
        crc_result=vertical.crc_result,
        support_package=vertical.support_package,
    )


__all__ = [
    "ConsolidatedBaseResult",
    "REnt001VerticalResult",
    "run_r_ent_001_vertical",
]
