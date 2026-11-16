"""Synthetic QTG/PRICE/HIS003 shared-DIP tests; never operational."""
from datetime import date
from decimal import Decimal
from inspect import signature

import pytest

from eios.core.price_qtg_his003_synthetic_link import (
    link_synthetic_qtg_price_his003, SyntheticPriceHistoryQTGLink,
)
from eios.core.projection_quality_producer import produce_projection_quality
from eios.core.projection_quality_consumer import consume_projection_quality
from eios.core.projection_synthetic_adapter import (
    build_projection_only_synthetic_material_bundle,
)
from eios.pricing.company_coverage import PriceCoverageError
from test_price_his003_reconciliation import fixture as historical_fixture
from test_reference_simulation_execution import _bundle, _qtg, _runtime
from test_projection_synthetic_foundation import _dataset


def sources(qtg_bundle=None):
    qtg_bundle = qtg_bundle or _bundle()
    receipt, consumption = _qtg(qtg_bundle)
    purchase, context = _runtime(qtg_bundle)
    values = historical_fixture()
    reference = values["payload"].references[0].model_copy(update={
        "article_identity": purchase.article_id,
        "supplier_identity": purchase.supplier_id,
        "quantity": purchase.quantity,
    })
    values["payload"].references = (reference,)
    values["payload"].purchase_operation = purchase.model_copy(deep=True)
    values["payload"].decision_context = context.model_copy(deep=True)
    company_id = "COMPANY-MOCK-001"
    values["profile"] = values["profile"].model_copy(update={
        "company_id": company_id,
        "decision_id": context.decision_id,
        "scenario_id": context.scenario_id,
        "parameters_version": context.parameters_version,
        "data_snapshot_id": context.data_snapshot_id,
    })
    values["rule"] = values["rule"].model_copy(
        update={"version": context.rules_version},
    )
    source = values["historical_sources"][0]
    values["historical_sources"] = (source.model_copy(update={
        "dimension_evidences": tuple(
            item.model_copy(update={"captured_at": purchase.operation_date})
            for item in source.dimension_evidences
        ),
    }),)
    values["expected_company_id"] = company_id
    values["purchase"] = purchase
    values["context"] = context
    values.update({
        "envelope": qtg_bundle.envelope,
        "receipt": receipt,
        "consumption": consumption,
    })
    return values


def run(value):
    return link_synthetic_qtg_price_his003(**value)


def test_synthetic_qtg_reconciles_exact_sources_without_authority():
    result = run(sources())
    assert isinstance(result, SyntheticPriceHistoryQTGLink)
    assert result.company_id == "COMPANY-MOCK-001"
    assert result.qtg_quality_status == "NO_APTO"
    assert result.qtg_quality_confidence == "BAJA"
    assert result.price_history.price_result.pr_value == Decimal("20.25")
    assert result.price_history.historical_references[0].assessment.outcome == "FALSE"
    assert result.price_history.qtg_status == "NOT_ASSESSED"
    assert result.execution_mode == "SYNTHETIC_TEST"
    assert result.consumption_scope == "TEST_ONLY"
    assert result.operational_path == "FORBIDDEN"
    assert result.decision_authority is False
    assert result.envelope_fingerprint == sources()["envelope"].fingerprint


def test_synthetic_qtg_reconciliation_is_deterministic():
    arguments = sources()
    left = run(arguments)
    right = run(arguments)
    assert left.model_dump(mode="json") == right.model_dump(mode="json")
    assert left.receipt_fingerprint == arguments["receipt"].fingerprint
    assert left.consumption_fingerprint == arguments["consumption"].fingerprint


@pytest.mark.parametrize("field,value", [
    ("article_id", "FOREIGN-ARTICLE"),
    ("supplier_id", "FOREIGN-SUPPLIER"),
    ("unit_price", Decimal("99")),
])
def test_foreign_purchase_rejected_before_price_or_his003(field, value):
    arguments = sources()
    arguments["purchase"] = arguments["purchase"].model_copy(
        update={field: value},
    )
    with pytest.raises(ValueError, match="QTG DIP purchase"):
        run(arguments)


@pytest.mark.parametrize("field,value", [
    ("data_snapshot_id", "FOREIGN-SNAPSHOT"),
    ("parameters_version", "FOREIGN-PARAM"),
    ("rules_version", "FOREIGN-RULES"),
])
def test_foreign_decision_context_rejected(field, value):
    arguments = sources()
    arguments["context"] = arguments["context"].model_copy(
        update={field: value},
    )
    with pytest.raises(ValueError, match="QTG DIP context"):
        run(arguments)


def test_other_company_rejected_against_qtg_dip():
    arguments = sources()
    arguments["expected_company_id"] = "FOREIGN-COMPANY"
    with pytest.raises(ValueError, match="company scope"):
        run(arguments)


def test_unvalidated_qtg_receipt_payload_is_rejected():
    arguments = sources()
    arguments["receipt"] = arguments["receipt"].to_payload()
    with pytest.raises(TypeError, match="ProjectionQualityReceipt"):
        run(arguments)


def test_plain_qtg_status_is_not_an_accepted_input():
    params = signature(link_synthetic_qtg_price_his003).parameters
    assert "qtg_status" not in params
    assert "qtg_result" not in params
    assert "mode" not in params
    assert "receipt" in params and "consumption" in params
    assert "envelope" in params


def test_missing_price_economic_evidence_rejected_even_with_valid_qtg():
    arguments = sources()
    arguments["payload"].economic_basis_comparisons = tuple(
        item for item in arguments["payload"].economic_basis_comparisons
        if item.dimension != "TAX"
    )
    with pytest.raises(PriceCoverageError):
        run(arguments)


def test_forged_his003_evidence_rejected_despite_valid_qtg():
    arguments = sources()
    group = arguments["historical_sources"][0]
    forged = group.dimension_evidences[0].model_copy(
        update={"demonstration_ref": "his003_dimension:wrong"},
    )
    arguments["historical_sources"] = (
        group.model_copy(update={
            "dimension_evidences": (forged, *group.dimension_evidences[1:]),
        }),
    )
    with pytest.raises(ValueError, match="determinación exacta"):
        run(arguments)


def test_synthetic_qtg_apto_does_not_create_operational_authority(tmp_path):
    def complete(values):
        values["flows/inventory.json"]["perimeters"][0]["limitations"] = []
        for finding in values["flows/review.json"]["findings"]:
            if finding["condition"] in {
                "HORIZON_CLASSIFICATION",
                "FLOW_ATTRIBUTE_SUPPORT",
                "ECONOMIC_DUPLICATION",
            }:
                finding["flow_ids"] = ["FLOW-MOCK-PAYMENT-001"]

    bundle = build_projection_only_synthetic_material_bundle(
        _dataset(tmp_path, complete),
    )
    report = run(sources(bundle))
    assert report.qtg_quality_status == "APTO"
    assert report.qtg_quality_confidence == "ALTA"
    assert report.operational_path == "FORBIDDEN"
    assert report.decision_authority is False


def test_synthetic_receipt_cannot_be_substituted_by_operational_mode():
    arguments = sources()
    with pytest.raises(ValueError):
        produce_projection_quality(
            envelope=arguments["envelope"],
            execution_mode="OPERATIONAL",
        )


def test_crossed_qtg_envelope_rejected_before_reconciliation(tmp_path):
    first = sources()
    def changed(values):
        values["flows/inventory.json"]["perimeters"][0][
            "coverage_reason"
        ] = "Foreign valid synthetic material"

    different = build_projection_only_synthetic_material_bundle(
        _dataset(tmp_path, changed),
    )
    first["envelope"] = different.envelope
    with pytest.raises(ValueError):
        run(first)


def test_qtg_link_retains_source_values():
    arguments = sources()
    before = arguments["payload"].model_dump(mode="json")
    run(arguments)
    assert arguments["payload"].model_dump(mode="json") == before
