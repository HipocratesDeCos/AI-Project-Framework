"""Reproducibility helpers for the C0 trace contract."""
from __future__ import annotations

from uuid import NAMESPACE_URL, uuid5

from .fingerprint import assessment_fingerprint, input_fingerprint
from .models import Assessment, DecisionContext, InputContract, Rule, Trace


def build_trace(
    context: DecisionContext,
    input_contract: InputContract,
    rule: Rule,
    evidence_ids: tuple[str, ...],
    assessment: Assessment,
) -> Trace:
    """Build a deterministic C0 Trace bound to the complete Assessment payload."""
    input_hash = input_fingerprint(input_contract)
    assessment_hash = assessment_fingerprint(assessment)
    material = "|".join(
        (
            context.decision_id,
            context.scenario_id,
            context.rules_version,
            context.parameters_version,
            context.data_snapshot_id,
            input_hash,
            rule.rule_id,
            rule.version,
            ",".join(evidence_ids),
            assessment.status,
            assessment.outcome or "NONE",
            assessment_hash,
        )
    )
    return Trace(
        trace_id=str(uuid5(NAMESPACE_URL, f"eios:c0:{material}")),
        decision_id=context.decision_id,
        scenario_id=context.scenario_id,
        rules_version=context.rules_version,
        parameters_version=context.parameters_version,
        data_snapshot_id=context.data_snapshot_id,
        input_fingerprint=input_hash,
        assessment_fingerprint=assessment_hash,
        rule_id=rule.rule_id,
        assessment_status=assessment.status,
        assessment_outcome=assessment.outcome,
        evidence_ids=evidence_ids,
    )


__all__ = ["build_trace"]
