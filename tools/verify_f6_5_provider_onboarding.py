"""F6.5 verify pinned synthetic provider onboarding in an isolated offline venv.

Reuses the real F5.10 platform kit and audits four independent external wheels
F6.2–F6.5 by exact source bytes, metadata, versions and imported module hashes.
There are NO real company connections, credentials or grants in this suite.
"""
from __future__ import annotations

import argparse
import ast
from email.parser import Parser
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import venv
import zipfile

from build_f5_10_release_kit import BUNDLE_FILENAME, safe_extract_kit
from f5_10_certify_deployment import digest_file, validate_kit
from verify_f6_2_external_company_adapter import audit_wheel as audit_f62
from verify_f6_3_documentary_boundary import (
    _build_sample, audit_evidence_wheel, SAMPLE_F6_2, SAMPLE as SAMPLE_F6_3,
)
from verify_f6_4_custody_portability import (
    SAMPLE as SAMPLE_F6_4, audit_custody_wheel,
)

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "tests/fixtures/f6_5_onboarding_consumer"
NAME = "eios-onboarding-example"
VERSION = "0.1.0"
FILES = frozenset({
    "eios_onboarding_example/__init__.py",
    "eios_onboarding_example/onboarding.py",
    "eios_onboarding_example/demo.py",
})
DEPENDENCIES = frozenset({
    "pydantic", "eios-kernel", "eios-input-contracts",
    "eios-capability-catalog", "eios-catalog-governance",
    "eios-company-adapter-example", "eios-evidence-boundary-example",
    "eios-custody-example",
})


def audit_onboarding_wheel(wheel: Path) -> dict[str, str]:
    with zipfile.ZipFile(wheel) as z:
        names = z.namelist()
        if len(set(names)) != len(names):
            raise ValueError("Duplicate F6.5 wheel entries")
        if {name for name in names if name.endswith(".py")} != FILES:
            raise ValueError("Unexpected F6.5 modules")
        if any(name.startswith("eios/") or ".data/" in name for name in names):
            raise ValueError("Canonical EIOS modules or executable .data/ in F6.5 wheel")
        hashes = {}
        for module in sorted(FILES):
            source = SAMPLE / "src" / module
            if not source.is_file() or z.read(module) != source.read_bytes():
                raise ValueError("F6.5 wheel source does not match external canonical source")
            data = z.read(module)
            hashes[module] = sha256(data).hexdigest()
            tree = ast.parse(data.decode("utf-8"), filename=module)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported = [item.name for item in node.names]
                elif isinstance(node, ast.ImportFrom):
                    imported = [] if node.level else [node.module or ""]
                else:
                    continue
                if any(name == "eios" or name.startswith("eios.") for name in imported):
                    raise ValueError("F6.5 imports the canonical EIOS engine directly")
        meta_names = [x for x in names if x.endswith(".dist-info/METADATA")]
        if len(meta_names) != 1 or not meta_names[0].startswith(
            "eios_onboarding_example-0.1.0.dist-info/"
        ):
            raise ValueError("Incorrect onboarding metadata path")
        meta = Parser().parsestr(z.read(meta_names[0]).decode("utf-8"))
        if meta.get("Name", "").lower() != NAME or meta.get("Version") != VERSION:
            raise ValueError("Incorrect F6.5 distribution identity")
        deps = meta.get_all("Requires-Dist") or []
        parsed = [
            item.split(">")[0].split("<")[0].split("=")[0].split(" ")[0].lower().replace("_", "-")
            for item in deps
        ]
        if set(parsed) != DEPENDENCIES or len(parsed) != len(DEPENDENCIES):
            raise ValueError("F6.5 onboarding has unexpected dependencies")
        for dep in DEPENDENCIES - {"pydantic"}:
            if not any(item.replace(" ", "").lower().startswith(dep + "==0.1.0") for item in deps):
                raise ValueError("F6.5 unpinned neutral/external dependency: " + dep)
        return hashes


def verify(bundle: Path) -> dict:
    if not bundle.is_file() or bundle.name != BUNDLE_FILENAME:
        raise ValueError("The F5.10 platform kit ZIP is required for F6.5")
    with tempfile.TemporaryDirectory(prefix="eios-f6-5-onboarding-") as temp:
        root = Path(temp)
        extracted = root / "platform-kit"
        safe_extract_kit(bundle, extracted)
        checked = validate_kit(extracted)
        manifest = json.loads((extracted / "manifest.json").read_text(encoding="utf-8"))
        packages = (
            (SAMPLE_F6_2, "eios_company_adapter_example", "eios-company-adapter-example", audit_f62),
            (SAMPLE_F6_3, "eios_evidence_boundary_example", "eios-evidence-boundary-example", audit_evidence_wheel),
            (SAMPLE_F6_4, "eios_custody_example", "eios-custody-example", audit_custody_wheel),
            (SAMPLE, "eios_onboarding_example", NAME, audit_onboarding_wheel),
        )
        wheels = []
        for source, prefix, name, audit in packages:
            wheel = _build_sample(source, root, prefix)
            hashes = audit(wheel)
            wheels.append((name, wheel, hashes))
        neutral = [row for row in manifest["wheels"] if row["role"] != "example"]
        if len(neutral) + 1 != checked["wheel_count"]:
            raise ValueError("Incorrect F5.10 neutral kit inventory")
        pinned = [
            (row["name"], row["version"], row["sha256"]) for row in neutral
        ] + [
            (name, VERSION, digest_file(wheel)) for name, wheel, _ in wheels
        ]
        lock = root / "onboarding.lock"
        lock.write_text(
            "\n".join(
                f"{name}=={version} --hash=sha256:{digest}"
                for name, version, digest in sorted(pinned)
            ) + "\n", encoding="utf-8",
        )
        fresh = root / "clean-venv"
        venv.EnvBuilder(with_pip=True, system_site_packages=False).create(fresh)
        python = fresh / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env["PYTHONNOUSERSITE"] = "1"
        env["PIP_NO_INDEX"] = "1"
        install = subprocess.run([
            str(python), "-m", "pip", "install",
            "--no-index", "--require-hashes", "--only-binary=:all:",
            "--find-links", str(extracted / "wheels"),
            *[part for _, wheel, _ in wheels for part in ("--find-links", str(wheel.parent))],
            "-r", str(lock),
        ], cwd=root, env=env, capture_output=True, text=True, timeout=220)
        if install.returncode:
            raise RuntimeError("F6.5 offline wheel install failed: " + install.stderr[-3500:])
        valid = subprocess.run(
            [str(python), "-m", "pip", "check"], cwd=root, env=env,
            capture_output=True, text=True, timeout=45,
        )
        if valid.returncode:
            raise RuntimeError("F6.5 dependency check failed: " + valid.stdout[-2500:])
        expected = wheels[-1][2]
        check_imported_bytes = subprocess.run([
            str(python), "-I", "-c",
            "import hashlib,importlib,json,sys; expected=json.loads(sys.argv[1]); "
            "actual={k:hashlib.sha256(open(importlib.import_module(k[:-3].replace('/', '.').removesuffix('.__init__')).__file__, 'rb').read()).hexdigest() for k in expected}; "
            "assert actual==expected,(actual,expected); print('F6_5_ONBOARDING_BYTES_VERIFIED')",
            json.dumps(expected),
        ], cwd=root, env=env, capture_output=True, text=True, timeout=45)
        if (
            check_imported_bytes.returncode
            or "F6_5_ONBOARDING_BYTES_VERIFIED" not in check_imported_bytes.stdout
        ):
            raise ValueError("Installed F6.5 module bytes differ from audited wheel")
        outcomes = []
        for number in (1, 2):
            outside = root / f"external-consumer-{number}"
            outside.mkdir()
            process = subprocess.run(
                [str(python), "-I", "-m", "eios_onboarding_example.demo"],
                cwd=outside, env=env, capture_output=True, text=True, timeout=80,
            )
            if process.returncode:
                raise RuntimeError("External F6.5 onboarding failed: " + process.stderr[-3500:])
            try:
                result = json.loads(process.stdout)
            except ValueError as exc:
                raise ValueError("F6.5 outcome is not JSON") from exc
            if (
                result.get("verification") != "F6_5_PROVIDER_ONBOARDING_SYNTHETIC_ONLY_PASS"
                or result.get("companies") != 2
                or result.get("registrations_per_company") != 3
                or result.get("provider_connection") != "TEST_DOUBLES_ONLY"
                or result.get("enterprise_identity_authentication") != "NOT_TESTED"
                or result.get("documentary_authentication") != "NOT_TESTED"
                or result.get("human_review_authorization") != "NOT_TESTED"
                or result.get("production_authorized") is not False
                or result.get("operational_path") != "FORBIDDEN"
                or len(result.get("receipts", ())) != 2
                or len(list((outside / "synthetic-onboarding-custody").glob("*.json"))) != 2
                or any(
                    row.get("status") != "SYNTHETIC_PROVIDER_ONBOARDING_READY"
                    or row.get("production_authorized") is not False
                    or row.get("decision_authority") is not False
                    or row.get("real_provider_connected") is not False
                    or row.get("real_document_authenticated") is not False
                    or row.get("real_reviewer_authorized") is not False
                    for row in result["receipts"]
                )
            ):
                raise ValueError("Onboarding incorrectly claimed real provider access or authority")
            outcomes.append(result)
        if outcomes[0] != outcomes[1]:
            raise ValueError("Two external F6.5 executions diverged")
        return {
            "verification": "F6_5_EXTERNAL_ONBOARDING_OFFLINE_CERTIFICATION_PASS",
            "platform_manifest_sha256": checked["manifest_sha256"],
            "external_wheels": {
                name: digest_file(wheel) for name, wheel, _ in wheels
            },
            "onboarding_module_hashes": expected,
            "isolated_install": True,
            "offline": True,
            "independent_runs": 2,
            "synthetic_companies": 2,
            "real_identity_or_documents": "NOT_TESTED",
            "production_authorized": False,
            "operational_path": "FORBIDDEN",
        }


def _build_sample(source: Path, destination: Path, prefix: str) -> Path:
    """Use the existing canonical independent external-wheel builder."""
    from verify_f6_3_documentary_boundary import _build_sample as build
    return build(source, destination, prefix)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit-dir", type=Path, default=Path("dist/release-kit"))
    args = parser.parse_args()
    print(json.dumps(
        verify(args.kit_dir.resolve() / BUNDLE_FILENAME),
        sort_keys=True, ensure_ascii=False, indent=2,
    ))


if __name__ == "__main__":
    main()
