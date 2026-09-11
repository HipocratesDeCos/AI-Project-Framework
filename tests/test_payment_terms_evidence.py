from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, PurchaseOperation
from eios.payment import PurchasePaymentTermEvidence, resolve_purchase_payment_term


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-PAY",
        scenario_id="S-PAY",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-PAY",
        scenario_id="S-PAY",
        article_id="ART-PAY",
        supplier_id="SUP-PAY",
        quantity=Decimal("5"),
        unit_price=Decimal("10"),
        currency="EUR",
        operation_date="2026-09-11",
    )


def _known(days: int = 60) -> PurchasePaymentTermEvidence:
    return PurchasePaymentTermEvidence(
        decision_id="D-PAY",
        scenario_id="S-PAY",
        article_id="ART-PAY",
        supplier_id="SUP-PAY",
        evaluated_purchase_ref="purchase:D-PAY:S-PAY",
        state="KNOWN",
        offered_payment_term_days=days,
        semantic_ref="payment-term:days-after-invoice",
        purchase_applicability_ref="offer:PAY-001:applies-to-purchase",
        source_ref="offer:PAY-001",
        captured_at="2026-09-11",
        evidence_refs=("EV-PAY-001",),
        trace_refs=("TRACE-UPSTREAM-PAY",),
    )


def test_known_payment_term_preserves_context_and_evidence() -> None:
    result = resolve_purchase_payment_term(_purchase(), _context(), _known(90))

    assert result.state == "KNOWN"
    assert result.offered_payment_term_days == 90
    assert result.rules_version == "rules-v1"
    assert result.parameters_version == "params-v1"
    assert result.data_snapshot_id == "snapshot-v1"
    assert result.evidence_refs == ("EV-PAY-001",)
    assert result.trace_refs == ("TRACE-UPSTREAM-PAY",)


def test_zero_days_is_valid_only_when_explicitly_evidenced() -> None:
    result = resolve_purchase_payment_term(_purchase(), _context(), _known(0))
    assert result.state == "KNOWN"
    assert result.offered_payment_term_days == 0


def test_missing_payment_term_is_not_silently_zero() -> None:
    evidence = PurchasePaymentTermEvidence(
        decision_id="D-PAY",
        scenario_id="S-PAY",
        article_id="ART-PAY",
        supplier_id="SUP-PAY",
        evaluated_purchase_ref="purchase:D-PAY:S-PAY",
        state="NOT_EVIDENCED",
        limitations=("PAYMENT_TERM_NOT_PROVIDED",),
    )

    result = resolve_purchase_payment_term(_purchase(), _context(), evidence)
    assert result.state == "NOT_EVIDENCED"
    assert result.offered_payment_term_days is None
    assert result.limitations == ("PAYMENT_TERM_NOT_PROVIDED",)


def test_conflicting_payment_terms_do_not_publish_unique_value() -> None:
    evidence = PurchasePaymentTermEvidence(
        decision_id="D-PAY",
        scenario_id="S-PAY",
        article_id="ART-PAY",
        supplier_id="SUP-PAY",
        evaluated_purchase_ref="purchase:D-PAY:S-PAY",
        state="CONFLICTING_DATA",
        evidence_refs=("EV-PAY-60", "EV-PAY-90"),
        issue_refs=("ISSUE-PAY-CONFLICT",),
    )

    result = resolve_purchase_payment_term(_purchase(), _context(), evidence)
    assert result.state == "CONFLICTING_DATA"
    assert result.offered_payment_term_days is None
    assert result.evidence_refs == ("EV-PAY-60", "EV-PAY-90")
    assert result.issue_refs == ("ISSUE-PAY-CONFLICT",)


def test_known_requires_full_purchase_specific_evidence() -> None:
    with pytest.raises(ValueError, match="KNOWN requiere"):
        PurchasePaymentTermEvidence(
            decision_id="D-PAY",
            scenario_id="S-PAY",
            article_id="ART-PAY",
            supplier_id="SUP-PAY",
            evaluated_purchase_ref="purchase:D-PAY:S-PAY",
            state="KNOWN",
            offered_payment_term_days=60,
        )


def test_not_evidenced_cannot_publish_declared_value_as_known() -> None:
    with pytest.raises(ValueError, match="NOT_EVIDENCED"):
        PurchasePaymentTermEvidence(
            decision_id="D-PAY",
            scenario_id="S-PAY",
            article_id="ART-PAY",
            supplier_id="SUP-PAY",
            evaluated_purchase_ref="purchase:D-PAY:S-PAY",
            state="NOT_EVIDENCED",
            offered_payment_term_days=60,
        )


def test_conflicting_data_requires_issue_reference() -> None:
    with pytest.raises(ValueError, match="issue_refs"):
        PurchasePaymentTermEvidence(
            decision_id="D-PAY",
            scenario_id="S-PAY",
            article_id="ART-PAY",
            supplier_id="SUP-PAY",
            evaluated_purchase_ref="purchase:D-PAY:S-PAY",
            state="CONFLICTING_DATA",
        )


def test_not_determinable_requires_explicit_context() -> None:
    with pytest.raises(ValueError, match="issue_refs o limitations"):
        PurchasePaymentTermEvidence(
            decision_id="D-PAY",
            scenario_id="S-PAY",
            article_id="ART-PAY",
            supplier_id="SUP-PAY",
            evaluated_purchase_ref="purchase:D-PAY:S-PAY",
            state="NOT_DETERMINABLE",
        )


def test_resolver_rejects_evidence_for_another_purchase_identity() -> None:
    evidence = _known().model_copy(update={"supplier_id": "SUP-OTHER"})
    with pytest.raises(ValueError, match="no pertenece"):
        resolve_purchase_payment_term(_purchase(), _context(), evidence)


def test_bool_is_not_accepted_as_day_count() -> None:
    with pytest.raises(ValueError, match="entero de días"):
        _known().__class__(
            **{
                **_known().model_dump(),
                "offered_payment_term_days": True,
            }
        )
