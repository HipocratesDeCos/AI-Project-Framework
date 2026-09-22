from datetime import date
from decimal import Decimal
from inspect import signature

import pytest

from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.pricing import (
    HIS003_DIMENSION_EVIDENCE_SOURCE_TYPE,
    HIS003_REQUIRED_DIMENSIONS,
    HistoricalComparabilityDimensionAuthority,
    HistoricalComparabilityDimensionDetermination,
    PriceReference,
    build_historical_commercial_comparability_observation,
    historical_comparability_dimension_ref,
)
from eios.rules.catalog import authorized_rule, authorized_rule_metadata
from eios.rules.history_comparability import R_HIS_003, evaluate_r_his_003
from eios.rules.orchestrator import HistoryComparabilityRuleInputs, run_domain_rules


EVAL_DATE = date(2026, 9, 22)


def _context():
    return DecisionContext(
        decision_id="D-HIS003",
        scenario_id="S-HIS003",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase():
    return PurchaseOperation(
        decision_id="D-HIS003",
        scenario_id="S-HIS003",
        article_id="ART-1",
        supplier_id="SUP-1",
        quantity=Decimal("10"),
        unit_price=Decimal("12"),
        currency="EUR",
        operation_date=EVAL_DATE,
    )


def _reference(*, operation_date=date(2026, 8, 20)):
    return PriceReference(
        source_transaction_id="REF-HIS003-1",
        article_identity="ART-1",
        supplier_identity="SUP-OLD",
        quantity=Decimal("8"),
        unit="unidad",
        unit_price=Decimal("11"),
        currency="EUR",
        operation_date=operation_date,
        commercial_conditions="documented historical terms",
        evidence_refs=("RAW-REF-EV",),
    )


def _authority(dimension):
    return HistoricalComparabilityDimensionAuthority(
        dimension=dimension,
        authority_ref=f"authority:his003:{dimension}",
        methodology_ref=f"methodology:his003:{dimension}",
        version="0.1",
    )


def _determination(dimension, state="EQUIVALENT", *, with_evidence=True):
    evidence_ids = (f"EV-{dimension}",) if with_evidence else ()
    return HistoricalComparabilityDimensionDetermination(
        dimension=dimension,
        state=state,
        authority=_authority(dimension),
        evidence_ids=evidence_ids,
        trace_refs=(f"TRACE-{dimension}",),
        reason=(
            f"{dimension} no determinable"
            if state == "NOT_DETERMINABLE"
            else None
        ),
    )


def _evidence(determination, *, state="DEMONSTRATED", demonstration_ref=None):
    return Evidence(
        evidence_id=determination.evidence_ids[0],
        source_type=HIS003_DIMENSION_EVIDENCE_SOURCE_TYPE,
        source_ref=f"source:{determination.dimension}",
        captured_at=EVAL_DATE,
        state=state,
        demonstration_ref=(
            historical_comparability_dimension_ref(determination)
            if state == "DEMONSTRATED" and demonstration_ref is None
            else demonstration_ref
        ),
    )


def _bundle(*, overrides=None):
    overrides = overrides or {}
    determinations = []
    evidences = []
    for dimension in HIS003_REQUIRED_DIMENSIONS:
        state = overrides.get(dimension, "EQUIVALENT")
        determination = _determination(
            dimension,
            state,
            with_evidence=state != "NOT_DETERMINABLE",
        )
        determinations.append(determination)
        if determination.evidence_ids:
            evidences.append(_evidence(determination))
    return tuple(determinations), tuple(evidences)


def _evaluate(*, overrides=None, reference=None):
    determinations, evidences = _bundle(overrides=overrides)
    return evaluate_r_his_003(
        purchase=_purchase(),
        context=_context(),
        rule=authorized_rule(R_HIS_003, "rules-v1"),
        reference=reference or _reference(),
        dimension_determinations=determinations,
        dimension_evidences=evidences,
    )


def test_any_material_difference_triggers_true():
    result = _evaluate(overrides={"PAYMENT_TERM": "MATERIALLY_DIFFERENT"})
    assert result.status == "EVALUABLE"
    assert result.outcome == "TRUE"


def test_material_difference_remains_sufficient_with_other_unknown_dimension():
    result = _evaluate(
        overrides={
            "PAYMENT_TERM": "MATERIALLY_DIFFERENT",
            "RAPPELS": "NOT_DETERMINABLE",
        }
    )
    assert result.status == "EVALUABLE"
    assert result.outcome == "TRUE"


def test_all_equivalent_or_not_applicable_is_false():
    result = _evaluate(overrides={"RAPPELS": "NOT_APPLICABLE"})
    assert result.status == "EVALUABLE"
    assert result.outcome == "FALSE"


def test_unresolved_dimension_without_material_difference_is_not_evaluable():
    result = _evaluate(overrides={"DISCOUNTS": "NOT_DETERMINABLE"})
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


def test_not_applicable_requires_evidence():
    with pytest.raises(ValueError, match="requiere evidencia"):
        _determination("RAPPELS", "NOT_APPLICABLE", with_evidence=False)


def test_exactly_seven_dimensions_are_required():
    determinations, evidences = _bundle()
    with pytest.raises(ValueError, match="siete dimensiones"):
        build_historical_commercial_comparability_observation(
            purchase=_purchase(),
            context=_context(),
            reference=_reference(),
            dimension_determinations=determinations[:-1],
            dimension_evidences=evidences[:-1],
        )


def test_forged_dimension_evidence_is_rejected():
    determinations, evidences = _bundle()
    forged_first = _evidence(
        determinations[0],
        demonstration_ref="his003_dimension:forged",
    )
    forged = (forged_first,) + evidences[1:]
    with pytest.raises(ValueError, match="determinación exacta"):
        evaluate_r_his_003(
            purchase=_purchase(),
            context=_context(),
            rule=authorized_rule(R_HIS_003, "rules-v1"),
            reference=_reference(),
            dimension_determinations=determinations,
            dimension_evidences=forged,
        )


def test_future_reference_is_not_evaluable():
    result = _evaluate(reference=_reference(operation_date=date(2026, 9, 23)))
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


def test_metadata_is_r3_medium_without_active_result():
    metadata = authorized_rule_metadata(R_HIS_003, "rules-v1")
    assert metadata.effect == "R3"
    assert metadata.severity == "MEDIA"
    assert metadata.active_result is None


def test_rule_api_does_not_accept_detached_observation():
    parameters = signature(evaluate_r_his_003).parameters
    assert "observation" not in parameters
    assert "reference" in parameters
    assert "dimension_determinations" in parameters
    assert "dimension_evidences" in parameters


def test_orchestrator_executes_his003_bundle():
    determinations, evidences = _bundle(
        overrides={"COMMERCIAL_CONDITIONS": "MATERIALLY_DIFFERENT"}
    )
    result = run_domain_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
        history_comparability=HistoryComparabilityRuleInputs(
            reference=_reference(),
            dimension_determinations=determinations,
            dimension_evidences=evidences,
        ),
    )
    assert R_HIS_003 in result.executed_rule_ids
    assessment = next(x for x in result.assessments if x.rule_id == R_HIS_003)
    assert assessment.outcome == "TRUE"
    assert result.crc_result.consolidated_result == "COMPRAR"


def test_price_comparability_status_is_not_an_input_to_his003():
    parameters = signature(evaluate_r_his_003).parameters
    assert "pricing_result" not in parameters
    assert "pricing_assessment" not in parameters
    assert "price_comparability" not in parameters
