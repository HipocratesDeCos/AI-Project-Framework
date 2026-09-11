"""Identity-safe resolver for factual purchase payment-term evidence."""
from __future__ import annotations

from eios.core.models import DecisionContext, PurchaseOperation

from .models import PaymentTermResult, PurchasePaymentTermEvidence


def resolve_purchase_payment_term(
    purchase: PurchaseOperation,
    context: DecisionContext,
    evidence: PurchasePaymentTermEvidence,
) -> PaymentTermResult:
    """Resolve one purchase-specific payment term without business evaluation."""
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")

    expected_identity = (
        purchase.decision_id,
        purchase.scenario_id,
        purchase.article_id,
        purchase.supplier_id,
    )
    evidence_identity = (
        evidence.decision_id,
        evidence.scenario_id,
        evidence.article_id,
        evidence.supplier_id,
    )
    if evidence_identity != expected_identity:
        raise ValueError("Payment term evidence no pertenece a la compra evaluada")

    return PaymentTermResult(
        decision_id=context.decision_id,
        scenario_id=context.scenario_id,
        article_id=purchase.article_id,
        supplier_id=purchase.supplier_id,
        rules_version=context.rules_version,
        parameters_version=context.parameters_version,
        data_snapshot_id=context.data_snapshot_id,
        evaluated_purchase_ref=evidence.evaluated_purchase_ref,
        state=evidence.state,
        offered_payment_term_days=evidence.offered_payment_term_days,
        evidence_refs=evidence.evidence_refs,
        issue_refs=evidence.issue_refs,
        trace_refs=evidence.trace_refs,
        limitations=evidence.limitations,
    )


__all__ = ["resolve_purchase_payment_term"]
