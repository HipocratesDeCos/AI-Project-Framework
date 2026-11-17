"""F6.4: isolated offline installation of external synthetic document custody.

Build 3 independent external wheels (F6.2, F6.3, F6.4), byte-audit, install
from the F5.10 platform kit with hashes, and demonstrate deterministic two-
company read-only review using local custody, always SYNTHETIC_TEST_ONLY.
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
    SAMPLE_F6_2, SAMPLE as SAMPLE_F6_3,
    _build_sample, audit_evidence_wheel,
)

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "tests/fixtures/f6_4_custody_consumer"
NAME = "eios-custody-example"
VERSION = "0.1.0"
FILES = frozenset({
    "eios_custody_example/__init__.py",
    "eios_custody_example/custody.py",
    "eios_custody_example/demo.py",
})
DEPENDENCIES = frozenset({
    "pydantic", "eios-kernel", "eios-input-contracts",
    "eios-capability-catalog", "eios-catalog-governance",
    "eios-company-adapter-example", "eios-evidence-boundary-example",
})


def audit_custody_wheel(wheel: Path) -> dict[str, str]:
    """Disallow bundling EIOS source, extra modules and undeclared dependencies."""
    with zipfile.ZipFile(wheel) as z:
        names = z.namelist()
        if len(set(names)) != len(names):
            raise ValueError("Duplicate F6.4 wheel entries")
        if {name for name in names if name.endswith(".py")} != FILES:
            raise ValueError("Unexpected F6.4 source modules")
        if any(name.startswith("eios/") or ".data/" in name for name in names):
            raise ValueError("Canonical EIOS source in external custody wheel")
        hashes = {}
        for module in sorted(FILES):
            src = SAMPLE / "src" / module
            if not src.is_file() or z.read(module) != src.read_bytes():
                raise ValueError("Canonical source differs from packaged custody module")
            data = z.read(module)
            hashes[module] = sha256(data).hexdigest()
            for node in ast.walk(ast.parse(data.decode("utf-8"), filename=module)):
                if isinstance(node, ast.ImportFrom):
                    imports = [] if node.level else [node.module or ""]
                elif isinstance(node, ast.Import):
                    imports = [item.name for item in node.names]
                else:
                    continue
                if any(item == "eios" or item.startswith("eios.") for item in imports):
                    raise ValueError("F6.4 bypasses F6.3 by importing canonical EIOS modules")
        matches = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(matches) != 1 or not matches[0].startswith("eios_custody_example-0.1.0.dist-info/"):
            raise ValueError("Invalid F6.4 wheel metadata")
        info = Parser().parsestr(z.read(matches[0]).decode("utf-8"))
        if info.get("Name", "").lower() != NAME or info.get("Version") != VERSION:
            raise ValueError("Invalid F6.4 distribution identity")
        specs = info.get_all("Requires-Dist") or []
        found = [
            req.split(">")[0].split("<")[0].split("=")[0].split(" ")[0].lower().replace("_", "-")
            for req in specs
        ]
        if set(found) != DEPENDENCIES or len(found) != len(DEPENDENCIES):
            raise ValueError("Undeclared F6.4 dependency")
        for dep in DEPENDENCIES - {"pydantic"}:
            if not any(spec.replace(" ", "").lower().startswith(dep + "==0.1.0") for spec in specs):
                raise ValueError("Unpinned F6.4 input boundary dependency: " + dep)
        return hashes


def verify(bundle: Path) -> dict:
    if bundle.name != BUNDLE_FILENAME or not bundle.is_file():
        raise ValueError("The existing platform-specific F5.10 kit is required")
    with tempfile.TemporaryDirectory(prefix="eios-f6-4-isolated-") as temp:
        root = Path(temp)
        extracted = root / "kit"
        safe_extract_kit(bundle, extracted)
        checked = validate_kit(extracted)
        manifest = json.loads((extracted / "manifest.json").read_text(encoding="utf-8"))
        f62 = _build_sample(SAMPLE_F6_2, root, "eios_company_adapter_example")
        audit_f62(f62)
        f63 = _build_sample(SAMPLE_F6_3, root, "eios_evidence_boundary_example")
        audit_evidence_wheel(f63)
        f64 = _build_sample(SAMPLE, root, "eios_custody_example")
        module_hashes = audit_custody_wheel(f64)
        neutral_wheels = [row for row in manifest["wheels"] if row["role"] != "example"]
        if len(neutral_wheels) + 1 != checked["wheel_count"]:
            raise ValueError("F5.10 neutral wheel inventory mismatch")
        pinned = [
            (row["name"], row["version"], row["sha256"])
            for row in neutral_wheels
        ] + [
            ("eios-company-adapter-example", "0.1.0", digest_file(f62)),
            ("eios-evidence-boundary-example", "0.1.0", digest_file(f63)),
            (NAME, VERSION, digest_file(f64)),
        ]
        lock = root / "custody-hash-locked-requirements.txt"
        lock.write_text(
            "\n".join(
                f"{name}=={version} --hash=sha256:{hash_value}"
                for name, version, hash_value in sorted(pinned)
            ) + "\n", encoding="utf-8",
        )
        venvroot = root / "fresh"
        venv.EnvBuilder(with_pip=True, system_site_packages=False).create(venvroot)
        python = venvroot / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env["PYTHONNOUSERSITE"] = "1"
        env["PIP_NO_INDEX"] = "1"
        command = [
            str(python), "-m", "pip", "install", "--no-index",
            "--require-hashes", "--only-binary=:all:",
            "--find-links", str(extracted / "wheels"),
            "--find-links", str(f62.parent),
            "--find-links", str(f63.parent),
            "--find-links", str(f64.parent),
            "-r", str(lock),
        ]
        proc = subprocess.run(
            command, cwd=root, env=env, text=True,
            capture_output=True, timeout=210,
        )
        if proc.returncode:
            raise RuntimeError("Offline F6.4 install failed: " + proc.stderr[-3500:])
        sanity = subprocess.run(
            [str(python), "-m", "pip", "check"], cwd=root, env=env,
            text=True, capture_output=True, timeout=50,
        )
        if sanity.returncode:
            raise RuntimeError("F6.4 dependency graph invalid: " + sanity.stdout[-1500:])
        imported = subprocess.run([
            str(python), "-I", "-c",
            "import hashlib,importlib,json,sys; expected=json.loads(sys.argv[1]); "
            "actual={k:hashlib.sha256(open(importlib.import_module(k[:-3].replace('/', '.').removesuffix('.__init__')).__file__, 'rb').read()).hexdigest() for k in expected}; "
            "assert actual==expected,(actual,expected); print('F6_4_WHEEL_MODULE_BYTES_MATCH')",
            json.dumps(module_hashes),
        ], cwd=root, env=env, capture_output=True, text=True, timeout=40)
        if imported.returncode or "F6_4_WHEEL_MODULE_BYTES_MATCH" not in imported.stdout:
            raise ValueError("Installed F6.4 modules differ from audited wheel")
        outputs = []
        for run_no in (1, 2):
            location = root / f"independent-client-{run_no}"
            location.mkdir()
            result = subprocess.run([
                str(python), "-I", "-m", "eios_custody_example.demo",
            ], cwd=location, env=env, text=True,
                capture_output=True, timeout=70)
            if result.returncode:
                raise RuntimeError("Independent F6.4 scenario failed: " + result.stderr[-3500:])
            try:
                record = json.loads(result.stdout)
            except ValueError as exc:
                raise ValueError("F6.4 output is not JSON") from exc
            if (
                record.get("verification") != "F6_4_EXTERNAL_CUSTODY_ISOLATED_SYNTHETIC_PASS"
                or record.get("company_count") != 2
                or record.get("immutable_record_count") != 2
                or record.get("production_authorized") is not False
                or record.get("operational_path") != "FORBIDDEN"
                or record.get("document_origin_authenticity") != "NOT_TESTED"
                or record.get("storage_security") != "HOST_RESPONSIBILITY_NOT_CERTIFIED"
                or len(record.get("receipts", ())) != 2
                or len(list((location / "synthetic-custody").glob("*.json"))) != 2
                or any(
                    item.get("real_company_authenticated") is not False
                    or item.get("real_document_authenticated") is not False
                    or item.get("real_human_authorized") is not False
                    or item.get("decision_authority") is not False
                    for item in record["receipts"]
                )
            ):
                raise ValueError("F6.4 scenario claimed unsupported trust or authority")
            outputs.append(record)
        if outputs[0] != outputs[1]:
            raise ValueError("Independent F6.4 executions differed")
        return {
            "verification": "F6_4_OFFLINE_EXTERNAL_CUSTODY_CERTIFICATION_PASS",
            "platform_kit_manifest_sha256": checked["manifest_sha256"],
            "custody_wheel_sha256": digest_file(f64),
            "custody_module_hashes": module_hashes,
            "offline": True,
            "external_installations": 1,
            "fresh_independent_runs": len(outputs),
            "companies": 2,
            "storage_security": "HOST_RESPONSIBILITY_NOT_CERTIFIED",
            "production_authorized": False,
            "operational_path": "FORBIDDEN",
        }


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
