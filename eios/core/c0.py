"""C0 application flow for the EIOS procurement MVP.

Flow:
Input Contract -> DecisionContext -> Evidence -> Evidence Validation
-> Rule -> Assessment -> Trace.

The module contains no persistence, API, LLM, SQL Server, negotiation,
scenario engine, CRC or decision automation.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from uuid import NAMESPACE_URL, uuid5

from .models import (
    Assessment,
    DecisionContext,
    Evidence,
    InputContract,
    Rule,
    Trace,
)
from .validation import validate_evidence

RulePredicate = Callable[[InputContract, tuple[Evidence, ...]], bool]


def _trace_id(
    context: DecisionContext,
    rule: Rule,
    evidence_ids: tuple[str, ...],
    status: str,
    outcome: str | None,
) -> str:
    """Create a deterministic trace identifier for the same evaluation inputs."""
    material = "|".join(
        (
            context.decision_id,
            context.scenario_id,
            context.rules_version,
            context.parameters_version,
            context.data_snapshot_id,
            rule.rule_id,
            rule.version,
            ",".join(evidence_ids),
            status,
            outcome or "NONE",
        )
    )
    return str(uuid5(NAMESPACE_URL, f"eios:c0:{material}"))


def evaluate_rule(
    input_contract: InputContract,
    context: DecisionContext,
    evidence: Iterable[Evidence],
    rule: Rule,
    predicate: RulePredicate,
) -> tuple[Assessment, Trace]:
    """Evaluate one rule under the C0 evidence invariant."""
    if input_contract.decision_id != context.decision_id:
        raise ValueError("Input Contract y DecisionContext tienen decision_id distintos")
    if input_contract.scenario_id != context.scenario_id:
        raise ValueError("Input Contract y DecisionContext tienen scenario_id distintos")
    if rule.version != context.rules_version:
        raise ValueError("La versión de la regla no coincide con DecisionContext.rules_version")

    evidence_tuple = tuple(evidence)
    validations = tuple(validate_evidence(item) for item in evidence_tuple)
    valid_evidence = tuple(
        item for item, validation in zip(evidence_tuple, validations, strict=True)
        if validation.status == "VALID"
    )
    evidence_ids = tuple(item.evidence_id for item in valid_evidence)

    if rule.requires_evidence and not valid_evidence:
        assessment = Assessment(
            rule_id=rule.rule_id,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=tuple(item.evidence_id for item in evidence_tuple),
            reason="La regla requiere evidencia DEMONSTRATED válida",
        )
        trace = Trace(
            trace_id=_trace_id(context, rule, evidence_ids, assessment.status, assessment.outcome),
            decision_id=context.decision_id,
            scenario_id=context.scenario_id,
            rule_id=rule.rule_id,
            assessment_status=assessment.status,
            assessment_outcome=assessment.outcome,
            evidence_ids=tuple(item.evidence_id for item in evidence_tuple),
        )
        return assessment, trace

    outcome = bool(predicate(input_contract, valid_evidence))
    assessment = Assessment(
        rule_id=rule.rule_id,
        status="EVALUABLE",
        outcome="TRUE" if outcome else "FALSE",
        evidence_ids=evidence_ids,
        reason="Regla evaluada con evidencia suficiente" if valid_evidence else "Regla evaluada sin requisito de evidencia",
    )
    trace = Trace(
        trace_id=_trace_id(context, rule, evidence_ids, assessment.status, assessment.outcome),
        decision_id=context.decision_id,
        scenario_id=context.scenario_id,
        rule_id=rule.rule_id,
        assessment_status=assessment.status,
        assessment_outcome=assessment.outcome,
        evidence_ids=evidence_ids,
    )
    return assessment, trace


def run_c0(
    input_contract: InputContract,
    context: DecisionContext,
    evidence: Iterable[Evidence],
    rules: Iterable[tuple[Rule, RulePredicate]],
) -> tuple[tuple[Assessment, ...], tuple[Trace, ...]]:
    """Run the complete C0 flow for one input and a set of rules."""
    evidence_tuple = tuple(evidence)
    assessments: list[Assessment] = []
    traces: list[Trace] = []

    for rule, predicate in rules:
        assessment, trace = evaluate_rule(
            input_contract=input_contract,
            context=context,
            evidence=evidence_tuple,
            rule=rule,
            predicate=predicate,
        )
        assessments.append(assessment)
        traces.append(trace)

    return tuple(assessments), tuple(traces)


__all__ = ["RulePredicate", "evaluate_rule", "run_c0"]
