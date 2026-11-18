"""F7.5 — immutable release identity tests."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from tools.verify_f7_5_release_identity import (
    KIT_NAME,
    POLICY,
    ReleaseIdentityError,
    build_identity,
    validate_receipt,
    verify,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA = "1" * 40


def copy_repo(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    shutil.copytree(
        ROOT,
        target,
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "dist"),
    )
    return target


def fake_kit(directory: Path, *, platform: str = "linux") -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    kit = directory / KIT_NAME
    manifest = {
        "purpose": "SYNTHETIC_TECHNICAL_ONBOARDING_ONLY",
        "python_minor": "3.12",
        "platform": platform,
        "machine": "x86_64",
    }
    with ZipFile(kit, "w", ZIP_DEFLATED) as archive:
        archive.writestr(
            "manifest.json",
            json.dumps(manifest, sort_keys=True, separators=(",", ":")),
        )
        archive.writestr("requirements.lock", "synthetic-test-only\n")
    return kit


def test_release_identity_is_deterministic(tmp_path: Path):
    kit = fake_kit(tmp_path / "kit")
    a = build_identity(root=ROOT, kit=kit, source_sha=SOURCE_SHA)
    b = build_identity(root=ROOT, kit=kit, source_sha=SOURCE_SHA)
    assert a == b
    assert a["release_status"] == "RELEASE_CANDIDATE"
    assert a["authority"]["operational_path"] == "FORBIDDEN"


def test_same_source_release_id_across_platform_artifacts(tmp_path: Path):
    linux = fake_kit(tmp_path / "linux", platform="linux")
    windows = fake_kit(tmp_path / "windows", platform="win32")
    a = build_identity(root=ROOT, kit=linux, source_sha=SOURCE_SHA)
    b = build_identity(root=ROOT, kit=windows, source_sha=SOURCE_SHA)
    assert a["source_release_id"] == b["source_release_id"]
    assert a["artifact_release_id"] != b["artifact_release_id"]


def test_source_sha_changes_source_release_id(tmp_path: Path):
    kit = fake_kit(tmp_path / "kit")
    a = build_identity(root=ROOT, kit=kit, source_sha="1" * 40)
    b = build_identity(root=ROOT, kit=kit, source_sha="2" * 40)
    assert a["source_release_id"] != b["source_release_id"]


def test_kit_bytes_change_artifact_identity(tmp_path: Path):
    first = fake_kit(tmp_path / "first")
    second = fake_kit(tmp_path / "second")
    with second.open("ab") as handle:
        handle.write(b"DIFFERENT_BYTES")
    a = build_identity(root=ROOT, kit=first, source_sha=SOURCE_SHA)
    b = build_identity(root=ROOT, kit=second, source_sha=SOURCE_SHA)
    assert a["source_release_id"] == b["source_release_id"]
    assert a["artifact_release_id"] != b["artifact_release_id"]


def test_receipt_tamper_is_rejected(tmp_path: Path):
    kit = fake_kit(tmp_path / "kit")
    receipt = build_identity(root=ROOT, kit=kit, source_sha=SOURCE_SHA)
    receipt["neutral_stack"]["eios-kernel"] = "9.9.9"
    with pytest.raises(
        ReleaseIdentityError,
        match="SOURCE_RELEASE_ID_PAYLOAD_MISMATCH",
    ):
        validate_receipt(receipt)


def test_policy_authority_escalation_is_rejected(tmp_path: Path):
    repo = copy_repo(tmp_path)
    policy_path = repo / POLICY.relative_to(ROOT)
    data = json.loads(policy_path.read_text(encoding="utf-8"))
    data["authority"]["production_authorized"] = True
    policy_path.write_text(json.dumps(data), encoding="utf-8")
    kit = fake_kit(tmp_path / "kit")
    with pytest.raises(ReleaseIdentityError, match="AUTHORITY_ESCALATION"):
        build_identity(root=repo, kit=kit, source_sha=SOURCE_SHA)


def test_neutral_version_change_without_policy_update_is_rejected(tmp_path: Path):
    repo = copy_repo(tmp_path)
    pyproject = repo / "packaging/eios-kernel/pyproject.toml"
    pyproject.write_text(
        pyproject.read_text(encoding="utf-8").replace(
            'version = "0.1.0"', 'version = "0.2.0"', 1
        ),
        encoding="utf-8",
    )
    kit = fake_kit(tmp_path / "kit")
    with pytest.raises(
        ReleaseIdentityError,
        match="NEUTRAL_STACK_VERSION_MISMATCH",
    ):
        build_identity(root=repo, kit=kit, source_sha=SOURCE_SHA)


def test_durable_receipt_round_trip(tmp_path: Path):
    kit_dir = tmp_path / "kit"
    fake_kit(kit_dir)
    output = tmp_path / "identity.json"
    result = verify(
        root=ROOT,
        kit_dir=kit_dir,
        output=output,
        source_sha=SOURCE_SHA,
    )
    assert result["verification"] == "F7_5_IMMUTABLE_RELEASE_IDENTITY_PASS"
    persisted = json.loads(output.read_text(encoding="utf-8"))
    assert persisted["source_release_id"] == result["source_release_id"]
    assert persisted["artifact_release_id"] == result["artifact_release_id"]
