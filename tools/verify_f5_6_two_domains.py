"""F5.6 — independently installed procurement and sales neutral-input clients.

Procurement: five audited wheels, real PRICE C1 + TCO, documentary gate closed.
Sales: only eios-kernel and eios-input-contracts; no procurement modules.
Two fresh venvs outside checkout and python -I with SHA-256 checks for every
installed EIOS module. Exactly one neutral contract implementation is reused.
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
    from .build_eios_kernel_distribution import audit_wheel as audit_kernel
    from .build_eios_input_contracts_distribution import audit_wheel as audit_inputs
    from .build_eios_contracts_distribution import audit_wheel as audit_c0
    from .build_eios_price_distribution import audit_wheel as audit_price
    from .build_eios_tco_distribution import audit_wheel as audit_tco
else:
    from build_eios_kernel_distribution import audit_wheel as audit_kernel
    from build_eios_input_contracts_distribution import audit_wheel as audit_inputs
    from build_eios_contracts_distribution import audit_wheel as audit_c0
    from build_eios_price_distribution import audit_wheel as audit_price
    from build_eios_tco_distribution import audit_wheel as audit_tco

ROOT = Path(__file__).resolve().parents[1]
WHEEL_SPECS = {
    "eios-kernel": ("kernel", "eios_kernel-*.whl", "0.1.0", audit_kernel),
    "eios-input-contracts": ("inputs", "eios_input_contracts-*.whl", "0.1.0", audit_inputs),
    "eios-contracts-procurement": (
        "contracts", "eios_contracts_procurement-*.whl", "0.1.0", audit_c0,
    ),
    "eios-price-procurement": (
        "price", "eios_price_procurement-*.whl", "0.2.0", audit_price,
    ),
    "eios-tco-procurement": (
        "tco", "eios_tco_procurement-*.whl", "0.2.0", audit_tco,
    ),
}

COMMON = r"""
import hashlib
import importlib
import importlib.util
import json
import sys
from importlib import metadata
from pathlib import Path

expected = json.loads(sys.argv[1])
for dist, version in expected["versions"].items():
    assert metadata.version(dist) == version, dist
try:
    metadata.version("eios-mvp")
except metadata.PackageNotFoundError:
    pass
else:
    raise AssertionError("Legacy monolithic package installed")

for path, digest in expected["hashes"].items():
    module = importlib.import_module(
        path[:-3].replace("/", ".").removesuffix(".__init__")
    )
    assert hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() == digest, path

from eios.input_contracts import (
    CapabilityInputBinding, CapabilityInputEnvelope, CapabilityInputSpec,
    InputContractError, bind_capability_inputs,
)
from eios.kernel.execution import (
    KernelCapabilityResult, KernelCapabilityStatus,
    KernelContext, KernelOperation, KernelPlan, KernelStatus, execute_kernel,
)
assert CapabilityInputEnvelope.model_fields["provenance_status"].default == (
    "UNVERIFIED_ADAPTER_RESPONSIBILITY"
)
"""

SALES = COMMON + r"""
from decimal import Decimal
from pydantic import BaseModel, Field

assert importlib.util.find_spec("eios.core") is None
assert importlib.util.find_spec("eios.pricing") is None
assert importlib.util.find_spec("eios.tco") is None
assert importlib.util.find_spec("openpyxl") is None
for forbidden in ("eios-contracts-procurement", "eios-price-procurement", "eios-tco-procurement"):
    try:
        metadata.version(forbidden)
    except metadata.PackageNotFoundError:
        pass
    else:
        raise AssertionError("Procurement dependency leaked into sales")

class SalesQuote(BaseModel):
    company_id: str
    customer_id: str
    product_id: str
    offered_price: Decimal = Field(ge=0)
    payment_days: int = Field(ge=0)

context = KernelContext(
    project_id="F5_6_SALES", decision_id="SYNTH-SALE-88",
    scenario_id="CLIENT-A", rules_version="SYNTH-SALES-R1",
    parameters_version="SYNTH-SALES-P1", data_snapshot_id="SYNTH-SALES-S1",
)
offer = SalesQuote(
    company_id="F5_6_SALES", customer_id="CUSTOMER-SYNTH",
    product_id="SKU-SYNTH", offered_price=Decimal("12.50"),
    payment_days=30,
)
operation = KernelOperation(
    decision_id=context.decision_id, scenario_id=context.scenario_id, payload=offer,
)
plan = KernelPlan(
    capabilities=("SALES_FIELDS", "SALES_DOCUMENTARY"),
    policy_version="SYNTH-SALES-POLICY",
)
calls = []
def fields(payload, ctx):
    assert type(payload) is SalesQuote
    assert payload.company_id == ctx.project_id  # sale domain adapter checks business ID
    assert payload.payment_days == 30
    calls.append("SALES_FIELDS")
    payload.offered_price = Decimal("0")
    return KernelCapabilityResult(
        capability="SALES_FIELDS", status=KernelCapabilityStatus.COMPLETED,
        result_available=True, trace_references=("SYNTH-SALES-FIELDS",),
    )

def documentary(payload, ctx):
    assert payload.offered_price == Decimal("12.50")
    calls.append("SALES_DOCUMENTARY")
    return KernelCapabilityResult(
        capability="SALES_DOCUMENTARY", status=KernelCapabilityStatus.NOT_EVALUABLE,
        result_available=False, unresolved_items=("SALES_EVIDENCE_MISSING",),
    )

def entry(capability, fn):
    return CapabilityInputBinding(
        spec=CapabilityInputSpec(
            project_id=context.project_id, capability=capability,
            schema_id="synthetic.sales.quote", schema_version="v1",
            payload_type=SalesQuote,
        ),
        envelope=CapabilityInputEnvelope(
            **{field: getattr(context, field) for field in KernelContext.model_fields},
            capability=capability, schema_id="synthetic.sales.quote",
            schema_version="v1", payload=offer,
        ),
        invoker=fn,
    )

entries = {
    "SALES_FIELDS": entry("SALES_FIELDS", fields),
    "SALES_DOCUMENTARY": entry("SALES_DOCUMENTARY", documentary),
}
invokers = bind_capability_inputs(
    operation=operation, context=context, plan=plan, bindings=entries,
)
outcome = execute_kernel(operation, context, plan, invokers)
assert calls == ["SALES_FIELDS", "SALES_DOCUMENTARY"]
assert offer.offered_price == Decimal("12.50")
assert outcome.status == KernelStatus.PARTIALLY_COMPLETED
assert outcome.unresolved_items == ("SALES_EVIDENCE_MISSING",)
assert outcome.decision_authority is False
assert outcome.operational_path == "FORBIDDEN"
assert outcome.provenance_status == "UNVERIFIED_ADAPTER_RESPONSIBILITY"

calls.clear()
wrong = entries["SALES_DOCUMENTARY"].envelope.model_copy(
    update={"data_snapshot_id": "FOREIGN-SNAPSHOT"}
)
try:
    bind_capability_inputs(
        operation=operation, context=context, plan=plan,
        bindings={**entries, "SALES_DOCUMENTARY": CapabilityInputBinding(
            spec=entries["SALES_DOCUMENTARY"].spec,
            envelope=wrong, invoker=documentary,
        )},
    )
except InputContractError:
    pass
else:
    raise AssertionError("Unmatched sales snapshot accepted")
assert calls == []

print(json.dumps({
    "consumer": "sales",
    "kernel_version": metadata.version("eios-kernel"),
    "inputs_version": metadata.version("eios-input-contracts"),
    "status": outcome.status.value,
    "operational_path": outcome.operational_path,
    "module_hashes": expected["hashes"],
}, sort_keys=True))
"""

PROCUREMENT = COMMON + r"""
from datetime import date
from decimal import Decimal

from eios.core.models import PurchaseOperation, DecisionContext, EvidenceValidation
from eios.pricing import run_price_intelligence, run_price_intelligence_for_company
from eios.pricing.models import (
    PriceIntelligenceInput, PriceIntelligenceAssessmentContext, PriceReference,
)
from eios.pricing.company_coverage import PriceCompanyCoverageProfile, PriceCoverageError
from eios.pricing.representativeness import RepresentativenessObservation
from eios.pricing.sufficiency import SufficiencyObservation
from eios.tco import CostComponent, TCOInput, calculate_tco

assert TCOInput.model_fields["purchase_operation"].annotation is PurchaseOperation
assert PriceIntelligenceInput.model_fields["purchase_operation"].annotation is PurchaseOperation

context = KernelContext(
    project_id="F5_6_PURCHASING", decision_id="SYNTH-BUY-88",
    scenario_id="BASE", rules_version="SYNTH-BUY-R1",
    parameters_version="SYNTH-BUY-P1", data_snapshot_id="SYNTH-BUY-S1",
)
purchase = PurchaseOperation(
    decision_id=context.decision_id, scenario_id=context.scenario_id,
    article_id="SUBSTRATE-SYNTH", supplier_id="SUPPLIER-SYNTH",
    quantity=Decimal("10"), unit_price=Decimal("5"),
    currency="EUR", operation_date=date(2026, 11, 1),
)
operation = KernelOperation(
    decision_id=context.decision_id, scenario_id=context.scenario_id, payload=purchase,
)
decision = DecisionContext(
    decision_id=context.decision_id, scenario_id=context.scenario_id,
    rules_version=context.rules_version, parameters_version=context.parameters_version,
    data_snapshot_id=context.data_snapshot_id,
)
refs = tuple(PriceReference(
    source_transaction_id=f"R{i}", article_identity=purchase.article_id,
    supplier_identity=purchase.supplier_id, quantity=purchase.quantity, unit="EA",
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
    methodology_version="F5-6",
)
assessments = PriceIntelligenceAssessmentContext(
    temporal={f"R{i}": ("ELIGIBLE", "SYNTH-TEMP") for i in (1, 2)},
    representativeness={
        f"R{i}": RepresentativenessObservation(
            ordinary_market_context=True, exceptional_condition=False,
            material_commercial_distortion=False,
            evidence_refs=(f"E{i}",), rule_reference="SYNTH-RULE-REP",
            trace_reference="SYNTH-TRACE-REP",
        ) for i in (1, 2)
    },
    sufficiency=SufficiencyObservation(
        selected_reference_ids=("R1", "R2"),
        evidence_sufficient=True, contradictions_resolved=True,
        evidence_refs=("E1", "E2"),
        rule_reference="SYNTH-RULE-SUFF", trace_reference="SYNTH-TRACE-SUFF",
    ),
)
analytical = run_price_intelligence(price_payload, assessments)
assert analytical.pr_status == "PR_AVAILABLE"
assert analytical.pr_value == Decimal("11.00")
profile = PriceCompanyCoverageProfile(
    profile_id="PROFILE-SYNTH", company_id="COMPANY-SYNTH",
    decision_id=decision.decision_id, scenario_id=decision.scenario_id,
    parameters_version=decision.parameters_version,
    data_snapshot_id=decision.data_snapshot_id, source_ref="SYNTH-PROFILE",
    evidence_id="EPROFILE", rule_reference="SYNTH-PROFILE-RULE",
    trace_reference="SYNTH-PROFILE-TRACE",
)
cost_input = TCOInput(
    purchase_operation=purchase,
    attributable_costs=(CostComponent(
        component="TRANSPORT", amount=Decimal("7.50"), currency="EUR",
        attribution_ref="SYNTH-DOC", rule_reference="SYNTH-TRANSPORT-RULE",
    ),),
)
cost = calculate_tco(cost_input)
assert cost.value == Decimal("57.50") and cost.complete

plan = KernelPlan(capabilities=("PRICE", "TCO"), policy_version="SYNTH-PURCHASE-POLICY")
calls = []
def price_producer(p, ctx):
    assert p == purchase and ctx == context
    calls.append("PRICE")
    try:
        run_price_intelligence_for_company(
            price_payload, assessments, profile,
            expected_company_id="COMPANY-SYNTH",
        )
    except PriceCoverageError as error:
        assert not error.report.complete
        assert "NORMALIZATION_BASIS_MISSING" in error.report.issues
        return KernelCapabilityResult(
            capability="PRICE", status=KernelCapabilityStatus.NOT_EVALUABLE,
            result_available=False,
            unresolved_items=("PRICE_DOCUMENTARY_COVERAGE_MISSING",),
        )
    raise AssertionError("Unproven documentary PRICE passed strict intake")

def tco_producer(p, ctx):
    assert p == purchase and ctx == context
    calls.append("TCO")
    computed = calculate_tco(cost_input)
    assert computed.value == Decimal("57.50")
    return KernelCapabilityResult(
        capability="TCO", status=KernelCapabilityStatus.COMPLETED,
        result_available=computed.complete,
        trace_references=("SYNTHETIC-TCO",),
    )

def entry(capability, producer):
    return CapabilityInputBinding(
        spec=CapabilityInputSpec(
            project_id=context.project_id, capability=capability,
            schema_id="eios.procurement.purchase", schema_version="v1",
            payload_type=PurchaseOperation,
        ),
        envelope=CapabilityInputEnvelope(
            **{field: getattr(context, field) for field in KernelContext.model_fields},
            capability=capability, schema_id="eios.procurement.purchase",
            schema_version="v1", payload=purchase,
        ),
        invoker=producer,
    )

bindings = {
    "PRICE": entry("PRICE", price_producer),
    "TCO": entry("TCO", tco_producer),
}
invokers = bind_capability_inputs(
    operation=operation, context=context, plan=plan, bindings=bindings,
)
outcome = execute_kernel(operation, context, plan, invokers)
assert calls == ["PRICE", "TCO"]
assert outcome.status == KernelStatus.PARTIALLY_COMPLETED
assert outcome.unresolved_items == ("PRICE_DOCUMENTARY_COVERAGE_MISSING",)
assert outcome.decision_authority is False
assert outcome.operational_path == "FORBIDDEN"
assert outcome.provenance_status == "UNVERIFIED_ADAPTER_RESPONSIBILITY"

calls.clear()
bad = bindings["TCO"].envelope.model_copy(
    update={"schema_version": "INCOMPATIBLE"}
)
try:
    bind_capability_inputs(
        operation=operation, context=context, plan=plan,
        bindings={**bindings, "TCO": CapabilityInputBinding(
            spec=bindings["TCO"].spec, envelope=bad, invoker=tco_producer,
        )},
    )
except InputContractError:
    pass
else:
    raise AssertionError("Mismatched second capability schema accepted")
assert calls == []

print(json.dumps({
    "consumer": "procurement",
    "kernel_version": metadata.version("eios-kernel"),
    "inputs_version": metadata.version("eios-input-contracts"),
    "price": str(analytical.pr_value),
    "tco": str(cost.value),
    "status": outcome.status.value,
    "operational_path": outcome.operational_path,
    "module_hashes": expected["hashes"],
}, sort_keys=True))
"""


def inspect_wheels(selected: dict[str, Path]) -> dict[str, str]:
    """No duplicated EIOS path, and each byte matches the canonical repo source."""
    all_hashes: dict[str, str] = {}
    for dist, wheel in selected.items():
        WHEEL_SPECS[dist][3](wheel)
        with zipfile.ZipFile(wheel) as archive:
            entries = archive.namelist()
            if len(entries) != len(set(entries)):
                raise ValueError(f"Duplicate ZIP paths in {dist}")
            for name in entries:
                if not name.startswith("eios/"):
                    continue
                if name in all_hashes:
                    raise ValueError(f"Duplicate EIOS installed path: {name}")
                if not name.endswith(".py"):
                    raise ValueError(f"Unexpected EIOS payload: {name}")
                canonical = ROOT / name
                if not canonical.is_file() or archive.read(name) != canonical.read_bytes():
                    raise ValueError(f"Noncanonical EIOS source in {dist}: {name}")
                all_hashes[name] = hashlib.sha256(canonical.read_bytes()).hexdigest()
    if "eios/input_contracts/contracts.py" not in all_hashes:
        raise ValueError("Neutral input contract source missing")
    if "eios/kernel/execution.py" not in all_hashes:
        raise ValueError("Neutral kernel source missing")
    return all_hashes


def check(wheels: dict[str, Path]) -> dict:
    if set(wheels) != set(WHEEL_SPECS):
        raise ValueError("All five independently built wheel distributions required")
    paths = {dist: file.resolve() for dist, file in wheels.items()}
    results = {}
    with tempfile.TemporaryDirectory(prefix="eios-f5-6-domain-clients-") as workspace:
        for mode, distributions, program in (
            ("sales", ("eios-kernel", "eios-input-contracts"), SALES),
            ("procurement", tuple(WHEEL_SPECS), PROCUREMENT),
        ):
            selected = {name: paths[name] for name in distributions}
            expected_hashes = inspect_wheels(selected)
            root = Path(workspace) / mode
            root.mkdir()
            venv_path = root / "venv"
            venv.EnvBuilder(with_pip=True, system_site_packages=False).create(venv_path)
            python = venv_path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            environment = os.environ.copy()
            environment.pop("PYTHONPATH", None)
            environment["PYTHONNOUSERSITE"] = "1"
            environment["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
            install = subprocess.run(
                [str(python), "-m", "pip", "install", "--no-cache-dir",
                 *(str(selected[dist]) for dist in distributions)],
                cwd=root, env=environment, capture_output=True, text=True, timeout=240,
            )
            if install.returncode:
                raise RuntimeError(
                    f"{mode}: wheel install failed: {install.stderr[-4500:]}"
                )
            check_deps = subprocess.run(
                [str(python), "-m", "pip", "check"],
                cwd=root, env=environment, capture_output=True, text=True, timeout=45,
            )
            if check_deps.returncode:
                raise RuntimeError(f"{mode}: dependency check failed: {check_deps.stdout}")
            report = subprocess.run(
                [str(python), "-I", "-c", program, json.dumps({
                    "versions": {dist: WHEEL_SPECS[dist][2] for dist in distributions},
                    "hashes": expected_hashes,
                })],
                cwd=root, env=environment, capture_output=True, text=True, timeout=80,
            )
            if report.returncode:
                raise RuntimeError(
                    f"{mode}: technical input contract failed:\n"
                    + report.stdout[-2000:] + "\n" + report.stderr[-4500:]
                )
            result = json.loads(report.stdout)
            if result.get("consumer") != mode:
                raise ValueError(f"{mode}: wrong consumer result")
            if result.get("module_hashes") != expected_hashes:
                raise ValueError(f"{mode}: wheel bytes/installed source changed")
            if result.get("status") != "PARTIALLY_COMPLETED":
                raise ValueError(f"{mode}: unexpected technical status")
            if result.get("operational_path") != "FORBIDDEN":
                raise ValueError(f"{mode}: business authority leaked")
            if mode == "procurement" and (
                result.get("price") != "11.00" or result.get("tco") != "57.50"
            ):
                raise ValueError("Canonical PRICE/TCO calculation regression")
            results[mode] = result
    return {
        "verification": "F5_6_NEUTRAL_INPUT_TWO_DOMAINS_SUCCESS",
        "neutral_kernel_sha256": results["sales"]["module_hashes"]["eios/kernel/execution.py"],
        "neutral_input_sha256": results["sales"]["module_hashes"]["eios/input_contracts/contracts.py"],
        "sales_installed_without_procurement": True,
        "procurement_real_price": results["procurement"]["price"],
        "procurement_real_tco": results["procurement"]["tco"],
        "statuses": {mode: result["status"] for mode, result in results.items()},
        "operational_path": "FORBIDDEN",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for folder in ("kernel", "inputs", "contracts", "price", "tco"):
        parser.add_argument(f"--{folder}-dir", type=Path, default=Path("dist") / folder)
    opts = parser.parse_args()
    wheels: dict[str, Path] = {}
    for dist, (folder, pattern, _, _) in WHEEL_SPECS.items():
        found = list(getattr(opts, folder + "_dir").resolve().glob(pattern))
        if len(found) != 1:
            raise SystemExit(f"Expected exactly one wheel for {dist}: {len(found)} found")
        wheels[dist] = found[0]
    print(json.dumps(check(wheels), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
