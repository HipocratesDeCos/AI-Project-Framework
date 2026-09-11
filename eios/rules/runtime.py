"""Generic vertical runtime for already-produced individual rule Assessments.

The runtime composes closed EIOS contracts without evaluating the business rule
condition itself:
Assessment -> reproducible Trace -> C0 capability adapter -> CRC contribution
-> O1 support package.

Rule-specific modules remain responsible for producing a valid Assessment and
for enforcing their own normative metadata authority.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from eios.core.c0_reproducibility import build_trace
from eios.core.capability_adapters import adapt_c0
from eios.core.crc_mvp import CRCInput, CRCResult, RuleMetadata, resolve_crc
from eios.core.models import Assessment, DecisionContext, PurchaseOperation, Rule, Trace
from eios.core.orchestration import CapabilityExecution, DecisionSupportPackage, build_support_package


ConsolidatedBaseResult = Literal[
    "COMPRAR",
    "NEGOCIAR",
    "COMPRAR CONDICIONADO",
    "NO COMPRAR",
    "INFORMACIÓN INSUFICIENTE",
]


class RuleVerticalResult(BaseModel):
    """Reusable traceable output for one already-evaluated rule."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    assessment: Assessment
    trace: Trace
    c0_capability: CapabilityExecution
    crc_result: CRCResult
    support_package: DecisionSupportPackage


def _validate_vertical_identity(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    assessment: Assessment,
    metadata: RuleMetadata,
) -> None:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    if rule.version != context.rules_version:
        raise ValueError("Rule.version incompatible con DecisionContext.rules_version")
    if assessment.rule_id != rule.rule_id:
        raise ValueError("Assessment.rule_id debe coincidir con Rule.rule_id")
    if metadata.rule_id != rule.rule_id:
        raise ValueError("RuleMetadata.rule_id debe coincidir con Rule.rule_id")
    if metadata.version != rule.version:
        raise ValueError("RuleMetadata.version debe coincidir con Rule.version")


def run_assessment_vertical(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    assessment: Assessment,
    base_result: ConsolidatedBaseResult,
    rule_metadata: RuleMetadata,
) -> RuleVerticalResult:
    """Compose one individual Assessment through existing C0/CRC/O1 contracts.

    This function never calculates the rule condition and never creates rule
    metadata.  Both are supplied by the caller/rule-specific layer.
    """

    _validate_vertical_identity(purchase, context, rule, assessment, rule_metadata)

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
        {rule.rule_id: rule_metadata},
    )
    support_package = build_support_package(
        purchase,
        context,
        capability_results=(capability,),
    )

    return RuleVerticalResult(
        assessment=assessment,
        trace=trace,
        c0_capability=capability,
        crc_result=crc_result,
        support_package=support_package,
    )


__all__ = [
    "ConsolidatedBaseResult",
    "RuleVerticalResult",
    "run_assessment_vertical",
]
