"""F6.7 — integral failures invalidate stale F6.6 success and stop closed."""
from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
for fixture_name in (
    "f6_2_external_company_adapter",
    "f6_3_documentary_boundary_consumer",
    "f6_4_custody_consumer",
    "f6_5_onboarding_consumer",
):
    sys.path.insert(0, str(ROOT / "tests" / "fixtures" / fixture_name / "src"))

from eios_onboarding_example.demo import fixture  # noqa: E402
from eios_onboarding_example.onboarding import review_with_onboarded_providers  # noqa: E402
from eios_onboarding_example.pilot import assess_read_only_rehearsal  # noqa: E402
from eios_onboarding_example.pilot_demo import manifest_for  # noqa: E402
from eios_onboarding_example.safe_stop import revalidate_before_rehearsal_reuse  # noqa: E402
from eios_onboarding_example.safe_stop_demo import run  # noqa: E402


def ready(tmp_path, company="EXTERNAL_COMPANY_A"):
    folder = tmp_path / company
    folder.mkdir()
    prepared, request, pin, registry, endpoints = fixture(company, folder)
    technical = review_with_onboarded_providers(
        prepared=prepared, request=request, pin=pin,
        registry_source=registry, endpoints=endpoints,
    )
    manifest = manifest_for(pin, request)
    previous = assess_read_only_rehearsal(
        manifest=manifest, pin=pin, request=request,
        technical_review=technical,
    )
    assert previous.synthetic_rehearsal_complete is True
    return [prepared, request, pin, registry, endpoints, manifest, previous]


def revalidate(items):
    return revalidate_before_rehearsal_reuse(
        previous=items[6], manifest=items[5], prepared=items[0],
        request=items[1], pin=items[2],
        registry_source=items[3], endpoints=items[4],
    )


def assert_stopped(result, code=None):
    assert result.status == "SAFE_STOPPED"
    assert result.previous_result_invalidated is True
    assert result.fresh_revalidation_passed is False
    assert result.production_authorized is False
    assert result.decision_authority is False
    assert result.real_pilot_admitted is False
    assert result.operational_path == "FORBIDDEN"
    if code is not None:
        assert code in result.failure_code


def test_demo_proves_one_healthy_revalidation_and_one_revocation_stop(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = run()
    assert result["verification"] == "F6_7_INTEGRAL_SAFE_STOP_SYNTHETIC_PASS"
    assert result["healthy_revalidated"] == 1
    assert result["safe_stopped"] == 1
    assert result["previous_results_invalidated"] == 1
    assert result["production_authorized"] is False
    assert result["decision_authority"] is False
    assert result["operational_path"] == "FORBIDDEN"


def test_unchanged_chain_can_only_revalidate_as_synthetic(tmp_path):
    items = ready(tmp_path)
    result = revalidate(items)
    assert result.status == "SYNTHETIC_CHAIN_REVALIDATED"
    assert result.previous_result_invalidated is False
    assert result.fresh_revalidation_passed is True
    assert result.failure_code is None
    assert result.production_authorized is False
    assert result.operational_path == "FORBIDDEN"


def test_provider_revocation_after_prior_success_invalidates_stale_result(tmp_path):
    items = ready(tmp_path)
    source = items[3]
    source.snapshot = replace(source.snapshot, revision=2)
    result = revalidate(items)
    assert_stopped(result, "ONBOARDING_STALE_OR_REVOKED_REVISION")


def test_provider_expiry_after_prior_success_invalidates_stale_result(tmp_path):
    items = ready(tmp_path)
    source = items[3]
    rows = tuple(
        replace(row, valid_to=items[1].reviewed_at - timedelta(seconds=1))
        if row.role == "DOCUMENT" else row
        for row in source.snapshot.registrations
    )
    source.snapshot = replace(source.snapshot, registrations=rows)
    result = revalidate(items)
    assert_stopped(result, "ONBOARDING_REGISTRY_DIGEST_CHANGED")


def test_document_tampering_after_prior_success_is_safe_stopped(tmp_path):
    items = ready(tmp_path)
    document_endpoint = items[4]["DOCUMENT"].client
    path = document_endpoint.vault.record_path_for_tests(document_endpoint.binding)
    raw = path.read_bytes()
    path.write_bytes(raw.replace(b"content_b64", b"content_b65", 1))
    result = revalidate(items)
    assert_stopped(result, "CUSTODY_SCHEMA_MISMATCH")


def test_company_project_or_snapshot_drift_stops_before_provider_reuse(tmp_path):
    for field in ("company_id", "project_id", "data_snapshot_id"):
        root = tmp_path / field
        root.mkdir()
        items = ready(root)
        items[1] = items[1].model_copy(update={field: "FOREIGN"})
        result = revalidate(items)
        assert_stopped(result, "F6_7_CONTEXT_OR_VERSION_CHANGED")
        assert result.failure_stage == "CONTEXT_REBIND"


def test_provider_interruption_after_prior_success_is_safe_stopped(tmp_path):
    items = ready(tmp_path)
    source = items[4]["IDENTITY"].client
    def interrupted(*args, **kwargs):
        raise RuntimeError("SYNTHETIC_PROVIDER_INTERRUPTED")
    source.resolve_identity = interrupted
    result = revalidate(items)
    assert_stopped(result, "SYNTHETIC_PROVIDER_INTERRUPTED")


def test_permission_revocation_between_fresh_checks_is_propagated_to_safe_stop(tmp_path):
    items = ready(tmp_path)
    permission = items[4]["REVIEW_PERMISSION"].client
    original = permission.resolve_permission
    def revoked(*args, **kwargs):
        value = original(*args, **kwargs)
        if permission.calls >= 2:
            return replace(value, grant_ref="REVOKED_GRANT")
        return value
    permission.resolve_permission = revoked
    result = revalidate(items)
    assert_stopped(result, "SYNTHETIC_TRUST_STATE_CHANGED")


def test_safe_stop_reason_is_deterministic_for_same_failure(tmp_path):
    items = ready(tmp_path)
    items[3].snapshot = replace(items[3].snapshot, revision=2)
    first = revalidate(items)
    second = revalidate(items)
    assert first.failure_code == second.failure_code
    assert first.reasons == second.reasons
    assert first.result_fingerprint == second.result_fingerprint
