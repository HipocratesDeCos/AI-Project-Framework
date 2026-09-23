"""Authorized provenance-safe executable bridge for R-ROT-002."""
from __future__ import annotations

from eios.core.models import Assessment, DecisionContext, Evidence, PurchaseOperation, Rule
from eios.core.validation import validate_evidence
from eios.rotation import (
    ROT002_MVP_EXCEPTION_TYPES,
    RotationExceptionEvidence,
    SalesActivityWindowEvidence,
)


R_ROT_002 = "R-ROT-002"


def _validate_identity(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    sales_activity: SalesActivityWindowEvidence,
    exceptions: RotationExceptionEvidence,
) -> None:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    if rule.rule_id != R_ROT_002:
        raise ValueError("El bridge solo evalúa R-ROT-002")
    if rule.version != context.rules_version:
        raise ValueError("Rule.version incompatible con DecisionContext.rules_version")
    if not rule.requires_evidence:
        raise ValueError("R-ROT-002 requiere evidencia")
    if sales_activity.article_id != purchase.article_id:
        raise ValueError("SalesActivityWindowEvidence article_id incompatible")
    if sales_activity.evaluation_date != purchase.operation_date:
        raise ValueError("SalesActivityWindowEvidence evaluation_date incompatible")
    if exceptions.article_id != purchase.article_id:
        raise ValueError("RotationExceptionEvidence article_id incompatible")
    if exceptions.evaluation_date != purchase.operation_date:
        raise ValueError("RotationExceptionEvidence evaluation_date incompatible")


def _evidence_map(evidences: tuple[Evidence, ...]) -> dict[str, Evidence]:
    ids = tuple(item.evidence_id for item in evidences)
    if len(ids) != len(set(ids)):
        raise ValueError("rotation evidences contiene evidence_id duplicados")
    return {item.evidence_id: item for item in evidences}


def _is_demonstrated(evidence: Evidence | None) -> bool:
    return (
        evidence is not None
        and evidence.state == "DEMONSTRATED"
        and validate_evidence(evidence).status == "VALID"
    )


def _refs_are_demonstrated(
    refs: tuple[str, ...],
    evidence_by_id: dict[str, Evidence],
) -> bool:
    return bool(refs) and all(_is_demonstrated(evidence_by_id.get(ref)) for ref in refs)


def _exception_state(
    exceptions: RotationExceptionEvidence,
    evidence_by_id: dict[str, Evidence],
) -> str:
    determinations = {item.exception_type: item for item in exceptions.determinations}

    # Existential positive proof: one demonstrated exception is sufficient.
    for item in exceptions.determinations:
        if item.state == "PRESENT" and _refs_are_demonstrated(
            item.evidence_refs, evidence_by_id
        ):
            return "EXCEPTION_PRESENT"

    # Any unresolved or conflicting determination prevents a negative proof.
    if any(
        item.state in {"NOT_DETERMINABLE", "CONFLICTING"}
        for item in exceptions.determinations
    ):
        return "NOT_EVALUABLE"

    if set(determinations) != set(ROT002_MVP_EXCEPTION_TYPES):
        return "NOT_EVALUABLE"

    if any(item.state != "NOT_PRESENT" for item in determinations.values()):
        return "NOT_EVALUABLE"

    if not all(
        _refs_are_demonstrated(item.evidence_refs, evidence_by_id)
        for item in determinations.values()
    ):
        return "NOT_EVALUABLE"

    scope_demonstrated = any(
        _is_demonstrated(item)
        and item.demonstration_ref == exceptions.exception_scope_ref
        for item in evidence_by_id.values()
    )
    if not scope_demonstrated:
        return "NOT_EVALUABLE"
    return "NO_EXCEPTION_DEMONSTRATED"


def evaluate_r_rot_002(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    sales_activity: SalesActivityWindowEvidence,
    exceptions: RotationExceptionEvidence,
    evidences: tuple[Evidence, ...],
) -> Assessment:
    """Evaluate R-ROT-002 while preserving the authorized exception semantics."""

    _validate_identity(purchase, context, rule, sales_activity, exceptions)
    evidence_by_id = _evidence_map(evidences)

    activity_refs = tuple(dict.fromkeys(sales_activity.evidence_refs))
    if not activity_refs or not all(
        _is_demonstrated(evidence_by_id.get(evidence_id))
        for evidence_id in activity_refs
    ):
        return Assessment(
            rule_id=R_ROT_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=list(activity_refs),
            reason="R-ROT-002 no evaluable: evidencia de actividad de ventas insuficiente.",
        )

    exception_status = _exception_state(exceptions, evidence_by_id)
    evidence_ids = list(
        dict.fromkeys(
            (
                *activity_refs,
                *exceptions.evidence_refs,
                *(
                    ref
                    for item in exceptions.determinations
                    for ref in item.evidence_refs
                ),
            )
        )
    )

    if sales_activity.activity_state == "SALES_ACTIVITY_PRESENT":
        return Assessment(
            rule_id=R_ROT_002,
            status="EVALUABLE",
            outcome="FALSE",
            evidence_ids=evidence_ids,
            reason="R-ROT-002 no demostrada: existe actividad de ventas válida en la ventana.",
        )

    if sales_activity.activity_state in {
        "NOT_EVIDENCED",
        "CONFLICTING_DATA",
        "NOT_DETERMINABLE",
    }:
        return Assessment(
            rule_id=R_ROT_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-ROT-002 no evaluable: actividad de ventas no concluyente.",
        )

    if exception_status == "EXCEPTION_PRESENT":
        return Assessment(
            rule_id=R_ROT_002,
            status="EVALUABLE",
            outcome="FALSE",
            evidence_ids=evidence_ids,
            reason="R-ROT-002 exceptuada: ausencia de ventas demostrada pero existe excepción MVP.",
        )

    if exception_status != "NO_EXCEPTION_DEMONSTRATED":
        return Assessment(
            rule_id=R_ROT_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-ROT-002 no evaluable: ausencia de excepción no demostrada.",
        )

    return Assessment(
        rule_id=R_ROT_002,
        status="EVALUABLE",
        outcome="TRUE",
        evidence_ids=evidence_ids,
        reason="R-ROT-002 demostrada: cero ventas válidas y ausencia de excepción MVP demostradas.",
    )


__all__ = ["R_ROT_002", "evaluate_r_rot_002"]
