"""F7.5 — immutable, content-addressed EIOS Motor release identity."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tomllib
from typing import Any
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "08_Implementacion" / "phase7_release_identity_policy_v0.1.json"
KIT_NAME = "EIOS_F5_10_Neutral_Onboarding_Kit.zip"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")

PYPROJECTS = {
    "eios-kernel": "packaging/eios-kernel/pyproject.toml",
    "eios-input-contracts": "packaging/eios-input-contracts/pyproject.toml",
    "eios-capability-catalog": "packaging/eios-capability-catalog/pyproject.toml",
    "eios-catalog-governance": "packaging/eios-catalog-governance/pyproject.toml",
}


class ReleaseIdentityError(ValueError):
    pass


def fail(code: str) -> None:
    raise ReleaseIdentityError("F7_5_RELEASE_IDENTITY_REJECTED:" + code)


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical_digest(payload: dict[str, Any]) -> str:
    raw = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return digest_bytes(raw)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        fail("INVALID_JSON:" + str(exc))
    if type(value) is not dict:
        fail("JSON_OBJECT_REQUIRED:" + str(path))
    return value


def resolve_source_sha(root: Path = ROOT) -> str:
    env_sha = os.environ.get("GITHUB_SHA", "").strip().lower()
    try:
        git_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        ).stdout.strip().lower()
    except (OSError, subprocess.SubprocessError):
        git_sha = ""
    source = git_sha or env_sha
    if not SHA40.fullmatch(source):
        fail("EXACT_SOURCE_SHA_REQUIRED")
    if env_sha and SHA40.fullmatch(env_sha) and git_sha and env_sha != git_sha:
        fail("GITHUB_SHA_DOES_NOT_MATCH_CHECKOUT")
    return source


def _package_versions(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for distribution, relative in PYPROJECTS.items():
        path = root / relative
        try:
            project = tomllib.loads(path.read_text(encoding="utf-8"))["project"]
        except (OSError, UnicodeError, ValueError, KeyError) as exc:
            fail("INVALID_PYPROJECT:" + distribution + ":" + str(exc))
        if project.get("name") != distribution:
            fail("DISTRIBUTION_NAME_CHANGED:" + distribution)
        version = project.get("version")
        if type(version) is not str:
            fail("DISTRIBUTION_VERSION_INVALID:" + distribution)
        result[distribution] = version
    return result


def _kit_identity(kit: Path) -> dict[str, Any]:
    if not kit.is_file() or kit.name != KIT_NAME:
        fail("F5_10_KIT_REQUIRED")
    try:
        with ZipFile(kit) as archive:
            names = archive.namelist()
            if "manifest.json" not in names:
                fail("KIT_MANIFEST_MISSING")
            raw_manifest = archive.read("manifest.json")
    except (OSError, ValueError):
        fail("INVALID_KIT_ZIP")
    manifest = json.loads(raw_manifest)
    if type(manifest) is not dict:
        fail("KIT_MANIFEST_OBJECT_REQUIRED")
    if manifest.get("purpose") != "SYNTHETIC_TECHNICAL_ONBOARDING_ONLY":
        fail("KIT_PURPOSE_CHANGED")
    python_minor = manifest.get("python_minor")
    if python_minor != "3.12":
        fail("PYTHON_MINOR_NOT_CERTIFIED")
    platform = manifest.get("platform")
    machine = manifest.get("machine")
    if not all(type(v) is str and v for v in (platform, machine)):
        fail("KIT_PLATFORM_IDENTITY_MISSING")
    return {
        "kit_filename": kit.name,
        "kit_sha256": digest_file(kit),
        "kit_manifest_sha256": digest_bytes(raw_manifest),
        "platform": platform,
        "machine": machine,
        "python_minor": python_minor,
    }


def build_identity(
    *,
    root: Path,
    kit: Path,
    source_sha: str,
) -> dict[str, Any]:
    if not SHA40.fullmatch(source_sha):
        fail("EXACT_SOURCE_SHA_REQUIRED")
    policy = _load_json(root / POLICY.relative_to(ROOT))
    if policy.get("schema") != "EIOS_IMMUTABLE_RELEASE_IDENTITY/v0.1":
        fail("POLICY_IDENTITY_CHANGED")
    if policy.get("phase") != "F7.5":
        fail("PHASE_CHANGED")
    if policy.get("baseline_main_sha") != "7a2de895505de1fe8066aff9f58c7a9529a4f714":
        fail("BASELINE_MAIN_SHA_CHANGED")
    if policy.get("release_status") != "RELEASE_CANDIDATE":
        fail("RELEASE_STATUS_CHANGED")
    if policy.get("identity_scheme") != "SHA256_CANONICAL_JSON_V1":
        fail("IDENTITY_SCHEME_CHANGED")

    expected_stack = policy.get("neutral_stack")
    actual_stack = _package_versions(root)
    if actual_stack != expected_stack:
        fail("NEUTRAL_STACK_VERSION_MISMATCH")

    evidence_entries = policy.get("required_governance_evidence")
    if type(evidence_entries) is not list or len(evidence_entries) != 4:
        fail("GOVERNANCE_EVIDENCE_SET_CHANGED")
    evidence: list[dict[str, str]] = []
    expected_phases = ["F7.1", "F7.2", "F7.3", "F7.4"]
    for index, entry in enumerate(evidence_entries):
        if type(entry) is not list or len(entry) != 2:
            fail("INVALID_GOVERNANCE_EVIDENCE_ENTRY")
        relative, pass_code = entry
        path = root / relative
        data = _load_json(path)
        if data.get("phase") != expected_phases[index]:
            fail("GOVERNANCE_PHASE_MISMATCH:" + expected_phases[index])
        evidence.append({
            "path": relative,
            "sha256": digest_file(path),
            "required_gate": pass_code,
        })

    authority = policy.get("authority")
    expected_authority = {
        "production_authorized": False,
        "decision_authority": False,
        "real_pilot_admitted": False,
        "operational_path": "FORBIDDEN",
    }
    if authority != expected_authority:
        fail("AUTHORITY_ESCALATION")

    source_payload = {
        "candidate_label": policy["candidate_label"],
        "release_status": policy["release_status"],
        "source_sha": source_sha,
        "neutral_stack": actual_stack,
        "governance_evidence": evidence,
        "authority": authority,
    }
    source_release_id = canonical_digest(source_payload)

    artifact = _kit_identity(kit)
    artifact_payload = {
        "source_release_id": source_release_id,
        "artifact": artifact,
    }
    artifact_release_id = canonical_digest(artifact_payload)

    receipt = {
        "schema": "EIOS_RELEASE_IDENTITY_RECEIPT/v0.1",
        "phase": "F7.5",
        **source_payload,
        "source_release_id": source_release_id,
        "artifact": artifact,
        "artifact_release_id": artifact_release_id,
        "identity_scheme": "SHA256_CANONICAL_JSON_V1",
    }
    validate_receipt(receipt)
    return receipt


def validate_receipt(receipt: dict[str, Any]) -> None:
    if receipt.get("schema") != "EIOS_RELEASE_IDENTITY_RECEIPT/v0.1":
        fail("RECEIPT_SCHEMA_CHANGED")
    source_payload = {
        "candidate_label": receipt.get("candidate_label"),
        "release_status": receipt.get("release_status"),
        "source_sha": receipt.get("source_sha"),
        "neutral_stack": receipt.get("neutral_stack"),
        "governance_evidence": receipt.get("governance_evidence"),
        "authority": receipt.get("authority"),
    }
    if canonical_digest(source_payload) != receipt.get("source_release_id"):
        fail("SOURCE_RELEASE_ID_PAYLOAD_MISMATCH")
    artifact_payload = {
        "source_release_id": receipt.get("source_release_id"),
        "artifact": receipt.get("artifact"),
    }
    if canonical_digest(artifact_payload) != receipt.get("artifact_release_id"):
        fail("ARTIFACT_RELEASE_ID_PAYLOAD_MISMATCH")
    authority = receipt.get("authority", {})
    if (
        authority.get("production_authorized") is not False
        or authority.get("decision_authority") is not False
        or authority.get("real_pilot_admitted") is not False
        or authority.get("operational_path") != "FORBIDDEN"
    ):
        fail("AUTHORITY_ESCALATION")


def verify(
    *,
    root: Path = ROOT,
    kit_dir: Path,
    output: Path | None = None,
    source_sha: str | None = None,
) -> dict[str, Any]:
    sha = source_sha or resolve_source_sha(root)
    receipt = build_identity(
        root=root,
        kit=kit_dir / KIT_NAME,
        source_sha=sha,
    )
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        serialized = json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        output.write_text(serialized, encoding="utf-8")
        check = json.loads(output.read_text(encoding="utf-8"))
        validate_receipt(check)
    return {
        "verification": "F7_5_IMMUTABLE_RELEASE_IDENTITY_PASS",
        "candidate_label": receipt["candidate_label"],
        "release_status": receipt["release_status"],
        "source_sha": receipt["source_sha"],
        "source_release_id": receipt["source_release_id"],
        "artifact_release_id": receipt["artifact_release_id"],
        "platform": receipt["artifact"]["platform"],
        "python_minor": receipt["artifact"]["python_minor"],
        "receipt": receipt,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--source-sha")
    args = parser.parse_args()
    result = verify(
        kit_dir=args.kit_dir.resolve(),
        output=args.output.resolve() if args.output else None,
        source_sha=args.source_sha,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
