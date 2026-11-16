"""F4.4: two independent, isolated consumers, ONE audited eios-kernel wheel.

Two different adapter programs are copied to distinct temporary project roots.
Each installs the exact same wheel into its OWN fresh virtual environment and
runs with -I, outside this repository. The verifier checks both wheel payload
digests, domain-specific policies and project identity, no authority, and
adversarial self-tests reported by the independent programs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import venv
import zipfile

if __package__:
    from .build_eios_kernel_distribution import SOURCE_FILES, audit_wheel
else:  # Run directly as python tools/verify_f4_4_two_consumers.py
    from build_eios_kernel_distribution import SOURCE_FILES, audit_wheel

ROOT = Path(__file__).resolve().parents[1]
CONSUMERS = {
    "purchasing": {
        "path": Path("tests/fixtures/f4_4_consumers/purchasing/consumer.py"),
        "project_id": "F4_4_PURCHASING",
        "policy": "purchase-policy-v1",
        "main_status": "COMPLETED",
        "parameter_value": "5",
    },
    "sales": {
        "path": Path("tests/fixtures/f4_4_consumers/sales/consumer.py"),
        "project_id": "F4_4_SALES",
        "policy": "sales-policy-v7",
        "main_status": "PARTIALLY_COMPLETED",
        "parameter_value": "30",
    },
}

MODULE_HASH_KEYS = {
    "eios/kernel/execution.py": "kernel_sha256",
    "eios/parameters/center.py": "parameters_sha256",
}
EXPECTED_FLAGS = {
    "scope_rejected": True,
    "identity_rejected": True,
    "reserved_boundaries_blocked": True,
    "unauthorized_write_rejected": True,
    "decision_authority": False,
    "operational_path": "FORBIDDEN",
    "kernel_version": "0.1.0",
}


def expected_module_hashes(wheel: Path) -> dict[str, str]:
    audit_wheel(wheel)
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        if not set(MODULE_HASH_KEYS).issubset(names):
            raise ValueError("Missing expected kernel modules in wheel")
        return {
            key: hashlib.sha256(archive.read(relative)).hexdigest()
            for relative, key in MODULE_HASH_KEYS.items()
        }


def validate_result(name: str, result: dict, hashes: dict[str, str]) -> None:
    expected = CONSUMERS[name]
    if set(result) != set(EXPECTED_FLAGS) | set(hashes) | {
        "consumer", "project_id", "policy", "main_status", "parameter_value",
    }:
        raise ValueError(f"Invalid contract keys for {name}")
    for key, value in {
        "consumer": name,
        **{k: expected[k] for k in (
            "project_id", "policy", "main_status", "parameter_value",
        )},
        **EXPECTED_FLAGS, **hashes,
    }.items():
        if result[key] != value or type(result[key]) is not type(value):
            raise ValueError(f"{name} violates consumer contract: {key}")


def isolated_consumer(
    name: str, wheel: Path, home: Path, hashes: dict[str, str],
) -> dict:
    project_root = home / name
    project_root.mkdir()
    script = project_root / "consumer.py"
    shutil.copyfile(ROOT / CONSUMERS[name]["path"], script)

    env_path = project_root / "env"
    venv.EnvBuilder(with_pip=True, system_site_packages=False).create(env_path)
    python = env_path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env["PYTHONNOUSERSITE"] = "1"
    env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"

    install = subprocess.run(
        [str(python), "-m", "pip", "install", "--no-cache-dir", str(wheel.resolve())],
        cwd=project_root, env=env, capture_output=True, text=True, timeout=180,
    )
    if install.returncode:
        raise RuntimeError(f"{name}: wheel install failed: {install.stderr[-2000:]}")

    completed = subprocess.run(
        [str(python), "-I", str(script)],
        cwd=project_root, env=env, capture_output=True, text=True, timeout=60,
    )
    if completed.returncode:
        raise RuntimeError(
            f"{name}: isolated adapter failed:\n"
            f"{completed.stdout[-1000:]}\n{completed.stderr[-2500:]}"
        )
    result = json.loads(completed.stdout)
    if not isinstance(result, dict):
        raise ValueError(f"{name}: consumer must return JSON object")
    validate_result(name, result, hashes)
    return result


def check_two_consumers(wheel: Path) -> dict:
    wheel = wheel.resolve()
    hashes = expected_module_hashes(wheel)
    if len(set(CONSUMERS)) != 2 or len({v["project_id"] for v in CONSUMERS.values()}) != 2:
        raise ValueError("Two genuinely distinct project IDs are required")
    if len({v["policy"] for v in CONSUMERS.values()}) != 2:
        raise ValueError("Independent policies are required")
    with tempfile.TemporaryDirectory(prefix="eios-f4-4-consumers-") as root:
        base = Path(root)
        results = {
            name: isolated_consumer(name, wheel, base, hashes)
            for name in CONSUMERS
        }
    if results["purchasing"]["kernel_sha256"] != results["sales"]["kernel_sha256"]:
        raise ValueError("Consumers do not execute the same kernel bytes")
    if results["purchasing"]["parameters_sha256"] != results["sales"]["parameters_sha256"]:
        raise ValueError("Consumers do not execute the same Parameter Centre bytes")
    return {
        "verification": "F4.4_ISOLATED_TWO_CONSUMERS_SUCCESS",
        "wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
        "consumer_statuses": {
            name: result["main_status"] for name, result in results.items()
        },
        "project_ids": {
            name: result["project_id"] for name, result in results.items()
        },
        "kernel_module_sha256": hashes["kernel_sha256"],
        "parameter_center_sha256": hashes["parameters_sha256"],
        "decision_authority": False,
        "operational_path": "FORBIDDEN",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel-dir", type=Path, default=Path("dist/kernel"))
    args = parser.parse_args()
    wheels = list(args.wheel_dir.resolve().glob("eios_kernel-*.whl"))
    if len(wheels) != 1:
        raise SystemExit("Expected exactly one audited eios-kernel wheel")
    print(json.dumps(check_two_consumers(wheels[0]), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
