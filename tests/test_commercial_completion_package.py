from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from eios.commercial import (
    DiscountOpportunityEvidence,
    RappelApplicabilityEvidence,
    R_COM_001,
    R_COM_002,
    build_rappel_effective_cost,
    evaluate_r_com_001,
    evaluate_r_com_002,
)
from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.rules.catalog import authorized_rule, authorized_rule_metadata
from eios.rules.orchestrator import (
    CommercialDiscountRuleInputs,
    CommercialRappelRuleInputs,
    run_domain_rules,
)


OP_DATE = date(2026, 9, 23)


def _purchase():
    return PurchaseOperation(
        decision_id="D-COM",
        scenario_id="S-COM",
        article_id="ART-001",
        supplier_id="SUP-001",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=OP_DATE,
    )


def _context():
    return DecisionContext(
        decision_id="D-COM",
        scenario_id="S-COM",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snap-com",
    )


def _ev(eid, ref, state="DEMONSTRATED"):
    return Evidence(
        evidence_id=eid,
        source_type="commercial-test",
        source_ref="commercial:test",
        captured_at=OP_DATE,
        state=state,
        demonstration_ref=ref if state == "DEMONSTRATED" else None,
    )


def _discount(**overrides):
    values = dict(
        article_id="ART-001",
        supplier_id="SUP-001",
        evaluation_date=OP_DATE,
        opportunity_ref="discount:opportunity",
        applicability_ref="discount:applicable",
        opportunity_state="AVAILABLE",
        applicability_state="CONFIRMED",
        evidence_refs=("E-DISC-OPP", "E-DISC-APP"),
        trace_refs=("trace:discount",),
    )
    values.update(overrides)
    return DiscountOpportunityEvidence(**values)


def _discount_evidence():
    return (
        _ev("E-DISC-OPP", "discount:opportunity"),
        _ev("E-DISC-APP", "discount:applicable"),
    )


def _rappel(**overrides):
    values = dict(
        article_id="ART-001",
        supplier_id="SUP-001",
        evaluation_date=OP_DATE,
        agreement_ref="rappel:agreement",
        applicability_ref="rappel:applicable",
        economic_basis_ref="rappel:basis",
        applicability_state="CONFIRMED",
        eligible_base_amount=Decimal("50"),
        rebate_rate_pct=Decimal("10"),
        currency="EUR",
        evidence_refs=("E-RAP-AGR", "E-RAP-APP", "E-RAP-BAS"),
        trace_refs=("trace:rappel",),
    )
    values.update(overrides)
    return RappelApplicabilityEvidence(**values)


def _rappel_evidence():
    return (
        _ev("E-RAP-AGR", "rappel:agreement"),
        _ev("E-RAP-APP", "rappel:applicable"),
        _ev("E-RAP-BAS", "rappel:basis"),
    )


def test_com001_available_confirmed_is_true():
    result = evaluate_r_com_001(
        purchase=_purchase(),
        context=_context(),
        rule=authorized_rule(R_COM_001, "rules-v1"),
        discount=_discount(),
        evidences=_discount_evidence(),
    )
    assert result.status == "EVALUABLE"
    assert result.outcome == "TRUE"


def test_com001_not_available_demonstrated_is_false():
    d = _discount(opportunity_state="NOT_AVAILABLE", applicability_state="NOT_CONFIRMED")
    result = evaluate_r_com_001(
        purchase=_purchase(), context=_context(),
        rule=authorized_rule(R_COM_001, "rules-v1"),
        discount=d, evidences=_discount_evidence(),
    )
    assert result.status == "EVALUABLE"
    assert result.outcome == "FALSE"


@pytest.mark.parametrize(
    ("opportunity_state", "applicability_state"),
    [
        ("AVAILABLE", "CONDITIONAL"),
        ("AVAILABLE", "NOT_CONFIRMED"),
        ("NOT_DETERMINABLE", "NOT_DETERMINABLE"),
        ("CONFLICTING", "CONFLICTING"),
    ],
)
def test_com001_nonconclusive_states_are_not_evaluable(opportunity_state, applicability_state):
    result = evaluate_r_com_001(
        purchase=_purchase(), context=_context(),
        rule=authorized_rule(R_COM_001, "rules-v1"),
        discount=_discount(
            opportunity_state=opportunity_state,
            applicability_state=applicability_state,
        ),
        evidences=_discount_evidence(),
    )
    assert result.status == "NOT_EVALUABLE"


def test_com001_gap_does_not_demonstrate():
    evidences = (
        _ev("E-DISC-OPP", "discount:opportunity", state="GAP"),
        _ev("E-DISC-APP", "discount:applicable"),
    )
    result = evaluate_r_com_001(
        purchase=_purchase(), context=_context(),
        rule=authorized_rule(R_COM_001, "rules-v1"),
        discount=_discount(), evidences=evidences,
    )
    assert result.status == "NOT_EVALUABLE"


def test_com001_identity_mismatch_fails_closed():
    with pytest.raises(ValueError, match="incompatible"):
        evaluate_r_com_001(
            purchase=_purchase(), context=_context(),
            rule=authorized_rule(R_COM_001, "rules-v1"),
            discount=_discount(supplier_id="OTHER"),
            evidences=_discount_evidence(),
        )


def test_com002_builds_exact_linear_cost():
    cost = build_rappel_effective_cost(
        purchase=_purchase(), rappel=_rappel(), evidences=_rappel_evidence()
    )
    assert cost.purchase_gross_amount == Decimal("50")
    assert cost.rebate_amount == Decimal("5")
    assert cost.effective_cost_after_rappel == Decimal("45")


def test_com002_confirmed_rappel_is_true():
    result = evaluate_r_com_002(
        purchase=_purchase(), context=_context(),
        rule=authorized_rule(R_COM_002, "rules-v1"),
        rappel=_rappel(), evidences=_rappel_evidence(),
    )
    assert result.status == "EVALUABLE"
    assert result.outcome == "TRUE"


def test_com002_not_applicable_demonstrated_is_false():
    r = _rappel(applicability_state="NOT_APPLICABLE")
    result = evaluate_r_com_002(
        purchase=_purchase(), context=_context(),
        rule=authorized_rule(R_COM_002, "rules-v1"),
        rappel=r, evidences=_rappel_evidence(),
    )
    assert result.status == "EVALUABLE"
    assert result.outcome == "FALSE"


@pytest.mark.parametrize("state", ["CONDITIONAL", "NOT_DETERMINABLE", "CONFLICTING"])
def test_com002_unresolved_states_are_not_evaluable(state):
    result = evaluate_r_com_002(
        purchase=_purchase(), context=_context(),
        rule=authorized_rule(R_COM_002, "rules-v1"),
        rappel=_rappel(applicability_state=state), evidences=_rappel_evidence(),
    )
    assert result.status == "NOT_EVALUABLE"


@pytest.mark.parametrize("rate", [Decimal("0"), Decimal("-1"), Decimal("101")])
def test_com002_invalid_rate_is_rejected(rate):
    with pytest.raises(ValidationError):
        _rappel(rebate_rate_pct=rate)


def test_com002_currency_mismatch_is_not_evaluable():
    result = evaluate_r_com_002(
        purchase=_purchase(), context=_context(),
        rule=authorized_rule(R_COM_002, "rules-v1"),
        rappel=_rappel(currency="USD"), evidences=_rappel_evidence(),
    )
    assert result.status == "NOT_EVALUABLE"


def test_com002_rebate_cannot_exceed_purchase_gross():
    result = evaluate_r_com_002(
        purchase=_purchase(), context=_context(),
        rule=authorized_rule(R_COM_002, "rules-v1"),
        rappel=_rappel(eligible_base_amount=Decimal("1000"), rebate_rate_pct=Decimal("100")),
        evidences=_rappel_evidence(),
    )
    assert result.status == "NOT_EVALUABLE"


def test_catalog_metadata_matches_authority():
    m1 = authorized_rule_metadata(R_COM_001, "rules-v1")
    m2 = authorized_rule_metadata(R_COM_002, "rules-v1")
    assert (m1.effect, m1.severity, m1.active_result) == ("R2", "MEDIA", "NEGOCIAR")
    assert (m2.effect, m2.severity, m2.active_result) == ("R3", "MEDIA", None)


def test_com001_crc_negotiates():
    result = run_domain_rules(
        purchase=_purchase(), context=_context(), base_result="COMPRAR",
        commercial_discount=CommercialDiscountRuleInputs(
            discount=_discount(), evidences=_discount_evidence()
        ),
    )
    assert result.crc_result.consolidated_result == "NEGOCIAR"


def test_com002_r3_does_not_change_crc_result():
    result = run_domain_rules(
        purchase=_purchase(), context=_context(), base_result="COMPRAR",
        commercial_rappel=CommercialRappelRuleInputs(
            rappel=_rappel(), evidences=_rappel_evidence()
        ),
    )
    assert result.crc_result.consolidated_result == "COMPRAR"


def test_commercial_rules_omitted_without_bundles():
    result = run_domain_rules(
        purchase=_purchase(), context=_context(), base_result="COMPRAR"
    )
    assert R_COM_001 in result.omitted_rule_ids
    assert R_COM_002 in result.omitted_rule_ids
