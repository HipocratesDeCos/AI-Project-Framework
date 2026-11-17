"""F6.2 — audit and independently install external adapter with F5.10 kit wheels.

All data and approvals are synthetic. The package is never added to eios/.
The source tree is used ONLY to build its own wheel. Installed execution
takes place in a fresh venv and working directory, outside the checkout.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
from email.parser import Parser
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import venv
import zipfile

from build_f5_10_release_kit import BUNDLE_FILENAME, safe_extract_kit
from f5_10_certify_deployment import digest_file, validate_kit

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "tests/fixtures/f6_2_external_company_adapter"
NAME = "eios-company-adapter-example"
VERSION = "0.1.0"
MODULES = frozenset({
    "eios_company_adapter_example/__init__.py",
    "eios_company_adapter_example/adapter.py",
    "eios_company_adapter_example/demo.py",
})
ALLOWED_EIOS_IMPORTS = frozenset({
    "eios.kernel.execution",
    "eios.input_contracts",
    "eios.capability_catalog",
    "eios.catalog_governance",
})
REQUIRED_DEPS = frozenset({
    "eios-kernel", "eios-input-contracts",
    "eios-capability-catalog", "eios-catalog-governance", "pydantic",
})


def audit_wheel(wheel: Path) -> dict:
    source_root = SAMPLE / "src"
    if not (SAMPLE / "pyproject.toml").is_file():
        raise ValueError("Independent adapter packaging metadata missing")
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate external wheel paths")
        python_modules = {item for item in names if item.endswith(".py")}
        if python_modules != MODULES or any(x.startswith("eios/") or ".data/" in x for x in names):
            raise ValueError("External wheel includes EIOS core or unexpected Python files")
        hashes = {}
        for name in MODULES:
            expected = source_root / name
            if not expected.is_file():
                raise ValueError("Missing canonical external adapter source")
            packed = archive.read(name)
            if packed != expected.read_bytes():
                raise ValueError("External wheel source bytes differ from canonical adapter")
            hashes[name] = hashlib.sha256(packed).hexdigest()
            tree = ast.parse(packed.decode("utf-8"), filename=name)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.level > 1:
                        raise ValueError("Unsafe relative source import")
                    imported = () if node.level else (node.module or "",)
                elif isinstance(node, ast.Import):
                    imported = tuple(alias.name for alias in node.names)
                else:
                    continue
                for module in imported:
                    if module == "eios" or module.startswith("eios."):
                        if module not in ALLOWED_EIOS_IMPORTS:
                            raise ValueError("Business-specific EIOS import in external adapter")
        metadata_files = [x for x in names if x.endswith(".dist-info/METADATA")]
        if len(metadata_files) != 1:
            raise ValueError("External adapter METADATA not unique")
        meta = Parser().parsestr(archive.read(metadata_files[0]).decode("utf-8"))
        if meta.get("Name", "").lower() != NAME or meta.get("Version") != VERSION:
            raise ValueError("External adapter identity/version mismatch")
        declarations = meta.get_all("Requires-Dist") or []
        deps = {
            text.split(">")[0].split("<")[0].split("=")[0].split(" ")[0].lower().replace("_", "-")
            for text in declarations
        }
        if deps != REQUIRED_DEPS or len(declarations) != len(REQUIRED_DEPS):
            raise ValueError("External adapter dependency graph differs from approved neutral graph")
        for name in REQUIRED_DEPS - {"pydantic"}:
            if not any(name in x.replace(" ", "").lower() and "==0.1.0" in x.replace(" ", "") for x in declarations):
                raise ValueError("External EIOS dependency not exactly pinned: " + name)
        return hashes


def verify(bundle: Path) -> dict:
    if not bundle.is_file() or bundle.name != BUNDLE_FILENAME:
        raise ValueError("F6.2 requires the existing F5.10 platform ZIP")
    with tempfile.TemporaryDirectory(prefix="eios-f6-2-independent-") as temp:
        root = Path(temp)
        extracted = root / "neutrals"
        safe_extract_kit(bundle, extracted)
        checked = validate_kit(extracted)
        manifest = json.loads((extracted / "manifest.json").read_text(encoding="utf-8"))
        wheel_dir = root / "external-distribution"
        wheel_dir.mkdir()
        cmd = [
            sys.executable, "-m", "pip", "wheel", "--no-deps",
            "--no-build-isolation", "--wheel-dir", str(wheel_dir), str(SAMPLE),
        ]
        built = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=150)
        if built.returncode:
            raise RuntimeError("Cannot build standalone external adapter wheel: " + built.stderr[-3000:])
        candidates = list(wheel_dir.glob("eios_company_adapter_example-*.whl"))
        if len(candidates) != 1:
            raise ValueError("Expected exactly one external adapter wheel")
        adapter_wheel = candidates[0]
        module_hashes = audit_wheel(adapter_wheel)
        entries = [x for x in manifest["wheels"] if x["role"] != "example"]
        if len(entries) + 1 != checked["wheel_count"]:
            raise ValueError("Existing F5.10 sample has not been excluded from F6.2 installation")
        records = [
            (item["name"], item["version"], item["sha256"])
            for item in entries
        ] + [(NAME, VERSION, digest_file(adapter_wheel))]
        lock = root / "external.lock"
        lock.write_text(
            "\n".join(
                f"{name}=={version} --hash=sha256:{sha}"
                for name, version, sha in sorted(records)
            ) + "\n",
            encoding="utf-8",
        )
        environment = root / "clean-venv"
        venv.EnvBuilder(with_pip=True, system_site_packages=False).create(environment)
        python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env["PYTHONNOUSERSITE"] = "1"
        env["PIP_NO_INDEX"] = "1"
        installed = subprocess.run([
            str(python), "-m", "pip", "install",
            "--no-index", "--require-hashes", "--only-binary=:all:",
            "--find-links", str(extracted / "wheels"),
            "--find-links", str(wheel_dir), "-r", str(lock),
        ], cwd=root, env=env, capture_output=True, text=True, timeout=180)
        if installed.returncode:
            raise RuntimeError("Independent offline F6.2 install failed: " + installed.stderr[-3500:])
        checked_deps = subprocess.run(
            [str(python), "-m", "pip", "check"],
            cwd=root, env=env, capture_output=True, text=True, timeout=40,
        )
        if checked_deps.returncode:
            raise RuntimeError("External adapter dependencies invalid: " + checked_deps.stdout[-2000:])
        working = root / "outside-checkout"
        working.mkdir()
        run = subprocess.run(
            [str(python), "-I", "-m", "eios_company_adapter_example.demo"],
            cwd=working, env=env, capture_output=True, text=True, timeout=80,
        )
        if run.returncode:
            raise RuntimeError("Independent adapter E2E failed: " + run.stderr[-4000:])
        try:
            result = json.loads(run.stdout)
        except ValueError as exc:
            raise ValueError("External adapter returned invalid JSON") from exc
        if (
            result.get("verification") != "F6_2_EXTERNAL_SYNTHETIC_COMPANY_ADAPTER_SUCCESS"
            or result.get("production_authorized") is not False
            or result.get("operational_path") != "FORBIDDEN"
            or result.get("real_source_authentication") != "NOT_TESTED"
            or result.get("human_authorization") != "SYNTHETIC_TEST_DOUBLE_ONLY"
            or len(result.get("cases", [])) != 2
            or len(list(working.glob("catalog_*.json"))) != 2
            or any(case.get("status") != "PARTIALLY_COMPLETED" for case in result["cases"])
        ):
            raise ValueError("F6.2 external certification exceeded synthetic-only scope")
        return {
            "verification": "F6_2_EXTERNAL_COMPANY_ADAPTER_ISOLATED_PASS",
            "external_wheel_sha256": digest_file(adapter_wheel),
            "module_hashes": module_hashes,
            "base_manifest_sha256": checked["manifest_sha256"],
            "companies": sorted(case["company_id"] for case in result["cases"]),
            "independent_python": True,
            "offline": True,
            "data_provenance": "UNVERIFIED_ADAPTER_RESPONSIBILITY",
            "operational_path": "FORBIDDEN",
            "production_authorized": False,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit-dir", type=Path, default=Path("dist/release-kit"))
    args = parser.parse_args()
    report = verify(args.kit_dir.resolve() / BUNDLE_FILENAME)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
