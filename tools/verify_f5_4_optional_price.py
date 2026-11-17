"""F5.4: isolated canonical PRICE C1 tests with and without neutral EIOS kernel.

A deliberate boundary: eios-price-procurement and eios-tco-procurement
BOTH own eios/core/models.py. This verifier rejects combined installation.
Only PRICE by itself and PRICE + non-overlapping kernel are permitted.
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
    from .build_eios_price_distribution import SOURCE_FILES, ROOT, audit_wheel
    from .build_eios_kernel_distribution import audit_wheel as audit_kernel
    from .build_eios_tco_distribution import audit_wheel as audit_tco
    from .build_eios_contracts_distribution import audit_wheel as audit_contracts
else:
    from build_eios_price_distribution import SOURCE_FILES, ROOT, audit_wheel
    from build_eios_kernel_distribution import audit_wheel as audit_kernel
    from build_eios_tco_distribution import audit_wheel as audit_tco
    from build_eios_contracts_distribution import audit_wheel as audit_contracts


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

from pydantic import ValidationError

mode, hashes_json = sys.argv[1:3]
hashes = json.loads(hashes_json)
assert metadata.version("eios-price-procurement") == "0.2.0"
assert metadata.version("eios-contracts-procurement") == "0.1.0"
for missing in ("eios-mvp", "eios-tco-procurement"):
    try:
        metadata.version(missing)
    except metadata.PackageNotFoundError:
        pass
    else:
        raise AssertionError("Unexpected overlapping distribution: " + missing)
for name in ("eios.frontend", "eios.company_app",
             "eios.core.execution_boundary", "eios.rules", "eios.quality",
             "eios.finance", "openpyxl", "streamlit"):
    assert importlib.util.find_spec(name) is None, name
for path, digest in hashes.items():
    module_name = path[:-3].replace("/", ".").removesuffix(".__init__")
    module = importlib.import_module(module_name)
    assert hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() == digest, path

from eios.core.models import (
    DecisionContext, EvidenceValidation, PurchaseOperation,
)
from eios.pricing import run_price_intelligence, run_price_intelligence_for_company
from eios.pricing.engine import run_price_intelligence as canonical_engine
from eios.pricing.company_coverage import (
    PriceCompanyCoverageProfile, PriceCoverageError,
    assess_price_company_coverage,
)
from eios.pricing.models import (
    PriceIntelligenceAssessmentContext, PriceIntelligenceInput, PriceReference,
)
from eios.pricing.representativeness import RepresentativenessObservation
from eios.pricing.sufficiency import SufficiencyObservation

assert run_price_intelligence is canonical_engine
decision = DecisionContext(
    decision_id="D-F5-4", scenario_id="S-F5-4", rules_version="RULES-1",
    parameters_version="PARAMS-1", data_snapshot_id="SYNTHETIC-SNAPSHOT-1",
)
purchase = PurchaseOperation(
    decision_id="D-F5-4", scenario_id="S-F5-4",
    article_id="SUBSTRATE-SYNTH", supplier_id="SUP-SYNTH",
    quantity=Decimal("1"), unit_price=Decimal("15"),
    currency="EUR", operation_date=date(2026, 11, 1),
)
references = tuple(PriceReference(
    source_transaction_id=f"R{i}", article_identity=purchase.article_id,
    supplier_identity="SUP-SYNTH", quantity=Decimal("1"), unit="EA",
    unit_price=Decimal(value), currency="EUR",
    operation_date=date(2026, 10, 15), evidence_refs=(f"E{i}",),
) for i, value in ((1, "10.00"), (2, "12.00")))
payload = PriceIntelligenceInput(
    decision_context=decision, purchase_operation=purchase,
    references=references,
    evidence_validations=tuple(
        EvidenceValidation(evidence_id=f"E{i}", status="VALID", reason="synthetic")
        for i in (1, 2)
    ) + (EvidenceValidation(evidence_id="EPROFILE", status="VALID", reason="synthetic"),),
    normalization_basis=None, economic_basis_evidence=(),
    methodology_version="C1-F5-4",
)
assessment = PriceIntelligenceAssessmentContext(
    temporal={f"R{i}": ("ELIGIBLE", "SYNTH-RULE-T") for i in (1, 2)},
    representativeness={
        f"R{i}": RepresentativenessObservation(
            ordinary_market_context=True, exceptional_condition=False,
            material_commercial_distortion=False,
            contradiction_material_unresolved=False,
            evidence_refs=(f"E{i}",), rule_reference="SYNTH-RULE-REP",
            trace_reference="SYNTH-TRACE-REP",
        ) for i in (1, 2)
    },
    sufficiency=SufficiencyObservation(
        selected_reference_ids=("R1", "R2"),
        evidence_refs=("E1", "E2"), rule_reference="SYNTH-RULE-SUF",
        trace_reference="SYNTH-TRACE-SUF", evidence_sufficient=True,
        contradictions_resolved=True,
    ),
)
synthetic_result = run_price_intelligence(payload, assessment)
assert synthetic_result.pr_value == Decimal("11.00")
assert synthetic_result.pr_status == "PR_AVAILABLE"
assert synthetic_result.counts.n_selected == 2
assert synthetic_result.reference_set == ("R1", "R2")
assert synthetic_result.data_snapshot_id == decision.data_snapshot_id

empty = PriceIntelligenceInput(
    decision_context=decision, purchase_operation=purchase,
    references=(), evidence_validations=(),
    methodology_version="C1-F5-4",
)
no_references = run_price_intelligence(
    empty, PriceIntelligenceAssessmentContext(
        sufficiency=SufficiencyObservation(selected_reference_ids=()),
    ),
)
assert no_references.pr_status == "PR_NOT_JUSTIFIABLE"
assert no_references.pr_value is None
assert no_references.counts.n_selected == 0

# A plausible C1 number alone is NOT admission of company documentary coverage.
profile = PriceCompanyCoverageProfile(
    profile_id="PROFILE-SYNTH", company_id="COMPANY-SYNTH",
    decision_id=decision.decision_id, scenario_id=decision.scenario_id,
    parameters_version=decision.parameters_version,
    data_snapshot_id=decision.data_snapshot_id,
    source_ref="SYNTH-DOC", evidence_id="EPROFILE",
    rule_reference="SYNTH-RULE-PROFILE", trace_reference="SYNTH-TRACE-PROFILE",
)
report = assess_price_company_coverage(
    payload, profile, expected_company_id="COMPANY-SYNTH",
)
assert report.status == "INCOMPLETE"
assert "NORMALIZATION_BASIS_MISSING" in report.issues
assert "MATERIAL_COMPARISON_MISSING:R1:QUANTITY" in report.issues
try:
    run_price_intelligence_for_company(
        payload, assessment, profile, expected_company_id="COMPANY-SYNTH",
    )
except PriceCoverageError as exc:
    assert not exc.report.complete
else:
    raise AssertionError("Missing documentary coverage accepted")
foreign = assess_price_company_coverage(
    payload, profile, expected_company_id="FOREIGN-COMPANY",
)
assert "COMPANY_SCOPE_MISMATCH" in foreign.issues

if mode == "price-only":
    assert importlib.util.find_spec("eios.kernel") is None
    assert importlib.util.find_spec("eios.parameters") is None
elif mode == "price-and-kernel":
    assert metadata.version("eios-kernel") == "0.1.0"
    from eios.kernel.execution import (
        KernelCapabilityResult, KernelCapabilityStatus, KernelContext,
        KernelOperation, KernelPlan, KernelStatus, execute_kernel,
    )
    from eios.parameters.center import ParameterConfigurationCenter
    assert ParameterConfigurationCenter.__name__ == "ParameterConfigurationCenter"
    context = KernelContext(
        project_id="SYNTH-F5-4-PROCUREMENT", decision_id=decision.decision_id,
        scenario_id=decision.scenario_id, rules_version=decision.rules_version,
        parameters_version=decision.parameters_version,
        data_snapshot_id=decision.data_snapshot_id,
    )
    operation = KernelOperation(
        decision_id=decision.decision_id,
        scenario_id=decision.scenario_id, payload=payload,
    )
    plan = KernelPlan(capabilities=("PRICE",), policy_version="SYNTH-F5-4")

    def strict_price_invoker(p, ctx):
        # Trusted project identity and source authentication remain the adapter's job.
        assert ctx.project_id == "SYNTH-F5-4-PROCUREMENT"
        for field in DecisionContext.model_fields:
            assert getattr(p.decision_context, field) == getattr(ctx, field)
        assert p.purchase_operation == purchase
        resolved = run_price_intelligence_for_company(
            p, assessment, profile, expected_company_id="COMPANY-SYNTH",
        )
        return KernelCapabilityResult(
            capability="PRICE", status=KernelCapabilityStatus.COMPLETED,
            result_available=resolved.pr_value is not None,
        )
    failed = execute_kernel(operation, context, plan, {"PRICE": strict_price_invoker})
    assert failed.status == KernelStatus.FAILED
    assert failed.failure_reason.startswith("PRICE:")
    assert failed.decision_authority is False
    assert failed.operational_path == "FORBIDDEN"
    assert failed.provenance_status == "UNVERIFIED_ADAPTER_RESPONSIBILITY"

    def unsubstantiated_price(p, ctx):
        assert ctx.project_id == "SYNTH-F5-4-PROCUREMENT"
        result = run_price_intelligence(
            empty, PriceIntelligenceAssessmentContext(
                sufficiency=SufficiencyObservation(selected_reference_ids=()),
            ),
        )
        assert result.pr_status == "PR_NOT_JUSTIFIABLE"
        return KernelCapabilityResult(
            capability="PRICE", status=KernelCapabilityStatus.NOT_EVALUABLE,
            result_available=False,
            unresolved_items=("PRICE_NOT_JUSTIFIABLE",),
        )
    partial = execute_kernel(operation, context, plan, {"PRICE": unsubstantiated_price})
    assert partial.status == KernelStatus.PARTIALLY_COMPLETED
    assert partial.unresolved_items == ("PRICE_NOT_JUSTIFIABLE",)
    assert partial.decision_authority is False
    assert partial.operational_path == "FORBIDDEN"
else:
    raise ValueError("Unknown PRICE test mode")

print(json.dumps({
    "mode": mode,
    "price_version": metadata.version("eios-price-procurement"),
    "module_hashes": hashes,
    "synthetic_reference_price": str(synthetic_result.pr_value),
    "synthetic_reference_status": synthetic_result.pr_status,
    "company_documentary_coverage": report.status,
    "no_reference_status": no_references.pr_status,
    "operational_path": "FORBIDDEN",
}, sort_keys=True))
"""


def content_hashes(wheel: Path) -> dict[str, str]:
    audit_wheel(wheel)
    with zipfile.ZipFile(wheel) as archive:
        expected = {
            path.as_posix(): hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            for path in SOURCE_FILES
        }
        for path, digest in expected.items():
            if hashlib.sha256(archive.read(path)).hexdigest() != digest:
                raise ValueError(f"Wheel does not contain canonical PRICE source: {path}")
        return expected


def installed_paths(wheel: Path) -> set[str]:
    with zipfile.ZipFile(wheel) as archive:
        return {item for item in archive.namelist() if item.startswith("eios/")}


def ensure_no_shared_paths(first: Path, second: Path) -> None:
    shared = installed_paths(first) & installed_paths(second)
    if shared:
        raise ValueError("Wheel path collision: " + ", ".join(sorted(shared)))


def verify_shared_contracts(price_wheel: Path, tco_wheel: Path, contracts_wheel: Path) -> str:
    """New wheels must have no duplicate installed paths."""
    audit_tco(tco_wheel)
    audit_contracts(contracts_wheel)
    for a, b in (
        (price_wheel, tco_wheel),
        (price_wheel, contracts_wheel),
        (tco_wheel, contracts_wheel),
    ):
        ensure_no_shared_paths(a, b)
    if installed_paths(contracts_wheel) != {"eios/core/models.py"}:
        raise ValueError("Unexpected shared contracts module ownership")
    return "SINGLE_C0_OWNER_VERIFIED"

def check(price_wheel: Path, kernel_wheel: Path, tco_wheel: Path, contracts_wheel: Path) -> dict:
    price_wheel, kernel_wheel, tco_wheel, contracts_wheel = (
        path.resolve() for path in (price_wheel, kernel_wheel, tco_wheel, contracts_wheel)
    )
    hashes = content_hashes(price_wheel)
    audit_kernel(kernel_wheel)
    ensure_no_shared_paths(price_wheel, kernel_wheel)
    ensure_no_shared_paths(kernel_wheel, contracts_wheel)
    tco_relation = verify_shared_contracts(price_wheel, tco_wheel, contracts_wheel)
    with zipfile.ZipFile(contracts_wheel) as archive:
        canonical = archive.read("eios/core/models.py")
    canonical_digest = hashlib.sha256((ROOT / "eios/core/models.py").read_bytes()).hexdigest()
    if hashlib.sha256(canonical).hexdigest() != canonical_digest:
        raise ValueError("Shared contracts wheel is not canonical")
    hashes["eios/core/models.py"] = canonical_digest
    reports = []
    with tempfile.TemporaryDirectory(prefix="eios-f5-4-price-") as temporary:
        root = Path(temporary)
        for mode in ("price-only", "price-and-kernel"):
            project = root / mode
            project.mkdir()
            home = project / "venv"
            venv.EnvBuilder(with_pip=True, system_site_packages=False).create(home)
            python = home / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            environment = os.environ.copy()
            environment.pop("PYTHONPATH", None)
            environment["PYTHONNOUSERSITE"] = "1"
            environment["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
            wheels = [str(price_wheel), str(contracts_wheel)]
            if mode == "price-and-kernel":
                wheels.append(str(kernel_wheel))
            installed = subprocess.run(
                [str(python), "-m", "pip", "install", "--no-cache-dir", *wheels],
                env=environment, cwd=project, capture_output=True, text=True, timeout=180,
            )
            if installed.returncode:
                raise RuntimeError(f"{mode}: install failed: {installed.stderr[-3000:]}")
            tested = subprocess.run(
                [str(python), "-I", "-c", SMOKE, mode, json.dumps(hashes)],
                env=environment, cwd=project, capture_output=True, text=True, timeout=75,
            )
            if tested.returncode:
                raise RuntimeError(
                    f"{mode}: probe failed:\n{tested.stdout[-1500:]}\n{tested.stderr[-3000:]}"
                )
            report = json.loads(tested.stdout)
            if report.get("mode") != mode or report.get("module_hashes") != hashes:
                raise ValueError("PRICE installation failed SHA256 contract")
            for key, expected in {
                "price_version": "0.2.0",
                "synthetic_reference_price": "11.00",
                "synthetic_reference_status": "PR_AVAILABLE",
                "company_documentary_coverage": "INCOMPLETE",
                "no_reference_status": "PR_NOT_JUSTIFIABLE",
                "operational_path": "FORBIDDEN",
            }.items():
                if report.get(key) != expected:
                    raise ValueError(f"{mode}: PRICE contract violation: {key}")
            reports.append(mode)
    return {
        "verification": "F5.4_OPTIONAL_PRICE_DISTRIBUTION_SUCCESS",
        "price_wheel_sha256": hashlib.sha256(price_wheel.read_bytes()).hexdigest(),
        "price_module_sha256": hashes,
        "tested_modes": reports,
        "synthetic_price": "11.00",
        "documentary_coverage": "INCOMPLETE",
        "price_plus_tco": tco_relation,
        "operational_path": "FORBIDDEN",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--price-dir", type=Path, default=Path("dist/price"))
    parser.add_argument("--kernel-dir", type=Path, default=Path("dist/kernel"))
    parser.add_argument("--tco-dir", type=Path, default=Path("dist/tco"))
    parser.add_argument("--contracts-dir", type=Path, default=Path("dist/contracts"))
    args = parser.parse_args()
    price = list(args.price_dir.resolve().glob("eios_price_procurement-*.whl"))
    kernel = list(args.kernel_dir.resolve().glob("eios_kernel-*.whl"))
    tco = list(args.tco_dir.resolve().glob("eios_tco_procurement-*.whl"))
    contracts = list(args.contracts_dir.resolve().glob("eios_contracts_procurement-*.whl"))
    if len(price) != 1 or len(kernel) != 1 or len(tco) != 1 or len(contracts) != 1:
        raise SystemExit("Expected PRICE, neutral kernel, TCO and shared contracts wheels")
    print(json.dumps(check(price[0], kernel[0], tco[0], contracts[0]), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
