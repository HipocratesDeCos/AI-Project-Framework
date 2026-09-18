"""Compare captured associations with an explicitly declared required calendar."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt

from .documentary_payment_capture import DocumentaryLocator, DocumentaryPaymentCapture
from .documentary_payment_review import _reference


class RequiredInstallment(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    installment_ref: str = Field(min_length=1)
    sequence: StrictInt = Field(gt=0)
    amount: Decimal = Field(gt=0, allow_inf_nan=False)
    currency: str = Field(min_length=1)
    due_date: date
    locators: tuple[DocumentaryLocator, ...] = Field(min_length=1)


class RequiredInstallmentCalendar(BaseModel):
    """Caller-supplied requirement, not a discovered or authenticated calendar."""
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    declaration_ref: str = Field(min_length=1)
    authority_ref: str = Field(min_length=1)
    case_kind: Literal["SYNTHETIC", "PRESENTED_OPERATIONAL"]
    operation_ref: str = Field(min_length=1)
    order_ref: str = Field(min_length=1)
    order_version: str = Field(min_length=1)
    confirmation_ref: str = Field(min_length=1)
    total_due: Decimal = Field(gt=0, allow_inf_nan=False)
    currency: str = Field(min_length=1)
    installments: tuple[RequiredInstallment, ...] = Field(min_length=1)


@dataclass(frozen=True, init=False)
class RequiredInstallmentCoverage:
    _material: bytes

    def __init__(self):
        raise TypeError("Use check_required_installment_coverage")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()


def check_required_installment_coverage(
    *, capture: DocumentaryPaymentCapture, calendar: RequiredInstallmentCalendar,
) -> RequiredInstallmentCoverage:
    """Observe structural matches only; do not run Finance, review content or QTG."""
    if not isinstance(capture, DocumentaryPaymentCapture) or not isinstance(calendar, RequiredInstallmentCalendar):
        raise TypeError("Expected constructed capture and declared calendar")
    calendar = RequiredInstallmentCalendar.model_validate(calendar.model_dump(mode="python"))
    for key in ("declaration_ref", "authority_ref", "operation_ref", "order_ref", "order_version", "confirmation_ref", "currency"):
        _reference(getattr(calendar, key))
    identities, sequences = set(), set()
    for installment in calendar.installments:
        _reference(installment.installment_ref)
        _reference(installment.currency)
        if installment.installment_ref in identities or installment.sequence in sequences:
            raise ValueError("Duplicate required installment identity or sequence")
        if installment.currency != calendar.currency:
            raise ValueError("Required calendar must use its declared currency without FX")
        identities.add(installment.installment_ref)
        sequences.add(installment.sequence)
        for locator in installment.locators:
            _reference(locator.document_ref)
            _reference(locator.section)
    ordered = sorted(calendar.installments, key=lambda i: i.sequence)
    if any(a.due_date >= b.due_date for a, b in zip(ordered, ordered[1:])):
        raise ValueError("Declared sequence requires strictly increasing due dates")
    if sum((i.amount for i in ordered), Decimal(0)) != calendar.total_due:
        raise ValueError("Declared total differs from required installment sum")
    source = capture.to_payload()
    if source["schema_version"] != "DOC-PAY-CAP-01/v0.1":
        raise ValueError("Unsupported capture schema")
    reference_mismatches = [key for key in ("operation_ref", "order_ref", "order_version", "confirmation_ref")
                            if source[key] != getattr(calendar, key)]
    bindings = {b["installment_ref"]: b for b in source["bindings"]}
    flows = {f["flow_id"]: f for f in source["finance_package"]["finance_input"]["cash_flows"]}
    observations = []
    for installment in ordered:
        binding = bindings.get(installment.installment_ref)
        issues = []
        flow = flows.get(binding["flow_id"]) if binding else None
        if binding is None:
            issues.append("MISSING_ASSOCIATION")
        elif flow is None or flow["flow_type"] != "PAYMENT":
            issues.append("MISSING_PAYMENT_FLOW")
        else:
            if flow["amount"] is None or Decimal(flow["amount"]) != installment.amount:
                issues.append("AMOUNT_MISMATCH")
            if flow["currency"] != installment.currency:
                issues.append("CURRENCY_MISMATCH")
            if flow["due_date"] != installment.due_date.isoformat():
                issues.append("DUE_DATE_MISMATCH")
            if any(locator.model_dump(mode="json") not in binding["locators"] for locator in installment.locators):
                issues.append("REQUIRED_SUPPORT_NOT_ASSOCIATED")
        observations.append(dict(installment_ref=installment.installment_ref,
            flow_id=binding["flow_id"] if binding else None, issues=issues,
            observed_evidence_state=flow["evidence_state"] if flow else None,
            observed_due_date_evidenced=flow["due_date_evidenced"] if flow else None))
    unexpected = sorted(set(bindings) - identities)
    bound_ids = {b["flow_id"] for b in bindings.values()}
    unassociated = sorted(f["flow_id"] for f in flows.values()
                          if f["flow_type"] == "PAYMENT" and f["flow_id"] not in bound_ids)
    payload = dict(schema_version="DOC-PAY-COVER-01/v0.1", capture=source,
        capture_fingerprint=capture.fingerprint, calendar=calendar.model_dump(mode="json"),
        reference_mismatches=reference_mismatches, observations=observations,
        unexpected_installment_refs=unexpected, unassociated_payment_flow_ids=unassociated,
        required_calendar_matches=not reference_mismatches and not unexpected and not any(o["issues"] for o in observations),
        assurance_scope="DECLARED_CALENDAR_STRUCTURAL_MATCH_ONLY")
    result = object.__new__(RequiredInstallmentCoverage)
    object.__setattr__(result, "_material", json.dumps(payload, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8"))
    return result


def validate_coverage_for_material(
    coverage: RequiredInstallmentCoverage, capture: DocumentaryPaymentCapture,
    calendar: RequiredInstallmentCalendar,
) -> None:
    if not isinstance(coverage, RequiredInstallmentCoverage) or not isinstance(capture, DocumentaryPaymentCapture) or not isinstance(calendar, RequiredInstallmentCalendar):
        raise TypeError("Expected coverage, capture and calendar")
    calendar = RequiredInstallmentCalendar.model_validate(calendar.model_dump(mode="python"))
    payload = coverage.to_payload()
    if payload["capture"] != capture.to_payload() or payload["capture_fingerprint"] != capture.fingerprint or payload["calendar"] != calendar.model_dump(mode="json"):
        raise ValueError("Coverage belongs to different examined material")
