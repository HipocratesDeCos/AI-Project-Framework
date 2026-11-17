"""F5.5 — real co-installation of kernel, one C0 owner, PRICE and TCO.

No source paths in runtime: new venv outside repo + python -I. The four wheels
have pairwise disjoint eios/ payloads and canonical SHA-256 installed bytes.
Proof uses real PRICE and TCO calculators, no fake business formulas or authority.
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
    from .build_eios_contracts_distribution import audit_wheel as audit_contracts
    from .build_eios_kernel_distribution import audit_wheel as audit_kernel
    from .build_eios_price_distribution import audit_wheel as audit_price
    from .build_eios_tco_distribution import audit_wheel as audit_tco
else:
    from build_eios_contracts_distribution import audit_wheel as audit_contracts
    from build_eios_kernel_distribution import audit_wheel as audit_kernel
    from build_eios_price_distribution import audit_wheel as audit_price
    from build_eios_tco_distribution import audit_wheel as audit_tco

ROOT = Path(__file__).resolve().parents[1]
WHEEL_NAMES = (
    "eios-kernel", "eios-contracts-procurement",
    "eios-price-procurement", "eios-tco-procurement",
)
VERSIONS = ("0.1.0", "0.1.0", "0.2.0", "0.2.0")

SMOKE = r"""
import hashlib
import importlib
import importlib.util
import json
import sys
from datetime import date
from decimal import Decimal
from importlib import metadata
from pathlib import Path

expected = json.loads(sys.argv[1])
for name, version in expected["versions"].items():
    assert metadata.version(name) == version, name
try:
    metadata.version("eios-mvp")
except metadata.PackageNotFoundError:
    pass
else:
    raise AssertionError("Full legacy EIOS app was installed")

for module_name in ("eios.company_app", "eios.core.execution_boundary", "eios.quality"):
    assert importlib.util.find_spec(module_name) is None, module_name

for path, digest in expected["modules"].items():
    module_name = path[:-3].replace("/", ".").removesuffix(".__init__")
    loaded = importlib.import_module(module_name)
    installed = Path(loaded.__file__).read_bytes()
    assert hashlib.sha256(installed).hexdigest() == digest, path

from eios.core.models import PurchaseOperation, DecisionContext, EvidenceValidation
from eios.tco import calculate_tco, TCOInput, CostComponent
from eios.pricing import run_price_intelligence, run_price_intelligence_for_company
from eios.pricing.models import (
    PriceIntelligenceInput, PriceIntelligenceAssessmentContext, PriceReference,
)
from eios.pricing.company_coverage import (
    PriceCompanyCoverageProfile, PriceCoverageError,
)
from eios.pricing.sufficiency import SufficiencyObservation
from eios.pricing.representativeness import RepresentativenessObservation
from eios.kernel.execution import (
    KernelCapabilityResult, KernelCapabilityStatus, KernelContext,
    KernelOperation, KernelPlan, KernelStatus, execute_kernel,
)
from eios.parameters.center import ParameterConfigurationCenter

assert TCOInput.model_fields["purchase_operation"].annotation is PurchaseOperation
assert PriceIntelligenceInput.model_fields["purchase_operation"].annotation is PurchaseOperation
assert PriceIntelligenceInput.model_fields["decision_context"].annotation is DecisionContext
assert ParameterConfigurationCenter.__name__ == "ParameterConfigurationCenter"

decision = DecisionContext(
    decision_id="SYNTH-F5-5", scenario_id="BASE",
    rules_version="RULES-1", parameters_version="PARAM-1",
    data_snapshot_id="SYNTH-SNAPSHOT-1",
)
purchase = PurchaseOperation(
    decision_id=decision.decision_id, scenario_id=decision.scenario_id,
    article_id="SUBSTRATE-SYNTH", supplier_id="SUP-SYNTH",
    quantity=Decimal("10"), unit_price=Decimal("5"),
    currency="EUR", operation_date=date(2026, 11, 1),
)
cost_input = TCOInput(
    purchase_operation=purchase,
    attributable_costs=(CostComponent(
        component="TRANSPORT", amount=Decimal("7.50"),
        currency="EUR", attribution_ref="DOC-SYNTH",
        rule_reference="RULE-TRANSPORT",
    ),),
)
cost = calculate_tco(cost_input)
assert cost.complete and cost.value == Decimal("57.50")
assert cost.currency == "EUR"

refs = tuple(PriceReference(
    source_transaction_id=f"R{i}", article_identity=purchase.article_id,
    supplier_identity=purchase.supplier_id, quantity=Decimal("10"), unit="EA",
    unit_price=Decimal(value), currency="EUR",
    operation_date=date(2026, 10, 20), evidence_refs=(f"E{i}",),
) for i, value in ((1, "10.00"), (2, "12.00")))
price_payload = PriceIntelligenceInput(
    decision_context=decision, purchase_operation=purchase, references=refs,
    evidence_validations=tuple(
        EvidenceValidation(evidence_id=f"E{i}", status="VALID", reason="synthetic")
        for i in (1, 2)
    ) + (EvidenceValidation(
        evidence_id="EPROFILE", status="VALID", reason="synthetic",
    ),),
    methodology_version="F5-5",
)
assessment = PriceIntelligenceAssessmentContext(
    temporal={f"R{i}": ("ELIGIBLE", "SYNTH-RULE") for i in (1, 2)},
    representativeness={
        f"R{i}": RepresentativenessObservation(
            ordinary_market_context=True, exceptional_condition=False,
            material_commercial_distortion=False,
            evidence_refs=(f"E{i}",), rule_reference="SYNTH-REP",
            trace_reference="SYNTH-TRACE",
        ) for i in (1, 2)
    },
    sufficiency=SufficiencyObservation(
        selected_reference_ids=("R1", "R2"),
        evidence_sufficient=True, contradictions_resolved=True,
        evidence_refs=("E1", "E2"),
        rule_reference="SYNTH-SUFF", trace_reference="SYNTH-TRACE",
    ),
)
price = run_price_intelligence(price_payload, assessment)
assert price.pr_status == "PR_AVAILABLE" and price.pr_value == Decimal("11.00")
assert price.reference_set == ("R1", "R2")

# The ordinary analytical result never bypasses the strict company gate.
profile = PriceCompanyCoverageProfile(
    profile_id="PROFILE-SYNTH", company_id="COMPANY-SYNTH",
    decision_id=decision.decision_id, scenario_id=decision.scenario_id,
    parameters_version=decision.parameters_version,
    data_snapshot_id=decision.data_snapshot_id,
    source_ref="PROFILE-DOC", evidence_id="EPROFILE",
    rule_reference="PROFILE-RULE", trace_reference="PROFILE-TRACE",
)
try:
    run_price_intelligence_for_company(
        price_payload, assessment, profile,
        expected_company_id="COMPANY-SYNTH",
    )
except PriceCoverageError as exc:
    assert not exc.report.complete
    assert "NORMALIZATION_BASIS_MISSING" in exc.report.issues
else:
    raise AssertionError("Unproven PRICE admitted")

ctx = KernelContext(
    project_id="F5_5_SYNTH_PURCHASING",
    decision_id=decision.decision_id, scenario_id=decision.scenario_id,
    rules_version=decision.rules_version,
    parameters_version=decision.parameters_version,
    data_snapshot_id=decision.data_snapshot_id,
)
called = []
def price_invoker(payload, execution_context):
    assert payload == purchase
    assert execution_context == ctx
    called.append("PRICE")
    try:
        run_price_intelligence_for_company(
            price_payload, assessment, profile,
            expected_company_id="COMPANY-SYNTH",
        )
    except PriceCoverageError:
        return KernelCapabilityResult(
            capability="PRICE", status=KernelCapabilityStatus.NOT_EVALUABLE,
            result_available=False,
            unresolved_items=("PRICE_DOCUMENTARY_COVERAGE_MISSING",),
        )
    raise AssertionError("Missing documentary PRICE coverage accepted")

def tco_invoker(payload, execution_context):
    assert payload == purchase
    assert execution_context == ctx
    called.append("TCO")
    produced = calculate_tco(cost_input)
    assert produced.value == Decimal("57.50")
    return KernelCapabilityResult(
        capability="TCO", status=KernelCapabilityStatus.COMPLETED,
        result_available=produced.complete, trace_references=("SYNTH-TCO",),
    )

operation = KernelOperation(
    decision_id=decision.decision_id,
    scenario_id=decision.scenario_id, payload=purchase,
)
plan = KernelPlan(capabilities=("PRICE", "TCO"), policy_version="SYNTH-F5-5")
execution = execute_kernel(operation, ctx, plan, {
    "PRICE": price_invoker, "TCO": tco_invoker,
})
assert called == ["PRICE", "TCO"]
assert execution.status == KernelStatus.PARTIALLY_COMPLETED
assert execution.unresolved_items == ("PRICE_DOCUMENTARY_COVERAGE_MISSING",)
assert execution.decision_authority is False
assert execution.operational_path == "FORBIDDEN"
assert execution.provenance_status == "UNVERIFIED_ADAPTER_RESPONSIBILITY"

# Inconsistent operation identity must fail BEFORE either producer is called.
called.clear()
bad = KernelOperation(
    decision_id="FOREIGN", scenario_id=decision.scenario_id, payload=purchase,
)
try:
    execute_kernel(bad, ctx, plan, {
        "PRICE": price_invoker, "TCO": tco_invoker,
    })
except Exception:
    pass
else:
    raise AssertionError("Kernel accepted an inconsistent operation identity")
assert called == []

print(json.dumps({
    "verification": "FOUR_WHEELS_ONE_C0_OWNER_SUCCESS",
    "modules": expected["modules"],
    "tco": str(cost.value),
    "price": str(price.pr_value),
    "price_coverage": "NOT_EVALUABLE",
    "execution": execution.status.value,
    "operational_path": execution.operational_path,
}, sort_keys=True))
"""


def owned_paths(wheel: Path) -> set[str]:
    with zipfile.ZipFile(wheel) as archive:
        return {x for x in archive.namelist() if x.startswith("eios/")}


def verify_payloads(wheels: dict[str, Path]) -> dict[str, str]:
    audit = {
        "eios-kernel": audit_kernel,
        "eios-contracts-procurement": audit_contracts,
        "eios-price-procurement": audit_price,
        "eios-tco-procurement": audit_tco,
    }
    all_modules: dict[str, str] = {}
    for name, path in wheels.items():
        audit[name](path)
        with zipfile.ZipFile(path) as archive:
            for installed in owned_paths(path):
                if installed in all_modules:
                    raise ValueError(f"Duplicate installed EIOS module: {installed}")
                if not installed.endswith(".py"):
                    raise ValueError(f"Non-Python code in EIOS payload: {installed}")
                canonical = ROOT / installed
                if not canonical.is_file():
                    raise ValueError(f"No canonical source for {installed}")
                source = canonical.read_bytes()
                packed = archive.read(installed)
                if source != packed:
                    raise ValueError(f"Wheel content differs from canonical code: {installed}")
                all_modules[installed] = hashlib.sha256(source).hexdigest()
    if "eios/core/models.py" not in owned_paths(wheels["eios-contracts-procurement"]):
        raise ValueError("Shared contracts package does not own C0 models")
    if any(
        "eios/core/models.py" in owned_paths(path)
        for name, path in wheels.items() if name != "eios-contracts-procurement"
    ):
        raise ValueError("C0 model still duplicated by another wheel")
    return all_modules


def check(wheels: dict[str, Path]) -> dict:
    if set(wheels) != set(WHEEL_NAMES):
        raise ValueError("Four required distributions must be provided")
    wheels = {name: wheel.resolve() for name, wheel in wheels.items()}
    hashes = verify_payloads(wheels)
    with tempfile.TemporaryDirectory(prefix="eios-f5-5-combined-") as directory:
        root = Path(directory)
        home = root / "venv"
        venv.EnvBuilder(with_pip=True, system_site_packages=False).create(home)
        python = home / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env["PYTHONNOUSERSITE"] = "1"
        env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
        installed = subprocess.run(
            [str(python), "-m", "pip", "install", "--no-cache-dir",
             *(str(wheels[name]) for name in WHEEL_NAMES)],
            cwd=root, env=env, capture_output=True, text=True, timeout=180,
        )
        if installed.returncode:
            raise RuntimeError("Combined wheel installation failed: " + installed.stderr[-3000:])
        checked = subprocess.run(
            [str(python), "-m", "pip", "check"],
            cwd=root, env=env, capture_output=True, text=True, timeout=45,
        )
        if checked.returncode:
            raise RuntimeError("Combined dependency check failed: " + checked.stdout[-3000:])
        tested = subprocess.run(
            [str(python), "-I", "-c", SMOKE,
             json.dumps({"versions": dict(zip(WHEEL_NAMES, VERSIONS)), "modules": hashes})],
            cwd=root, env=env, capture_output=True, text=True, timeout=75,
        )
        if tested.returncode:
            raise RuntimeError(
                "Combined real PRICE/TCO execution failed:\n"
                + tested.stdout[-2000:] + "\n" + tested.stderr[-3500:]
            )
        report = json.loads(tested.stdout)
        if report["modules"] != hashes or report["operational_path"] != "FORBIDDEN":
            raise ValueError("Combined execution violated canonical/authority contract")
        if report["tco"] != "57.50" or report["price"] != "11.00":
            raise ValueError("Combined PRICE/TCO numerical regression")
    return {
        "verification": "F5_5_SHARED_C0_CONTRACTS_SUCCESS",
        "sha256_by_module": hashes,
        "distribution_versions": dict(zip(WHEEL_NAMES, VERSIONS)),
        "physical_collisions": 0,
        "price": "11.00",
        "tco": "57.50",
        "operational_path": "FORBIDDEN",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name, folder in (
        ("kernel", "kernel"), ("contracts", "contracts"),
        ("price", "price"), ("tco", "tco"),
    ):
        parser.add_argument(f"--{name}-dir", type=Path, default=Path("dist") / folder)
    opts = parser.parse_args()
    mapping = {
        "eios-kernel": ("kernel", "eios_kernel-*.whl"),
        "eios-contracts-procurement": ("contracts", "eios_contracts_procurement-*.whl"),
        "eios-price-procurement": ("price", "eios_price_procurement-*.whl"),
        "eios-tco-procurement": ("tco", "eios_tco_procurement-*.whl"),
    }
    wheels = {}
    for dist, (directory, pattern) in mapping.items():
        found = list(getattr(opts, directory).resolve().glob(pattern))
        if len(found) != 1:
            raise SystemExit(f"Expected one wheel for {dist}, found {len(found)}")
        wheels[dist] = found[0]
    print(json.dumps(check(wheels), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
