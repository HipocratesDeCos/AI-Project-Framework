"""F8.1: fourth-domain experiment, NOT a generic project certifier.

Build an independent energy wheel; reuse the *unchanged* F5.10 kit's four
neutral wheels and dependency wheels, excluding its maintenance example from
the new install. Run twice in isolated workspaces. No kernel/API changes.
"""
from __future__ import annotations

import argparse
import ast
from hashlib import sha256
from importlib import metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import venv
import zipfile

from build_f5_10_release_kit import BUNDLE_FILENAME, safe_extract_kit
from f5_10_certify_deployment import NEUTRAL, SAMPLE, validate_kit

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tests/fixtures/f8_1_energy_consumer"
PACKAGE = "eios_energy_example"
DIST = "eios-energy-example"
ALLOWED = {
    "eios.kernel.execution", "eios.input_contracts",
    "eios.capability_catalog", "eios.catalog_governance",
}
PY_FILES = {
    f"{PACKAGE}/__init__.py", f"{PACKAGE}/consumer.py",
}


def verify_source() -> None:
    pyproject = (SOURCE / "pyproject.toml").read_text(encoding="utf-8")
    for name, version in NEUTRAL.items():
        if f'"{name}=={version}"' not in pyproject:
            raise ValueError(f"Unpinned/missing neutral dependency: {name}")
    if '"eios-mvp"' in pyproject:
        raise ValueError("Monolith included")
    actual = {
        p.relative_to(SOURCE / "src").as_posix()
        for p in (SOURCE / "src").rglob("*.py")
    }
    if actual != PY_FILES:
        raise ValueError("Foreign source code in fourth consumer")
    for rel in sorted(actual):
        file = SOURCE / "src" / rel
        tree = ast.parse(file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports = [part.name for part in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    raise ValueError("Relative module import forbidden")
                imports = [node.module or ""]
            else:
                continue
            for name in imports:
                if (name == "eios" or name.startswith("eios.")) and name not in ALLOWED:
                    raise ValueError("Forbidden internal EIOS import: " + name)


def build_wheel(destination: Path) -> Path:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "wheel", "--no-deps",
         "--no-build-isolation", "--wheel-dir", str(destination), str(SOURCE)],
        capture_output=True, text=True, timeout=100,
    )
    if result.returncode:
        raise RuntimeError("Independent energy build failed: " + result.stderr[-2000:])
    matches = list(destination.glob("eios_energy_example-0.1.0-*.whl"))
    if len(matches) != 1:
        raise RuntimeError("Exactly one independent wheel expected")
    wheel = matches[0]
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        if len(set(names)) != len(names):
            raise ValueError("Duplicate wheel members")
        found = {name for name in names if name.endswith(".py")}
        if found != PY_FILES or any(name.startswith("eios/") for name in names):
            raise ValueError("Fourth-domain wheel contains foreign Python modules")
        for relative in PY_FILES:
            source = SOURCE / "src" / relative
            if sha256(source.read_bytes()).digest() != sha256(archive.read(relative)).digest():
                raise ValueError("Wheel not identical to fourth-domain source")
    return wheel


def check(kit_zip: Path) -> dict:
    verify_source()
    with tempfile.TemporaryDirectory(prefix="eios-f8-1-") as tmp:
        root = Path(tmp)
        kit = root / "kit"
        safe_extract_kit(kit_zip, kit)
        validated = validate_kit(kit)
        if any(validated["versions"].get(k) != v for k, v in NEUTRAL.items()):
            raise ValueError("Uncertified neutral distribution mix")
        wheels = root / "new-project-wheels"
        wheels.mkdir()
        energy_wheel = build_wheel(wheels)
        energy_hash = sha256(energy_wheel.read_bytes()).hexdigest()
        requirements = [
            line for line in (kit / "requirements.lock").read_text().splitlines()
            if not line.startswith("eios-maintenance-example==")
        ]
        requirements.append(f"{DIST}==0.1.0 --hash=sha256:{energy_hash}")
        lock = root / "new-project-requirements.lock"
        lock.write_text("\n".join(sorted(requirements)) + "\n", encoding="utf-8")

        # Deliberate tamper probe: bytes do not match the original exact lock.
        tampered = root / "tampered.whl"
        payload = bytearray(energy_wheel.read_bytes())
        payload[-1] ^= 1
        tampered.write_bytes(payload)
        if sha256(tampered.read_bytes()).hexdigest() == energy_hash:
            raise AssertionError("Tampered wheel passed immutable hash test")
        tampered.unlink()

        results = []
        for n in (1, 2):
            work = root / f"separate-run-{n}"
            work.mkdir()
            envdir = work / "venv"
            venv.EnvBuilder(with_pip=True).create(envdir)
            python = envdir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            env = os.environ.copy()
            env.pop("PYTHONPATH", None)
            env["PYTHONNOUSERSITE"] = "1"
            env["PIP_NO_INDEX"] = "1"
            installed = subprocess.run(
                [str(python), "-m", "pip", "install", "--no-index",
                 "--only-binary=:all:", "--require-hashes",
                 "--find-links", str(kit / "wheels"),
                 "--find-links", str(wheels), "-r", str(lock)],
                cwd=work, env=env, capture_output=True, text=True, timeout=210,
            )
            if installed.returncode:
                raise RuntimeError("Offline fourth-domain install failed: " + installed.stderr[-3500:])
            checked = subprocess.run(
                [str(python), "-m", "pip", "check"],
                cwd=work, env=env, capture_output=True, text=True, timeout=50,
            )
            if checked.returncode:
                raise RuntimeError("Fourth-domain dependency graph failed: " + checked.stdout[-1000:])
            outside = work / "outside-checkout"
            outside.mkdir()
            execution = subprocess.run(
                [str(python), "-I", "-m", f"{PACKAGE}.consumer"],
                cwd=outside, env=env, capture_output=True, text=True, timeout=70,
            )
            if execution.returncode:
                raise RuntimeError("Fourth-domain consumer failed: " + execution.stderr[-3500:])
            data = json.loads(execution.stdout)
            if (
                data.get("domain") != "energy_management"
                or data.get("initial_status") != "PARTIALLY_COMPLETED"
                or data.get("decision_authority") is not False
                or data.get("operational_path") != "FORBIDDEN"
                or data.get("production_authorized") is not False
                or data.get("real_pilot_admitted") is not False
                or not all(data.get(k) is True for k in (
                    "invalid_authorization_rejected", "cross_project_rejected",
                    "schema_version_rejected", "unregistered_capability_rejected",
                    "missing_binding_rejected", "tampered_ledger_rejected",
                    "producer_input_isolated",
                ))
            ):
                raise ValueError("Fourth-domain evidence insufficient")
            results.append(data)
        if results[0] != results[1]:
            raise ValueError("Independent runs diverged")
        return {
            "verification": "F8_1_FOURTH_DOMAIN_EXPERIMENT_PASS",
            "domain": "energy_management",
            "independent_wheel_sha256": energy_hash,
            "unchanged_f5_10_manifest_sha256": validated["manifest_sha256"],
            "isolated_runs": 2,
            "technical_observation": results[0],
            "production_authorized": False,
            "decision_authority": False,
            "operational_path": "FORBIDDEN",
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit-dir", type=Path, default=Path("dist/release-kit"))
    args = parser.parse_args()
    print(json.dumps(check(args.kit_dir.resolve() / BUNDLE_FILENAME), sort_keys=True))


if __name__ == "__main__":
    main()
