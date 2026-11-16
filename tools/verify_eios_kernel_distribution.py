"""Verify an EIOS kernel wheel in a genuinely isolated Python environment.

The test executes OUTSIDE the repository with a fresh venv and its own
dependencies. It never imports code from the source checkout.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import venv

from build_eios_kernel_distribution import audit_wheel


SMOKE = """
import importlib.util
import sys
from pydantic import BaseModel
from eios.kernel.execution import (
    KernelCapabilityResult, KernelCapabilityStatus, KernelContext, KernelOperation,
    KernelPlan, KernelStatus, execute_kernel,
)
from eios.parameters.center import ParameterConfigurationCenter

assert importlib.util.find_spec("eios.core") is None
assert importlib.util.find_spec("eios.company_local_finance_version_source") is None
assert importlib.util.find_spec("eios.parameters.local_finance_version_source") is None
assert importlib.util.find_spec("openpyxl") is None
assert importlib.util.find_spec("streamlit") is None

class OtherDomain(BaseModel):
    case_reference: str

context = KernelContext(
    project_id="INDEPENDENT-PROJECT", decision_id="D-01", scenario_id="S-01",
    rules_version="1", parameters_version="1", data_snapshot_id="TEST-01",
)
operation = KernelOperation(
    decision_id="D-01", scenario_id="S-01",
    payload=OtherDomain(case_reference="EXTERNAL-01"),
)
plan = KernelPlan(capabilities=("CHECK",), policy_version="1")
def invoker(payload, context):
    assert payload.case_reference == "EXTERNAL-01"
    return KernelCapabilityResult(
        capability="CHECK", status=KernelCapabilityStatus.COMPLETED,
        result_available=True,
    )
result = execute_kernel(operation, context, plan, {"CHECK": invoker})
assert result.status == KernelStatus.COMPLETED
assert result.decision_authority is False
assert result.operational_path == "FORBIDDEN"
assert result.provenance_status == "UNVERIFIED_ADAPTER_RESPONSIBILITY"
assert execute_kernel(
    operation, context, KernelPlan(capabilities=("QTG",), policy_version="1"),
    {"QTG": invoker},
).status == KernelStatus.BLOCKED
assert ParameterConfigurationCenter.__module__ == "eios.parameters.center"
assert "eios.core" not in sys.modules
print("F4.3 independent wheel smoke: SUCCESS")
"""


def check(wheel: Path) -> None:
    audit_wheel(wheel)
    with tempfile.TemporaryDirectory(prefix="eios-kernel-check-") as temp:
        temp_path = Path(temp)
        env_path = temp_path / "venv"
        venv.EnvBuilder(with_pip=True, system_site_packages=False).create(env_path)
        python = env_path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env["PYTHONNOUSERSITE"] = "1"
        subprocess.run(
            [str(python), "-m", "pip", "install", "--disable-pip-version-check", str(wheel.resolve())],
            cwd=temp_path, env=env, check=True,
        )
        subprocess.run(
            [str(python), "-I", "-c", SMOKE],
            cwd=temp_path, env=env, check=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel-dir", type=Path, default=Path("dist/kernel"))
    args = parser.parse_args()
    wheels = list(args.wheel_dir.resolve().glob("eios_kernel-*.whl"))
    if len(wheels) != 1:
        raise SystemExit("Expected exactly one eios-kernel wheel in --wheel-dir")
    check(wheels[0])


if __name__ == "__main__":
    main()
