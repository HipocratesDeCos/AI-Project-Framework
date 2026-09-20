import base64
from dataclasses import FrozenInstanceError
from hashlib import sha256
import json
from pathlib import Path
import shutil

import pytest

from eios.core._projection_synthetic_foundation import (
    SyntheticSemanticAdapterError, _build_synthetic_foundation,
    _build_synthetic_stage3, _build_synthetic_stage4, _build_synthetic_stage5,
)
from eios.core.projection_criteria_manifest import REQUIRED_FUNCTIONS
from eios.core.projection_mock_dataset import load_projection_mock_dataset
from eios.core.treasury_documentary_support import CONDITIONS as TREASURY_CONDITIONS
from eios.core.treasury_mandate_verification import (
    CONDITIONS as TREASURY_MANDATE_CONDITIONS,
)


STRUCTURAL = Path(__file__).parent / "fixtures" / "projection_only_mock_dataset_01"


def _components():
    document_content = b"Synthetic payment terms"
    document_base64 = base64.b64encode(document_content).decode("ascii")
    document_sha256 = sha256(document_content).hexdigest()
    presented_criteria = []
    authorized_criteria = []
    for index, function in enumerate(REQUIRED_FUNCTIONS, start=1):
        content = f"Synthetic criterion material: {function}".encode()
        digest = sha256(content).hexdigest()
        reference = f"CRITERION-MOCK-{index:03d}"
        presented_criteria.append({
            "reference": reference, "version": "1.0",
            "content_base64": base64.b64encode(content).decode("ascii"),
            "sha256": digest,
        })
        authorized_criteria.append({
            "function": function, "reference": reference, "version": "1.0",
            "content_sha256": digest,
        })
    treasury_criterion = next(
        item for item in authorized_criteria
        if item["function"] == "INITIAL_TREASURY_SUFFICIENCY"
    )

    def encoded_document(reference, content):
        return {
            "document_ref": reference,
            "content_base64": base64.b64encode(content).decode("ascii"),
            "sha256": sha256(content).hexdigest(),
        }

    treasury_document_ref = "TREASURY-DOC-MOCK-001"
    treasury_locator = {
        "document_ref": treasury_document_ref, "page": 1, "section": "Mock balance",
    }
    mandate_documents = [
        encoded_document("TREASURY-MANDATE-DOC-MOCK-001", b"Synthetic treasury mandate"),
    ]
    channel_documents = [
        encoded_document("TREASURY-CHANNEL-DOC-MOCK-001", b"Synthetic channel recognition"),
    ]
    contrast_documents = [
        encoded_document("TREASURY-CONTRAST-DOC-MOCK-001", b"Synthetic mandate contrast"),
    ]
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
            "confirmation_ref": "CONFIRMATION-MOCK-001",
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
        "criteria/projection_criteria.json": {
            "case_kind": "SYNTHETIC",
            "presented_criteria": presented_criteria,
            "manifest": {
                "manifest_ref": "PROJECTION-CRITERIA-MOCK-001",
                "manifest_version": "1.0",
                "authority_ref": "SYNTHETIC-AUTHORITY-MOCK-001",
                "authorized_at": "2026-09-20T10:00:00+00:00",
                "criteria": authorized_criteria,
            },
        },
        "treasury/material.json": {
            "case_kind": "SYNTHETIC",
            "support": {
                "record_ref": "TREASURY-SUPPORT-MOCK-001",
                "target_company_scope": "COMPANY-MOCK-001",
                "case_kind": "SYNTHETIC",
                "documents": [
                    encoded_document(treasury_document_ref, b"Synthetic treasury support"),
                ],
                "declaration": {
                    "documentary_company": "COMPANY-MOCK-001",
                    "currency": "EUR",
                    "economic_date": "2026-09-20",
                    "available_amount": "1000",
                    "locators": [treasury_locator],
                },
                "observations": [{
                    "condition": condition,
                    "outcome": "DECLARED_CONSISTENT",
                    "note": "Synthetic assertion only",
                    "locators": [treasury_locator],
                } for condition in TREASURY_CONDITIONS],
                "reviewer_ref": None,
                "reviewed_at": None,
            },
            "assessment": {
                "assessment_ref": "TREASURY-ASSESSMENT-MOCK-001",
                "declarations": [{
                    "condition": condition,
                    "criterion_reference": treasury_criterion["reference"],
                    "criterion_version": treasury_criterion["version"],
                    "applicability": "APPLIES",
                    "applicability_reason": "Synthetic documentary-cutoff use",
                    "necessity": "NECESSARY_FOR_DETERMINED_PROJECTION",
                    "necessity_reason": "Synthetic contextual assertion",
                    "impact_reason": "Presented explanation only",
                    "support_assessment": "DECLARED_SUFFICIENT",
                    "support_reason": "Synthetic assertion, not source verification",
                    "observation_conditions": [condition],
                    "support_locators": [{
                        "origin": "TREASURY_SUPPORT",
                        **treasury_locator,
                    }],
                } for condition in TREASURY_CONDITIONS],
                "additional_documents": [],
                "additional_case_kind": None,
                "reviewer_ref": None,
                "reviewed_at": None,
            },
        },
        "treasury/mandate.json": {
            "case_kind": "SYNTHETIC",
            "verification_ref": "TREASURY-MANDATE-VERIFY-MOCK-001",
            "company_scope": "COMPANY-MOCK-001",
            "reviewer_ref": "TREASURY-REVIEWER-MOCK-001",
            "mandate_ref": "TREASURY-MANDATE-MOCK-001",
            "target_review_ref": "TREASURY-REVIEW-MOCK-001",
            "verifier_ref": "TREASURY-VERIFIER-MOCK-001",
            "verified_at": "2026-09-20T10:30:00+00:00",
            "channel_ref": "TREASURY-CHANNEL-MOCK-001",
            "channel_kind": "SYNTHETIC_CORPORATE_DIRECTORY",
            "recognition_basis": "INDEPENDENTLY_SUPPORTED",
            "mandate_kind": "SYNTHETIC",
            "mandate_documents": mandate_documents,
            "channel_recognition_documents": channel_documents,
            "contrast_documents": contrast_documents,
            "observations": [{
                "condition": condition,
                "outcome": "CONFIRMED_BY_CONTRAST",
                "note": "Synthetic confirmation only",
                "locators": [{
                    "origin": "CONTRAST_SUPPORT",
                    "document_ref": "TREASURY-CONTRAST-DOC-MOCK-001",
                    "page": 1,
                    "section": "Mock contrast",
                }],
            } for condition in TREASURY_MANDATE_CONDITIONS],
        },
        "treasury/review.json": {
            "case_kind": "SYNTHETIC",
            "review_ref": "TREASURY-REVIEW-MOCK-001",
            "reviewer_ref": "TREASURY-REVIEWER-MOCK-001",
            "reviewed_at": "2026-09-20T10:45:00+00:00",
            "findings": [{
                "condition": condition,
                "outcome": "CONFIRMED_BY_REVIEW",
                "note": "Synthetic review finding only",
                "locators": [treasury_locator],
            } for condition in TREASURY_CONDITIONS],
            "previous_review_ref": None,
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



def test_builds_private_synthetic_criteria_stage(tmp_path):
    dataset = _dataset(tmp_path)
    result = _build_synthetic_stage4(dataset)
    assert result.dataset_fingerprint == dataset.fingerprint
    preparation = result.finance_quality_preparation.to_payload()
    manifest = result.criteria_manifest.to_payload()
    assert preparation["capture_fingerprint"] == result.stage3.payment_capture.fingerprint
    assert preparation["coverage_fingerprint"] == result.stage3.required_installment_coverage.fingerprint
    assert len(preparation["presented_criteria"]) == len(REQUIRED_FUNCTIONS) == 6
    assert manifest["required_functions"] == list(REQUIRED_FUNCTIONS)
    assert manifest["schema_version"] == "QTG-PROJECTION-CRITERIA-MANIFEST-01/v0.2"
    assert preparation["review"] is None and preparation["designation"] is None
    assert not {"quality_result", "quality_checks", "authorized", "status"} & preparation.keys()
    with pytest.raises(FrozenInstanceError):
        result.dataset_fingerprint = "changed"


def test_s4_rejects_valid_but_noncanonical_criterion_base64(tmp_path):
    def noncanonical(values):
        item = values["criteria/projection_criteria.json"]["presented_criteria"][0]
        item["content_base64"] = "Zh=="
        item["sha256"] = sha256(b"f").hexdigest()
    with pytest.raises(SyntheticSemanticAdapterError) as error:
        _build_synthetic_stage4(_dataset(tmp_path, noncanonical))
    assert error.value.code == "CRITERIA_PREPARATION_REJECTED"
    assert "canonical base64" in str(error.value)


def test_s4_rejects_presented_criterion_digest_mismatch(tmp_path):
    def mismatch(values):
        values["criteria/projection_criteria.json"]["presented_criteria"][0][
            "sha256"] = sha256(b"other").hexdigest()
    with pytest.raises(SyntheticSemanticAdapterError) as error:
        _build_synthetic_stage4(_dataset(tmp_path, mismatch))
    assert error.value.code == "CRITERIA_PREPARATION_REJECTED"
    assert "sha256" in str(error.value)


def test_s4_requires_exact_six_manifest_functions(tmp_path):
    def missing(values):
        values["criteria/projection_criteria.json"]["manifest"]["criteria"].pop()
    with pytest.raises(SyntheticSemanticAdapterError) as error:
        _build_synthetic_stage4(_dataset(tmp_path, missing))
    assert error.value.code == "CRITERIA_MANIFEST_REJECTED"
    assert "exact PROJECTION_ONLY" in str(error.value)


def test_s4_rejects_manifest_presented_content_mismatch(tmp_path):
    def mismatch(values):
        values["criteria/projection_criteria.json"]["manifest"]["criteria"][0][
            "content_sha256"] = "0" * 64
    with pytest.raises(SyntheticSemanticAdapterError) as error:
        _build_synthetic_stage4(_dataset(tmp_path, mismatch))
    assert error.value.code == "CRITERIA_BINDING_REJECTED"
    assert error.value.component == "S4"


@pytest.mark.parametrize("mutation,code", [
    (lambda values: values["criteria/projection_criteria.json"].update(
        {"case_kind": "PRESENTED_OPERATIONAL"}), "INVALID_COMPONENT"),
    (lambda values: values["criteria/projection_criteria.json"]["manifest"].update(
        {"authorized_at": "2026-09-20T10:00:00"}), "CRITERIA_MANIFEST_REJECTED"),
])
def test_s4_rejects_operational_promotion_and_naive_authorization_time(
    tmp_path, mutation, code,
):
    with pytest.raises(SyntheticSemanticAdapterError) as error:
        _build_synthetic_stage4(_dataset(tmp_path, mutation))
    assert error.value.code == code


def test_s4_preserves_negative_payment_coverage_without_quality_conclusion(tmp_path):
    def mismatch(values):
        values["finance/finance_input.json"]["cash_flows"][0]["amount"] = "204"
    result = _build_synthetic_stage4(_dataset(tmp_path, mismatch))
    preparation = result.finance_quality_preparation.to_payload()
    assert preparation["coverage"]["required_calendar_matches"] is False
    assert preparation["coverage"]["observations"][0]["issues"] == ["AMOUNT_MISMATCH"]
    assert preparation["assurance_scope"] == "BOUND_PRESENTED_MATERIAL_ONLY"
    assert "quality_result" not in preparation


def test_s4_does_not_execute_finance_quality_or_qtg(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("execution boundary crossed")
    monkeypatch.setattr("eios.finance.engine.calculate_finance_basic", forbidden)
    monkeypatch.setattr("eios.finance.provenance.run_provenanced_finance_basic", forbidden)
    monkeypatch.setattr("eios.quality.gate.evaluate_quality", forbidden)
    result = _build_synthetic_stage4(_dataset(tmp_path))
    assert result.criteria_manifest.to_payload()["profile"] == "PROJECTION_ONLY"



def test_builds_private_synthetic_treasury_stage(tmp_path):
    dataset = _dataset(tmp_path)
    result = _build_synthetic_stage5(dataset)
    assert result.dataset_fingerprint == dataset.fingerprint
    support = result.treasury_support.to_payload()
    assessment = result.treasury_assessment.to_payload()
    mandate = result.treasury_mandate.to_payload()
    review = result.treasury_review.to_payload()
    assert support["preparation_fingerprint"] == (
        result.stage4.finance_quality_preparation.fingerprint)
    assert support["case_kind"] == mandate["mandate_kind"] == "SYNTHETIC"
    assert assessment["pending_conditions"] == []
    assert mandate["verification_outcome"] == "ACREDITADO_POR_CONTRASTE"
    assert review["pending_controls"] == []
    assert review["assurance_scope"] == "AUTHORIZED_REVIEWER_PRESENTED_FINDINGS"
    for payload in (support, assessment, mandate, review):
        assert not {"quality_result", "quality_checks", "status", "confidence"} & payload.keys()
    with pytest.raises(FrozenInstanceError):
        result.dataset_fingerprint = "changed"


def test_s5_rejects_noncanonical_treasury_document_base64(tmp_path):
    def noncanonical(values):
        item = values["treasury/material.json"]["support"]["documents"][0]
        item["content_base64"] = "Zh=="
        item["sha256"] = sha256(b"f").hexdigest()
    with pytest.raises(SyntheticSemanticAdapterError) as error:
        _build_synthetic_stage5(_dataset(tmp_path, noncanonical))
    assert error.value.code == "TREASURY_SUPPORT_REJECTED"
    assert "canonical base64" in str(error.value)


def test_s5_rejects_treasury_document_digest_mismatch(tmp_path):
    def mismatch(values):
        values["treasury/material.json"]["support"]["documents"][0][
            "sha256"] = sha256(b"other").hexdigest()
    with pytest.raises(SyntheticSemanticAdapterError) as error:
        _build_synthetic_stage5(_dataset(tmp_path, mismatch))
    assert error.value.code == "TREASURY_SUPPORT_REJECTED"
    assert "sha256" in str(error.value)


def test_s5_requires_initial_treasury_sufficiency_criterion_binding(tmp_path):
    def wrong_criterion(values):
        other = next(item for item in values["criteria/projection_criteria.json"][
            "manifest"]["criteria"]
            if item["function"] != "INITIAL_TREASURY_SUFFICIENCY")
        declaration = values["treasury/material.json"]["assessment"]["declarations"][0]
        declaration["criterion_reference"] = other["reference"]
        declaration["criterion_version"] = other["version"]
    with pytest.raises(SyntheticSemanticAdapterError) as error:
        _build_synthetic_stage5(_dataset(tmp_path, wrong_criterion))
    assert error.value.code == "TREASURY_ASSESSMENT_REJECTED"
    assert "INITIAL_TREASURY_SUFFICIENCY" in str(error.value)


def test_s5_preserves_unresolved_mandate_and_review_findings(tmp_path):
    def incomplete(values):
        values["treasury/mandate.json"]["observations"] = (
            values["treasury/mandate.json"]["observations"][:1])
        values["treasury/review.json"]["findings"] = (
            values["treasury/review.json"]["findings"][:1])
    result = _build_synthetic_stage5(_dataset(tmp_path, incomplete))
    mandate = result.treasury_mandate.to_payload()
    review = result.treasury_review.to_payload()
    assert mandate["verification_outcome"] == "INCONCLUYENTE"
    assert len(mandate["pending_conditions"]) == 5
    assert review["findings"][0]["outcome"] == "CONFIRMED_BY_REVIEW"
    assert review["assurance_scope"] == "PRESENTED_UNAUTHORIZED_OR_UNRESOLVED_FINDINGS"
    assert len(review["pending_controls"]) == 5


@pytest.mark.parametrize("component,path", [
    ("treasury_material", "treasury/material.json"),
    ("treasury_mandate", "treasury/mandate.json"),
    ("treasury_review", "treasury/review.json"),
])
def test_s5_rejects_operational_promotion(tmp_path, component, path):
    def operational(values):
        values[path]["case_kind"] = "PRESENTED_OPERATIONAL"
    with pytest.raises(SyntheticSemanticAdapterError) as error:
        _build_synthetic_stage5(_dataset(tmp_path, operational))
    assert error.value.code == "INVALID_COMPONENT"
    assert error.value.component == component


def test_s5_rejects_detached_review_identity(tmp_path):
    def detached(values):
        values["treasury/review.json"]["reviewer_ref"] = "OTHER-REVIEWER"
    with pytest.raises(SyntheticSemanticAdapterError) as error:
        _build_synthetic_stage5(_dataset(tmp_path, detached))
    assert error.value.code == "TREASURY_REVIEW_REJECTED"
    assert "Reviewer differs from mandate" in str(error.value)


def test_s5_rejects_naive_verification_time(tmp_path):
    def naive(values):
        values["treasury/mandate.json"]["verified_at"] = "2026-09-20T10:30:00"
    with pytest.raises(SyntheticSemanticAdapterError) as error:
        _build_synthetic_stage5(_dataset(tmp_path, naive))
    assert error.value.code == "TREASURY_MANDATE_REJECTED"
    assert "timezone-aware" in str(error.value)


def test_s5_preserves_unknown_treasury_amount(tmp_path):
    def unknown(values):
        values["treasury/material.json"]["support"]["declaration"]["available_amount"] = None
        for observation in values["treasury/material.json"]["support"]["observations"]:
            if observation["condition"] == "AMOUNT_SUPPORT":
                observation.update(
                    outcome="NOT_ESTABLISHED",
                    note="Synthetic amount not established",
                    locators=[],
                )
    result = _build_synthetic_stage5(_dataset(tmp_path, unknown))
    support = result.treasury_support.to_payload()
    assert support["declaration"]["available_amount"] is None
    assert support["technical_comparisons"]["amount_matches"] is None


def test_s5_does_not_execute_finance_quality_or_qtg(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("execution boundary crossed")
    monkeypatch.setattr("eios.finance.engine.calculate_finance_basic", forbidden)
    monkeypatch.setattr("eios.finance.provenance.run_provenanced_finance_basic", forbidden)
    monkeypatch.setattr("eios.quality.gate.evaluate_quality", forbidden)
    result = _build_synthetic_stage5(_dataset(tmp_path))
    assert result.treasury_review.to_payload()["review_ref"] == "TREASURY-REVIEW-MOCK-001"
