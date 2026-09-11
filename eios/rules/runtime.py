"""Reusable vertical runtime for already-produced EIOS rule Assessments.

The runtime composes closed contracts without calculating business conditions:
Assessment(s) -> reproducible Trace(s) -> C0 capability adapter -> CRC -> O1
support package.

Rule-specific modules remain responsible for producing valid Assessments and
for supplying authorized RuleMetadata.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Sequence

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


@dataclass(frozen=True)
class RuleAssessmentBinding:
    """Explicit ordered binding between one rule, its Assessment and metadata."""

    rule: Rule
    assessment: Assessment
    metadata: RuleMetadata


class RuleSetVerticalResult(BaseModel):
    """Traceable vertical output for an ordered set of individual rules."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    assessments: tuple[Assessment, ...]
    traces: tuple[Trace, ...]
    c0_capability: CapabilityExecution
    crc_result: CRCResult
    support_package: DecisionSupportPackage


class RuleVerticalResult(BaseModel):
    """Compatibility view for one individual rule execution."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    assessment: Assessment
    trace: Trace
    c0_capability: CapabilityExecution
    crc_result: CRCResult
    support_package: DecisionSupportPackage


def _validate_purchase_context(purchase: PurchaseOperation, context: DecisionContext) -> None:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")


def _validate_binding(
    context: DecisionContext,
    binding: RuleAssessmentBinding,
) -> None:
    rule = binding.rule
    assessment = binding.assessment
    metadata = binding.metadata
    if rule.version != context.rules_version:
        raise ValueError("Rule.version incompatible con DecisionContext.rules_version")
    if assessment.rule_id != rule.rule_id:
        raise ValueError("Assessment.rule_id debe coincidir con Rule.rule_id")
    if metadata.rule_id != rule.rule_id:
        raise ValueError("RuleMetadata.rule_id debe coincidir con Rule.rule_id")
    if metadata.version != rule.version:
        raise ValueError("RuleMetadata.version debe coincidir con Rule.version")


def run_assessment_set_vertical(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    bindings: Sequence[RuleAssessmentBinding],
    base_result: ConsolidatedBaseResult,
) -> RuleSetVerticalResult:
    """Compose an ordered set of individual Assessments through C0/CRC/O1.

    Binding order is preserved in traces and CRC input. Duplicate rule IDs are
    rejected so one rule cannot silently contribute more than once.
    """

    _validate_purchase_context(purchase, context)
    binding_tuple = tuple(bindings)
    rule_ids = tuple(binding.rule.rule_id for binding in binding_tuple)
    if len(rule_ids) != len(set(rule_ids)):
        raise ValueError("No se permiten rule_id duplicados en una ejecución vertical")

    for binding in binding_tuple:
        _validate_binding(context, binding)

    assessments = tuple(binding.assessment for binding in binding_tuple)
    traces = tuple(
        build_trace(
            context,
            purchase,
            binding.rule,
            tuple(binding.assessment.evidence_ids),
            binding.assessment,
        )
        for binding in binding_tuple
    )
    metadata = {binding.rule.rule_id: binding.metadata for binding in binding_tuple}

    capability = adapt_c0(assessments, traces)
    crc_result = resolve_crc(
        CRCInput(
            assessments=list(assessments),
            decision_context=context,
            base_result=base_result,
        ),
        metadata,
    )
    support_package = build_support_package(
        purchase,
        context,
        capability_results=(capability,),
    )

    return RuleSetVerticalResult(
        assessments=assessments,
        traces=traces,
        c0_capability=capability,
        crc_result=crc_result,
        support_package=support_package,
    )


def run_assessment_vertical(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    assessment: Assessment,
    base_result: ConsolidatedBaseResult,
    rule_metadata: RuleMetadata,
) -> RuleVerticalResult:
    """Compose one Assessment using the generic set runtime."""

    result = run_assessment_set_vertical(
        purchase=purchase,
        context=context,
        bindings=(
            RuleAssessmentBinding(
                rule=rule,
                assessment=assessment,
                metadata=rule_metadata,
            ),
        ),
        base_result=base_result,
    )
    return RuleVerticalResult(
        assessment=result.assessments[0],
        trace=result.traces[0],
        c0_capability=result.c0_capability,
        crc_result=result.crc_result,
        support_package=result.support_package,
    )


__all__ = [
    "ConsolidatedBaseResult",
    "RuleAssessmentBinding",
    "RuleSetVerticalResult",
    "RuleVerticalResult",
    "run_assessment_set_vertical",
    "run_assessment_vertical",
]
