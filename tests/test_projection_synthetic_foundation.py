import base64
from dataclasses import FrozenInstanceError
from hashlib import sha256
import json
from pathlib import Path
import shutil

import pytest

from eios.core._projection_synthetic_foundation import (
    SyntheticSemanticAdapterError, _build_synthetic_foundation,
    _build_synthetic_stage3,
)
from eios.core.projection_mock_dataset import load_projection_mock_dataset


STRUCTURAL = Path(__file__).parent / "fixtures" / "projection_only_mock_dataset_01"


def _components():
    document_content = b"Synthetic payment terms"
    document_base64 = base64.b64encode(document_content).decode("ascii")
    document_sha256 = sha256(document_content).hexdigest()
    return {
        "identity/operation.json": {
            "case_kind": "SYNTHETIC",
            "purchase": {"decision_id": "DECISION-MOCK-001", "scenario_id": "SCENARIO-MOCK-001",
                "article_id": "ARTICLE-MOCK-001", "supplier_id": "SUPPLIER-MOCK-001",
                "quantity": "10", "unit_price": "20.50", "currency": "EUR",
                "operation_date": "2026-09-20"},
            "evidence": [{"evidence_id": "EVIDENCE-MOCK-001", "source_type": "SYNTHETIC_FIXTURE",
                "source_ref": "mock:operation", "captured_at": "2026-09-20", "state": "GAP",
                "demonstration_ref": None}],
        },
        "identity/decision_context.json": {
            "case_kind": "SYNTHETIC", "decision_id": "DECISION-MOCK-001",
            "scenario_id": "SCENARIO-MOCK-001", "rules_version": "RULES-MOCK-001",
            "parameters_version": "PARAMETERS-MOCK-001", "data_snapshot_id": "SNAPSHOT-MOCK-001",
        },
        "finance/finance_input.json": {
            "case_kind": "SYNTHETIC", "company_id": "COMPANY-MOCK-001",
            "effective_at": "2026-09-20T10:00:00+00:00",
            "snapshot": {"company_scope": "COMPANY-MOCK-001", "as_of_date": "2026-09-20",
                "data_snapshot_id": "SNAPSHOT-MOCK-001", "currency": "EUR",
                "available_treasury": "1000", "treasury_evidence_ref": "mock:treasury",
                "external_liquidity": None},
            "cash_flows": [{"flow_id": "FLOW-MOCK-PAYMENT-001", "flow_type": "PAYMENT",
                "amount": "205", "currency": "EUR", "due_date": "2026-09-25",
                "due_date_evidenced": True, "source_ref": "mock:payment",
                "evidence_state": "DEMONSTRATED"}],
            "horizon_days": 30, "treasury_minimum": "100", "working_capital_input": None,
        },
        "finance/parameter_resolutions.json": {
            "case_kind": "SYNTHETIC", "requested_parameter_ids": ["P-FIN-001", "P-FIN-002"],
            "definitions": [
                {"parameter_id": "P-FIN-001", "value_type": "numeric", "unit": "días", "restricted": False},
                {"parameter_id": "P-FIN-002", "value_type": "numeric", "unit": "EUR", "restricted": False}],
            "configurations": [
                {"configuration_id": 1, "parameter_id": "P-FIN-001", "company_id": "COMPANY-MOCK-001",
                    "value": "30", "value_type": "numeric", "unit": "días",
                    "valid_from": "2026-09-01T00:00:00+00:00", "valid_to": None,
                    "created_at": "2026-09-01T00:00:00+00:00", "updated_at": "2026-09-01T00:00:00+00:00"},
                {"configuration_id": 2, "parameter_id": "P-FIN-002", "company_id": "COMPANY-MOCK-001",
                    "value": "100", "value_type": "numeric", "unit": "EUR",
                    "valid_from": "2026-09-01T00:00:00+00:00", "valid_to": None,
                    "created_at": "2026-09-01T00:00:00+00:00", "updated_at": "2026-09-01T00:00:00+00:00"}],
        },
        "documents/payment_documents.json": {
            "case_kind": "SYNTHETIC", "operation_ref": "OPERATION-MOCK-001",
            "order_ref": "ORDER-MOCK-001", "order_version": "1",
            "confirmation_ref": "CONFIRMATION-MOCK-001", "external_review_ref": None,
            "documents": [{"document_ref": "PAYMENT-DOC-MOCK-001",
                "content_base64": document_base64, "sha256": document_sha256}],
            "bindings": [{"installment_ref": "INSTALLMENT-MOCK-001",
                "flow_id": "FLOW-MOCK-PAYMENT-001",
                "locators": [{"document_ref": "PAYMENT-DOC-MOCK-001", "page": 1,
                    "section": "Payment terms"}]}],
        },
        "documents/required_installment_calendar.json": {
            "case_kind": "SYNTHETIC", "declaration_ref": "CALENDAR-MOCK-001",
            "authority_ref": "AUTHORITY-MOCK-001", "operation_ref": "OPERATION-MOCK-001",
            "order_ref": "ORDER-MOCK-001", "order_version": "1",
            "confirmation_ref": "CONFIRMATION-MOCK-001", "total_due": "205",
            "currency": "EUR",
            "installments": [{"installment_ref": "INSTALLMENT-MOCK-001", "sequence": 1,
                "amount": "205", "currency": "EUR", "due_date": "2026-09-25",
                "locators": [{"document_ref": "PAYMENT-DOC-MOCK-001", "page": 1,
                    "section": "Payment terms"}]}],
        },
    }


def _dataset(tmp_path, mutate=None):
    root = tmp_path / "dataset"
    shutil.copytree(STRUCTURAL, root)
    values = _components()
    if mutate is not None:
        mutate(values)
    manifest_path = root / "dataset_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for relative, value in values.items():
        content = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        (root / relative).write_bytes(content)
        for record in manifest["components"].values():
            if record["path"] == relative:
                record["sha256"] = sha256(content).hexdigest()
                break
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return load_projection_mock_dataset(root)


def test_builds_private_synthetic_identity_and_finance_foundation(tmp_path):
    dataset = _dataset(tmp_path)
    result = _build_synthetic_foundation(dataset)
    assert result.dataset_fingerprint == dataset.fingerprint
    assert result.purchase.supplier_id == "SUPPLIER-MOCK-001"
    assert result.context == result.finance_input.context
    assert result.finance_package.finance_input == result.finance_input
    assert result.finance_package.horizon_resolution.value == "30"
    assert result.finance_package.treasury_minimum_resolution.value == "100"
    with pytest.raises(FrozenInstanceError):
        result.dataset_fingerprint = "changed"


def test_structural_fixture_is_intentionally_semantically_incomplete():
    dataset = load_projection_mock_dataset(STRUCTURAL)
    with pytest.raises(SyntheticSemanticAdapterError) as error:
        _build_synthetic_foundation(dataset)
    assert error.value.code == "INVALID_COMPONENT"
    assert error.value.component == "operation"


@pytest.mark.parametrize("mutation", [
    lambda values: values["identity/operation.json"].update({"unexpected": True}),
    lambda values: values["identity/operation.json"].update({"case_kind": "PRESENTED_OPERATIONAL"}),
    lambda values: values["finance/finance_input.json"].update({"horizon_days": "30"}),
])
def test_rejects_schema_drift_operational_promotion_and_coercion(tmp_path, mutation):
    dataset = _dataset(tmp_path, mutation)
    with pytest.raises(SyntheticSemanticAdapterError) as error:
        _build_synthetic_foundation(dataset)
    assert error.value.code == "INVALID_COMPONENT"


def test_rejects_detached_identity_and_parameter_inventory(tmp_path):
    def detached(values):
        values["identity/decision_context.json"]["decision_id"] = "OTHER"
    with pytest.raises(SyntheticSemanticAdapterError, match="identity mismatch"):
        _build_synthetic_foundation(_dataset(tmp_path, detached))

    def missing_parameter(values):
        values["finance/parameter_resolutions.json"]["definitions"].pop()
    with pytest.raises(SyntheticSemanticAdapterError, match="inventory"):
        _build_synthetic_foundation(_dataset(tmp_path / "other", missing_parameter))


def test_does_not_execute_finance_quality_or_qtg(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("execution boundary crossed")
    monkeypatch.setattr("eios.finance.engine.calculate_finance_basic", forbidden)
    monkeypatch.setattr("eios.finance.provenance.run_provenanced_finance_basic", forbidden)
    monkeypatch.setattr("eios.quality.gate.evaluate_quality", forbidden)
    assert _build_synthetic_foundation(_dataset(tmp_path)).finance_input.cash_flows


def test_requires_validated_dataset():
    with pytest.raises(TypeError):
        _build_synthetic_foundation({})



def test_builds_private_synthetic_payment_stage(tmp_path):
    dataset = _dataset(tmp_path)
    result = _build_synthetic_stage3(dataset)
    assert result.dataset_fingerprint == dataset.fingerprint
    assert result.foundation.finance_package.finance_input == result.foundation.finance_input
    assert result.payment_capture.document_bytes("PAYMENT-DOC-MOCK-001") == b"Synthetic payment terms"
    assert result.required_installment_calendar.total_due == 205
    coverage = result.required_installment_coverage.to_payload()
    assert coverage["required_calendar_matches"] is True
    assert coverage["capture_fingerprint"] == result.payment_capture.fingerprint
    assert "quality_result" not in coverage
    with pytest.raises(FrozenInstanceError):
        result.dataset_fingerprint = "changed"


def test_rejects_valid_but_noncanonical_base64(tmp_path):
    def noncanonical(values):
        document = values["documents/payment_documents.json"]["documents"][0]
        document["content_base64"] = "Zh=="
        document["sha256"] = sha256(b"f").hexdigest()
    with pytest.raises(SyntheticSemanticAdapterError) as error:
        _build_synthetic_stage3(_dataset(tmp_path, noncanonical))
    assert error.value.code == "PAYMENT_CAPTURE_REJECTED"
    assert error.value.component == "payment_documents"
    assert "canonical base64" in str(error.value)


def test_rejects_document_content_digest_mismatch(tmp_path):
    def wrong_digest(values):
        values["documents/payment_documents.json"]["documents"][0]["sha256"] = sha256(b"other").hexdigest()
    with pytest.raises(SyntheticSemanticAdapterError, match="sha256"):
        _build_synthetic_stage3(_dataset(tmp_path, wrong_digest))


@pytest.mark.parametrize("mutation,component", [
    (lambda values: values["documents/payment_documents.json"].update(
        {"case_kind": "PRESENTED_OPERATIONAL"}), "payment_documents"),
    (lambda values: values["documents/required_installment_calendar.json"][
        "installments"][0].update({"sequence": "1"}), "required_installment_calendar"),
])
def test_s3_rejects_operational_promotion_and_coercion(tmp_path, mutation, component):
    with pytest.raises(SyntheticSemanticAdapterError) as error:
        _build_synthetic_stage3(_dataset(tmp_path, mutation))
    assert error.value.code == "INVALID_COMPONENT"
    assert error.value.component == component


def test_s3_preserves_structural_coverage_conflict(tmp_path):
    def mismatch(values):
        values["finance/finance_input.json"]["cash_flows"][0]["amount"] = "204"
    result = _build_synthetic_stage3(_dataset(tmp_path, mismatch))
    coverage = result.required_installment_coverage.to_payload()
    assert coverage["required_calendar_matches"] is False
    assert coverage["observations"][0]["issues"] == ["AMOUNT_MISMATCH"]
    assert result.foundation.finance_input.cash_flows[0].amount == 204


def test_s3_preserves_reference_conflict_for_coverage(tmp_path):
    def mismatch(values):
        values["documents/required_installment_calendar.json"]["order_version"] = "2"
    result = _build_synthetic_stage3(_dataset(tmp_path, mismatch))
    coverage = result.required_installment_coverage.to_payload()
    assert coverage["required_calendar_matches"] is False
    assert coverage["reference_mismatches"] == ["order_version"]


def test_s3_does_not_execute_finance_quality_or_qtg(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("execution boundary crossed")
    monkeypatch.setattr("eios.finance.engine.calculate_finance_basic", forbidden)
    monkeypatch.setattr("eios.finance.provenance.run_provenanced_finance_basic", forbidden)
    monkeypatch.setattr("eios.quality.gate.evaluate_quality", forbidden)
    result = _build_synthetic_stage3(_dataset(tmp_path))
    assert result.required_installment_coverage.to_payload()["required_calendar_matches"]
