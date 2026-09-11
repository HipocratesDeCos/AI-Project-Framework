from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from eios.core.models import DecisionContext, PurchaseOperation
from eios.supplier import (
    ExternalSupplierMetric,
    StructuralComparisonRequest,
    SupplierCandidateEvidence,
    SupplierDataIssueRef,
    SupplierEvidenceInput,
    SupplierHistoricalFact,
    SupplierObservation,
    SupplierSignal,
    evaluate_supplier_evidence,
)

EVAL_DATE = date(2026, 9, 11)


def context(**overrides):
    data = {
        "decision_id": "D-1",
        "scenario_id": "S-1",
        "rules_version": "rules-v1",
        "parameters_version": "params-v1",
        "data_snapshot_id": "snap-1",
    }
    data.update(overrides)
    return DecisionContext(**data)


def operation(**overrides):
    data = {
        "decision_id": "D-1",
        "scenario_id": "S-1",
        "article_id": "A-1",
        "supplier_id": "SUP-CURRENT",
        "quantity": Decimal("10"),
        "unit_price": Decimal("100"),
        "currency": "EUR",
        "operation_date": date(2026, 9, 11),
    }
    data.update(overrides)
    return PurchaseOperation(**data)


def contradiction(issue_id="ISS-1"):
    return SupplierDataIssueRef(
        issue_id=issue_id,
        issue_type="CONTRADICTION",
        issue_record_ref=f"REC-{issue_id}",
        evidence_refs=(f"E-{issue_id}-1", f"E-{issue_id}-2"),
    )


def candidate(candidate_id="C-1", supplier_id="SUP-ALT", **overrides):
    data = {
        "candidate_id": candidate_id,
        "supplier_id": supplier_id,
        "object_id": "A-1",
        "state": "CURRENT_OPERATION_DEMONSTRATED",
        "evidence_id": f"E-{candidate_id}",
        "source_ref": f"SRC-{candidate_id}",
        "captured_at": date(2026, 9, 10),
        "applicability_ref": f"APP-{candidate_id}",
        "valid_from": date(2026, 9, 1),
        "valid_to": date(2026, 9, 30),
    }
    data.update(overrides)
    return SupplierCandidateEvidence(**data)


def current_obs(observation_id="O-CUR", **overrides):
    data = {
        "observation_id": observation_id,
        "supplier_id": "SUP-CURRENT",
        "candidate_id": None,
        "object_id": "A-1",
        "dimension": "AVAILABILITY",
        "state": "KNOWN",
        "value_kind": "TEXT",
        "value_text": "AVAILABLE",
        "unit": None,
        "semantic_ref": "SEM-AVAILABILITY",
        "source_ref": f"SRC-{observation_id}",
        "evidence_id": f"E-{observation_id}",
        "captured_at": date(2026, 9, 10),
    }
    data.update(overrides)
    return SupplierObservation(**data)


def candidate_obs(observation_id="O-ALT", candidate_id="C-1", supplier_id="SUP-ALT", **overrides):
    data = {
        "observation_id": observation_id,
        "supplier_id": supplier_id,
        "candidate_id": candidate_id,
        "object_id": "A-1",
        "dimension": "AVAILABILITY",
        "state": "KNOWN",
        "value_kind": "TEXT",
        "value_text": "AVAILABLE",
        "unit": None,
        "semantic_ref": "SEM-AVAILABILITY",
        "source_ref": f"SRC-{observation_id}",
        "evidence_id": f"E-{observation_id}",
        "captured_at": date(2026, 9, 10),
    }
    data.update(overrides)
    return SupplierObservation(**data)


def decimal_current(observation_id="P-CUR", **overrides):
    data = {
        "dimension": "PAYMENT_TERM",
        "value_kind": "DECIMAL",
        "value_text": None,
        "value_decimal": Decimal("60"),
        "unit": "days",
        "semantic_ref": "SEM-PAYMENT-DAYS",
    }
    data.update(overrides)
    return current_obs(observation_id, **data)


def decimal_candidate(observation_id="P-ALT", **overrides):
    data = {
        "dimension": "PAYMENT_TERM",
        "value_kind": "DECIMAL",
        "value_text": None,
        "value_decimal": Decimal("90"),
        "unit": "days",
        "semantic_ref": "SEM-PAYMENT-DAYS",
    }
    data.update(overrides)
    return candidate_obs(observation_id, **data)


def metric(metric_id="M-1", **overrides):
    data = {
        "metric_id": metric_id,
        "supplier_id": "SUP-ALT",
        "metric_name": "EXTERNAL_RELIABILITY",
        "data_state": "KNOWN",
        "value": Decimal("0.97"),
        "unit": "ratio",
        "scope_ref": "SCOPE-1",
        "period_start": date(2026, 1, 1),
        "period_end": date(2026, 8, 31),
        "methodology_ref": "METHOD-EXT-1",
        "source_ref": "SRC-METRIC-1",
        "captured_at": date(2026, 9, 10),
        "usage_state": "AUTHORIZED_EXTERNAL_METRIC",
        "usage_authority_ref": "AUTH-EXT-1",
    }
    data.update(overrides)
    return ExternalSupplierMetric(**data)


def payload(**overrides):
    data = {
        "context": context(),
        "purchase_operation": operation(),
        "company_scope": "COMPANY-1",
        "evaluation_date": EVAL_DATE,
        "methodology_version": "0.3",
        "candidates": (),
        "observations": (),
        "historical_facts": (),
        "external_metrics": (),
        "signals": (),
        "comparison_requests": (),
    }
    data.update(overrides)
    return SupplierEvidenceInput(**data)


def comparison(comparison_id="CMP-1", current="O-CUR", alt="O-ALT", **overrides):
    data = {
        "comparison_id": comparison_id,
        "current_observation_id": current,
        "candidate_observation_id": alt,
    }
    data.update(overrides)
    return StructuralComparisonRequest(**data)


def test_demonstrated_current_candidate_resolves_as_evidenced():
    result = evaluate_supplier_evidence(payload(candidates=(candidate(),)))
    assert result.candidate_resolutions[0].state == "EVIDENCED_CANDIDATE"
    assert result.unresolved_items == ()


def test_reference_only_resolves_not_evidenced():
    item = candidate(state="REFERENCE_ONLY", applicability_ref=None)
    result = evaluate_supplier_evidence(payload(candidates=(item,)))
    assert result.candidate_resolutions[0].state == "NOT_EVIDENCED"
    assert result.unresolved_items[0].item_type == "CANDIDATE"


def test_reference_only_requires_minimum_evidence():
    with pytest.raises(ValidationError):
        candidate(state="REFERENCE_ONLY", evidence_id=None, applicability_ref=None)


def test_gap_resolves_not_evidenced_without_becoming_false():
    item = candidate(
        state="GAP", evidence_id=None, source_ref=None, captured_at=None,
        applicability_ref=None, valid_from=None, valid_to=None,
    )
    result = evaluate_supplier_evidence(payload(candidates=(item,)))
    assert result.candidate_resolutions[0].state == "NOT_EVIDENCED"


def test_conflicting_candidate_requires_contradiction_issue():
    with pytest.raises(ValidationError):
        candidate(state="CONFLICTING_DATA", applicability_ref=None, issue_refs=())


def test_contradiction_requires_two_distinct_evidence_refs():
    with pytest.raises(ValidationError):
        SupplierDataIssueRef(
            issue_id="I-X", issue_type="CONTRADICTION", issue_record_ref="REC-X",
            evidence_refs=("E-1",),
        )


def test_conflicting_candidate_is_preserved():
    item = candidate(
        state="CONFLICTING_DATA", applicability_ref=None,
        issue_refs=(contradiction(),),
    )
    result = evaluate_supplier_evidence(payload(candidates=(item,)))
    assert result.candidate_resolutions[0].state == "CONFLICTING_DATA"
    assert result.conflicting_items[0].item_type == "CANDIDATE"


def test_current_candidate_expired_is_rejected_by_envelope():
    with pytest.raises(ValidationError):
        payload(candidates=(candidate(valid_to=date(2026, 9, 10)),))


def test_current_candidate_not_yet_valid_is_rejected_by_envelope():
    with pytest.raises(ValidationError):
        payload(candidates=(candidate(valid_from=date(2026, 9, 12)),))


def test_candidate_captured_in_future_is_rejected():
    with pytest.raises(ValidationError):
        payload(candidates=(candidate(captured_at=date(2026, 9, 12)),))


def test_current_supplier_cannot_be_candidate():
    with pytest.raises(ValidationError):
        payload(candidates=(candidate(supplier_id="SUP-CURRENT"),))


def test_candidate_object_must_match_purchase_article():
    with pytest.raises(ValidationError):
        payload(candidates=(candidate(object_id="A-OTHER"),))


def test_duplicate_candidate_id_is_rejected():
    with pytest.raises(ValidationError):
        payload(candidates=(candidate(), candidate(supplier_id="SUP-2")))


def test_same_supplier_can_have_two_distinct_candidate_proposals():
    item = payload(candidates=(candidate("C-1"), candidate("C-2")))
    result = evaluate_supplier_evidence(item)
    assert [x.candidate_id for x in result.candidate_resolutions] == ["C-1", "C-2"]


def test_known_observation_keeps_exact_typed_value():
    item = decimal_current()
    assert item.value_decimal == Decimal("60")
    assert item.value_text is None


def test_known_observation_rejects_multiple_values():
    with pytest.raises(ValidationError):
        decimal_current(value_text="also text")


def test_non_known_observation_cannot_publish_value():
    with pytest.raises(ValidationError):
        current_obs(state="NOT_EVIDENCED")


def test_alternative_observation_must_reference_candidate_id():
    item = current_obs(observation_id="ALT-WITHOUT-CANDIDATE", supplier_id="SUP-ALT")
    with pytest.raises(ValidationError):
        payload(candidates=(candidate(),), observations=(item,))


def test_alternative_observation_supplier_must_match_candidate():
    item = candidate_obs(supplier_id="SUP-WRONG")
    with pytest.raises(ValidationError):
        payload(candidates=(candidate(),), observations=(item,))


def test_observation_object_must_match_purchase_article():
    with pytest.raises(ValidationError):
        payload(observations=(current_obs(object_id="A-OTHER"),))


def test_observation_captured_in_future_is_rejected():
    with pytest.raises(ValidationError):
        payload(observations=(current_obs(captured_at=date(2026, 9, 12)),))


@pytest.mark.parametrize(
    "field,value_kind",
    [("value_integer", "INTEGER"), ("value_decimal", "DECIMAL")],
)
def test_bool_cannot_be_coerced_to_numeric_observation(field, value_kind):
    kwargs = {
        "observation_id": f"STRICT-{field}",
        "supplier_id": "SUP-CURRENT",
        "object_id": "A-1",
        "dimension": "LEAD_TIME",
        "state": "KNOWN",
        "value_kind": value_kind,
        field: True,
        "unit": "days",
        "semantic_ref": "SEM-STRICT",
        "source_ref": "SRC-STRICT",
        "evidence_id": "E-STRICT",
        "captured_at": date(2026, 9, 10),
    }
    with pytest.raises(ValidationError):
        SupplierObservation(**kwargs)


def test_value_boolean_requires_real_bool_before_coercion():
    with pytest.raises(ValidationError):
        SupplierObservation(
            observation_id="BOOL-X", supplier_id="SUP-CURRENT", object_id="A-1",
            dimension="OTHER_EVIDENCED_CONDITION", state="KNOWN", value_kind="BOOLEAN",
            value_boolean="true", semantic_ref="SEM-BOOL", source_ref="SRC-BOOL",
            evidence_id="E-BOOL", captured_at=date(2026, 9, 10),
        )


@pytest.mark.parametrize(
    "value_kind,value_field,value",
    [("TEXT", "value_text", "x"), ("DATE", "value_date", date(2026, 9, 10)), ("BOOLEAN", "value_boolean", True)],
)
def test_text_date_boolean_reject_units(value_kind, value_field, value):
    kwargs = {
        "observation_id": f"UNIT-{value_kind}", "supplier_id": "SUP-CURRENT",
        "object_id": "A-1", "dimension": "OTHER_EVIDENCED_CONDITION",
        "state": "KNOWN", "value_kind": value_kind, value_field: value,
        "unit": "forbidden", "semantic_ref": "SEM-X", "source_ref": "SRC-X",
        "evidence_id": "E-X", "captured_at": date(2026, 9, 10),
    }
    with pytest.raises(ValidationError):
        SupplierObservation(**kwargs)


def test_text_availability_is_preserved_without_quantity_inference():
    obs = current_obs(value_text="Supplier states available")
    result = evaluate_supplier_evidence(payload(observations=(obs,)))
    restored = result.observations[0]
    assert restored.value_text == "Supplier states available"
    assert restored.value_decimal is None
    assert restored.value_integer is None


@pytest.mark.parametrize(
    "event_date,captured_at",
    [(date(2026, 9, 12), date(2026, 9, 10)), (date(2026, 9, 10), date(2026, 9, 12))],
)
def test_historical_fact_cannot_be_future_or_captured_future(event_date, captured_at):
    fact = SupplierHistoricalFact(
        fact_id="F-1", supplier_id="SUP-CURRENT", event_type="DELIVERY",
        event_date=event_date, captured_at=captured_at, scope_ref="SCOPE",
        source_ref="SRC", evidence_id="E-F",
    )
    with pytest.raises(ValidationError):
        payload(historical_facts=(fact,))


@pytest.mark.parametrize(
    "observed_at,captured_at",
    [(date(2026, 9, 12), date(2026, 9, 10)), (date(2026, 9, 10), date(2026, 9, 12))],
)
def test_signal_cannot_be_future_or_captured_future(observed_at, captured_at):
    signal = SupplierSignal(
        signal_id="S-1", supplier_id="SUP-CURRENT", signal_type="NOTICE",
        observed_at=observed_at, captured_at=captured_at, scope_ref="SCOPE",
        source_ref="SRC", evidence_id="E-S",
    )
    with pytest.raises(ValidationError):
        payload(signals=(signal,))


def test_historical_fact_is_preserved_without_score_or_severity():
    fact = SupplierHistoricalFact(
        fact_id="F-1", supplier_id="SUP-CURRENT", event_type="LATE_DELIVERY",
        event_date=date(2026, 8, 1), captured_at=date(2026, 8, 2), scope_ref="PO-1",
        source_ref="ERP-1", evidence_id="E-F",
    )
    result = evaluate_supplier_evidence(payload(historical_facts=(fact,)))
    serialized = result.historical_facts[0].model_dump()
    assert "score" not in serialized and "severity" not in serialized and "effect" not in serialized


def test_signal_is_preserved_without_criticality():
    signal = SupplierSignal(
        signal_id="S-1", supplier_id="SUP-CURRENT", signal_type="DOCUMENT_NOTICE",
        observed_at=date(2026, 9, 1), captured_at=date(2026, 9, 2), scope_ref="DOC-1",
        source_ref="ERP-1", evidence_id="E-S",
    )
    result = evaluate_supplier_evidence(payload(signals=(signal,)))
    assert "criticality" not in result.signals[0].model_dump()


@pytest.mark.parametrize("kind", ["fact", "metric", "signal"])
def test_unrelated_supplier_records_are_rejected(kind):
    values = {}
    if kind == "fact":
        values["historical_facts"] = (SupplierHistoricalFact(
            fact_id="F-X", supplier_id="SUP-OUT", event_type="X",
            event_date=date(2026, 9, 1), captured_at=date(2026, 9, 2),
            scope_ref="S", source_ref="SRC", evidence_id="E",
        ),)
    elif kind == "metric":
        values["external_metrics"] = (metric(supplier_id="SUP-OUT"),)
    else:
        values["signals"] = (SupplierSignal(
            signal_id="S-X", supplier_id="SUP-OUT", signal_type="X",
            observed_at=date(2026, 9, 1), captured_at=date(2026, 9, 2),
            scope_ref="S", source_ref="SRC", evidence_id="E",
        ),)
    with pytest.raises(ValidationError):
        payload(**values)


def test_known_authorized_external_metric_is_preserved():
    result = evaluate_supplier_evidence(payload(candidates=(candidate(),), external_metrics=(metric(),)))
    assert result.external_metrics[0].value == Decimal("0.97")
    assert result.external_metrics[0].usage_state == "AUTHORIZED_EXTERNAL_METRIC"


def test_external_metric_rejects_bool_before_decimal_coercion():
    with pytest.raises(ValidationError):
        metric(value=True)


def test_authorized_external_metric_requires_authority_ref():
    with pytest.raises(ValidationError):
        metric(usage_authority_ref=None)


def test_non_known_metric_cannot_publish_value():
    with pytest.raises(ValidationError):
        metric(data_state="NOT_EVIDENCED")


def test_conflicting_metric_requires_contradiction_issue():
    with pytest.raises(ValidationError):
        metric(
            data_state="CONFLICTING_DATA", value=None, period_start=None, period_end=None,
            methodology_ref=None, source_ref=None, captured_at=None,
            usage_state="CONTEXT_ONLY_METRIC", usage_authority_ref=None,
        )


def test_context_only_metric_is_never_auto_elevated():
    item = metric(usage_state="CONTEXT_ONLY_METRIC", usage_authority_ref="AUTH-PRESENT")
    result = evaluate_supplier_evidence(payload(candidates=(candidate(),), external_metrics=(item,)))
    assert result.external_metrics[0].usage_state == "CONTEXT_ONLY_METRIC"


def test_explicit_request_produces_one_structural_comparison():
    result = evaluate_supplier_evidence(payload(
        candidates=(candidate(),), observations=(current_obs(), candidate_obs()),
        comparison_requests=(comparison(),),
    ))
    assert len(result.structural_comparisons) == 1
    assert result.structural_comparisons[0].state == "STRUCTURALLY_COMPARABLE"


def test_engine_never_generates_comparison_cross_product():
    result = evaluate_supplier_evidence(payload(
        candidates=(candidate(),),
        observations=(current_obs(), candidate_obs("O-A1"), candidate_obs("O-A2")),
        comparison_requests=(comparison(alt="O-A1"),),
    ))
    assert len(result.structural_comparisons) == 1


def test_reference_only_candidate_makes_requested_comparison_unknown():
    ref = candidate(state="REFERENCE_ONLY", applicability_ref=None)
    result = evaluate_supplier_evidence(payload(
        candidates=(ref,), observations=(current_obs(), candidate_obs()),
        comparison_requests=(comparison(),),
    ))
    cmp = result.structural_comparisons[0]
    assert cmp.state == "UNKNOWN"
    assert "CANDIDATE_NOT_EVIDENCED_CURRENTLY" in cmp.limitations


def test_not_evidenced_observation_makes_comparison_unknown():
    alt = candidate_obs(
        state="NOT_EVIDENCED", value_text=None, source_ref=None,
        evidence_id=None, captured_at=None,
    )
    result = evaluate_supplier_evidence(payload(
        candidates=(candidate(),), observations=(current_obs(), alt),
        comparison_requests=(comparison(),),
    ))
    assert result.structural_comparisons[0].state == "UNKNOWN"


def test_conflicting_observation_makes_comparison_not_structurally_comparable():
    alt = candidate_obs(
        state="CONFLICTING_DATA", value_text=None, source_ref=None,
        evidence_id=None, captured_at=None, issue_refs=(contradiction(),),
    )
    result = evaluate_supplier_evidence(payload(
        candidates=(candidate(),), observations=(current_obs(), alt),
        comparison_requests=(comparison(),),
    ))
    cmp = result.structural_comparisons[0]
    assert cmp.state == "NOT_STRUCTURALLY_COMPARABLE"
    assert cmp.issue_refs
    assert any(x.item_type == "COMPARISON" for x in result.conflicting_items)


def test_observation_outside_current_validity_is_not_structurally_comparable():
    alt = candidate_obs(valid_to=date(2026, 9, 10))
    result = evaluate_supplier_evidence(payload(
        candidates=(candidate(),), observations=(current_obs(), alt),
        comparison_requests=(comparison(),),
    ))
    assert result.structural_comparisons[0].state == "NOT_STRUCTURALLY_COMPARABLE"
    assert "OBSERVATION_OUTSIDE_VALIDITY" in result.structural_comparisons[0].limitations


def test_dimension_mismatch_precedes_price_authority_requirement():
    current = decimal_current(
        observation_id="PRICE-CUR", dimension="PRICE_REFERENCE", unit="EUR",
        semantic_ref="SEM-PRICE", value_decimal=Decimal("100"),
    )
    alt = decimal_candidate(
        observation_id="DELIVERY-ALT", dimension="LEAD_TIME", unit="days",
        semantic_ref="SEM-LEAD", value_decimal=Decimal("5"),
    )
    result = evaluate_supplier_evidence(payload(
        candidates=(candidate(),), observations=(current, alt),
        comparison_requests=(comparison(current="PRICE-CUR", alt="DELIVERY-ALT"),),
    ))
    cmp = result.structural_comparisons[0]
    assert cmp.state == "NOT_STRUCTURALLY_COMPARABLE"
    assert "DIMENSION_INCOMPATIBLE" in cmp.limitations
    assert "PRICE_COMPARABILITY_AUTHORITY_REQUIRED" not in cmp.limitations


def test_two_price_observations_without_price_authority_are_unknown():
    current = decimal_current(
        observation_id="PRICE-CUR", dimension="PRICE_REFERENCE", unit="EUR",
        semantic_ref="SEM-PRICE", value_decimal=Decimal("100"),
    )
    alt = decimal_candidate(
        observation_id="PRICE-ALT", dimension="PRICE_REFERENCE", unit="EUR",
        semantic_ref="SEM-PRICE", value_decimal=Decimal("95"),
    )
    result = evaluate_supplier_evidence(payload(
        candidates=(candidate(),), observations=(current, alt),
        comparison_requests=(comparison(current="PRICE-CUR", alt="PRICE-ALT"),),
    ))
    cmp = result.structural_comparisons[0]
    assert cmp.state == "UNKNOWN"
    assert cmp.difference_decimal is None
    assert "PRICE_COMPARABILITY_AUTHORITY_REQUIRED" in cmp.limitations


def test_two_price_observations_with_authority_ref_are_structurally_comparable_only():
    current = decimal_current(
        observation_id="PRICE-CUR", dimension="PRICE_REFERENCE", unit="EUR",
        semantic_ref="SEM-PRICE", value_decimal=Decimal("100"),
    )
    alt = decimal_candidate(
        observation_id="PRICE-ALT", dimension="PRICE_REFERENCE", unit="EUR",
        semantic_ref="SEM-PRICE", value_decimal=Decimal("95"),
    )
    result = evaluate_supplier_evidence(payload(
        candidates=(candidate(),), observations=(current, alt),
        comparison_requests=(comparison(
            current="PRICE-CUR", alt="PRICE-ALT", comparison_authority_ref="PRICE-RESULT-1"
        ),),
    ))
    cmp = result.structural_comparisons[0]
    assert cmp.state == "STRUCTURALLY_COMPARABLE"
    assert cmp.comparison_authority_ref == "PRICE-RESULT-1"
    assert cmp.difference_decimal == Decimal("-5")


@pytest.mark.parametrize(
    "candidate_overrides,expected_limit",
    [
        ({"semantic_ref": "SEM-OTHER"}, "SEMANTIC_REF_INCOMPATIBLE"),
        ({"unit": "weeks"}, "UNIT_INCOMPATIBLE"),
        ({"value_kind": "INTEGER", "value_decimal": None, "value_integer": 90}, "VALUE_KIND_INCOMPATIBLE"),
    ],
)
def test_structural_mismatches_are_not_comparable(candidate_overrides, expected_limit):
    cur = decimal_current()
    alt = decimal_candidate(**candidate_overrides)
    result = evaluate_supplier_evidence(payload(
        candidates=(candidate(),), observations=(cur, alt),
        comparison_requests=(comparison(current="P-CUR", alt="P-ALT"),),
    ))
    cmp = result.structural_comparisons[0]
    assert cmp.state == "NOT_STRUCTURALLY_COMPARABLE"
    assert expected_limit in cmp.limitations


def test_compatible_decimal_comparison_returns_exact_descriptive_difference():
    result = evaluate_supplier_evidence(payload(
        candidates=(candidate(),), observations=(decimal_current(), decimal_candidate()),
        comparison_requests=(comparison(current="P-CUR", alt="P-ALT"),),
    ))
    cmp = result.structural_comparisons[0]
    assert cmp.state == "STRUCTURALLY_COMPARABLE"
    assert cmp.difference_decimal == Decimal("30")
    assert "better" not in cmp.model_dump() and "worse" not in cmp.model_dump()


def test_context_and_purchase_decision_identity_must_match():
    with pytest.raises(ValidationError):
        payload(context=context(decision_id="D-OTHER"))


def test_context_and_purchase_scenario_identity_must_match():
    with pytest.raises(ValidationError):
        payload(context=context(scenario_id="S-OTHER"))


def test_methodology_version_is_fixed_to_closed_v03():
    with pytest.raises(ValidationError):
        payload(methodology_version="0.4")


def test_comparison_rejects_unknown_observation_reference():
    with pytest.raises(ValidationError):
        payload(
            candidates=(candidate(),), observations=(current_obs(), candidate_obs()),
            comparison_requests=(comparison(alt="MISSING"),),
        )


def test_comparison_current_side_must_be_current_supplier_observation():
    with pytest.raises(ValidationError):
        payload(
            candidates=(candidate(),), observations=(current_obs(), candidate_obs()),
            comparison_requests=(comparison(current="O-ALT", alt="O-ALT"),),
        )


def test_namespace_item_refs_distinguish_equal_textual_ids():
    unresolved_candidate = candidate(
        candidate_id="X", state="GAP", evidence_id=None, source_ref=None,
        captured_at=None, applicability_ref=None, valid_from=None, valid_to=None,
    )
    unresolved_obs = current_obs(
        observation_id="X", state="NOT_EVIDENCED", value_text=None,
        source_ref=None, evidence_id=None, captured_at=None,
    )
    result = evaluate_supplier_evidence(payload(
        candidates=(unresolved_candidate,), observations=(unresolved_obs,),
    ))
    assert [(x.item_type, x.item_id) for x in result.unresolved_items] == [
        ("CANDIDATE", "X"), ("OBSERVATION", "X")
    ]


def test_unresolved_aggregation_preserves_first_appearance_by_domain_then_input_order():
    c2 = candidate("C-2", "SUP-2", state="GAP", evidence_id=None, source_ref=None,
                   captured_at=None, applicability_ref=None, valid_from=None, valid_to=None)
    c1 = candidate("C-1", "SUP-1", state="REFERENCE_ONLY", applicability_ref=None)
    o2 = current_obs("O-2", state="NOT_EVIDENCED", value_text=None,
                     source_ref=None, evidence_id=None, captured_at=None)
    o1 = current_obs("O-1", state="NOT_EVIDENCED", value_text=None,
                     source_ref=None, evidence_id=None, captured_at=None)
    result = evaluate_supplier_evidence(payload(candidates=(c2, c1), observations=(o2, o1)))
    assert [(x.item_type, x.item_id) for x in result.unresolved_items] == [
        ("CANDIDATE", "C-2"), ("CANDIDATE", "C-1"),
        ("OBSERVATION", "O-2"), ("OBSERVATION", "O-1"),
    ]


def test_empty_collections_do_not_claim_business_nonexistence():
    result = evaluate_supplier_evidence(payload())
    assert result.candidate_resolutions == ()
    assert result.unresolved_items == ()
    assert result.conflicting_items == ()


def test_engine_does_not_mutate_payload():
    item = payload(
        candidates=(candidate(),), observations=(current_obs(), candidate_obs()),
        comparison_requests=(comparison(),),
    )
    before = item.model_dump()
    evaluate_supplier_evidence(item)
    assert item.model_dump() == before


def test_result_contains_no_decisional_fields():
    result = evaluate_supplier_evidence(payload(candidates=(candidate(),)))
    forbidden = {
        "supplier_score", "supplier_rank", "preferred_supplier", "supplier_risk_level",
        "reliability_score", "compliance_score", "rule_comparable", "assessment",
        "outcome", "effect", "severity", "recommendation", "crc_result", "purchase_decision",
    }

    def all_keys(value):
        if isinstance(value, dict):
            for key, child in value.items():
                yield key
                yield from all_keys(child)
        elif isinstance(value, (list, tuple)):
            for child in value:
                yield from all_keys(child)

    keys = set(all_keys(result.model_dump()))
    assert forbidden.isdisjoint(keys)
