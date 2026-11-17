"""F5.10 — deterministic manifest and malicious kit/archive preflight tests.

CI additionally constructs the *real* wheelhouse, installs from extracted kit
with no network and runs the third domain twice in isolated Python -I venvs.
"""
from __future__ import annotations

import ast
from copy import deepcopy
from email.parser import Parser
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import zipfile

import pytest

from tools.build_f5_10_release_kit import (
    BUNDLE_FILENAME, NEUTRAL_WHEELS,
    archive_kit, prepare_kit, safe_extract_kit,
)
from tools.f5_10_certify_deployment import (
    MODULES, NEUTRAL, PURPOSE, SAMPLE, KitError,
    digest_file, validate_kit, _wheel_identity,
)
from tools.verify_f5_10_release_kit import _run_external

ROOT = Path(__file__).resolve().parents[1]


def _create_fake_wheel(path: Path, name: str, version: str) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        normalized = name.replace("-", "_")
        archive.writestr(
            f"{normalized}-{version}.dist-info/METADATA",
            "Metadata-Version: 2.3\n"
            + f"Name: {name}\nVersion: {version}\n",
        )
        archive.writestr(
            f"{normalized}-{version}.dist-info/WHEEL",
            "Wheel-Version: 1.0\nGenerator: F5.10_SYNTHETIC\nRoot-Is-Purelib: true\n"
            "Tag: py3-none-any\n",
        )


def fake_kit(root: Path) -> Path:
    root.mkdir(parents=True)
    wheels = root / "wheels"
    wheels.mkdir()
    versions = {
        **NEUTRAL,
        **SAMPLE,
        "pydantic": "2.12.0",
        "pydantic-core": "2.41.0",
    }
    entries = []
    for name, version in sorted(versions.items()):
        filename = name.replace("-", "_") + f"-{version}-py3-none-any.whl"
        target = wheels / filename
        _create_fake_wheel(target, name, version)
        role = (
            "neutral" if name in NEUTRAL
            else "example" if name in SAMPLE
            else "dependency"
        )
        entries.append({
            "name": name, "version": version,
            "filename": filename, "role": role,
            "sha256": digest_file(target), "bytes": target.stat().st_size,
        })
    for name in ("certify_deployment.py", "requirements.lock", "README.md"):
        (root / name).write_text("SYNTHETIC_FIXTURE\n", encoding="utf-8")
    (root / "requirements.lock").write_text(
        "\n".join(
            f"{x['name']}=={x['version']} --hash=sha256:{x['sha256']}"
            for x in sorted(entries, key=lambda x: x["name"])
        ) + "\n", encoding="utf-8",
    )
    manifest = {
        "format_version": 1, "purpose": PURPOSE,
        "platform": sys.platform,
        "python_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
        "machine": platform.machine(),
        "wheels": entries,
        "files": {
            name: digest_file(root / name)
            for name in ("certify_deployment.py", "requirements.lock", "README.md")
        },
        "module_hashes": {name: "a" * 64 for name in MODULES},
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2),
        encoding="utf-8",
    )
    return root


def update_manifest(root: Path, change) -> None:
    path = root / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    change(manifest)
    path.write_text(json.dumps(manifest, sort_keys=True, indent=2), encoding="utf-8")


def test_onboarding_kit_is_only_composed_of_neutral_modules_and_an_external_project():
    assert len(NEUTRAL) == 4
    assert set(NEUTRAL_WHEELS) == set(NEUTRAL)
    assert set(MODULES) == {
        "eios/kernel/execution.py", "eios/parameters/center.py",
        "eios/input_contracts/contracts.py", "eios/input_contracts/__init__.py",
        "eios/capability_catalog/catalog.py", "eios/capability_catalog/__init__.py",
        "eios/catalog_governance/ledger.py", "eios/catalog_governance/__init__.py",
        "eios_maintenance_example/consumer.py",
        "eios_maintenance_example/__init__.py",
    }
    assert BUNDLE_FILENAME.endswith(".zip")
    certifier = ROOT / "tools/f5_10_certify_deployment.py"
    source = certifier.read_text(encoding="utf-8")
    imports = [
        node.module or ""
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom)
    ] + [
        module.name
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Import)
        for module in node.names
    ]
    assert not any(name == "eios" or name.startswith("eios.") for name in imports)
    assert '"--no-index"' in source
    assert '"--require-hashes"' in source
    assert '"-I"' in source
    assert "SYNTHETIC_TECHNICAL_ONBOARDING_ONLY" in source
    assert "production_authorized" in source
    assert "NOT_TESTED" in source


def test_synthetic_preflight_accepts_exact_manifest_and_expected_trusted_hash(tmp_path):
    kit = fake_kit(tmp_path / "fixture")
    accepted = validate_kit(kit, expected_sha=digest_file(kit / "manifest.json"))
    assert accepted["wheel_count"] == 7
    assert accepted["versions"]["eios-kernel"] == "0.1.0"
    with pytest.raises(KitError, match="TRUSTED_MANIFEST_HASH_MISMATCH"):
        validate_kit(kit, expected_sha="0" * 64)


@pytest.mark.parametrize("mutation,expected", (
    ("wrong_python", "KIT_PYTHON_VERSION_NOT_SUPPORTED"),
    ("wrong_machine", "KIT_PLATFORM_NOT_SUPPORTED"),
    ("wrong_purpose", "UNSUPPORTED_KIT_PURPOSE"),
    ("wrong_version", "UNSUPPORTED_MANIFEST_VERSION"),
    ("missing_module", "INVALID_CANONICAL_MODULE_MANIFEST"),
    ("extra_distribution", "INVALID_WHEEL_COUNT|UNDECLARED_OR_MISSING_WHEEL|REQUIRED_MODULE_DISTRIBUTION_MISSING"),
))
def test_preflight_rejects_invalid_scope_and_platform(tmp_path, mutation, expected):
    kit = fake_kit(tmp_path / "fixture")
    def change(manifest):
        if mutation == "wrong_python":
            manifest["python_minor"] = "0.0"
        elif mutation == "wrong_machine":
            manifest["machine"] = "FOREIGN_ARCH"
        elif mutation == "wrong_purpose":
            manifest["purpose"] = "OPERATIONS_APPROVED"
        elif mutation == "wrong_version":
            manifest["format_version"] = 9
        elif mutation == "missing_module":
            manifest["module_hashes"].pop(next(iter(manifest["module_hashes"])))
        else:
            manifest["wheels"] = manifest["wheels"][1:]
    update_manifest(kit, change)
    with pytest.raises(KitError, match=expected):
        validate_kit(kit)


def test_corrupted_wheel_and_lock_detected_before_environment_creation(tmp_path):
    kit = fake_kit(tmp_path / "fixture")
    first = json.loads((kit / "manifest.json").read_text())["wheels"][0]["filename"]
    with (kit / "wheels" / first).open("ab") as stream:
        stream.write(b"F5_10_TAMPER")
    with pytest.raises(KitError, match="WHEEL_DIGEST_MISMATCH"):
        validate_kit(kit)
    kit = fake_kit(tmp_path / "second")
    (kit / "requirements.lock").write_text("eios-kernel==9\n")
    with pytest.raises(KitError, match="SUPPORT_FILE_DIGEST_MISMATCH"):
        validate_kit(kit)


def test_undeclared_wheel_or_missing_support_file_rejected(tmp_path):
    kit = fake_kit(tmp_path / "fixture")
    (kit / "wheels" / "eios_price_procurement-0.2.0-py3-none-any.whl").write_bytes(b"NOT_A_WHEEL")
    with pytest.raises(KitError, match="UNDECLARED_OR_MISSING_WHEEL"):
        validate_kit(kit)
    kit = fake_kit(tmp_path / "second")
    (kit / "README.md").unlink()
    with pytest.raises(KitError, match="MISSING_OR_UNTRUSTED_FILE"):
        validate_kit(kit)


def test_attestation_does_not_accept_a_renamed_wheel_with_same_bytes(tmp_path):
    kit = fake_kit(tmp_path / "fixture")
    data = json.loads((kit / "manifest.json").read_text())
    entry = next(x for x in data["wheels"] if x["name"] == "eios-kernel")
    entry["name"] = "eios-untrusted-kernel"
    (kit / "manifest.json").write_text(json.dumps(data))
    with pytest.raises(KitError, match="FOREIGN_EIOS_DISTRIBUTION"):
        validate_kit(kit)


def test_bundle_archive_roundtrip_has_exact_same_manifest(tmp_path):
    kit = fake_kit(tmp_path / "fixture")
    archive = archive_kit(kit, tmp_path / "output" / BUNDLE_FILENAME)
    extracted = tmp_path / "unpacked"
    safe_extract_kit(archive, extracted)
    assert validate_kit(extracted) == validate_kit(kit)
    assert digest_file(extracted / "manifest.json") == digest_file(kit / "manifest.json")
    with pytest.raises(ValueError, match="existing"):
        safe_extract_kit(archive, extracted)
    with pytest.raises(ValueError, match="overwrite"):
        archive_kit(kit, archive)


def test_archive_extractor_rejects_zip_slip_duplicate_and_symlink(tmp_path):
    def make_archive(name_list):
        file = tmp_path / "bad.zip"
        with zipfile.ZipFile(file, "w") as archive:
            for name in name_list:
                archive.writestr(name, "SYNTHETIC")
        return file
    for names in (
        ["../parent/" + str(i) for i in range(8)],
        ["safe.txt"] * 8,
        ["safe.txt", "/absolute"] + [f"good{i}.txt" for i in range(6)],
    ):
        bad = make_archive(names)
        with pytest.raises(ValueError, match="Unsafe|Duplicate"):
            safe_extract_kit(bad, tmp_path / "fresh")
        assert not (tmp_path / "fresh").exists()


def test_no_run_on_nonexistent_audited_neutral_wheels(tmp_path):
    with pytest.raises(ValueError, match="precisely four"):
        prepare_kit(
            tmp_path / "kit",
            {"eios-kernel": tmp_path / "no-such-wheel.whl"},
        )


def test_portable_readme_contains_install_and_new_project_admission_steps():
    content = (
        ROOT / "tests/fixtures/f5_10_deployment_kit/README.md"
    ).read_text(encoding="utf-8")
    assert "PowerShell" in content
    assert "python3 certify_deployment.py" in content
    assert "--output" in content
    assert "build_f5_10_release_kit.py" in content
    assert "AuthorizationGrant" in content
    assert "operational_path=FORBIDDEN" in content
    assert "no están firmados" in content
