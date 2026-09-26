"""Run and verify the complete, strictly synthetic Reference Business Case 002."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import tempfile

from eios.core.case_provenance import classify_reference_operational_simulation
from eios.core.price_integration import build_reference_observed_price_invoker
from eios.core.projection_quality_consumer import consume_projection_quality
from eios.core.projection_quality_producer import produce_projection_quality
from eios.core.reference_c0_observation import (
    _close_reference_c0_observation, validate_reference_c0_observation_payload,
)
from eios.core.reference_decision_twin_observation import (
    _close_reference_decision_twin_observation,
    validate_reference_decision_twin_observation_payload,
)
from eios.core.reference_ladder_observation import (
    _close_reference_ladder_observation, validate_reference_ladder_observation_payload,
)
from eios.core.reference_ni_observation import (
    _close_reference_ni_observation, validate_reference_ni_observation_payload,
)
from eios.core.reference_price_observation import (
    _close_reference_price_observation, validate_reference_price_observation_payload,
)
from eios.core.reference_scenario_coordination_observation import (
    _close_reference_scenario_coordination_observation,
    validate_reference_scenario_coordination_observation_payload,
)
from eios.core.reference_simulation_execution import run_reference_operational_simulation
from eios.core.reference_supplier_risk_observation import (
    _close_reference_supplier_risk_observation,
    validate_reference_supplier_risk_observation_payload,
)
from eios.core.reference_tco_observation import (
    _close_reference_tco_observation, validate_reference_tco_observation_payload,
)
from eios.core.tco_integration import build_reference_observed_tco_invoker
from eios.rules.decision_twin_integration import (
    ProvenancedDecisionTwinAlternativeInput,
    build_reference_observed_decision_twin_invoker,
)
from eios.rules.negotiation_provenance import (
    build_reference_observed_c0_bound_ni_invoker,
    build_reference_observed_c0_bound_ladder_invoker,
)
from eios.rules.provenance import (
    AssessmentTraceBinding, build_reference_observed_rules_engine_c0_invoker,
)
from eios.rules.scenario_integration import build_reference_observed_scenario_coordination_invoker
from eios.supplier.risk_value import build_reference_observed_supplier_risk_value_invoker
from eios.tco.models import TCOInput

from .reference_business_case_002_material import (
    c0_sources, negotiation_material, price_sources, scenario_material,
    supplier_sources,
)


CASE_ID = "REF-BUSINESS-002"
POLICY_VERSION = "REF-BUSINESS-002-v1"
OBSERVATIONS = {
    "price": (_close_reference_price_observation, validate_reference_price_observation_payload,
              "price_invoker"),
    "tco": (_close_reference_tco_observation, validate_reference_tco_observation_payload,
            "tco_invoker"),
    "supplier-risk": (_close_reference_supplier_risk_observation,
                      validate_reference_supplier_risk_observation_payload, "supplier_invoker"),
    "c0": (_close_reference_c0_observation, validate_reference_c0_observation_payload,
           "c0_invoker"),
    "decision-twin": (_close_reference_decision_twin_observation,
                      validate_reference_decision_twin_observation_payload, "twin_invoker"),
    "scenario-coordination": (_close_reference_scenario_coordination_observation,
                              validate_reference_scenario_coordination_observation_payload,
                              "scenario_invoker"),
    "negotiation-intelligence": (_close_reference_ni_observation,
                                 validate_reference_ni_observation_payload, "ni_invoker"),
    "negotiation-ladder": (_close_reference_ladder_observation,
                           validate_reference_ladder_observation_payload, "ladder_invoker"),
}


def execute_reference_business_case_002():
    """Return one terminal and eight sidecars captured from that exact call."""
    bundle, purchase, context, _, assessment, trace = c0_sources()
    _, _, _, price_input, price_assessment = price_sources()
    _, _, _, supplier, risk, supplier_evidences = supplier_sources()
    _, _, _, preparation, scenario_inputs = scenario_material()
    _, _, _, content, ni_evidences, bindings = negotiation_material()
    receipt = produce_projection_quality(
        envelope=bundle.envelope, execution_mode="SYNTHETIC_TEST",
    )
    consumption = consume_projection_quality(
        receipt=receipt, envelope=bundle.envelope,
        execution_mode="SYNTHETIC_TEST", consumption_scope="TEST_ONLY",
    )
    alternatives = tuple(
        ProvenancedDecisionTwinAlternativeInput(
            representation_ref=f"REF-BUSINESS-002-ALT-{index}", scenario_input=item,
        ) for index, item in enumerate(scenario_inputs, start=1)
    )
    negotiation = dict(
        purchase=purchase, content_evidence=content, evidences=ni_evidences,
        bindings=bindings, reference_case_id=CASE_ID,
    )
    invokers = {
        "price_invoker": build_reference_observed_price_invoker(
            payload=price_input, assessment_context=price_assessment,
            reference_case_id=CASE_ID,
        ),
        "tco_invoker": build_reference_observed_tco_invoker(
            payload=TCOInput(purchase_operation=purchase), reference_case_id=CASE_ID,
        ),
        "supplier_invoker": build_reference_observed_supplier_risk_value_invoker(
            reference_case_id=CASE_ID, purchase=purchase, supplier_result=supplier,
            risk_assessments=(risk,), value_assessments=(), evidences=supplier_evidences,
        ),
        "c0_invoker": build_reference_observed_rules_engine_c0_invoker(
            bindings=(AssessmentTraceBinding(assessment=assessment, trace=trace),),
            base_result="INFORMACIÓN INSUFICIENTE", reference_case_id=CASE_ID,
        ),
        "twin_invoker": build_reference_observed_decision_twin_invoker(
            purchase=purchase, preparation=preparation, alternatives=alternatives,
            reference_case_id=CASE_ID,
        ),
        "scenario_invoker": build_reference_observed_scenario_coordination_invoker(
            purchase=purchase, preparation=preparation, inputs=scenario_inputs,
            reference_case_id=CASE_ID,
        ),
        "ni_invoker": build_reference_observed_c0_bound_ni_invoker(**negotiation),
        "ladder_invoker": build_reference_observed_c0_bound_ladder_invoker(**negotiation),
    }
    terminal = run_reference_operational_simulation(
        provenance=classify_reference_operational_simulation(
            bundle=bundle, reference_case_id=CASE_ID,
        ),
        bundle=bundle, receipt=receipt, consumption=consumption,
        purchase=purchase, context=context, policy_version=POLICY_VERSION,
        price_invoker=invokers["price_invoker"],
        tco_invoker=invokers["tco_invoker"],
        supplier_risk_value_invoker=invokers["supplier_invoker"],
        rules_invoker=invokers["c0_invoker"],
        decision_twin_invoker=invokers["twin_invoker"],
        scenario_coordination_invoker=invokers["scenario_invoker"],
        negotiation_intelligence_invoker=invokers["ni_invoker"],
        negotiation_ladder_invoker=invokers["ladder_invoker"],
    )
    payload = terminal.to_payload()
    if payload["execution_outcome"]["status"] != "PARTIALLY_COMPLETED" or \
            payload["operational_path"] != "FORBIDDEN" or \
            payload["decision_authority"] is not False or \
            payload["operational_effect"] is not False:
        raise ValueError("Case 002 lost its expected synthetic partial scope")
    sidecars = {}
    for name, (close, validate, invoker_name) in OBSERVATIONS.items():
        sidecar = close(execution=terminal, **{invoker_name: invokers[invoker_name]})
        sidecars[name] = sidecar.to_payload()
        validate(sidecars[name], payload)
    return payload, sidecars


def _json(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def _files(terminal: dict, sidecars: dict[str, dict]) -> dict[str, str]:
    return {"reference-result.json": _json(terminal), **{
        f"reference-{name}.json": _json(payload)
        for name, payload in sidecars.items()
    }}


def create_reference_business_case_002(output_dir: Path) -> tuple[Path, ...]:
    output_dir = Path(output_dir)
    if output_dir.exists():
        raise FileExistsError(f"Output already exists: {output_dir}")
    if not output_dir.parent.is_dir():
        raise ValueError(f"Output parent directory does not exist: {output_dir.parent}")
    files = _files(*execute_reference_business_case_002())
    stage = Path(tempfile.mkdtemp(prefix=".reference-002-", dir=output_dir.parent))
    try:
        for name, content in files.items():
            (stage / name).write_text(content, encoding="utf-8")
        stage.rename(output_dir)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return tuple(output_dir / name for name in files)


def verify_reference_business_case_002(directory: Path) -> str:
    directory = Path(directory)
    if not directory.is_dir():
        raise ValueError(f"Package directory does not exist: {directory}")
    expected = _files(*execute_reference_business_case_002())
    actual = {path.name for path in directory.iterdir()}
    if actual != set(expected):
        raise ValueError("Package file inventory differs from exact case 002 replay")
    for name, content in expected.items():
        if (directory / name).read_text(encoding="utf-8") != content:
            raise ValueError(f"Package differs from exact case 002 replay: {name}")
    return json.loads(expected["reference-result.json"])["terminal_fingerprint"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output-dir", type=Path)
    action.add_argument("--verify-dir", type=Path)
    args = parser.parse_args()
    if args.verify_dir is not None:
        print("Paquete 002 verificado por repetición exacta: "
              + verify_reference_business_case_002(args.verify_dir))
        return
    paths = create_reference_business_case_002(args.output_dir)
    terminal = json.loads(paths[0].read_text(encoding="utf-8"))
    print("Simulación 002: estado " + terminal["execution_outcome"]["status"]
          + "; ruta operacional FORBIDDEN; autoridad decisional false.")
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
