"""Provenance-safe Commercial rules COM001/COM002."""
from __future__ import annotations

from decimal import Decimal

from eios.core.models import Assessment, DecisionContext, Evidence, PurchaseOperation, Rule
from eios.core.validation import validate_evidence

from .models import DiscountOpportunityEvidence, RappelApplicabilityEvidence, RappelEffectiveCostEvidence


R_COM_001 = "R-COM-001"
R_COM_002 = "R-COM-002"


def _evidence_map(evidences: tuple[Evidence, ...]) -> dict[str, Evidence]:
    ids = tuple(item.evidence_id for item in evidences)
    if len(ids) != len(set(ids)):
        raise ValueError("commercial evidences contiene evidence_id duplicados")
    return {item.evidence_id: item for item in evidences}


def _demonstrates_ref(evidences: tuple[Evidence, ...], ref: str) -> tuple[str, ...]:
    return tuple(
        item.evidence_id
        for item in evidences
        if item.state == "DEMONSTRATED"
        and item.demonstration_ref == ref
        and validate_evidence(item).status == "VALID"
    )


def _validate_rule_identity(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    expected_rule_id: str,
) -> None:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    if rule.rule_id != expected_rule_id:
        raise ValueError(f"rule_id debe ser {expected_rule_id}")
    if rule.version != context.rules_version:
        raise ValueError("Rule.version incompatible con DecisionContext.rules_version")
    if not rule.requires_evidence:
        raise ValueError("Commercial rules requieren evidencia")


def evaluate_r_com_001(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    discount: DiscountOpportunityEvidence,
    evidences: tuple[Evidence, ...],
) -> Assessment:
    _validate_rule_identity(purchase, context, rule, R_COM_001)
    if (
        discount.article_id != purchase.article_id
        or discount.supplier_id != purchase.supplier_id
        or discount.evaluation_date != purchase.operation_date
    ):
        raise ValueError("DiscountOpportunityEvidence incompatible con PurchaseOperation")

    by_id = _evidence_map(evidences)
    if any(ref not in by_id or by_id[ref].state != "DEMONSTRATED" for ref in discount.evidence_refs):
        return Assessment(
            rule_id=R_COM_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=list(discount.evidence_refs),
            reason="R-COM-001 no evaluable: evidence_refs no demostradas.",
        )

    opportunity_ids = _demonstrates_ref(evidences, discount.opportunity_ref)
    applicability_ids = _demonstrates_ref(evidences, discount.applicability_ref)
    evidence_ids = list(dict.fromkeys((*discount.evidence_refs, *opportunity_ids, *applicability_ids)))

    if discount.opportunity_state == "AVAILABLE" and discount.applicability_state == "CONFIRMED":
        if not opportunity_ids or not applicability_ids:
            return Assessment(
                rule_id=R_COM_001,
                status="NOT_EVALUABLE",
                outcome=None,
                evidence_ids=evidence_ids,
                reason="R-COM-001 no evaluable: oportunidad o aplicabilidad no demostrada.",
            )
        return Assessment(
            rule_id=R_COM_001,
            status="EVALUABLE",
            outcome="TRUE",
            evidence_ids=evidence_ids,
            reason="R-COM-001 demostrada: descuento disponible y aplicable confirmado.",
        )

    if discount.opportunity_state == "NOT_AVAILABLE":
        if not opportunity_ids:
            return Assessment(
                rule_id=R_COM_001,
                status="NOT_EVALUABLE",
                outcome=None,
                evidence_ids=evidence_ids,
                reason="R-COM-001 no evaluable: ausencia de descuento no demostrada.",
            )
        return Assessment(
            rule_id=R_COM_001,
            status="EVALUABLE",
            outcome="FALSE",
            evidence_ids=evidence_ids,
            reason="R-COM-001 no demostrada: descuento no disponible.",
        )

    return Assessment(
        rule_id=R_COM_001,
        status="NOT_EVALUABLE",
        outcome=None,
        evidence_ids=evidence_ids,
        reason="R-COM-001 no evaluable: oportunidad o aplicabilidad no concluyente.",
    )


def build_rappel_effective_cost(
    *,
    purchase: PurchaseOperation,
    rappel: RappelApplicabilityEvidence,
    evidences: tuple[Evidence, ...],
) -> RappelEffectiveCostEvidence:
    if (
        rappel.article_id != purchase.article_id
        or rappel.supplier_id != purchase.supplier_id
        or rappel.evaluation_date != purchase.operation_date
    ):
        raise ValueError("RappelApplicabilityEvidence incompatible con PurchaseOperation")
    if rappel.currency != purchase.currency:
        raise ValueError("currency de rappel incompatible con PurchaseOperation")

    agreement_ids = _demonstrates_ref(evidences, rappel.agreement_ref)
    applicability_ids = _demonstrates_ref(evidences, rappel.applicability_ref)
    basis_ids = _demonstrates_ref(evidences, rappel.economic_basis_ref)
    if not agreement_ids or not applicability_ids or not basis_ids:
        raise ValueError("rappel agreement/applicability/economic basis no demostrados")

    purchase_gross = purchase.quantity * purchase.unit_price
    rebate_amount = rappel.eligible_base_amount * rappel.rebate_rate_pct / Decimal("100")
    if rebate_amount > purchase_gross:
        raise ValueError("rebate_amount supera purchase_gross_amount")
    effective = purchase_gross - rebate_amount

    return RappelEffectiveCostEvidence(
        article_id=rappel.article_id,
        supplier_id=rappel.supplier_id,
        evaluation_date=rappel.evaluation_date,
        agreement_ref=rappel.agreement_ref,
        purchase_gross_amount=purchase_gross,
        eligible_base_amount=rappel.eligible_base_amount,
        rebate_rate_pct=rappel.rebate_rate_pct,
        rebate_amount=rebate_amount,
        effective_cost_after_rappel=effective,
        currency=rappel.currency,
        evidence_refs=tuple(dict.fromkeys((*rappel.evidence_refs, *agreement_ids, *applicability_ids, *basis_ids))),
        trace_refs=rappel.trace_refs,
    )


def evaluate_r_com_002(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    rappel: RappelApplicabilityEvidence,
    evidences: tuple[Evidence, ...],
) -> Assessment:
    _validate_rule_identity(purchase, context, rule, R_COM_002)

    if (
        rappel.article_id != purchase.article_id
        or rappel.supplier_id != purchase.supplier_id
        or rappel.evaluation_date != purchase.operation_date
    ):
        raise ValueError("RappelApplicabilityEvidence incompatible con PurchaseOperation")

    if rappel.applicability_state == "NOT_APPLICABLE":
        ids = _demonstrates_ref(evidences, rappel.applicability_ref)
        if not ids:
            return Assessment(
                rule_id=R_COM_002,
                status="NOT_EVALUABLE",
                outcome=None,
                evidence_ids=list(rappel.evidence_refs),
                reason="R-COM-002 no evaluable: no aplicabilidad no demostrada.",
            )
        return Assessment(
            rule_id=R_COM_002,
            status="EVALUABLE",
            outcome="FALSE",
            evidence_ids=list(dict.fromkeys((*rappel.evidence_refs, *ids))),
            reason="R-COM-002 no demostrada: rappel no aplicable a la operación.",
        )

    if rappel.applicability_state != "CONFIRMED":
        return Assessment(
            rule_id=R_COM_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=list(rappel.evidence_refs),
            reason="R-COM-002 no evaluable: rappel no confirmado.",
        )

    try:
        cost = build_rappel_effective_cost(purchase=purchase, rappel=rappel, evidences=evidences)
    except ValueError as exc:
        return Assessment(
            rule_id=R_COM_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=list(rappel.evidence_refs),
            reason=f"R-COM-002 no evaluable: {exc}",
        )

    outcome = "TRUE" if (
        cost.rebate_amount > 0
        and cost.effective_cost_after_rappel < cost.purchase_gross_amount
    ) else "FALSE"
    return Assessment(
        rule_id=R_COM_002,
        status="EVALUABLE",
        outcome=outcome,
        evidence_ids=list(cost.evidence_refs),
        reason=(
            "R-COM-002 demostrada: rappel confirmado mejora el coste efectivo."
            if outcome == "TRUE"
            else "R-COM-002 no demostrada: rappel confirmado no mejora el coste efectivo."
        ),
    )


__all__ = [
    "R_COM_001",
    "R_COM_002",
    "build_rappel_effective_cost",
    "evaluate_r_com_001",
    "evaluate_r_com_002",
]
