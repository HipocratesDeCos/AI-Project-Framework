"""F6.4 adversarial tests: a synthetic vault is not documentary authority."""
from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
import json
import os
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
for fixture in (
    "f6_2_external_company_adapter",
    "f6_3_documentary_boundary_consumer",
    "f6_4_custody_consumer",
):
    sys.path.insert(0, str(ROOT / "tests" / "fixtures" / fixture / "src"))

from eios_custody_example import (  # noqa: E402
    CustodyError, DocumentBinding, SyntheticCustodyVault,
    VaultDocumentProvider,
)
from eios_custody_example.demo import run, _binding  # noqa: E402
from eios_evidence_boundary_example.demo import scenario  # noqa: E402
from eios_evidence_boundary_example.review import (  # noqa: E402
    DocumentaryBoundaryError, review_synthetic_boundary,
)


def setup_case(root: Path, company: str = "EXTERNAL_COMPANY_A"):
    root.mkdir(exist_ok=True)
    vault = SyntheticCustodyVault(root)
    prepared, request, identity, original, grant = scenario(company)
    binding = _binding(request)
    return vault, binding, [prepared, request, identity, original, grant]


def review_with_vault(vault, binding, items):
    return review_synthetic_boundary(
        prepared=items[0], request=items[1],
        identity_source=items[2],
        document_source=VaultDocumentProvider(vault, binding),
        permission_source=items[4],
    )


def test_two_synthetic_companies_via_independent_custody_and_same_f63_api(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = run()
    assert result["verification"] == "F6_4_EXTERNAL_CUSTODY_ISOLATED_SYNTHETIC_PASS"
    assert result["company_count"] == 2
    assert result["immutable_record_count"] == 2
    assert result["production_authorized"] is False
    assert result["operational_path"] == "FORBIDDEN"
    assert result["document_origin_authenticity"] == "NOT_TESTED"
    assert all(case["real_document_authenticated"] is False for case in result["receipts"])
    assert all(case["real_human_authorized"] is False for case in result["receipts"])
    assert len(list((tmp_path / "synthetic-custody").glob("*.json"))) == 2


def test_write_once_and_double_f63_read_remain_synthetic(tmp_path):
    vault, binding, items = setup_case(tmp_path / "vault")
    vault.store_once(binding, items[3].value.content)
    receipt = review_with_vault(vault, binding, items)
    assert receipt.status == "SYNTHETIC_BOUNDARY_CHECKS_PASSED"
    assert receipt.operational_path == "FORBIDDEN"
    assert receipt.real_company_authenticated is False
    assert receipt.real_document_authenticated is False
    assert receipt.real_human_authorized is False
    assert receipt.decision_authority is False
    assert (items[2].calls, items[4].calls) == (2, 2)
    with pytest.raises(CustodyError, match="CUSTODY_RECORD_ALREADY_EXISTS"):
        vault.store_once(binding, items[3].value.content)
    assert len(list(vault.root.glob("*.json"))) == 1


def test_missing_trusted_expected_digest_does_not_write(tmp_path):
    vault, binding, items = setup_case(tmp_path / "vault")
    bad = replace(binding, expected_document_sha256="0" * 64)
    with pytest.raises(CustodyError, match="CUSTODY_SOURCE_DIGEST_MISMATCH"):
        vault.store_once(bad, items[3].value.content)
    assert list(vault.root.glob("*.json")) == []


@pytest.mark.parametrize("field", (
    "company_id", "project_id", "source_id", "data_snapshot_id",
    "document_ref",
))
def test_tenant_or_source_substitution_cannot_read_an_existing_record(tmp_path, field):
    vault, binding, items = setup_case(tmp_path / "vault")
    vault.store_once(binding, items[3].value.content)
    foreign = replace(binding, **{field: "FOREIGN_SCOPE"})
    with pytest.raises(CustodyError, match="CUSTODY_RECORD_NOT_AVAILABLE"):
        vault.load_verified(foreign)
    assert vault.load_verified(binding).content == items[3].value.content


@pytest.mark.parametrize("field", ("project_id", "company_id", "document_ref"))
def test_provider_rejects_foreign_identity_before_reading(tmp_path, field):
    vault, binding, items = setup_case(tmp_path / "vault")
    vault.store_once(binding, items[3].value.content)
    provider = VaultDocumentProvider(vault, binding)
    query = {
        "project_id": binding.project_id, "company_id": binding.company_id,
        "document_ref": binding.document_ref,
    }
    query[field] = "FOREIGN_SCOPE"
    with pytest.raises(CustodyError, match="CUSTODY_PROVIDER_SCOPE_MISMATCH"):
        provider.load_document(**query, reviewed_at=items[1].reviewed_at)


@pytest.mark.parametrize("edit,code", (
    (lambda x: {**x, "company_id": "FOREIGN"}, "CUSTODY_SCOPE_MISMATCH:company_id"),
    (lambda x: {**x, "format_version": 2}, "CUSTODY_FORMAT_MISMATCH"),
    (lambda x: {**x, "assurance": "REAL_AUTHENTICATED"}, "CUSTODY_PROVENANCE_PROMOTION"),
    (lambda x: {**x, "sha256": "0" * 64}, "CUSTODY_PINNED_DIGEST_MISMATCH"),
    (lambda x: {**x, "content_b64": "YQ=="}, "CUSTODY_CONTENT_TAMPERED"),
    (lambda x: {**x, "allowed_operational": True}, "CUSTODY_SCHEMA_MISMATCH"),
    (lambda x: {key: v for key, v in x.items() if key != "assurance"}, "CUSTODY_SCHEMA_MISMATCH"),
))
def test_tampered_files_fail_closed(tmp_path, edit, code):
    vault, binding, items = setup_case(tmp_path / "vault")
    vault.store_once(binding, items[3].value.content)
    path = vault.record_path_for_tests(binding)
    raw = json.loads(path.read_text(encoding="utf-8"))
    path.write_text(json.dumps(edit(raw)), encoding="utf-8")
    with pytest.raises(CustodyError, match=code):
        vault.load_verified(binding)


def test_duplicate_json_keys_and_truncated_files_are_rejected(tmp_path):
    vault, binding, items = setup_case(tmp_path / "vault")
    vault.store_once(binding, items[3].value.content)
    path = vault.record_path_for_tests(binding)
    valid = path.read_bytes()
    path.write_bytes(valid[:-1] + b', "format_version":1}')
    with pytest.raises(CustodyError, match="DUPLICATE_CUSTODY_KEY"):
        vault.load_verified(binding)
    path.write_bytes(b'{"format_version":1')
    with pytest.raises(CustodyError, match="CUSTODY_INVALID_RECORD"):
        vault.load_verified(binding)


def test_missing_or_oversized_custody_record_does_not_create_an_admission(tmp_path):
    vault, binding, items = setup_case(tmp_path / "vault")
    with pytest.raises(CustodyError, match="CUSTODY_RECORD_NOT_AVAILABLE"):
        review_with_vault(vault, binding, items)
    vault.store_once(binding, items[3].value.content)
    vault.record_path_for_tests(binding).write_bytes(b"x" * 96_001)
    with pytest.raises(CustodyError, match="CUSTODY_RECORD_SIZE_INVALID"):
        vault.load_verified(binding)


@pytest.mark.parametrize("invalid", (
    "PRESENTED_OPERATIONAL", "OPERATIONAL", "", None,
))
def test_non_synthetic_purpose_or_missing_value_is_rejected(invalid):
    binding = _binding(scenario("EXTERNAL_COMPANY_A")[1])
    with pytest.raises(CustodyError, match="NON_SYNTHETIC_CUSTODY_FORBIDDEN"):
        replace(binding, purpose=invalid)


@pytest.mark.parametrize("field,value", (
    ("project_id", "../../etc/passwd"),
    ("company_id", "../B"),
    ("document_ref", "/tmp/secret"),
    ("source_id", ""),
    ("data_snapshot_id", "\\..\\"),
))
def test_host_scope_rejects_path_like_identifiers(field, value):
    binding = _binding(scenario("EXTERNAL_COMPANY_A")[1])
    with pytest.raises(CustodyError, match="INVALID_CUSTODY_ID"):
        replace(binding, **{field: value})


def test_symlink_root_rejected_and_symlink_record_rejected_when_supported(tmp_path):
    root = tmp_path / "existing"
    root.mkdir()
    linked_root = tmp_path / "link"
    try:
        linked_root.symlink_to(root, target_is_directory=True)
    except OSError:
        pytest.skip("This platform's runner does not permit symlink creation")
    with pytest.raises(CustodyError, match="UNTRUSTED_CUSTODY_ROOT"):
        SyntheticCustodyVault(linked_root)
    vault, binding, items = setup_case(root)
    target = tmp_path / "target.json"
    target.write_bytes(b"not a verified document")
    vault.record_path_for_tests(binding).symlink_to(target)
    with pytest.raises(CustodyError, match="CUSTODY_SYMLINK_NOT_ALLOWED"):
        vault.load_verified(binding)


def test_no_implicit_root_creation(tmp_path):
    with pytest.raises(CustodyError, match="UNTRUSTED_CUSTODY_ROOT"):
        SyntheticCustodyVault(tmp_path / "missing")


def test_different_digest_cannot_replace_same_document(tmp_path):
    vault, binding, items = setup_case(tmp_path / "vault")
    vault.store_once(binding, items[3].value.content)
    altered = b"ALTERNATE SYNTHETIC DOCUMENT"
    alternate_pin = replace(
        binding, expected_document_sha256=sha256(altered).hexdigest(),
    )
    with pytest.raises(CustodyError, match="CUSTODY_RECORD_ALREADY_EXISTS"):
        vault.store_once(alternate_pin, altered)
    with pytest.raises(CustodyError, match="CUSTODY_PINNED_DIGEST_MISMATCH"):
        vault.load_verified(alternate_pin)


def test_external_document_is_still_unverified_by_identity_permission_double(tmp_path):
    vault, binding, items = setup_case(tmp_path / "vault")
    vault.store_once(binding, items[3].value.content)
    items[4].value = replace(items[4].value, permission="AUTHORIZE_PURCHASE")
    with pytest.raises(DocumentaryBoundaryError, match="REVIEW_PERMISSION_SCOPE_MISMATCH"):
        review_with_vault(vault, binding, items)
