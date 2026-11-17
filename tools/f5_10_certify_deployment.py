"""F5.10 — standalone, stdlib-only verifier in an extracted EIOS onboarding kit.

Does NOT import the EIOS checkout. Before installation: checks the complete
wheel inventory, each SHA-256, wheel identity/version, platform and strict
hash-locked requirements. Installation is offline (pip --no-index) inside a new
isolated venv. Then verifies imported physical bytes and exercises a SYNTHETIC
third-party maintenance consumer. It does not authenticate a project operator,
authorize an operational action or certify production security.

The manifest is not signed: a malicious distributor can replace BOTH manifest
and files. Supply --expected-manifest-sha256 from an independent trusted channel
if verification against a trusted external anchor is required.
"""
from __future__ import annotations

import argparse
from email.parser import Parser
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import venv
import zipfile

FORMAT_VERSION = 1
PURPOSE = "SYNTHETIC_TECHNICAL_ONBOARDING_ONLY"
NEUTRAL = {
    "eios-kernel": "0.1.0",
    "eios-input-contracts": "0.1.0",
    "eios-capability-catalog": "0.1.0",
    "eios-catalog-governance": "0.1.0",
}
SAMPLE = {"eios-maintenance-example": "0.1.0"}
PERMITTED_DEPENDENCIES = frozenset({
    "pydantic", "pydantic-core", "annotated-types",
    "typing-extensions", "typing-inspection",
})
NAME_RE = re.compile(r"[a-z0-9][a-z0-9_.-]*\Z")
VERSION_RE = re.compile(r"[0-9A-Za-z][0-9A-Za-z.+!_-]*\Z")
SHA_RE = re.compile(r"[a-f0-9]{64}\Z")
WHEEL_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.+-]*\.whl\Z")
MAX_BYTES = 40_000_000
MAX_WHEELS = 12

MODULES = (
    "eios/kernel/execution.py", "eios/parameters/center.py",
    "eios/input_contracts/contracts.py",
    "eios/input_contracts/__init__.py",
    "eios/capability_catalog/catalog.py",
    "eios/capability_catalog/__init__.py",
    "eios/catalog_governance/ledger.py",
    "eios/catalog_governance/__init__.py",
    "eios_maintenance_example/consumer.py",
    "eios_maintenance_example/__init__.py",
)


class KitError(ValueError):
    """The kit, installation or technical admission cannot be trusted."""


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1_048_576), b""):
            h.update(chunk)
    return h.hexdigest()


def _regular(path: Path, *, limit: int = MAX_BYTES) -> None:
    if not path.is_file() or path.is_symlink():
        raise KitError(f"MISSING_OR_UNTRUSTED_FILE:{path.name}")
    if path.stat().st_size > limit:
        raise KitError(f"FILE_OVER_SIZE_LIMIT:{path.name}")


def _wheel_identity(path: Path) -> tuple[str, str]:
    """Read actual wheel METADATA without importing or executing its code."""
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if len(set(names)) != len(names) or len(names) > 250:
                raise KitError("MALFORMED_WHEEL_MEMBER_SET")
            for info in archive.infolist():
                n = info.filename
                if (
                    not n or n.startswith("/") or "\\" in n or
                    any(part in ("", ".", "..") for part in n.split("/") if part != n.split("/")[-1])
                ):
                    raise KitError("UNSAFE_WHEEL_PATH")
                if info.file_size > MAX_BYTES:
                    raise KitError("UNSAFE_WHEEL_MEMBER_SIZE")
                if (info.external_attr >> 16) & 0o170000 == 0o120000:
                    raise KitError("WHEEL_SYMLINK_FORBIDDEN")
            meta = [n for n in names if n.endswith(".dist-info/METADATA")]
            if len(meta) != 1:
                raise KitError("WHEEL_METADATA_MISSING")
            raw = archive.read(meta[0])
            if len(raw) > 300_000:
                raise KitError("WHEEL_METADATA_OVER_SIZE")
            parsed = Parser().parsestr(raw.decode("utf-8"))
            name = parsed.get("Name", "").lower().replace("_", "-").replace(".", "-")
            version = parsed.get("Version", "")
            if not NAME_RE.fullmatch(name) or not VERSION_RE.fullmatch(version):
                raise KitError("WHEEL_IDENTITY_INVALID")
            return name, version
    except (zipfile.BadZipFile, UnicodeError, KeyError) as exc:
        raise KitError("INVALID_WHEEL_ARCHIVE") from exc


def validate_kit(kit: Path, expected_sha: str | None = None) -> dict:
    kit = kit.resolve(strict=True)
    if not kit.is_dir() or kit.is_symlink():
        raise KitError("KIT_DIRECTORY_REQUIRED")
    manifest = kit / "manifest.json"
    _regular(manifest, limit=100_000)
    actual_manifest_sha = digest_file(manifest)
    if expected_sha is not None:
        if not SHA_RE.fullmatch(expected_sha) or expected_sha != actual_manifest_sha:
            raise KitError("TRUSTED_MANIFEST_HASH_MISMATCH")
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise KitError("INVALID_KIT_MANIFEST_JSON") from exc
    if not isinstance(data, dict) or set(data) != {
        "format_version", "purpose", "platform", "python_minor", "machine",
        "wheels", "files", "module_hashes",
    }:
        raise KitError("INVALID_MANIFEST_SCHEMA")
    if type(data["format_version"]) is not int or data["format_version"] != FORMAT_VERSION:
        raise KitError("UNSUPPORTED_MANIFEST_VERSION")
    if data["purpose"] != PURPOSE:
        raise KitError("UNSUPPORTED_KIT_PURPOSE")
    if data["platform"] != sys.platform or data["machine"] != platform.machine():
        raise KitError("KIT_PLATFORM_NOT_SUPPORTED")
    if data["python_minor"] != f"{sys.version_info.major}.{sys.version_info.minor}":
        raise KitError("KIT_PYTHON_VERSION_NOT_SUPPORTED")
    entries = data["wheels"]
    if not isinstance(entries, list) or not (6 <= len(entries) <= MAX_WHEELS):
        raise KitError("INVALID_WHEEL_COUNT")
    found: dict[str, dict] = {}
    filenames: set[str] = set()
    wheels_dir = kit / "wheels"
    if not wheels_dir.is_dir() or wheels_dir.is_symlink():
        raise KitError("MISSING_WHEEL_DIRECTORY")
    for item in entries:
        if not isinstance(item, dict) or set(item) != {"name", "version", "filename", "sha256", "bytes", "role"}:
            raise KitError("INVALID_WHEEL_RECORD")
        name, version, filename = item["name"], item["version"], item["filename"]
        if (
            not isinstance(name, str) or not NAME_RE.fullmatch(name)
            or not isinstance(version, str) or not VERSION_RE.fullmatch(version)
            or not isinstance(filename, str) or not WHEEL_RE.fullmatch(filename)
            or not isinstance(item["sha256"], str) or not SHA_RE.fullmatch(item["sha256"])
            or type(item["bytes"]) is not int or not (0 < item["bytes"] <= MAX_BYTES)
            or item["role"] not in ("neutral", "example", "dependency")
            or name in found or filename in filenames
        ):
            raise KitError("MALFORMED_OR_DUPLICATED_WHEEL_IDENTITY")
        if (name in NEUTRAL and (item["role"] != "neutral" or version != NEUTRAL[name])):
            raise KitError("WRONG_NEUTRAL_DISTRIBUTION")
        if (name in SAMPLE and (item["role"] != "example" or version != SAMPLE[name])):
            raise KitError("WRONG_SAMPLE_DISTRIBUTION")
        if item["role"] == "dependency" and name not in PERMITTED_DEPENDENCIES:
            raise KitError("FOREIGN_RUNTIME_DEPENDENCY")
        if item["role"] != "dependency" and name not in {**NEUTRAL, **SAMPLE}:
            raise KitError("FOREIGN_EIOS_DISTRIBUTION")
        path = wheels_dir / filename
        _regular(path)
        if path.stat().st_size != item["bytes"] or digest_file(path) != item["sha256"]:
            raise KitError(f"WHEEL_DIGEST_MISMATCH:{filename}")
        if _wheel_identity(path) != (name, version):
            raise KitError(f"WHEEL_METADATA_MISMATCH:{filename}")
        found[name] = item
        filenames.add(filename)
    if set(found) - PERMITTED_DEPENDENCIES != set(NEUTRAL) | set(SAMPLE):
        raise KitError("REQUIRED_MODULE_DISTRIBUTION_MISSING")
    if "pydantic" not in found or "pydantic-core" not in found:
        raise KitError("CORE_RUNTIME_DEPENDENCIES_MISSING")
    actual_wheels = {f.name for f in wheels_dir.iterdir()}
    if actual_wheels != filenames:
        raise KitError("UNDECLARED_OR_MISSING_WHEEL")

    special = data["files"]
    if not isinstance(special, dict) or set(special) != {"certify_deployment.py", "requirements.lock", "README.md"}:
        raise KitError("UNDECLARED_SUPPORT_FILES")
    for name, expected in special.items():
        if not isinstance(expected, str) or not SHA_RE.fullmatch(expected):
            raise KitError("INVALID_SUPPORT_FILE_DIGEST")
        file = kit / name
        _regular(file, limit=500_000)
        if digest_file(file) != expected:
            raise KitError(f"SUPPORT_FILE_DIGEST_MISMATCH:{name}")
    allowed_root = set(special) | {"manifest.json", "wheels"}
    if {item.name for item in kit.iterdir()} != allowed_root:
        raise KitError("EXTRA_OR_MISSING_KIT_ROOT_FILE")
    modules = data["module_hashes"]
    if not isinstance(modules, dict) or set(modules) != set(MODULES):
        raise KitError("INVALID_CANONICAL_MODULE_MANIFEST")
    if not all(isinstance(v, str) and SHA_RE.fullmatch(v) for v in modules.values()):
        raise KitError("INVALID_CANONICAL_MODULE_HASH")
    lines = [
        f"{name}=={item['version']} --hash=sha256:{item['sha256']}"
        for name, item in sorted(found.items())
    ]
    if (kit / "requirements.lock").read_text(encoding="utf-8").splitlines() != lines:
        raise KitError("LOCKFILE_MANIFEST_MISMATCH")
    return {
        "manifest_sha256": actual_manifest_sha,
        "versions": {name: item["version"] for name, item in found.items()},
        "modules": modules,
        "wheel_count": len(found),
        "platform": data["platform"],
        "python_minor": data["python_minor"],
    }


VERIFY_INSTALLED = r"""
from importlib import import_module, metadata, util
import hashlib, json, sys
from pathlib import Path
cert = json.loads(sys.argv[1])
for dist, version in cert["versions"].items():
    assert metadata.version(dist) == version, (dist, version)
for rel, digest in cert["modules"].items():
    name = rel[:-3].replace("/", ".").removesuffix(".__init__")
    module = import_module(name)
    assert hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() == digest, rel
for module in ("eios.core", "eios.pricing", "eios.tco", "eios.company_app"):
    assert util.find_spec(module) is None, module
for dist in ("eios-mvp", "eios-contracts-procurement", "eios-price-procurement", "eios-tco-procurement"):
    try:
        metadata.version(dist)
    except metadata.PackageNotFoundError:
        continue
    raise AssertionError(f"Procurement distribution present: {dist}")
print(json.dumps({"imports_sha256": "VERIFIED", "no_business_packages": True}))
"""

REQUIRED_TRUE = (
    "false_grants_rejected", "cross_project_isolation", "schema_migration_rejected",
    "insufficient_scope_rejected", "stale_revision_rejected",
    "stale_invoker_rejected", "tampered_copy_rejected",
    "producer_input_isolated",
)


def certify(kit: Path, output: Path, expected_sha: str | None = None) -> dict:
    preflight = validate_kit(kit, expected_sha)
    kit = kit.resolve()
    output = output.absolute()
    if output.exists():
        raise KitError("CERTIFICATION_OUTPUT_MUST_NOT_EXIST")
    output.mkdir(parents=True)
    venv_dir = output / "venv"
    venv.EnvBuilder(with_pip=True, system_site_packages=False).create(venv_dir)
    python = venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env["PYTHONNOUSERSITE"] = "1"
    env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    env["PIP_NO_INDEX"] = "1"
    command = [
        str(python), "-m", "pip", "install", "--disable-pip-version-check",
        "--no-index", "--find-links", str(kit / "wheels"),
        "--require-hashes", "--only-binary=:all:",
        "-r", str(kit / "requirements.lock"),
    ]
    install = subprocess.run(command, cwd=output, env=env, capture_output=True, text=True, timeout=240)
    if install.returncode:
        raise KitError("OFFLINE_INSTALL_FAILED:" + install.stderr[-2500:])
    checked = subprocess.run(
        [str(python), "-m", "pip", "check"],
        cwd=output, env=env, capture_output=True, text=True, timeout=45,
    )
    if checked.returncode:
        raise KitError("INSTALLED_DEPENDENCY_GRAPH_INVALID:" + checked.stdout[-1500:])
    workspace = output / "workspace"
    workspace.mkdir()
    verified = subprocess.run(
        [str(python), "-I", "-c", VERIFY_INSTALLED,
         json.dumps({"versions": preflight["versions"], "modules": preflight["modules"]})],
        cwd=workspace, env=env, capture_output=True, text=True, timeout=50,
    )
    if verified.returncode:
        raise KitError("INSTALLED_SOURCE_MISMATCH:" + verified.stderr[-2300:])
    if json.loads(verified.stdout) != {"imports_sha256": "VERIFIED", "no_business_packages": True}:
        raise KitError("ISOLATED_IMPORT_CHECK_FAILED")
    exercise = subprocess.run(
        [str(python), "-I", "-m", "eios_maintenance_example.consumer"],
        cwd=workspace, env=env, capture_output=True, text=True, timeout=90,
    )
    if exercise.returncode:
        raise KitError("EXTERNAL_MAINTENANCE_CONSUMER_FAILED:" + exercise.stderr[-2800:])
    try:
        result = json.loads(exercise.stdout)
    except ValueError as exc:
        raise KitError("NON_JSON_CONSUMER_RESULT") from exc
    if (
        result.get("consumer") != "maintenance"
        or result.get("initial_status") != "PARTIALLY_COMPLETED"
        or result.get("later_status") != "COMPLETED"
        or result.get("decision_authority") is not False
        or result.get("operational_path") != "FORBIDDEN"
        or result.get("provenance_status") != "UNVERIFIED_ADAPTER_RESPONSIBILITY"
        or result.get("authorization") != "SYNTHETIC_TEST_DOUBLE_ONLY"
        or result.get("revision_history") != [1, 2]
        or any(result.get(field) is not True for field in REQUIRED_TRUE)
    ):
        raise KitError("TECHNICAL_ADMISSION_INVARIANT_FAILED")
    receipt = {
        "certificate_format": 1,
        "status": "TECHNICAL_ONBOARDING_PASS",
        "production_authorized": False,
        "operational_path": "FORBIDDEN",
        "scope": PURPOSE,
        "manifest_sha256": preflight["manifest_sha256"],
        "platform": preflight["platform"],
        "python_minor": preflight["python_minor"],
        "installed_distributions": preflight["versions"],
        "wheels_checked": preflight["wheel_count"],
        "module_bytes_verified": len(preflight["modules"]),
        "independent_demo": "equipment_maintenance",
        "result": result,
        "real_user_authentication": "NOT_TESTED",
        "real_documentary_admission": "NOT_TESTED",
    }
    (output / "technical_certification.json").write_text(
        json.dumps(receipt, sort_keys=True, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--expected-manifest-sha256")
    args = parser.parse_args()
    try:
        if args.output is not None:
            report = certify(args.kit, args.output, args.expected_manifest_sha256)
        else:
            report = {
                "status": "INTEGRITY_PREFLIGHT_PASS",
                "scope": PURPOSE,
                **validate_kit(args.kit, args.expected_manifest_sha256),
            }
    except (KitError, FileNotFoundError, OSError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f"F5.10 TECHNICAL ADMISSION REJECTED: {exc}\n")
    print(json.dumps(report, sort_keys=True, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
