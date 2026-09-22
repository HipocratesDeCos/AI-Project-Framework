from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.parameters.center import Configuration
from eios.parameters.resolution import ResolvedConfiguration
from eios.payment_terms import PaymentTermSemanticAuthority
from eios.rules.catalog import authorized_rule, authorized_rule_metadata
from eios.rules.payment import PAG001ParameterBundle, evaluate_r_pag_001
from eios.supplier.models import (
    SupplierEvidenceResult,
    SupplierObservation,
    SupplierResultIdentity,
)


EFFECTIVE_AT = datetime(2026, 9, 22, 9, 0, tzinfo=timezone.utc)
EVAL_DATE = EFFECTIVE_AT.date()


def _context():
    return DecisionContext(
        decision_id="DEC-PAG001",
        scenario_id="SCN-PAG001",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase(supplier_id="SUP-A"):
    return PurchaseOperation(
        decision_id="DEC-PAG001",
        scenario_id="SCN-PAG001",
        article_id="ART-1",
        supplier_id=supplier_id,
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=EVAL_DATE,
    )


def _supplier_result(*, offered_days=60, supplier_id="SUP-A", observations=None):
    identity = SupplierResultIdentity(
        decision_id="DEC-PAG001",
        scenario_id="SCN-PAG001",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
        company_scope="COMP-A",
        article_id="ART-1",
        evaluation_date=EVAL_DATE,
        methodology_version="0.3",
    )
    if observations is None:
        observations = (
            SupplierObservation(
                observation_id="OBS-PAY-1",
                supplier_id=supplier_id,
                candidate_id=None,
                object_id="ART-1",
                dimension="PAYMENT_TERM",
                state="KNOWN",
                value_kind="INTEGER",
                value_integer=offered_days,
                unit="days",
                semantic_ref="SEM-PAG-OFFERED-DAYS",
                source_ref="supplier-source:1",
                evidence_id="EV-SUP-PAY-1",
                captured_at=EVAL_DATE,
                valid_from=EVAL_DATE,
                valid_to=None,
                trace_refs=("trace-supplier-pay-1",),
            ),
        )
    return SupplierEvidenceResult(
        identity=identity,
        current_supplier_id=supplier_id,
        observations=observations,
    )


def _semantic_authority():
    return PaymentTermSemanticAuthority(
        semantic_ref="SEM-PAG-OFFERED-DAYS",
        meaning="OFFERED_PAYMENT_TERM_DAYS",
        authority_ref="authority:pag001-payment-term",
        methodology_ref="methodology:pag001-payment-term",
        version="0.1",
    )


def _resolved(parameter_id, value, unit, *, effective_at=EFFECTIVE_AT):
    cfg = Configuration(
        configuration_id={"P-PAG-002": 2, "P-PAG-003": 3, "P-PAG-004": 4}[parameter_id],
        parameter_id=parameter_id,
        company_id="COMP-A",
        value=str(value),
        value_type="DECIMAL" if parameter_id != "P-PAG-004" else "BOOLEAN",
        unit=unit,
        valid_from=EFFECTIVE_AT - timedelta(days=1),
        valid_to=None,
        created_at=EFFECTIVE_AT - timedelta(days=2),
        updated_at=EFFECTIVE_AT - timedelta(days=1),
    )
    return ResolvedConfiguration(
        configuration=cfg,
        parameters_version="params-v1",
        effective_at=effective_at,
    )


def _evidence(resolved, suffix):
    return Evidence(
        evidence_id=f"EV-{suffix}",
        source_type="ParameterConfigurationEvidence",
        source_ref=f"parameter:{resolved.parameter_id}",
        captured_at=EVAL_DATE,
        state="DEMONSTRATED",
        demonstration_ref=resolved.configuration_ref,
    )


def _bundle(*, target="90", tolerance="15", control="Sí"):
    target_r = _resolved("P-PAG-002", target, "días")
    tolerance_r = _resolved("P-PAG-003", tolerance, "días")
    control_r = _resolved("P-PAG-004", control, "Sí/No")
    return PAG001ParameterBundle(
        target_resolution=target_r,
        target_evidence=_evidence(target_r, "TARGET"),
        tolerance_resolution=tolerance_r,
        tolerance_evidence=_evidence(tolerance_r, "TOL"),
        control_resolution=control_r,
        control_evidence=_evidence(control_r, "CTRL"),
    )


def _evaluate(*, offered_days=60, supplier_result=None, parameters=None):
    context = _context()
    return evaluate_r_pag_001(
        purchase=_purchase(),
        context=context,
        rule=authorized_rule("R-PAG-001", context.rules_version),
        supplier_result=supplier_result or _supplier_result(offered_days=offered_days),
        semantic_authority=_semantic_authority(),
        parameters=parameters or _bundle(),
    )


def test_offered_below_effective_threshold_triggers():
    result = _evaluate(offered_days=60)
    assert result.status == "EVALUABLE"
    assert result.outcome == "TRUE"


def test_equality_with_effective_threshold_is_false():
    result = _evaluate(offered_days=75)
    assert result.status == "EVALUABLE"
    assert result.outcome == "FALSE"


def test_offered_above_effective_threshold_is_false():
    result = _evaluate(offered_days=90)
    assert result.status == "EVALUABLE"
    assert result.outcome == "FALSE"


def test_disabled_term_control_short_circuits_without_false():
    control_r = _resolved("P-PAG-004", "No", "Sí/No")
    parameters = PAG001ParameterBundle(
        target_resolution=None,
        target_evidence=None,
        tolerance_resolution=None,
        tolerance_evidence=None,
        control_resolution=control_r,
        control_evidence=_evidence(control_r, "CTRL"),
    )
    result = _evaluate(
        supplier_result=_supplier_result(observations=()),
        parameters=parameters,
    )
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None
    assert "deshabilitado" in result.reason


def test_missing_term_control_is_not_evaluable():
    parameters = _bundle()
    parameters = PAG001ParameterBundle(
        target_resolution=parameters.target_resolution,
        target_evidence=parameters.target_evidence,
        tolerance_resolution=parameters.tolerance_resolution,
        tolerance_evidence=parameters.tolerance_evidence,
        control_resolution=None,
        control_evidence=None,
    )
    result = _evaluate(parameters=parameters)
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


def test_missing_offered_term_is_not_evaluable():
    result = _evaluate(supplier_result=_supplier_result(observations=()))
    assert result.status == "NOT_EVALUABLE"
    assert "NOT_EVIDENCED" in result.reason


def test_multiple_payment_term_observations_are_not_evaluable():
    first = _supplier_result().observations[0]
    second = first.model_copy(update={"observation_id": "OBS-PAY-2", "evidence_id": "EV-SUP-PAY-2"})
    result = _evaluate(supplier_result=_supplier_result(observations=(first, second)))
    assert result.status == "NOT_EVALUABLE"
    assert "CONFLICTING_DATA" in result.reason


def test_missing_threshold_configuration_is_not_evaluable():
    parameters = _bundle()
    parameters = PAG001ParameterBundle(
        target_resolution=None,
        target_evidence=None,
        tolerance_resolution=parameters.tolerance_resolution,
        tolerance_evidence=parameters.tolerance_evidence,
        control_resolution=parameters.control_resolution,
        control_evidence=parameters.control_evidence,
    )
    result = _evaluate(parameters=parameters)
    assert result.status == "NOT_EVALUABLE"
    assert "MISSING_CONFIGURATION" in result.reason


def test_supplier_identity_mismatch_fails_closed():
    context = _context()
    with pytest.raises(ValueError, match="otro proveedor"):
        evaluate_r_pag_001(
            purchase=_purchase(supplier_id="SUP-B"),
            context=context,
            rule=authorized_rule("R-PAG-001", context.rules_version),
            supplier_result=_supplier_result(supplier_id="SUP-A"),
            semantic_authority=_semantic_authority(),
            parameters=_bundle(),
        )


def test_catalog_metadata_is_r2_high_negotiate():
    metadata = authorized_rule_metadata("R-PAG-001", "rules-v1")
    assert metadata.effect == "R2"
    assert metadata.severity == "ALTA"
    assert metadata.active_result == "NEGOCIAR"


def test_discount_control_is_not_required_by_core():
    result = _evaluate(offered_days=60)
    assert result.outcome == "TRUE"


def test_parameter_effective_context_must_match_exactly():
    target_r = _resolved("P-PAG-002", "90", "días")
    tolerance_r = _resolved("P-PAG-003", "15", "días")
    control_r = _resolved(
        "P-PAG-004",
        "Sí",
        "Sí/No",
        effective_at=EFFECTIVE_AT + timedelta(hours=1),
    )
    parameters = PAG001ParameterBundle(
        target_resolution=target_r,
        target_evidence=_evidence(target_r, "TARGET"),
        tolerance_resolution=tolerance_r,
        tolerance_evidence=_evidence(tolerance_r, "TOL"),
        control_resolution=control_r,
        control_evidence=_evidence(control_r, "CTRL"),
    )
    result = _evaluate(parameters=parameters)
    assert result.status == "NOT_EVALUABLE"
    assert "mismo contexto efectivo" in result.reason


def test_parameter_evidence_id_cannot_be_reused_across_parameters():
    parameters = _bundle()
    assert parameters.control_evidence is not None
    assert parameters.target_evidence is not None
    reused = parameters.target_evidence.model_copy(
        update={
            "evidence_id": parameters.control_evidence.evidence_id,
        }
    )
    parameters = PAG001ParameterBundle(
        target_resolution=parameters.target_resolution,
        target_evidence=reused,
        tolerance_resolution=parameters.tolerance_resolution,
        tolerance_evidence=parameters.tolerance_evidence,
        control_resolution=parameters.control_resolution,
        control_evidence=parameters.control_evidence,
    )
    result = _evaluate(parameters=parameters)
    assert result.status == "NOT_EVALUABLE"
    assert "reutilizada" in result.reason
