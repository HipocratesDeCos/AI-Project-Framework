"""F6.2 independent external-company adapter: tenant, source, schema, provenance."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import sys

import pytest
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/f6_2_external_company_adapter"
sys.path.insert(0, str(FIXTURE / "src"))

from eios_company_adapter_example.adapter import (  # noqa: E402
    AdapterError, CAPABILITIES, ExternalSourceScope,
    prepare_external_case,
)
from eios_company_adapter_example.demo import _record, run  # noqa: E402


def _raw(record):
    return (json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _scope(record, raw=None):
    data = _raw(record) if raw is None else raw
    return ExternalSourceScope(
        project_id=record["project_id"], company_id=record["company_id"],
        source_id=record["source_id"], expected_sha256=hashlib.sha256(data).hexdigest(),
        data_snapshot_id=record["data_snapshot_id"], rules_version="RULES_SYNTH",
        parameters_version="PARAMS_SYNTH", schema_version="v1",
        purpose="SYNTHETIC_TEST_ONLY",
    )


def _producers(calls=None):
    calls = [] if calls is None else calls
    def first(*args):
        calls.append("FIRST")
    def second(*args):
        calls.append("SECOND")
    return dict(zip(CAPABILITIES, (first, second)))


def test_two_external_tenants_run_via_real_catalog_governance_and_kernel(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    outcome = run()
    assert outcome["verification"] == "F6_2_EXTERNAL_SYNTHETIC_COMPANY_ADAPTER_SUCCESS"
    assert outcome["production_authorized"] is False
    assert outcome["operational_path"] == "FORBIDDEN"
    assert outcome["real_source_authentication"] == "NOT_TESTED"
    assert outcome["documentary_admission"] == "NOT_TESTED"
    assert outcome["human_authorization"] == "SYNTHETIC_TEST_DOUBLE_ONLY"
    assert len(outcome["cases"]) == 2
    assert len({r["project_id"] for r in outcome["cases"]}) == 2
    assert len({r["source_sha256"] for r in outcome["cases"]}) == 2
    assert all(r["status"] == "PARTIALLY_COMPLETED" for r in outcome["cases"])
    assert all(r["provenance_status"] == "UNVERIFIED_ADAPTER_RESPONSIBILITY" for r in outcome["cases"])
    assert len(list(tmp_path.glob("catalog_*.json"))) == 2


def test_prepared_case_is_not_an_operational_admission_and_does_not_invoke_producers():
    record = _record("A")
    calls = []
    prepared = prepare_external_case(
        scope=_scope(record), source_bytes=_raw(record), producers=_producers(calls),
    )
    assert calls == []
    assert prepared.company_id == "A"
    assert prepared.context.project_id == "MAINT_A"
    assert prepared.context.data_snapshot_id == "SYNTHETIC_SNAPSHOT_001"
    assert prepared.provenance_status == "UNVERIFIED_ADAPTER_RESPONSIBILITY"
    assert prepared.production_authorized is False
    assert prepared.operational_path == "FORBIDDEN"
    with pytest.raises(TypeError):
        prepared.bindings["FORBIDDEN"] = lambda *_: None


@pytest.mark.parametrize("field", (
    "project_id", "company_id", "source_id", "data_snapshot_id",
))
def test_cross_company_or_source_swap_is_blocked_before_producers(field):
    record = _record("COMPANY_A")
    foreign = {**record, field: "ATTACKER"}
    calls = []
    prepared_scope = _scope(record, _raw(foreign))  # even with recomputed digest
    with pytest.raises(AdapterError, match="EXTERNAL_SCOPE_MISMATCH:" + field):
        prepare_external_case(
            scope=prepared_scope, source_bytes=_raw(foreign), producers=_producers(calls),
        )
    assert calls == []


@pytest.mark.parametrize("change", (
    {"schema_version": "v2"},
    {"evidence_class": "PRESENTED_OPERATIONAL"},
    {"documentary_status": "VERIFIED"},
    {"decision_authority": True},
    {"operational_path": "ALLOWED"},
    {"hours_since_service": -1},
    {"hours_since_service": "100"},
    {"hours_since_service": True},
    {"service_interval_hours": 0},
    {"inspection_reference": ["UNTRUSTED"]},
))
def test_invalid_claims_schema_or_numeric_quality_rejected(change):
    record = {**_record("A"), **change}
    calls = []
    with pytest.raises(AdapterError, match="EXTERNAL_RECORD_SCHEMA_REJECTED"):
        prepare_external_case(
            scope=_scope(record), source_bytes=_raw(record),
            producers=_producers(calls),
        )
    assert calls == []


def test_modified_record_with_original_hash_is_blocked_even_when_payload_is_valid():
    record = _record("A")
    scope = _scope(record)
    changed = {**record, "hours_since_service": 500}
    calls = []
    with pytest.raises(AdapterError, match="SOURCE_HASH_MISMATCH"):
        prepare_external_case(scope=scope, source_bytes=_raw(changed), producers=_producers(calls))
    assert calls == []


@pytest.mark.parametrize("bytes_value,match", (
    (b'{"company_id":"A","company_id":"B"}', "INVALID_EXTERNAL_JSON"),
    (b'{"x": NaN}', "INVALID_EXTERNAL_JSON"),
    (b'[1,2,3]', "SOURCE_MUST_BE_JSON_OBJECT"),
    (b'not-json', "INVALID_EXTERNAL_JSON"),
    (b"\xff\xfe", "INVALID_EXTERNAL_JSON"),
))
def test_unsafe_external_json_does_not_reach_business_producers(bytes_value, match):
    record = _record("A")
    calls = []
    with pytest.raises(AdapterError, match=match):
        prepare_external_case(
            scope=_scope(record, bytes_value), source_bytes=bytes_value,
            producers=_producers(calls),
        )
    assert calls == []


@pytest.mark.parametrize("source", (None, "text", b"", b"x" * 32_769))
def test_missing_or_oversized_bytes_fail_closed(source):
    record = _record("A")
    with pytest.raises(AdapterError, match="INVALID_SOURCE_BYTES_OR_SIZE"):
        prepare_external_case(scope=_scope(record), source_bytes=source, producers=_producers())


def test_missing_undeclared_or_non_callable_producer_rejected():
    record = _record("A")
    for producers in ({}, {"O1": lambda *_: None}, {
        CAPABILITIES[0]: None, CAPABILITIES[1]: lambda *_: None,
    }):
        with pytest.raises(AdapterError, match="EXTERNAL_CAPABILITY_SET_MISMATCH|NONCALLABLE_EXTERNAL_PRODUCER"):
            prepare_external_case(
                scope=_scope(record), source_bytes=_raw(record), producers=producers,
            )


def test_scope_cannot_be_forged_by_source_record():
    record = _record("A")
    scope = _scope(record)
    for change in (
        {"purpose": "PRESENTED_OPERATIONAL"},
        {"expected_sha256": "bad"},
        {"schema_version": "v2"},
        {"company_id": ""},
        {"source_id": None},
    ):
        with pytest.raises(ValidationError):
            ExternalSourceScope.model_validate({**scope.model_dump(), **change})


def test_independent_adapter_imports_only_neutral_eios_packages():
    source_dir = FIXTURE / "src/eios_company_adapter_example"
    python_files = sorted(source_dir.glob("*.py"))
    assert {f.name for f in python_files} == {"__init__.py", "adapter.py", "demo.py"}
    allowed = (
        "eios.kernel.execution", "eios.input_contracts",
        "eios.capability_catalog", "eios.catalog_governance",
    )
    for path in python_files:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.level:
                    continue  # local relative import, no EIOS business dependency
                name = node.module or ""
                if name == "eios" or name.startswith("eios."):
                    assert name in allowed
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "eios" or alias.name.startswith("eios."):
                        assert alias.name in allowed
