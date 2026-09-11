"""Executable vertical slice for the authorized R-ENT-001 rule.

This module composes already-closed EIOS contracts:
ENT factual analysis -> individual Assessment -> reproducible Trace -> C0
capability envelope -> isolated CRC contribution -> O1 support package.

It does not create a general rule registry, execute other rules, replace CRC,
or make a business decision.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from eios.core.c0_reproducibility import build_trace
from eios.core.capability_adapters import adapt_c0
from eios.core.crc_mvp import CRCInput, CRCResult, RuleMetadata, resolve_crc
from eios.core.models import Assessment, DecisionContext, Evidence, PurchaseOperation, Rule, Trace
from eios.core.orchestration import CapabilityExecution, DecisionSupportPackage, build_support_package
from eios.delivery import DeliveryStockoutAnalysisInput, DeliveryStockoutAnalysisResult, analyze_delivery_stockout

from .delivery import R_ENT_001, evaluate_r_ent_001


ConsolidatedBaseResult = Literal[
    "COMPRAR",
    "NEGOCIAR",
    "COMPRAR CONDICIONADO",
    "NO COMPRAR",
    "INFORMACIÓN INSUFICIENTE",
]


class REnt001VerticalResult(BaseModel):
    """Traceable output of the isolated R-ENT-001 vertical execution.

    ``crc_result`` is the contribution of this isolated rule to CRC under the
    caller-supplied base result.  It is not a final human purchasing decision.
    """

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
    # Authority fixed by Matriz_Reglas_MVP for R-ENT-001.
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
    """Execute the closed vertical slice for R-ENT-001.

    The function intentionally accepts explicit rule metadata and an explicit
    CRC base result.  It does not invent a global rule registry or a preceding
    business result.
    """

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
    trace = build_trace(
        context,
        purchase,
        rule,
        tuple(assessment.evidence_ids),
        assessment,
    )
    capability = adapt_c0((assessment,), (trace,))
    crc_result = resolve_crc(
        CRCInput(
            assessments=[assessment],
            decision_context=context,
            base_result=base_result,
        ),
        {R_ENT_001: rule_metadata},
    )
    support_package = build_support_package(
        purchase,
        context,
        capability_results=(capability,),
    )

    return REnt001VerticalResult(
        analysis=analysis,
        assessment=assessment,
        trace=trace,
        c0_capability=capability,
        crc_result=crc_result,
        support_package=support_package,
    )


__all__ = [
    "ConsolidatedBaseResult",
    "REnt001VerticalResult",
    "run_r_ent_001_vertical",
]
