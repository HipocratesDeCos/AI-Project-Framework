"""Deterministic isolated QTG producer for the PROJECTION_ONLY profile."""
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Literal

from eios.quality.gate import QualityCheck, evaluate_quality

from .projection_criteria_manifest import REQUIRED_FUNCTIONS
from .projection_material_envelope import ProjectionMaterialEnvelope

ExecutionMode = Literal["SYNTHETIC_TEST", "OPERATIONAL"]
PRODUCER_ID = "QTG-PROJECTION-PRODUCER-01"
PRODUCER_VERSION = "0.1"
CATALOG_ID = "QTG-PROJECTION-CONTROL-CATALOG-01"
CATALOG_VERSION = "0.1"

_CATALOG = (
    ("PROJECTION_INITIAL_TREASURY", "INITIAL_TREASURY_SUFFICIENCY"),
    ("FLOW_INVENTORY_COMPLETENESS", "HORIZON_FLOW_INVENTORY_COMPLETENESS"),
    ("FLOW_HORIZON_CLASSIFICATION", "HORIZON_FLOW_INVENTORY_COMPLETENESS"),
    ("FLOW_AMOUNT_SUPPORT", "PARTICIPATING_FLOW_ATTRIBUTE_SUPPORT"),
    ("FLOW_CURRENCY_SUPPORT", "PARTICIPATING_FLOW_ATTRIBUTE_SUPPORT"),
    ("FLOW_DUE_DATE_SUPPORT", "PARTICIPATING_FLOW_ATTRIBUTE_SUPPORT"),
    ("FLOW_ECONOMIC_MEMBERSHIP", "PARTICIPATING_FLOW_ATTRIBUTE_SUPPORT"),
    ("FLOW_ECONOMIC_UNIQUENESS", "ECONOMIC_FLOW_UNIQUENESS"),
    ("PURCHASE_INSTALLMENT_COHERENCE", "DETERMINATE_PROJECTION_RELIABILITY"),
    ("PROJECTION_CONFLICTS_AND_LIMITATIONS", "DETERMINATE_PROJECTION_RELIABILITY"),
)


def _canonical(payload: dict) -> bytes:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8")


CATALOG_FINGERPRINT = sha256(_canonical({"catalog_id": CATALOG_ID,
    "catalog_version": CATALOG_VERSION, "families": _CATALOG})).hexdigest()


@dataclass(frozen=True, init=False)
class ProjectionQualityReceipt:
    _material: bytes

    def __init__(self):
        raise TypeError("Use produce_projection_quality")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()


def _bound_fingerprint(bound: dict) -> str:
    return sha256(_canonical(bound["payload"])).hexdigest()


def _recompute_membership(prepared: dict, treasury: dict, flow: dict) -> dict:
    treasury_review = treasury["review"]["payload"]
    flow_record = flow["record"]["payload"]
    flow_review = flow["review"]["payload"]
    treasury_seen = {item["condition"] for item in treasury_review["findings"]}
    flow_seen = {item["condition"] for item in flow_review["findings"]}
    assessed = {item["flow_id"] for item in flow_record["flow_assessments"]}
    captured = {item["flow_id"] for item in prepared["capture"][
        "finance_package"]["finance_input"]["cash_flows"]}
    candidates = {item["candidate_ref"] for item in flow_record["candidates"]}
    linked = {ref for item in flow_record["flow_assessments"] for ref in item["candidate_refs"]}
    captured_candidates = {item["candidate_ref"] for item in flow_record["candidates"]
                           if item["captured_flow_id"] is not None}
    installments = {item["installment_ref"] for item in prepared["calendar"]["installments"]}
    reviewed_installments = {item["installment_ref"]
        for finding in flow_review["findings"]
        if finding["condition"] == "PURCHASE_PAYMENT_COHERENCE"
        for item in finding["installment_findings"]}
    natures = {"payment_capture": prepared["capture"]["case_kind"],
        "required_calendar": prepared["calendar"]["case_kind"],
        "treasury_support": treasury["support"]["payload"]["case_kind"],
        "treasury_additional_material": treasury["assessment"]["payload"]["additional_case_kind"],
        "treasury_mandate": treasury["mandate"]["payload"]["mandate_kind"],
        "flow_inventory": flow_record["case_kind"],
        "flow_mandate": flow["mandate"]["payload"]["mandate_kind"]}
    return dict(treasury_pending_conditions=[condition for condition in
            treasury_review["condition_inventory"] if condition not in treasury_seen],
        flow_pending_conditions=[condition for condition in flow_review["condition_inventory"]
                                 if condition not in flow_seen],
        unassessed_captured_flow_ids=sorted(captured - assessed),
        unmatched_candidate_refs=sorted(candidates - linked - captured_candidates),
        unreviewed_required_installment_refs=sorted(installments - reviewed_installments),
        material_natures=natures,
        contains_synthetic_material=any(value == "SYNTHETIC" for value in natures.values()))


def _validate_envelope(envelope: ProjectionMaterialEnvelope) -> dict:
    if not isinstance(envelope, ProjectionMaterialEnvelope):
        raise TypeError("Expected constructed ProjectionMaterialEnvelope")
    payload = envelope.to_payload()
    if payload.get("schema_version") != "QTG-PROJECTION-MATERIAL-01/v0.1" \
            or payload.get("profile") != "PROJECTION_ONLY":
        raise ValueError("Unsupported projection material envelope")
    preparation = payload["preparation"]
    manifest = payload["criteria_manifest"]
    chains = [preparation, manifest, *payload["treasury_chain"].values(),
              *payload["flow_chain"].values()]
    if any(bound.get("fingerprint") != _bound_fingerprint(bound) for bound in chains):
        raise ValueError("Envelope contains a nonreproducible bound fingerprint")
    prepared, authorized = preparation["payload"], manifest["payload"]
    if authorized.get("schema_version") != "QTG-PROJECTION-CRITERIA-MANIFEST-01/v0.2" \
            or set(authorized.get("required_functions", ())) != set(REQUIRED_FUNCTIONS):
        raise ValueError("Envelope lacks the exact v0.2 criterion manifest")
    criteria = authorized.get("criteria", ())
    criterion_functions = [item["function"] for item in criteria]
    criterion_keys = [(item["reference"], item["version"]) for item in criteria]
    if len(criteria) != len(REQUIRED_FUNCTIONS) \
            or set(criterion_functions) != set(REQUIRED_FUNCTIONS) \
            or len(criterion_functions) != len(set(criterion_functions)) \
            or len(criterion_keys) != len(set(criterion_keys)):
        raise ValueError("Envelope criterion manifest is not exact and unique")
    presented_map = {(item["reference"], item["version"]): item["sha256"]
                     for item in prepared["presented_criteria"]}
    authorized_map = {(item["reference"], item["version"]): item["content_sha256"]
                      for item in authorized["criteria"]}
    if presented_map != authorized_map:
        raise ValueError("Envelope criterion material differs from manifest")
    treasury, flow = payload["treasury_chain"], payload["flow_chain"]
    if treasury["mandate"]["payload"].get("purpose_scope") != \
            "TREASURY_REVIEW_FOR_DOCUMENTARY_CUTOFF_PILOT" \
            or flow["mandate"]["payload"].get("purpose_scope") != \
            "FLOW_INVENTORY_REVIEW_FOR_PROJECTION_ONLY":
        raise ValueError("Envelope contains a foreign mandate purpose")
    comparisons = (
        (treasury["support"]["payload"]["preparation"], prepared),
        (treasury["assessment"]["payload"]["preparation"], prepared),
        (treasury["assessment"]["payload"]["treasury_support"], treasury["support"]["payload"]),
        (treasury["mandate"]["payload"]["target"], treasury["assessment"]["payload"]),
        (treasury["review"]["payload"]["assessment"], treasury["assessment"]["payload"]),
        (treasury["review"]["payload"]["mandate"], treasury["mandate"]["payload"]),
        (flow["record"]["payload"]["preparation"], prepared),
        (flow["mandate"]["payload"]["target"], flow["record"]["payload"]),
        (flow["review"]["payload"]["target"], flow["record"]["payload"]),
        (flow["review"]["payload"]["mandate"], flow["mandate"]["payload"]),
    )
    if any(left != right for left, right in comparisons):
        raise ValueError("Envelope chains do not belong to the same material")
    recomputed_membership = _recompute_membership(prepared, treasury, flow)
    if payload.get("recomputed_membership") != recomputed_membership:
        raise ValueError("Envelope membership summary is not reproducible")
    return payload


def _criterion(manifest: dict, function: str) -> dict:
    return next(item for item in manifest["criteria"] if item["function"] == function)


def _state(values: list[str | bool | None]) -> bool | None:
    if any(value is False or value in ("CONFLICT_REPORTED", "NOT_CONFIRMED",
            "DECLARED_INCONSISTENT", "CONFLICTING", "POSSIBLE_DUPLICATE") for value in values):
        return False
    if any(value is None or value in ("NOT_ESTABLISHED", "NOT_DETERMINED") for value in values):
        return None
    return True


def _finding(findings: list[dict], condition: str, target: str | None = None) -> dict | None:
    item = next((entry for entry in findings if entry["condition"] == condition), None)
    if item is None or target is None:
        return item
    refs = set(item.get("flow_ids", ()))
    return item if target in refs else None


def _check_entry(*, control: str, satisfied: bool | None, function: str,
    manifest: dict, reason: str, evidence_refs: tuple[str, ...] = (),
    applicable: bool = True) -> dict:
    criterion = _criterion(manifest, function)
    check = QualityCheck(control=control, satisfied=satisfied, critical=True,
        material=False, reason=reason, evidence_refs=evidence_refs, applicable=applicable)
    return {"check": asdict(check), "criterion_function": function,
        "criterion_reference": criterion["reference"],
        "criterion_version": criterion["version"],
        "criterion_sha256": criterion["content_sha256"]}


def _produce_inventory(payload: dict) -> list[dict]:
    prepared = payload["preparation"]["payload"]
    manifest = payload["criteria_manifest"]["payload"]
    treasury = {key: value["payload"] for key, value in payload["treasury_chain"].items()}
    flow = {key: value["payload"] for key, value in payload["flow_chain"].items()}
    inventory: list[dict] = []

    support_obs = {item["condition"]: item for item in treasury["support"]["observations"]}
    declarations = {item["condition"]: item for item in treasury["assessment"]["declarations"]}
    review_findings = {item["condition"]: item for item in treasury["review"]["findings"]}
    treasury_values: list[str | bool | None] = [
        treasury["mandate"]["verification_outcome"] == "ACREDITADO_POR_CONTRASTE",
        not treasury["review"]["pending_controls"], not treasury["assessment"]["pending_conditions"],
        not treasury["support"]["pending_controls"],
        *treasury["support"]["technical_comparisons"].values()]
    for condition in treasury["review"]["condition_inventory"]:
        observation, declaration, finding = (support_obs.get(condition),
            declarations.get(condition), review_findings.get(condition))
        treasury_values.extend([
            observation["outcome"] if observation else None,
            declaration["applicability"] == "APPLIES" if declaration else None,
            declaration["necessity"] == "NECESSARY_FOR_DETERMINED_PROJECTION" if declaration else None,
            declaration["support_assessment"] == "DECLARED_SUFFICIENT" if declaration else None,
            finding["outcome"] if finding else None])
    treasury_state = _state(treasury_values)
    inventory.append(_check_entry(control="PROJECTION_INITIAL_TREASURY",
        satisfied=treasury_state, function="INITIAL_TREASURY_SUFFICIENCY", manifest=manifest,
        reason="initial treasury chain satisfied" if treasury_state is True else
            "initial treasury chain is contradictory" if treasury_state is False else
            "initial treasury chain is incomplete or not evaluable",
        evidence_refs=(treasury["support"]["record_ref"], treasury["review"]["review_ref"])))

    flow_findings = flow["review"]["findings"]
    perimeter_states = [item["coverage_declaration"] for item in flow["record"]["perimeters"]]
    inventory_finding = _finding(flow_findings, "PERIMETER_COVERAGE")
    source_finding = _finding(flow_findings, "SOURCE_COVERAGE")
    captured_finding = _finding(flow_findings, "CAPTURED_FLOW_COVERAGE")
    unmatched_finding = _finding(flow_findings, "UNMATCHED_CANDIDATES")
    inventory_values: list[str | bool | None] = [
        flow["mandate"]["verification_outcome"] == "ACREDITADO_POR_CONTRASTE",
        not flow["record"]["pending_flow_ids"], not flow["record"]["unmatched_candidate_refs"],
        not flow["review"]["pending_conditions"],
        *perimeter_states,
        *(item["outcome"] if item else None for item in (
            inventory_finding, source_finding, captured_finding, unmatched_finding))]
    if any(state == "DECLARED_INCOMPLETE" for state in perimeter_states):
        inventory_values.append(False)
    if any(state == "NOT_ESTABLISHED" for state in perimeter_states):
        inventory_values.append(None)
    inventory_state = _state(inventory_values)
    inventory.append(_check_entry(control="FLOW_INVENTORY_COMPLETENESS",
        satisfied=inventory_state, function="HORIZON_FLOW_INVENTORY_COMPLETENESS",
        manifest=manifest, reason="flow inventory complete" if inventory_state is True else
        "flow inventory explicitly incomplete or conflicting" if inventory_state is False else
        "flow inventory incomplete or not evaluable",
        evidence_refs=(flow["record"]["record_ref"], flow["review"]["review_ref"])))

    assessments = {item["flow_id"]: item for item in flow["record"]["flow_assessments"]}
    cash_flows = prepared["capture"]["finance_package"]["finance_input"]["cash_flows"]
    horizon_review = _finding(flow_findings, "HORIZON_CLASSIFICATION")
    attribute_review = _finding(flow_findings, "FLOW_ATTRIBUTE_SUPPORT")
    uniqueness_review = _finding(flow_findings, "ECONOMIC_DUPLICATION")
    attribute_fields = (("FLOW_AMOUNT_SUPPORT", "amount_assessment"),
        ("FLOW_CURRENCY_SUPPORT", "currency_assessment"),
        ("FLOW_DUE_DATE_SUPPORT", "due_date_assessment"),
        ("FLOW_ECONOMIC_MEMBERSHIP", "economic_membership_assessment"))
    for captured in cash_flows:
        flow_id, assessment = captured["flow_id"], assessments.get(captured["flow_id"])
        horizon_item = _finding(flow_findings, "HORIZON_CLASSIFICATION", flow_id)
        horizon_values = [assessment["due_date_assessment"] if assessment else None,
            assessment["horizon_relevance"] if assessment else None,
            horizon_item["outcome"] if horizon_item else None]
        if assessment and assessment["horizon_relevance"] in ("WITHIN_HORIZON", "AFTER_HORIZON", "NON_FUTURE") \
                and assessment["due_date_assessment"] == "ESTABLISHED" \
                and horizon_item and horizon_item["outcome"] == "CONFIRMED_BY_REVIEW":
            horizon_state = True
        else:
            horizon_state = _state(horizon_values)
        inventory.append(_check_entry(control=f"FLOW_HORIZON_CLASSIFICATION:{flow_id}",
            satisfied=horizon_state, function="HORIZON_FLOW_INVENTORY_COMPLETENESS",
            manifest=manifest, reason="flow horizon classified" if horizon_state is True else
                "flow horizon classification contradictory" if horizon_state is False else
                "flow horizon classification not evaluable", evidence_refs=(flow_id,)))
        excluded = horizon_state is True and assessment["horizon_relevance"] == "AFTER_HORIZON"
        for family, field in attribute_fields:
            review = _finding(flow_findings, "FLOW_ATTRIBUTE_SUPPORT", flow_id)
            value = assessment[field] if assessment else None
            state = True if value == "ESTABLISHED" and review and \
                review["outcome"] == "CONFIRMED_BY_REVIEW" else _state([
                    value, review["outcome"] if review else None])
            inventory.append(_check_entry(control=f"{family}:{flow_id}", satisfied=state,
                function="PARTICIPATING_FLOW_ATTRIBUTE_SUPPORT", manifest=manifest,
                reason="flow is demonstrably after horizon" if excluded else
                    "flow attribute supported" if state is True else
                    "flow attribute contradictory" if state is False else "flow attribute not evaluable",
                evidence_refs=(flow_id,), applicable=not excluded))
        review = _finding(flow_findings, "ECONOMIC_DUPLICATION", flow_id)
        duplication = assessment["duplication_assessment"] if assessment else None
        unique_state = True if duplication == "DECLARED_UNIQUE" and review and \
            review["outcome"] == "CONFIRMED_BY_REVIEW" else _state([
                duplication, review["outcome"] if review else None])
        inventory.append(_check_entry(control=f"FLOW_ECONOMIC_UNIQUENESS:{flow_id}",
            satisfied=unique_state, function="ECONOMIC_FLOW_UNIQUENESS", manifest=manifest,
            reason="flow is demonstrably after horizon" if excluded else
                "economic uniqueness supported" if unique_state is True else
                "economic duplication conflict" if unique_state is False else
                "economic uniqueness not evaluable", evidence_refs=(flow_id,), applicable=not excluded))

    purchase = _finding(flow_findings, "PURCHASE_PAYMENT_COHERENCE")
    installment_findings = {item["installment_ref"]: item
        for item in purchase["installment_findings"]} if purchase else {}
    coverage = prepared["coverage"]
    for installment in prepared["calendar"]["installments"]:
        ref, finding = installment["installment_ref"], installment_findings.get(
            installment["installment_ref"])
        if coverage["required_calendar_matches"] and finding and \
                finding["outcome"] == "CONFIRMED_BY_REVIEW":
            state = True
        else:
            state = _state([coverage["required_calendar_matches"],
                finding["outcome"] if finding else None])
        inventory.append(_check_entry(control=f"PURCHASE_INSTALLMENT_COHERENCE:{ref}",
            satisfied=state, function="DETERMINATE_PROJECTION_RELIABILITY",
            manifest=manifest, reason="required installment coherent" if state is True else
                "required installment contradictory" if state is False else
                "required installment not evaluable", evidence_refs=(ref,)))

    conflict = _finding(flow_findings, "CONFLICTS_AND_LIMITATIONS")
    limitations = [value for item in flow["record"]["perimeters"] for value in item["limitations"]]
    explicit_conflicts = [item for item in flow_findings
        if item["outcome"] in ("CONFLICT_REPORTED", "NOT_CONFIRMED")]
    if limitations or explicit_conflicts:
        conflict_state = False
    elif conflict and conflict["outcome"] == "CONFIRMED_BY_REVIEW" \
            and not flow["review"]["pending_conditions"]:
        conflict_state = True
    else:
        conflict_state = None
    inventory.append(_check_entry(control="PROJECTION_CONFLICTS_AND_LIMITATIONS",
        satisfied=conflict_state, function="DETERMINATE_PROJECTION_RELIABILITY",
        manifest=manifest, reason="no unresolved projection conflict" if conflict_state is True else
            "projection conflict or limitation reported" if conflict_state is False else
            "projection conflicts or limitations not fully evaluated",
        evidence_refs=(flow["record"]["record_ref"], flow["review"]["review_ref"])))
    return inventory


def produce_projection_quality(*, envelope: ProjectionMaterialEnvelope,
    execution_mode: ExecutionMode) -> ProjectionQualityReceipt:
    payload = _validate_envelope(envelope)
    if execution_mode not in ("SYNTHETIC_TEST", "OPERATIONAL"):
        raise ValueError("Unsupported projection quality execution mode")
    synthetic = payload["recomputed_membership"]["contains_synthetic_material"]
    if execution_mode == "OPERATIONAL" and synthetic:
        raise ValueError("Operational projection quality rejects synthetic material")
    inventory = _produce_inventory(payload)
    controls = [entry["check"]["control"] for entry in inventory]
    if len(controls) != len(set(controls)):
        raise ValueError("Producer generated duplicate controls")
    checks = tuple(QualityCheck(**entry["check"]) for entry in inventory)
    result = evaluate_quality(checks)
    receipt_payload = dict(schema_version="QTG-PROJECTION-RECEIPT-01/v0.1",
        profile="PROJECTION_ONLY", execution_mode=execution_mode,
        operational_effect=execution_mode == "OPERATIONAL",
        producer_id=PRODUCER_ID, producer_version=PRODUCER_VERSION,
        catalog_id=CATALOG_ID, catalog_version=CATALOG_VERSION,
        catalog_fingerprint=CATALOG_FINGERPRINT,
        envelope=payload, envelope_fingerprint=envelope.fingerprint,
        control_inventory=inventory, gate_checks=[asdict(check) for check in checks],
        quality_result=asdict(result), assurance_scope=
            "SYNTHETIC_TEST_RESULT_ONLY" if execution_mode == "SYNTHETIC_TEST"
            else "OPERATIONAL_PROJECTION_INPUT_QUALITY_ONLY")
    receipt = object.__new__(ProjectionQualityReceipt)
    object.__setattr__(receipt, "_material", _canonical(receipt_payload))
    return receipt


def validate_projection_quality_receipt(*, receipt: ProjectionQualityReceipt,
    envelope: ProjectionMaterialEnvelope, execution_mode: ExecutionMode) -> None:
    if not isinstance(receipt, ProjectionQualityReceipt):
        raise TypeError("Expected constructed ProjectionQualityReceipt")
    recomputed = produce_projection_quality(envelope=envelope, execution_mode=execution_mode)
    if receipt.to_payload() != recomputed.to_payload() or receipt.fingerprint != recomputed.fingerprint:
        raise ValueError("Projection quality receipt is not reproducible from exact material")


__all__ = ["CATALOG_FINGERPRINT", "CATALOG_ID", "CATALOG_VERSION", "ExecutionMode",
    "PRODUCER_ID", "PRODUCER_VERSION", "ProjectionQualityReceipt",
    "produce_projection_quality", "validate_projection_quality_receipt"]
