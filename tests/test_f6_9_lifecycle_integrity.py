"""F6.9 — tamper-evident synthetic lifecycle history."""
from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
for fixture_name in (
    "f6_2_external_company_adapter",
    "f6_3_documentary_boundary_consumer",
    "f6_4_custody_consumer",
    "f6_5_onboarding_consumer",
):
    sys.path.insert(0, str(ROOT / "tests" / "fixtures" / fixture_name / "src"))

from eios_custody_example.custody import (  # noqa: E402
    DocumentBinding, SyntheticCustodyVault,
)
from eios_onboarding_example.demo import fixture  # noqa: E402
from eios_onboarding_example.onboarding import (  # noqa: E402
    PinnedOnboarding, fingerprint_provider_snapshot,
    review_with_onboarded_providers,
)
from eios_onboarding_example.pilot import assess_read_only_rehearsal  # noqa: E402
from eios_onboarding_example.pilot_demo import manifest_for  # noqa: E402
from eios_onboarding_example.safe_stop import revalidate_before_rehearsal_reuse  # noqa: E402
from eios_onboarding_example.recovery import recover_after_safe_stop  # noqa: E402
from eios_onboarding_example.lifecycle import (  # noqa: E402
    LifecycleError, record_lifecycle_event, verify_lifecycle_history,
)
from eios_onboarding_example.lifecycle_demo import run  # noqa: E402

SOURCE_ID = "F6_9_LIFECYCLE_JOURNAL"


def complete_case(tmp_path, company="EXTERNAL_COMPANY_A"):
    evidence = tmp_path / ("evidence-" + company)
    journal = tmp_path / ("journal-" + company)
    evidence.mkdir()
    journal.mkdir()
    prepared, request, pin, registry, endpoints = fixture(company, evidence)
    technical = review_with_onboarded_providers(
        prepared=prepared, request=request, pin=pin,
        registry_source=registry, endpoints=endpoints,
    )
    old_manifest = manifest_for(pin, request)
    baseline = assess_read_only_rehearsal(
        manifest=old_manifest, pin=pin, request=request,
        technical_review=technical,
    )
    registry.snapshot = replace(registry.snapshot, revision=2)
    stopped = revalidate_before_rehearsal_reuse(
        previous=baseline, manifest=old_manifest, prepared=prepared,
        request=request, pin=pin, registry_source=registry, endpoints=endpoints,
    )
    fresh_pin = PinnedOnboarding(
        project_id=registry.snapshot.project_id,
        company_id=registry.snapshot.company_id,
        expected_revision=registry.snapshot.revision,
        expected_digest=fingerprint_provider_snapshot(registry.snapshot),
    )
    recovery = recover_after_safe_stop(
        stopped=stopped, stale=baseline, manifest=manifest_for(fresh_pin, request),
        prepared=prepared, request=request, pin=fresh_pin,
        registry_source=registry, endpoints=endpoints,
    )
    vault = SyntheticCustodyVault(journal)
    first = record_lifecycle_event(
        vault=vault, request=request, source=baseline,
        baseline_manifest=old_manifest,
    )
    second = record_lifecycle_event(
        vault=vault, request=request, source=stopped, previous=first,
    )
    third = record_lifecycle_event(
        vault=vault, request=request, source=recovery, previous=second,
    )
    return request, vault, (first, second, third), (baseline, stopped, recovery)


def binding(request, receipt):
    return DocumentBinding(
        project_id=request.project_id,
        company_id=request.company_id,
        source_id=SOURCE_ID,
        data_snapshot_id=request.data_snapshot_id,
        document_ref=receipt.document_ref,
        expected_document_sha256=receipt.event_sha256,
    )


def assert_forbidden(result):
    assert result.production_authorized is False
    assert result.decision_authority is False
    assert result.real_pilot_admitted is False
    assert result.operational_path == "FORBIDDEN"


def test_demo_verifies_complete_hash_linked_history(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    output = run()
    assert output["verification"] == "F6_9_LIFECYCLE_INTEGRITY_SYNTHETIC_PASS"
    assert output["event_count"] == 3
    assert output["history_status"] == "SYNTHETIC_LIFECYCLE_HISTORY_VERIFIED"
    assert len(output["receipts"]) == 3
    assert_forbidden(type("R", (), output)())


def test_complete_history_is_verified_and_deterministic(tmp_path):
    request, vault, receipts, _ = complete_case(tmp_path)
    first = verify_lifecycle_history(
        vault=vault, request=request, receipts=receipts,
    )
    second = verify_lifecycle_history(
        vault=vault, request=request, receipts=receipts,
    )
    assert first == second
    assert first.event_count == 3
    assert first.head_sha256 == receipts[2].event_sha256
    assert_forbidden(first)


@pytest.mark.parametrize("order", ((1, 0, 2), (0, 2, 1), (2, 1, 0)))
def test_reordering_is_rejected(tmp_path, order):
    request, vault, receipts, _ = complete_case(tmp_path)
    shuffled = tuple(receipts[i] for i in order)
    with pytest.raises(LifecycleError):
        verify_lifecycle_history(vault=vault, request=request, receipts=shuffled)


@pytest.mark.parametrize("missing", (0, 1, 2))
def test_missing_event_is_rejected(tmp_path, missing):
    request, vault, receipts, _ = complete_case(tmp_path)
    incomplete = tuple(row for i, row in enumerate(receipts) if i != missing)
    with pytest.raises(LifecycleError, match="COMPLETE_THREE_STAGE_HISTORY_REQUIRED"):
        verify_lifecycle_history(vault=vault, request=request, receipts=incomplete)


def test_deleted_stored_event_is_rejected(tmp_path):
    request, vault, receipts, _ = complete_case(tmp_path)
    vault.record_path_for_tests(binding(request, receipts[1])).unlink()
    with pytest.raises(LifecycleError, match="LIFECYCLE_EVENT_NOT_VERIFIABLE"):
        verify_lifecycle_history(vault=vault, request=request, receipts=receipts)


def test_substituted_stored_bytes_are_rejected(tmp_path):
    request, vault, receipts, _ = complete_case(tmp_path)
    path = vault.record_path_for_tests(binding(request, receipts[1]))
    raw = json.loads(path.read_text(encoding="utf-8"))
    content = raw["content_b64"]
    raw["content_b64"] = ("A" if content[0] != "A" else "B") + content[1:]
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(LifecycleError, match="LIFECYCLE_EVENT_NOT_VERIFIABLE"):
        verify_lifecycle_history(vault=vault, request=request, receipts=receipts)


def test_broken_receipt_hash_link_is_rejected(tmp_path):
    request, vault, receipts, _ = complete_case(tmp_path)
    forged = (
        receipts[0],
        replace(receipts[1], previous_event_sha256="0" * 64),
        receipts[2],
    )
    with pytest.raises(LifecycleError, match="LIFECYCLE_HASH_CHAIN_BROKEN"):
        verify_lifecycle_history(vault=vault, request=request, receipts=forged)


def test_cross_company_receipt_mix_is_rejected(tmp_path):
    request_a, vault_a, receipts_a, _ = complete_case(tmp_path, "EXTERNAL_COMPANY_A")
    _, _, receipts_b, _ = complete_case(tmp_path, "EXTERNAL_COMPANY_B")
    mixed = (receipts_a[0], receipts_b[1], receipts_a[2])
    with pytest.raises(LifecycleError, match="LIFECYCLE_RECEIPT_SCOPE_OR_AUTHORITY_MISMATCH"):
        verify_lifecycle_history(vault=vault_a, request=request_a, receipts=mixed)


def test_forged_authority_receipt_is_rejected(tmp_path):
    request, vault, receipts, _ = complete_case(tmp_path)
    forged = (receipts[0], receipts[1], replace(receipts[2], production_authorized=True))
    with pytest.raises(LifecycleError, match="LIFECYCLE_RECEIPT_SCOPE_OR_AUTHORITY_MISMATCH"):
        verify_lifecycle_history(vault=vault, request=request, receipts=forged)


def test_duplicate_stage_write_is_rejected_by_existing_f6_4_write_once_vault(tmp_path):
    request, vault, _, sources = complete_case(tmp_path)
    with pytest.raises(Exception, match="CUSTODY_RECORD_ALREADY_EXISTS"):
        record_lifecycle_event(
            vault=vault, request=request, source=sources[0],
            baseline_manifest=manifest_for(
                PinnedOnboarding(
                    project_id=request.project_id,
                    company_id=request.company_id,
                    expected_revision=1,
                    expected_digest=sources[0].registry_digest,
                ),
                request,
            ),
        )


def test_safe_stop_must_link_exact_baseline(tmp_path):
    request, vault, receipts, sources = complete_case(tmp_path)
    wrong_first = replace(receipts[0], source_result_fingerprint="0" * 64)
    with pytest.raises(LifecycleError, match="INVALID_F6_7_SAFE_STOP_LINK"):
        record_lifecycle_event(
            vault=vault, request=request, source=sources[1], previous=wrong_first,
        )


def test_recovery_must_link_exact_safe_stop(tmp_path):
    request, vault, receipts, sources = complete_case(tmp_path)
    wrong_stop = replace(receipts[1], source_result_fingerprint="0" * 64)
    with pytest.raises(LifecycleError, match="INVALID_F6_8_RECOVERY_LINK"):
        record_lifecycle_event(
            vault=vault, request=request, source=sources[2], previous=wrong_stop,
        )


def test_baseline_requires_exact_snapshot_manifest(tmp_path):
    evidence = tmp_path / "evidence-snapshot"
    journal = tmp_path / "journal-snapshot"
    evidence.mkdir()
    journal.mkdir()
    prepared, request, pin, registry, endpoints = fixture("EXTERNAL_COMPANY_A", evidence)
    technical = review_with_onboarded_providers(
        prepared=prepared, request=request, pin=pin,
        registry_source=registry, endpoints=endpoints,
    )
    manifest = manifest_for(pin, request)
    baseline = assess_read_only_rehearsal(
        manifest=manifest, pin=pin, request=request, technical_review=technical,
    )
    wrong_manifest = replace(manifest, data_snapshot_id="FOREIGN_SNAPSHOT")
    vault = SyntheticCustodyVault(journal)
    with pytest.raises(LifecycleError, match="INVALID_F6_6_BASELINE"):
        record_lifecycle_event(
            vault=vault, request=request, source=baseline,
            baseline_manifest=wrong_manifest,
        )


def test_recovery_with_wrong_baseline_is_rejected_before_write(tmp_path):
    request, vault, receipts, sources = complete_case(tmp_path)
    forged_recovery = replace(sources[2], stale_result_fingerprint="0" * 64)
    with pytest.raises(LifecycleError, match="INVALID_F6_8_RECOVERY_LINK"):
        record_lifecycle_event(
            vault=vault, request=request, source=forged_recovery,
            previous=receipts[1],
        )


def test_baseline_rejects_manifest_with_same_scope_but_changed_checklist(tmp_path):
    evidence = tmp_path / "evidence-checklist"
    journal = tmp_path / "journal-checklist"
    evidence.mkdir()
    journal.mkdir()
    prepared, request, pin, registry, endpoints = fixture("EXTERNAL_COMPANY_A", evidence)
    technical = review_with_onboarded_providers(
        prepared=prepared, request=request, pin=pin,
        registry_source=registry, endpoints=endpoints,
    )
    manifest = manifest_for(pin, request)
    baseline = assess_read_only_rehearsal(
        manifest=manifest, pin=pin, request=request, technical_review=technical,
    )
    changed_first = replace(manifest.checks[0], support_ref="SYNTHETIC_CHANGED_SUPPORT")
    altered = replace(manifest, checks=(changed_first,) + manifest.checks[1:])
    vault = SyntheticCustodyVault(journal)
    with pytest.raises(LifecycleError, match="INVALID_F6_6_BASELINE"):
        record_lifecycle_event(
            vault=vault, request=request, source=baseline,
            baseline_manifest=altered,
        )
