"""Provenance-safe reuse of already-produced rule Assessments.

This module never evaluates business conditions. It verifies that an Assessment
and its Trace belong to the exact purchase/context in which they are reused,
then composes the already-produced material through C0/CRC/O1.
"""
from __future__ import annotations

from collections.abc import Callable, Sequence
from copy import deepcopy

from pydantic import BaseModel, ConfigDict

from eios.core.c0_reproducibility import build_trace
from eios.core.capability_adapters import adapt_c0
from eios.core.crc_mvp import CRCInput, resolve_crc
from eios.core.fingerprint import assessment_fingerprint, input_fingerprint
from eios.core.models import Assessment, DecisionContext, PurchaseOperation, Rule, Trace
from eios.core.orchestration import CapabilityExecution, build_support_package

from .catalog import authorized_rule, authorized_rule_metadata
from .runtime import ConsolidatedBaseResult, RuleSetVerticalResult


class AssessmentTraceBinding(BaseModel):
    """Immutable association of one Assessment with its original Trace."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    assessment: Assessment
    trace: Trace


ProvenancedRulesC0Invoker = Callable[[PurchaseOperation, DecisionContext], CapabilityExecution]


def _validate_purchase_context(
    purchase: PurchaseOperation,
    context: DecisionContext,
) -> None:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")


def _validate_provenance(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    assessment: Assessment,
    trace: Trace,
) -> None:
    """Fail closed unless Trace proves the complete Assessment provenance."""
    if rule.rule_id != assessment.rule_id:
        raise ValueError("Rule.rule_id incompatible con Assessment.rule_id")
    if rule.version != context.rules_version:
        raise ValueError("Rule.version incompatible con DecisionContext.rules_version")

    contextual = (
        ("decision_id", trace.decision_id, context.decision_id),
        ("scenario_id", trace.scenario_id, context.scenario_id),
        ("rules_version", trace.rules_version, context.rules_version),
        ("parameters_version", trace.parameters_version, context.parameters_version),
        ("data_snapshot_id", trace.data_snapshot_id, context.data_snapshot_id),
    )
    for field, actual, expected in contextual:
        if actual != expected:
            raise ValueError(f"Trace.{field} incompatible con DecisionContext")

    if trace.rule_id != assessment.rule_id:
        raise ValueError("Trace.rule_id incompatible con Assessment.rule_id")
    if trace.assessment_status != assessment.status:
        raise ValueError("Trace.assessment_status incompatible con Assessment.status")
    if trace.assessment_outcome != assessment.outcome:
        raise ValueError("Trace.assessment_outcome incompatible con Assessment.outcome")
    if trace.evidence_ids != tuple(assessment.evidence_ids):
        raise ValueError("Trace.evidence_ids incompatible con Assessment.evidence_ids")

    expected_input_hash = input_fingerprint(purchase)
    if trace.input_fingerprint != expected_input_hash:
        raise ValueError("Trace.input_fingerprint incompatible con PurchaseOperation")

    if trace.assessment_fingerprint is None:
        raise ValueError("Trace legacy sin assessment_fingerprint no es reutilizable")
    expected_assessment_hash = assessment_fingerprint(assessment)
    if trace.assessment_fingerprint != expected_assessment_hash:
        raise ValueError("Trace.assessment_fingerprint incompatible con Assessment")

    expected_trace = build_trace(
        context,
        purchase,
        rule,
        tuple(assessment.evidence_ids),
        assessment,
    )
    if trace.trace_id != expected_trace.trace_id:
        raise ValueError("Trace.trace_id no es reproducible para el material suministrado")


def validate_assessment_trace_binding(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    binding: AssessmentTraceBinding,
) -> AssessmentTraceBinding:
    """Validate and return a detached provenance-safe binding snapshot.

    This narrow public boundary performs no CRC/O1 composition and never
    evaluates a business rule. It exists so later integration layers can reuse
    the exact provenance checks without recreating or weakening them.
    """
    purchase_snapshot = purchase.model_copy(deep=True)
    context_snapshot = context.model_copy(deep=True)
    binding_snapshot = binding.model_copy(deep=True)

    _validate_purchase_context(purchase_snapshot, context_snapshot)
    rule = authorized_rule(
        binding_snapshot.assessment.rule_id,
        context_snapshot.rules_version,
    )
    _validate_provenance(
        purchase=purchase_snapshot,
        context=context_snapshot,
        rule=rule,
        assessment=binding_snapshot.assessment,
        trace=binding_snapshot.trace,
    )
    return binding_snapshot


def run_provenanced_assessments_vertical(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    bindings: Sequence[AssessmentTraceBinding],
    base_result: ConsolidatedBaseResult,
) -> RuleSetVerticalResult:
    """Compose already-produced Assessment+Trace bindings after provenance checks."""
    purchase_snapshot = purchase.model_copy(deep=True)
    context_snapshot = context.model_copy(deep=True)
    binding_snapshots = tuple(binding.model_copy(deep=True) for binding in bindings)

    _validate_purchase_context(purchase_snapshot, context_snapshot)

    rule_ids = tuple(binding.assessment.rule_id for binding in binding_snapshots)
    if len(rule_ids) != len(set(rule_ids)):
        raise ValueError("No se permiten rule_id duplicados en una ejecución vertical")

    assessments: list[Assessment] = []
    traces: list[Trace] = []
    metadata = {}

    for binding in binding_snapshots:
        assessment = binding.assessment.model_copy(deep=True)
        trace = binding.trace.model_copy(deep=True)
        rule = authorized_rule(assessment.rule_id, context_snapshot.rules_version)
        rule_metadata = authorized_rule_metadata(
            assessment.rule_id,
            context_snapshot.rules_version,
        )
        _validate_provenance(
            purchase=purchase_snapshot,
            context=context_snapshot,
            rule=rule,
            assessment=assessment,
            trace=trace,
        )
        assessments.append(assessment)
        traces.append(trace)
        metadata[rule.rule_id] = rule_metadata

    assessment_tuple = tuple(assessments)
    trace_tuple = tuple(traces)
    capability = adapt_c0(assessment_tuple, trace_tuple)
    crc_result = resolve_crc(
        CRCInput(
            assessments=list(assessment_tuple),
            decision_context=context_snapshot,
            base_result=base_result,
        ),
        metadata,
    )
    support_package = build_support_package(
        purchase_snapshot,
        context_snapshot,
        capability_results=(capability,),
    )

    return RuleSetVerticalResult(
        assessments=assessment_tuple,
        traces=trace_tuple,
        c0_capability=capability,
        crc_result=crc_result,
        support_package=support_package,
    )


def build_provenanced_rules_engine_c0_invoker(
    *,
    bindings: Sequence[AssessmentTraceBinding],
    base_result: ConsolidatedBaseResult,
) -> ProvenancedRulesC0Invoker:
    """Build an E2E C0 invoker that cannot relabel detached Assessments."""
    binding_snapshot = tuple(binding.model_copy(deep=True) for binding in bindings)

    def invoke(
        purchase: PurchaseOperation,
        context: DecisionContext,
    ) -> CapabilityExecution:
        result = run_provenanced_assessments_vertical(
            purchase=purchase.model_copy(deep=True),
            context=context.model_copy(deep=True),
            bindings=tuple(item.model_copy(deep=True) for item in binding_snapshot),
            base_result=base_result,
        )
        return result.c0_capability

    return invoke


__all__ = [
    "AssessmentTraceBinding",
    "ProvenancedRulesC0Invoker",
    "build_provenanced_rules_engine_c0_invoker",
    "run_provenanced_assessments_vertical",
    "validate_assessment_trace_binding",
]
