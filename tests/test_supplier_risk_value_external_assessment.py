from datetime import date
from decimal import Decimal
from inspect import signature

import pytest
from pydantic import ValidationError

from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.core.mvp_execution import MVP_CAPABILITY_ORDER, run_mvp_execution
from eios.core.orchestration import O1ExecutionStatus
from eios.supplier import (
    SupplierRiskDimensionAssessment,
    SupplierRiskValueResult,
    SupplierValueDimensionAssessment,
    SupplierEvidenceResult,
    SupplierResultIdentity,
    build_provenanced_supplier_risk_value_invoker,
    produce_supplier_risk_value,
)


def _context():
    return DecisionContext(
        decision_id="D-SRV",
        scenario_id="S-SRV",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snap-v1",
    )


def _purchase():
    return PurchaseOperation(
        decision_id="D-SRV",
        scenario_id="S-SRV",
        article_id="ART-1",
        supplier_id="SUP-CUR",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=date(2026, 9, 23),
    )


def _supplier_result():
    return SupplierEvidenceResult(
        identity=SupplierResultIdentity(
            decision_id="D-SRV",
            scenario_id="S-SRV",
            rules_version="rules-v1",
            parameters_version="params-v1",
            data_snapshot_id="snap-v1",
            company_scope="COMPANY-1",
            article_id="ART-1",
            evaluation_date=date(2026, 9, 23),
            methodology_version="0.3",
        ),
        current_supplier_id="SUP-CUR",
        candidates=(),
        candidate_resolutions=(),
    )


def _evidences():
    return (
        Evidence(
            evidence_id="E-AUTH-RISK",
            source_type="supplier-risk",
            source_ref="external:risk",
            captured_at=date(2026, 9, 23),
            state="DEMONSTRATED",
            demonstration_ref="authority:risk:v1",
        ),
        Evidence(
            evidence_id="E-AUTH-VALUE",
            source_type="supplier-value",
            source_ref="external:value",
            captured_at=date(2026, 9, 23),
            state="DEMONSTRATED",
            demonstration_ref="authority:value:v1",
        ),
        Evidence(
            evidence_id="E-RISK",
            source_type="supplier-risk",
            source_ref="external:risk:assessment",
            captured_at=date(2026, 9, 23),
            state="DEMONSTRATED",
            demonstration_ref="assessment:risk:1",
        ),
        Evidence(
            evidence_id="E-VALUE",
            source_type="supplier-value",
            source_ref="external:value:assessment",
            captured_at=date(2026, 9, 23),
            state="DEMONSTRATED",
            demonstration_ref="assessment:value:1",
        ),
    )


def _risk(**overrides):
    data = dict(
        supplier_id="SUP-CUR",
        dimension="RELIABILITY",
        state="FAVORABLE",
        authority_ref="authority:risk:v1",
        methodology_ref="method:risk:v1",
        assessment_ref="assessment:risk:1",
        evidence_refs=("E-RISK",),
        trace_refs=("TRACE-RISK",),
    )
    data.update(overrides)
    return SupplierRiskDimensionAssessment(**data)


def _value(**overrides):
    data = dict(
        supplier_id="SUP-CUR",
        comparison_supplier_id="SUP-ALT",
        dimension="PRICE",
        state="BETTER",
        authority_ref="authority:value:v1",
        methodology_ref="method:value:v1",
        assessment_ref="assessment:value:1",
        evidence_refs=("E-VALUE",),
        trace_refs=("TRACE-VALUE",),
    )
    data.update(overrides)
    return SupplierValueDimensionAssessment(**data)


def _supplier_result_with_alt():
    base = _supplier_result()
    from eios.supplier import SupplierCandidateEvidence, CandidateResolution
    candidate = SupplierCandidateEvidence(
        candidate_id="C-1",
        supplier_id="SUP-ALT",
        object_id="ART-1",
        state="CURRENT_OPERATION_DEMONSTRATED",
        evidence_id="E-CAND",
        source_ref="candidate:src",
        captured_at=date(2026, 9, 23),
        applicability_ref="candidate:applicable",
    )
    resolution = CandidateResolution(
        candidate_id="C-1",
        supplier_id="SUP-ALT",
        state="EVIDENCED_CANDIDATE",
    )
    return base.model_copy(update={
        "candidates": (candidate,),
        "candidate_resolutions": (resolution,),
    })


def test_risk_favorable_and_adverse_are_preserved_without_aggregation():
    result = produce_supplier_risk_value(
        purchase=_purchase(),
        context=_context(),
        supplier_result=_supplier_result(),
        risk_assessments=(
            _risk(state="FAVORABLE"),
            _risk(dimension="COMPLIANCE", state="ADVERSE", assessment_ref="assessment:risk:2"),
        ),
        value_assessments=(),
        evidences=_evidences(),
    )
    assert [x.state for x in result.risk_dimensions] == ["ADVERSE", "FAVORABLE"]
    assert result.unresolved_items == ()


@pytest.mark.parametrize("state", ["NOT_DETERMINABLE", "CONFLICTING"])
def test_unresolved_risk_states_are_explicit(state):
    result = produce_supplier_risk_value(
        purchase=_purchase(),
        context=_context(),
        supplier_result=_supplier_result(),
        risk_assessments=(_risk(state=state),),
        value_assessments=(),
        evidences=_evidences(),
    )
    assert len(result.unresolved_items) == 1
    assert state in result.unresolved_items[0]


def test_value_better_requires_comparison_supplier():
    with pytest.raises(ValidationError, match="comparison_supplier_id"):
        _value(comparison_supplier_id=None)


def test_value_self_comparison_is_rejected():
    with pytest.raises(ValidationError, match="consigo mismo"):
        _value(comparison_supplier_id="SUP-CUR")


def test_value_better_is_preserved_only_with_authorized_external_assessment():
    result = produce_supplier_risk_value(
        purchase=_purchase(),
        context=_context(),
        supplier_result=_supplier_result_with_alt(),
        risk_assessments=(),
        value_assessments=(_value(),),
        evidences=_evidences(),
    )
    assert result.value_dimensions[0].state == "BETTER"
    assert result.value_dimensions[0].comparison_supplier_id == "SUP-ALT"


def test_authority_ref_must_be_demonstrated():
    with pytest.raises(ValueError, match="authority_ref no demostrada"):
        produce_supplier_risk_value(
            purchase=_purchase(),
            context=_context(),
            supplier_result=_supplier_result(),
            risk_assessments=(_risk(authority_ref="missing:authority"),),
            value_assessments=(),
            evidences=_evidences(),
        )


def test_gap_does_not_authorize_assessment():
    gap = Evidence(
        evidence_id="E-AUTH-RISK",
        source_type="supplier-risk",
        source_ref="external:risk",
        captured_at=date(2026, 9, 23),
        state="GAP",
    )
    evidences = (gap, *_evidences()[1:])
    with pytest.raises(ValueError, match="authority_ref no demostrada"):
        produce_supplier_risk_value(
            purchase=_purchase(),
            context=_context(),
            supplier_result=_supplier_result(),
            risk_assessments=(_risk(),),
            value_assessments=(),
            evidences=evidences,
        )


def test_supplier_result_identity_mismatch_fails_closed():
    bad = _supplier_result().model_copy(
        update={"identity": _supplier_result().identity.model_copy(update={"data_snapshot_id": "OTHER"})}
    )
    with pytest.raises(ValueError, match="data_snapshot_id"):
        produce_supplier_risk_value(
            purchase=_purchase(),
            context=_context(),
            supplier_result=bad,
            risk_assessments=(_risk(),),
            value_assessments=(),
            evidences=_evidences(),
        )


def test_duplicate_risk_dimension_is_rejected():
    with pytest.raises(ValueError, match="Risk duplicada"):
        produce_supplier_risk_value(
            purchase=_purchase(),
            context=_context(),
            supplier_result=_supplier_result(),
            risk_assessments=(_risk(), _risk(assessment_ref="other")),
            value_assessments=(),
            evidences=_evidences(),
        )


def test_result_has_no_score_rank_or_recommendation_fields():
    fields = set(SupplierRiskValueResult.model_fields)
    forbidden = {
        "score", "supplier_score", "value_score", "risk_score",
        "rank", "selected_supplier", "preferred_supplier", "recommendation",
    }
    assert forbidden.isdisjoint(fields)


def test_ordering_is_deterministic():
    result = produce_supplier_risk_value(
        purchase=_purchase(),
        context=_context(),
        supplier_result=_supplier_result(),
        risk_assessments=(
            _risk(dimension="RELIABILITY", assessment_ref="R2"),
            _risk(dimension="AVAILABILITY", assessment_ref="R1"),
        ),
        value_assessments=(),
        evidences=_evidences(),
    )
    assert [x.dimension for x in result.risk_dimensions] == ["AVAILABILITY", "RELIABILITY"]


def test_o1_invoker_completed_without_unresolved():
    invoker = build_provenanced_supplier_risk_value_invoker(
        supplier_result=_supplier_result(),
        risk_assessments=(_risk(),),
        value_assessments=(),
        evidences=_evidences(),
    )
    execution = invoker(_purchase(), _context())
    assert execution.capability == "SUPPLIER_RISK_VALUE"
    assert execution.status == O1ExecutionStatus.COMPLETED
    assert execution.result_available is True


def test_o1_invoker_partial_with_unresolved_but_result_available():
    invoker = build_provenanced_supplier_risk_value_invoker(
        supplier_result=_supplier_result(),
        risk_assessments=(_risk(state="NOT_DETERMINABLE"),),
        value_assessments=(),
        evidences=_evidences(),
    )
    execution = invoker(_purchase(), _context())
    assert execution.status == O1ExecutionStatus.PARTIALLY_COMPLETED
    assert execution.result_available is True
    assert execution.unresolved_items


def test_o1_execution_exposes_supplier_risk_value_before_c0_without_raw_result():
    invoker = build_provenanced_supplier_risk_value_invoker(
        supplier_result=_supplier_result(),
        risk_assessments=(_risk(),),
        value_assessments=(),
        evidences=_evidences(),
    )
    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=_context(),
        policy_version="SRV-1",
        supplier_risk_value_invoker=invoker,
        rules_invoker=lambda *_: __import__(
            "eios.core.orchestration", fromlist=["CapabilityExecution"]
        ).CapabilityExecution(
            capability="C0",
            status=O1ExecutionStatus.COMPLETED,
            result_available=True,
        ),
    )
    assert tuple(x.capability for x in outcome.capability_results) == (
        "SUPPLIER_RISK_VALUE",
        "C0",
    )
    params = signature(run_mvp_execution).parameters
    assert "supplier_risk_value_invoker" in params
    assert "supplier_risk_value_result" not in params
    assert MVP_CAPABILITY_ORDER.index("SUPPLIER_RISK_VALUE") < MVP_CAPABILITY_ORDER.index("C0")
