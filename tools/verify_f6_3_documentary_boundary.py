"""F6.3: validate separately packaged synthetic identity/document/reviewer boundary.

Build an independent wheel, audit its imports and bytes, then install it and
the F6.2 adapter *offline* alongside the four neutral packages in a fresh venv.
Two external executions prove deterministic cross-tenant synthetic review.
No real identity provider, documents, operator credentials or QTG are touched.
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
from verify_f6_2_external_company_adapter import (
    SAMPLE as SAMPLE_F6_2, audit_wheel as audit_wheel_f6_2,
)

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "tests/fixtures/f6_3_documentary_boundary_consumer"
NAME = "eios-evidence-boundary-example"
VERSION = "0.1.0"
FILES = frozenset({
    "eios_evidence_boundary_example/__init__.py",
    "eios_evidence_boundary_example/review.py",
    "eios_evidence_boundary_example/demo.py",
})
EXPECTED = frozenset({
    "pydantic", "eios-kernel", "eios-input-contracts",
    "eios-capability-catalog", "eios-catalog-governance",
    "eios-company-adapter-example",
})


def _build_sample(source: Path, destination: Path, prefix: str) -> Path:
    target = destination / prefix
    target.mkdir()
    result = subprocess.run([
        sys.executable, "-m", "pip", "wheel", "--no-deps",
        "--no-build-isolation", "--wheel-dir", str(target), str(source),
    ], cwd=destination, capture_output=True, text=True, timeout=150)
    if result.returncode:
        raise RuntimeError("Independent wheel construction failed: " + result.stderr[-3000:])
    wheels = list(target.glob(prefix + "-*.whl"))
    if len(wheels) != 1:
        raise ValueError("Expected exactly one independent wheel for " + prefix)
    return wheels[0]


def audit_evidence_wheel(wheel: Path) -> dict[str, str]:
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate evidence wheel path")
        if {name for name in names if name.endswith(".py")} != FILES:
            raise ValueError("Unexpected source modules in evidence wheel")
        if any(name.startswith("eios/") or ".data/" in name for name in names):
            raise ValueError("Evidence consumer bundles an EIOS domain or core")
        hashes = {}
        for name in sorted(FILES):
            canonical = SAMPLE / "src" / name
            if not canonical.is_file():
                raise ValueError("Missing evidence boundary canonical source")
            content = archive.read(name)
            if content != canonical.read_bytes():
                raise ValueError("Evidence wheel source differs from canonical source")
            hashes[name] = sha256(content).hexdigest()
            tree = ast.parse(content.decode("utf-8"), filename=name)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    modules = [x.name for x in node.names]
                elif isinstance(node, ast.ImportFrom):
                    modules = [] if node.level else [node.module or ""]
                else:
                    continue
                for module in modules:
                    if module == "eios" or module.startswith("eios."):
                        raise ValueError("Evidence boundary must not import canonical EIOS")
        paths = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(paths) != 1 or not paths[0].startswith("eios_evidence_boundary_example-0.1.0.dist-info/"):
            raise ValueError("Evidence wheel metadata path not canonical")
        meta = Parser().parsestr(archive.read(paths[0]).decode("utf-8"))
        if meta.get("Name", "").lower() != NAME or meta.get("Version") != VERSION:
            raise ValueError("Unexpected evidence boundary wheel identity/version")
        deps = meta.get_all("Requires-Dist") or []
        parsed = [
            dep.split(">")[0].split("<")[0].split("=")[0].split(" ")[0].lower().replace("_", "-")
            for dep in deps
        ]
        if len(parsed) != len(EXPECTED) or set(parsed) != EXPECTED:
            raise ValueError("Evidence boundary dependency graph has changed")
        for name in EXPECTED - {"pydantic"}:
            if not any(
                dep.replace(" ", "").lower().startswith(name + "==0.1.0")
                for dep in deps
            ):
                raise ValueError("Unpinned dependency " + name)
    return hashes


def verify(bundle: Path) -> dict:
    if not bundle.is_file() or bundle.name != BUNDLE_FILENAME:
        raise ValueError("F6.3 requires F5.10/F6.1 neutral ZIP on this platform")
    with tempfile.TemporaryDirectory(prefix="eios-f6-3-outside-") as work:
        root = Path(work)
        extracted = root / "platform-kit"
        safe_extract_kit(bundle, extracted)
        platform_check = validate_kit(extracted)
        manifest = json.loads((extracted / "manifest.json").read_text(encoding="utf-8"))
        adapter = _build_sample(SAMPLE_F6_2, root, "eios_company_adapter_example")
        audit_wheel_f6_2(adapter)
        evidence = _build_sample(SAMPLE, root, "eios_evidence_boundary_example")
        hashes = audit_evidence_wheel(evidence)
        # F5.10's Maintenance demo is *not* part of this new consumer.
        wheels = [item for item in manifest["wheels"] if item["role"] != "example"]
        if len(wheels) + 1 != platform_check["wheel_count"]:
            raise ValueError("Incorrect neutral wheel inventory")
        locked = [
            (item["name"], item["version"], item["sha256"]) for item in wheels
        ] + [
            ("eios-company-adapter-example", "0.1.0", digest_file(adapter)),
            (NAME, VERSION, digest_file(evidence)),
        ]
        lock = root / "isolated-evidence.lock"
        lock.write_text(
            "\n".join(
                f"{name}=={version} --hash=sha256:{digest}"
                for name, version, digest in sorted(locked)
            ) + "\n",
            encoding="utf-8",
        )
        destination = root / "venv"
        venv.EnvBuilder(with_pip=True, system_site_packages=False).create(destination)
        python = destination / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env["PYTHONNOUSERSITE"] = "1"
        env["PIP_NO_INDEX"] = "1"
        installed = subprocess.run([
            str(python), "-m", "pip", "install", "--no-index",
            "--require-hashes", "--only-binary=:all:",
            "--find-links", str(extracted / "wheels"),
            "--find-links", str(adapter.parent),
            "--find-links", str(evidence.parent),
            "-r", str(lock),
        ], cwd=root, env=env, capture_output=True, text=True, timeout=200)
        if installed.returncode:
            raise RuntimeError("F6.3 offline install failed: " + installed.stderr[-3500:])
        deps = subprocess.run(
            [str(python), "-m", "pip", "check"], cwd=root, env=env,
            capture_output=True, text=True, timeout=40,
        )
        if deps.returncode:
            raise RuntimeError("External documentary dependencies invalid: " + deps.stdout[-2000:])
        verify_hashes = subprocess.run([
            str(python), "-I", "-c",
            "import hashlib,importlib,json,sys; expected=json.loads(sys.argv[1]); "
            "actual={k:hashlib.sha256(open(importlib.import_module(k[:-3].replace('/', '.').removesuffix('.__init__')).__file__, 'rb').read()).hexdigest() for k in expected}; "
            "assert actual==expected, (actual,expected); print('F6_3_IMPORTED_BYTES_MATCH_WHEEL')",
            json.dumps(hashes),
        ], cwd=root, env=env, capture_output=True, text=True, timeout=40)
        if verify_hashes.returncode or "F6_3_IMPORTED_BYTES_MATCH_WHEEL" not in verify_hashes.stdout:
            raise ValueError("Installed F6.3 module bytes are not the audited wheel bytes")
        outputs = []
        for run_no in (1, 2):
            outside = root / f"independent-run-{run_no}"
            outside.mkdir()
            completed = subprocess.run([
                str(python), "-I", "-m", "eios_evidence_boundary_example.demo",
            ], cwd=outside, env=env, capture_output=True, text=True, timeout=70)
            if completed.returncode:
                raise RuntimeError("F6.3 independent scenario rejected: " + completed.stderr[-3500:])
            try:
                result = json.loads(completed.stdout)
            except ValueError as exc:
                raise ValueError("Non-JSON F6.3 synthetic outcome") from exc
            if (
                result.get("verification") != "F6_3_SYNTHETIC_EXTERNAL_TRUST_BOUNDARY_PASS"
                or result.get("production_authorized") is not False
                or result.get("operational_path") != "FORBIDDEN"
                or result.get("real_enterprise_identity") != "NOT_TESTED"
                or result.get("real_document_authentication") != "NOT_TESTED"
                or result.get("real_human_review") != "NOT_TESTED"
                or len(result.get("receipts", ())) != 2
                or any(
                    receipt.get("real_company_authenticated") is not False
                    or receipt.get("real_document_authenticated") is not False
                    or receipt.get("real_human_authorized") is not False
                    or receipt.get("decision_authority") is not False
                    for receipt in result["receipts"]
                )
            ):
                raise ValueError("F6.3 claimed documentary or operational authority")
            outputs.append(result)
        if outputs[0] != outputs[1]:
            raise ValueError("Independent F6.3 executions diverged")
        return {
            "verification": "F6_3_EXTERNAL_DOCUMENTARY_GATE_ISOLATED_PASS",
            "neutral_kit_sha256": platform_check["manifest_sha256"],
            "adapter_wheel_sha256": digest_file(adapter),
            "evidence_wheel_sha256": digest_file(evidence),
            "audited_module_hashes": hashes,
            "offline_installation": True,
            "independent_runs": len(outputs),
            "independent_tenants": 2,
            "real_authentication": "NOT_TESTED",
            "operational_path": "FORBIDDEN",
            "production_authorized": False,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit-dir", type=Path, default=Path("dist/release-kit"))
    args = parser.parse_args()
    result = verify(args.kit_dir.resolve() / BUNDLE_FILENAME)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
