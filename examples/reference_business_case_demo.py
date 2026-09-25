"""Generate both synthetic reference results and their local review in one run."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import tempfile

from .reference_business_case_001 import (
    execute_reference_business_case_with_selected_observations,
)
from .reference_business_case_review import render_review


_NAMES = ("reference-negative-result.json", "reference-result.json", "reference-review.html")
_PRICE_NAMES = ("reference-negative-price.json", "reference-price.json")
_TCO_NAMES = ("reference-negative-tco.json", "reference-tco.json")
_SUPPLIER_NAMES = ("reference-negative-supplier-risk.json", "reference-supplier-risk.json")
_C0_NAMES = ("reference-negative-c0.json", "reference-c0.json")
_TWIN_NAMES = ("reference-negative-decision-twin.json", "reference-decision-twin.json")
_SCENARIO_NAMES = ("reference-negative-scenario-coordination.json",
                   "reference-scenario-coordination.json")
_NI_NAMES = ("reference-negative-negotiation-intelligence.json",
             "reference-negotiation-intelligence.json")


def create_reference_demo(output_dir: Path, *, with_price: bool = False,
                          with_tco: bool = False,
                          with_supplier_risk: bool = False,
                          with_c0: bool = False,
                          with_decision_twin: bool = False,
                          with_scenario_coordination: bool = False,
                          with_negotiation_intelligence: bool = False) -> tuple[Path, ...]:
    """Reuse closed runners and publish one complete local demonstration directory."""
    output_dir = Path(output_dir)
    if output_dir.exists():
        raise FileExistsError(f"Output already exists: {output_dir}")
    if not output_dir.parent.is_dir():
        raise ValueError(f"Output parent directory does not exist: {output_dir.parent}")

    observations = None
    tco_observations = None
    negative_run, negative_captures = execute_reference_business_case_with_selected_observations(
        variant="negative", with_price=with_price, with_tco=with_tco,
        with_supplier_risk=with_supplier_risk, with_c0=with_c0,
        with_decision_twin=with_decision_twin,
        with_scenario_coordination=with_scenario_coordination,
        with_negotiation_intelligence=with_negotiation_intelligence,
    )
    eligible_run, eligible_captures = execute_reference_business_case_with_selected_observations(
        variant="qtg-eligible", with_price=with_price, with_tco=with_tco,
        with_supplier_risk=with_supplier_risk, with_c0=with_c0,
        with_decision_twin=with_decision_twin,
        with_scenario_coordination=with_scenario_coordination,
        with_negotiation_intelligence=with_negotiation_intelligence,
    )
    negative, eligible = negative_run.to_payload(), eligible_run.to_payload()
    def pair(key):
        return (negative_captures[key].to_payload(), eligible_captures[key].to_payload())
    if with_price:
        observations = pair("price")
    if with_tco:
        tco_observations = pair("tco")
    supplier_observations = pair("supplier_risk") if with_supplier_risk else None
    c0_observations = pair("c0") if with_c0 else None
    twin_observations = pair("decision_twin") if with_decision_twin else None
    scenario_observations = pair("scenario_coordination") if with_scenario_coordination else None
    ni_observations = pair("negotiation_intelligence") if with_negotiation_intelligence else None
    html = render_review(negative, eligible, price_observations=observations,
                         tco_observations=tco_observations,
                         supplier_observations=supplier_observations,
                         c0_observations=c0_observations,
                         twin_observations=twin_observations,
                         scenario_observations=scenario_observations,
                         ni_observations=ni_observations)

    stage = Path(tempfile.mkdtemp(prefix=".reference-demo-", dir=output_dir.parent))
    try:
        for name, payload in zip(_NAMES[:2], (negative, eligible)):
            (stage / name).write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        (stage / _NAMES[2]).write_text(html, encoding="utf-8")
        if observations is not None:
            for name, payload in zip(_PRICE_NAMES, observations):
                (stage / name).write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        if tco_observations is not None:
            for name, payload in zip(_TCO_NAMES, tco_observations):
                (stage / name).write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        if supplier_observations is not None:
            for name, payload in zip(_SUPPLIER_NAMES, supplier_observations):
                (stage / name).write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        if c0_observations is not None:
            for name, payload in zip(_C0_NAMES, c0_observations):
                (stage / name).write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        if twin_observations is not None:
            for name, payload in zip(_TWIN_NAMES, twin_observations):
                (stage / name).write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        if scenario_observations is not None:
            for name, payload in zip(_SCENARIO_NAMES, scenario_observations):
                (stage / name).write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        if ni_observations is not None:
            for name, payload in zip(_NI_NAMES, ni_observations):
                (stage / name).write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        stage.rename(output_dir)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return tuple(output_dir / name for name in (
        _NAMES + (_PRICE_NAMES if with_price else ()) + (_TCO_NAMES if with_tco else ())
        + (_SUPPLIER_NAMES if with_supplier_risk else ())
        + (_C0_NAMES if with_c0 else ())
        + (_TWIN_NAMES if with_decision_twin else ())
        + (_SCENARIO_NAMES if with_scenario_coordination else ())
        + (_NI_NAMES if with_negotiation_intelligence else ())
    ))


def verify_reference_demo(directory: Path) -> tuple[str, str]:
    """Read and replay the fixed synthetic cases without changing the directory."""
    directory = Path(directory)
    if not directory.is_dir():
        raise ValueError(f"Demo directory does not exist: {directory}")
    negative = json.loads((directory / _NAMES[0]).read_text(encoding="utf-8"))
    eligible = json.loads((directory / _NAMES[1]).read_text(encoding="utf-8"))
    stored_html = (directory / _NAMES[2]).read_text(encoding="utf-8")
    present = tuple((directory / name).exists() for name in _PRICE_NAMES)
    if any(present) and not all(present):
        raise ValueError("Both PRICE observations are required together")
    observations = (tuple(json.loads((directory / name).read_text(encoding="utf-8"))
                          for name in _PRICE_NAMES) if all(present) else None)
    tco_present = tuple((directory / name).exists() for name in _TCO_NAMES)
    if any(tco_present) and not all(tco_present):
        raise ValueError("Both TCO observations are required together")
    tco_observations = (tuple(json.loads((directory / name).read_text(encoding="utf-8"))
                              for name in _TCO_NAMES) if all(tco_present) else None)
    supplier_present = tuple((directory / name).exists() for name in _SUPPLIER_NAMES)
    if any(supplier_present) and not all(supplier_present):
        raise ValueError("Both SUPPLIER_RISK_VALUE observations are required together")
    supplier_observations = (tuple(json.loads((directory / name).read_text(encoding="utf-8"))
                                   for name in _SUPPLIER_NAMES) if all(supplier_present) else None)
    c0_present = tuple((directory / name).exists() for name in _C0_NAMES)
    if any(c0_present) and not all(c0_present):
        raise ValueError("Both C0 observations are required together")
    c0_observations = (tuple(json.loads((directory / name).read_text(encoding="utf-8"))
                             for name in _C0_NAMES) if all(c0_present) else None)
    twin_present = tuple((directory / name).exists() for name in _TWIN_NAMES)
    if any(twin_present) and not all(twin_present):
        raise ValueError("Both DECISION_TWIN observations are required together")
    twin_observations = (tuple(json.loads((directory / name).read_text(encoding="utf-8"))
                               for name in _TWIN_NAMES) if all(twin_present) else None)
    scenario_present = tuple((directory / name).exists() for name in _SCENARIO_NAMES)
    if any(scenario_present) and not all(scenario_present):
        raise ValueError("Both SCENARIO_COORDINATION observations are required together")
    scenario_observations = (tuple(json.loads((directory / name).read_text(encoding="utf-8"))
                                   for name in _SCENARIO_NAMES) if all(scenario_present) else None)
    ni_present = tuple((directory / name).exists() for name in _NI_NAMES)
    if any(ni_present) and not all(ni_present):
        raise ValueError("Both NEGOTIATION_INTELLIGENCE observations are required together")
    ni_observations = (tuple(json.loads((directory / name).read_text(encoding="utf-8"))
                             for name in _NI_NAMES) if all(ni_present) else None)

    expected_html = render_review(negative, eligible, price_observations=observations,
                                  tco_observations=tco_observations,
                                  supplier_observations=supplier_observations,
                                  c0_observations=c0_observations,
                                  twin_observations=twin_observations,
                                  scenario_observations=scenario_observations,
                                  ni_observations=ni_observations)
    if stored_html != expected_html:
        raise ValueError("Review HTML differs from the two terminal artifacts")
    for variant, stored in (("negative", negative), ("qtg-eligible", eligible)):
        replayed, captures = execute_reference_business_case_with_selected_observations(
            variant=variant, with_price=observations is not None,
            with_tco=tco_observations is not None,
            with_supplier_risk=supplier_observations is not None,
            with_c0=c0_observations is not None,
            with_decision_twin=twin_observations is not None,
            with_scenario_coordination=scenario_observations is not None,
            with_negotiation_intelligence=ni_observations is not None,
        )
        index = 0 if variant == "negative" else 1
        for label, saved_pair, key in (
            ("PRICE", observations, "price"), ("TCO", tco_observations, "tco"),
            ("SUPPLIER_RISK_VALUE", supplier_observations, "supplier_risk"),
            ("C0", c0_observations, "c0"),
            ("DECISION_TWIN", twin_observations, "decision_twin"),
            ("SCENARIO_COORDINATION", scenario_observations, "scenario_coordination"),
            ("NEGOTIATION_INTELLIGENCE", ni_observations, "negotiation_intelligence"),
        ):
            if saved_pair is not None and saved_pair[index] != captures[key].to_payload():
                raise ValueError(f"{variant}: {label} observation differs from fixture replay")
        if stored != replayed.to_payload():
            raise ValueError(f"{variant}: terminal differs from the current fixture replay")
    return negative["terminal_fingerprint"], eligible["terminal_fingerprint"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output-dir", type=Path,
                        help="New directory for the two JSON files and read-only HTML")
    action.add_argument("--verify-dir", type=Path,
                        help="Read and replay an existing synthetic demo directory")
    parser.add_argument("--with-price", action="store_true",
                        help="Export both same-run PRICE observations and show them in HTML")
    parser.add_argument("--with-tco", action="store_true",
                        help="Export both same-run TCO observations and show them in HTML")
    parser.add_argument("--with-supplier-risk", action="store_true",
                        help="Export both synthetic supplier assessments and show their source limits")
    parser.add_argument("--with-c0", action="store_true",
                        help="Export both same-run C0/CRC observations and show their authority limits")
    parser.add_argument("--with-decision-twin", action="store_true",
                        help="Export both structural Twin comparisons and show their limits")
    parser.add_argument("--with-scenario-coordination", action="store_true",
                        help="Export both synthetic O2 support packages and show their limits")
    parser.add_argument("--with-negotiation-intelligence", action="store_true",
                        help="Export both synthetic C0-bound NI observations and show their limits")
    args = parser.parse_args()
    if args.verify_dir is not None:
        if (args.with_price or args.with_tco or args.with_supplier_risk
                or args.with_c0 or args.with_decision_twin
                or args.with_scenario_coordination or args.with_negotiation_intelligence):
            parser.error("Observation flags apply only to --output-dir; verification detects sidecars")
        negative_fp, eligible_fp = verify_reference_demo(args.verify_dir)
        print("Revisión y repetición sintética coinciden; ruta operacional FORBIDDEN.")
        print(f"negative: {negative_fp}")
        print(f"qtg-eligible: {eligible_fp}")
        return
    files = create_reference_demo(args.output_dir, with_price=args.with_price,
                                  with_tco=args.with_tco,
                                  with_supplier_risk=args.with_supplier_risk,
                                  with_c0=args.with_c0,
                                  with_decision_twin=args.with_decision_twin,
                                  with_scenario_coordination=args.with_scenario_coordination,
                                  with_negotiation_intelligence=args.with_negotiation_intelligence)
    print("Simulación sintética completada; ruta operacional FORBIDDEN.")
    for path in files:
        print(path)


if __name__ == "__main__":
    main()
