"""F5.3: prove TCO can be installed alone and next to the neutral kernel.

Two fresh venvs, both outside the repository: (1) standalone optional TCO
without kernel, (2) same TCO wheel alongside the existing F4 kernel wheel.
Every installed TCO module must match its canonical source bytes in the wheel.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import venv
import zipfile

if __package__:
    from .build_eios_tco_distribution import SOURCE_FILES, audit_wheel
    from .build_eios_kernel_distribution import audit_wheel as audit_kernel
else:
    from build_eios_tco_distribution import SOURCE_FILES, audit_wheel
    from build_eios_kernel_distribution import audit_wheel as audit_kernel


SMOKE = r"""
import hashlib
import importlib
import importlib.util
import json
from datetime import date
from decimal import Decimal
from importlib import metadata
from pathlib import Path
from pydantic import ValidationError
import sys

mode, expected_json = sys.argv[1], sys.argv[2]
expected_hashes = json.loads(expected_json)
assert metadata.version("eios-tco-procurement") == "0.1.0"
try:
    metadata.version("eios-mvp")
except metadata.PackageNotFoundError:
    pass
else:
    raise AssertionError("Legacy application installed in clean optional environment")

assert importlib.util.find_spec("eios.frontend") is None
assert importlib.util.find_spec("eios.company_app") is None
assert importlib.util.find_spec("eios.core.execution_boundary") is None
assert importlib.util.find_spec("openpyxl") is None

for module_path, expected in expected_hashes.items():
    name = module_path[:-3].replace("/", ".")
    if name.endswith(".__init__"):
        name = name.removesuffix(".__init__")
    module = importlib.import_module(name)
    assert hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() == expected

from eios.core.models import PurchaseOperation, DecisionContext
from eios.tco.models import CostComponent, TCOInput, TCOResult
from eios.tco.engine import calculate_tco
from eios.tco import calculate_tco as published_calculate_tco
assert published_calculate_tco is calculate_tco

purchase = PurchaseOperation(
    decision_id="SYNTH-F5-3-DEC", scenario_id="BASE",
    article_id="SUBSTRATE-SYNTH", supplier_id="SUPPLIER-SYNTH",
    quantity=Decimal("10"), unit_price=Decimal("5"),
    currency="EUR", operation_date=date(2026, 11, 1),
)
input_complete = TCOInput(
    purchase_operation=purchase,
    attributable_costs=(
        CostComponent(
            component="TRANSPORT", amount=Decimal("7.50"),
            currency="EUR", applicability="APPLICABLE",
            attribution_ref="SYNTH-DOC-1", rule_reference="SYNTH-RULE",
        ),
        CostComponent(
            component="INSURANCE", amount=None, currency="EUR",
            applicability="NOT_APPLICABLE",
        ),
    ),
)
complete = calculate_tco(input_complete)
assert isinstance(complete, TCOResult)
assert complete.complete
assert complete.value == Decimal("57.50")
assert complete.contributing_components == ("ACQUISITION", "TRANSPORT")
assert complete.unresolved_components == ()
assert complete.currency == "EUR"
assert complete.decision_id == purchase.decision_id
assert complete.scenario_id == purchase.scenario_id

incomplete = calculate_tco(TCOInput(
    purchase_operation=purchase,
    attributable_costs=(
        CostComponent(
            component="TRANSPORT", amount=Decimal("8"),
            currency="USD", applicability="APPLICABLE",
            attribution_ref="SYNTH-DOC-2", rule_reference="SYNTH-RULE",
        ),
        CostComponent(
            component="INSURANCE", amount=None, currency="EUR",
            applicability="APPLICABLE",
            attribution_ref="SYNTH-DOC-3", rule_reference="SYNTH-RULE",
        ),
    ),
))
assert not incomplete.complete
assert incomplete.value is None
assert incomplete.unresolved_components == ("TRANSPORT", "INSURANCE")
assert incomplete.limitations == (
    "CURRENCY_INCOMPATIBLE:TRANSPORT", "MISSING_AMOUNT:INSURANCE",
)

try:
    PurchaseOperation(
        decision_id="X", scenario_id="X", article_id="X", supplier_id="X",
        quantity=Decimal("-2"), unit_price=Decimal("3"),
        currency="EUR", operation_date=date(2026, 1, 1),
    )
except ValidationError:
    pass
else:
    raise AssertionError("Invalid quantity accepted")

if mode == "tco-only":
    assert importlib.util.find_spec("eios.kernel") is None
    assert importlib.util.find_spec("eios.parameters") is None
elif mode == "tco-and-kernel":
    assert metadata.version("eios-kernel") == "0.1.0"
    from eios.kernel.execution import (
        KernelCapabilityResult, KernelCapabilityStatus,
        KernelContext, KernelOperation, KernelPlan, KernelStatus,
        execute_kernel,
    )
    from eios.parameters.center import ParameterConfigurationCenter
    assert ParameterConfigurationCenter.__name__ == "ParameterConfigurationCenter"
    context = KernelContext(
        project_id="F5_3_PURCHASING_ONLY", decision_id=purchase.decision_id,
        scenario_id=purchase.scenario_id, rules_version="SYNTH-RULE-1",
        parameters_version="SYNTH-PARAM-1", data_snapshot_id="SYNTH-DATA-1",
    )
    expected_context = context.model_copy(deep=True)
    captured = []
    def tco_adapter(payload, execution_context):
        assert type(payload) is PurchaseOperation
        assert execution_context == expected_context
        assert payload == purchase
        result = calculate_tco(input_complete)
        captured.append(result.value)
        return KernelCapabilityResult(
            capability="TCO", status=KernelCapabilityStatus.COMPLETED,
            result_available=result.complete,
            trace_references=("SYNTH-TCO-F5-3",),
        )
    result = execute_kernel(
        KernelOperation(
            decision_id=purchase.decision_id,
            scenario_id=purchase.scenario_id, payload=purchase,
        ),
        context, KernelPlan(capabilities=("TCO",), policy_version="SYNTH-POLICY"),
        {"TCO": tco_adapter},
    )
    assert captured == [Decimal("57.50")]
    assert result.status == KernelStatus.COMPLETED
    assert result.decision_authority is False
    assert result.operational_path == "FORBIDDEN"
    assert result.provenance_status == "UNVERIFIED_ADAPTER_RESPONSIBILITY"
else:
    raise ValueError("Unknown mode")

print(json.dumps({
    "mode": mode,
    "tco_version": metadata.version("eios-tco-procurement"),
    "tco_modules": expected_hashes,
    "complete_total": str(complete.value),
    "incomplete_components": incomplete.unresolved_components,
    "operational_path": "FORBIDDEN",
}, sort_keys=True))
"""


def wheel_hashes(wheel: Path) -> dict[str, str]:
    audit_wheel(wheel)
    with zipfile.ZipFile(wheel) as archive:
        return {
            path.as_posix(): hashlib.sha256(archive.read(path.as_posix())).hexdigest()
            for path in SOURCE_FILES
        }


def check(tco_wheel: Path, kernel_wheel: Path) -> dict:
    """Check two isolated installations; no use of repository source modules."""
    tco_wheel = tco_wheel.resolve()
    kernel_wheel = kernel_wheel.resolve()
    hashes = wheel_hashes(tco_wheel)
    audit_kernel(kernel_wheel)
    with zipfile.ZipFile(tco_wheel) as tco_archive, zipfile.ZipFile(kernel_wheel) as kernel_archive:
        paths_tco = set(tco_archive.namelist())
        paths_kernel = set(kernel_archive.namelist())
        if paths_tco & paths_kernel:
            raise ValueError("EIOS kernel and TCO wheels share installed paths")
    reports = []
    with tempfile.TemporaryDirectory(prefix="eios-f5-3-tco-") as temporary:
        root = Path(temporary)
        for mode in ("tco-only", "tco-and-kernel"):
            project = root / mode
            project.mkdir()
            home = project / "venv"
            venv.EnvBuilder(with_pip=True, system_site_packages=False).create(home)
            python = home / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            environment = os.environ.copy()
            environment.pop("PYTHONPATH", None)
            environment["PYTHONNOUSERSITE"] = "1"
            environment["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
            wheels = [str(tco_wheel)]
            if mode == "tco-and-kernel":
                wheels.append(str(kernel_wheel))
            installed = subprocess.run(
                [str(python), "-m", "pip", "install", "--no-cache-dir", *wheels],
                env=environment, cwd=project, capture_output=True, text=True, timeout=180,
            )
            if installed.returncode:
                raise RuntimeError(f"{mode}: install failed: {installed.stderr[-3000:]}")
            tested = subprocess.run(
                [str(python), "-I", "-c", SMOKE, mode, json.dumps(hashes)],
                env=environment, cwd=project, capture_output=True, text=True, timeout=60,
            )
            if tested.returncode:
                raise RuntimeError(
                    f"{mode}: probe failed:\n{tested.stdout[-1500:]}\n{tested.stderr[-3000:]}"
                )
            report = json.loads(tested.stdout)
            if report["mode"] != mode or report["tco_modules"] != hashes:
                raise ValueError("Isolated consumer reported inconsistent TCO files")
            if report["complete_total"] != "57.50":
                raise ValueError("Wrong TCO cost calculation")
            if report["operational_path"] != "FORBIDDEN":
                raise ValueError("Invalid operational authority")
            reports.append(report)
    return {
        "verification": "F5.3_OPTIONAL_TCO_DISTRIBUTION_SUCCESS",
        "tco_wheel_sha256": hashlib.sha256(tco_wheel.read_bytes()).hexdigest(),
        "tco_module_sha256": hashes,
        "modes": [item["mode"] for item in reports],
        "verified_cost": "57.50",
        "operational_path": "FORBIDDEN",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tco-dir", type=Path, default=Path("dist/tco"))
    parser.add_argument("--kernel-dir", type=Path, default=Path("dist/kernel"))
    args = parser.parse_args()
    tco_wheels = list(args.tco_dir.resolve().glob("eios_tco_procurement-*.whl"))
    kernel_wheels = list(args.kernel_dir.resolve().glob("eios_kernel-*.whl"))
    if len(tco_wheels) != 1 or len(kernel_wheels) != 1:
        raise SystemExit("Expected exactly one wheel for each distribution")
    print(json.dumps(check(tco_wheels[0], kernel_wheels[0]), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
