from datetime import date
from decimal import Decimal

import pytest

from eios.core.capability_adapters import adapt_c0, adapt_price, adapt_qtg, adapt_tco, adapt_twin
from eios.core.decision_twin import ComparisonObservation, DecisionTwinComparison
from eios.core.models import Assessment, DecisionContext, Trace
from eios.core.orchestration import O1ExecutionStatus
from eios.pricing.models import PriceCounts, PriceIntelligenceResult
from eios.tco.models import TCOResult
from eios.quality.gate import QualityCheck, QualityTrustResult


def _trace(trace_id: str) -> Trace:
    return Trace(
        trace_id=trace_id,
        decision_id="D1",
        scenario_id="S1",
        rules_version="R1",
        parameters_version="P1",
        data_snapshot_id="DS1",
        input_fingerprint="a" * 64,
        rule_id="RULE1",
        assessment_status="EVALUABLE",
        assessment_outcome="FALSE",
    )


def _price(status: str) -> PriceIntelligenceResult:
    sufficient = status == "PR_AVAILABLE"
    limited = status == "PR_LIMITED"
    selected = 2 if sufficient else 1 if limited else 0
    return PriceIntelligenceResult(
        decision_id="D1", scenario_id="S1", data_snapshot_id="DS1", methodology_version="M1",
        pr_value=Decimal("10.00") if status != "PR_NOT_JUSTIFIABLE" else None,
        currency="EUR" if status != "PR_NOT_JUSTIFIABLE" else None,
        sufficiency_status="SUFFICIENT" if sufficient else "LIMITED" if limited else "NOT_JUSTIFIABLE",
        pr_status=status, pr_limitations=("LIMIT",) if limited else (),
        reference_set=("R1", "R2") if sufficient else ("R1",) if limited else (),
        counts=PriceCounts(n_raw=2 if sufficient else 1 if limited else 0, n_unique=2 if sufficient else 1 if limited else 0, n_comparable=2 if sufficient else 1 if limited else 0, n_representative=2 if sufficient else 1 if limited else 0, n_selected=selected),
        aggregation_method="MEDIAN_UNWEIGHTED", trace_references=("TRACE-PRICE",),
    )


def test_c0_false_is_completed_not_failed():
    assessment = Assessment(rule_id="RULE1", status="EVALUABLE", outcome="FALSE", evidence_ids=[], reason="evaluated")
    result = adapt_c0((assessment,), (_trace("TRACE-C0"),))
    assert result.status == O1ExecutionStatus.COMPLETED
    assert result.result_available is True


def test_c0_not_evaluable_remains_not_evaluable():
    assessment = Assessment(rule_id="RULE1", status="NOT_EVALUABLE", outcome=None, evidence_ids=[], reason="missing evidence")
    result = adapt_c0((assessment,), (_trace("TRACE-C0"),))
    assert result.status == O1ExecutionStatus.NOT_EVALUABLE
    assert result.result_available is False


def test_c0_cardinality_mismatch_is_rejected():
    with pytest.raises(ValueError):
        adapt_c0((), (_trace("TRACE-C0"),))


def test_price_available_and_limited_are_completed():
    assert adapt_price(_price("PR_AVAILABLE")).status == O1ExecutionStatus.COMPLETED
    limited = adapt_price(_price("PR_LIMITED"))
    assert limited.status == O1ExecutionStatus.COMPLETED
    assert limited.result_available is True
    assert limited.unresolved_items == ()


def test_price_not_justifiable_is_not_evaluable():
    result = adapt_price(_price("PR_NOT_JUSTIFIABLE"))
    assert result.status == O1ExecutionStatus.NOT_EVALUABLE
    assert result.result_available is False


def test_tco_incomplete_is_partial_and_preserves_unresolved_components():
    result = adapt_tco(TCOResult(decision_id="D1", scenario_id="S1", currency="EUR", value=None, unresolved_components=("TRANSPORT",), limitations=("MISSING_AMOUNT:TRANSPORT",)))
    assert result.status == O1ExecutionStatus.PARTIALLY_COMPLETED
    assert result.unresolved_items == ("TRANSPORT",)


def test_qtg_no_apto_is_still_completed_execution():
    result = adapt_qtg(QualityTrustResult(status="NO_APTO", confidence="BAJA", checks=(QualityCheck(control="C1", satisfied=False, critical=True),)))
    assert result.status == O1ExecutionStatus.COMPLETED
    assert result.result_available is True
    assert result.trace_references == ()


def test_qtg_evidence_refs_are_not_relabelled_as_trace_refs():
    result = adapt_qtg(QualityTrustResult(status="APTO", confidence="ALTA", checks=(QualityCheck(control="C1", satisfied=True, evidence_refs=("E1",)),)))
    assert result.trace_references == ()


def _twin(*, missing_attributes=(), trace_refs=("TRACE-TWIN",)):
    return DecisionTwinComparison(
        alternatives=("A", "B"),
        observations=(ComparisonObservation(attribute="price", values=(("A", 10), ("B", 12)), comparable=True, difference=True),),
        missing_attributes=missing_attributes,
        trace_refs=trace_refs,
    )


def test_twin_complete_is_completed():
    result = adapt_twin(_twin())
    assert result.status == O1ExecutionStatus.COMPLETED
    assert result.result_available is True
    assert result.trace_references == ("TRACE-TWIN",)
    assert result.unresolved_items == ()


def test_twin_missing_attributes_are_partial_not_completed():
    result = adapt_twin(_twin(missing_attributes=("delivery",)))
    assert result.status == O1ExecutionStatus.PARTIALLY_COMPLETED
    assert result.result_available is False
    assert result.unresolved_items == ("delivery",)
    assert result.trace_references == ("TRACE-TWIN",)
