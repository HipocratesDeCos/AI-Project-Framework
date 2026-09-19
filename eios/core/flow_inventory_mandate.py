"""Immutable receipt for flow-inventory mandate contrast; no quality evaluation."""
import base64
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt

from .documentary_payment_capture import DocumentaryMaterial
from .documentary_payment_review import _reference
from .finance_flow_completeness import FinanceFlowCompletenessRecord

CONDITIONS = ("PERSON_IDENTITY", "COMPANY_RELATION", "GRANTOR_AUTHORITY",
              "FLOW_INVENTORY_SCOPE", "VALIDITY_AND_KNOWN_CHANGES", "TARGET_RECORD_BINDING")
Condition = Literal["PERSON_IDENTITY", "COMPANY_RELATION", "GRANTOR_AUTHORITY",
                    "FLOW_INVENTORY_SCOPE", "VALIDITY_AND_KNOWN_CHANGES", "TARGET_RECORD_BINDING"]


class FlowMandateLocator(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    origin: Literal["MANDATE_DOCUMENT", "CHANNEL_RECOGNITION_SUPPORT", "CONTRAST_SUPPORT"]
    document_ref: str = Field(min_length=1)
    page: StrictInt = Field(gt=0)
    section: str = Field(min_length=1)


class FlowMandateObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    condition: Condition
    outcome: Literal["CONFIRMED_BY_CONTRAST", "NOT_CONFIRMED_BY_CONTRAST", "CONFLICT_REPORTED"]
    note: str = Field(min_length=1)
    locators: tuple[FlowMandateLocator, ...] = ()


@dataclass(frozen=True, init=False)
class FlowInventoryMandateVerification:
    _material: bytes

    def __init__(self): raise TypeError("Use build_flow_inventory_mandate_verification")
    def to_payload(self) -> dict: return json.loads(self._material)
    @property
    def fingerprint(self) -> str: return sha256(self._material).hexdigest()
    def document_bytes(self, origin: str, reference: str) -> bytes:
        key = {"MANDATE_DOCUMENT": "mandate_documents",
               "CHANNEL_RECOGNITION_SUPPORT": "channel_recognition_documents",
               "CONTRAST_SUPPORT": "contrast_documents"}.get(origin)
        if key:
            for item in self.to_payload()[key]:
                if item["document_ref"] == reference:
                    return base64.b64decode(item["content_base64"], validate=True)
        raise KeyError((origin, reference))


def build_flow_inventory_mandate_verification(*, target: FinanceFlowCompletenessRecord,
    verification_ref: str, company_scope: str, reviewer_ref: str, mandate_ref: str,
    target_review_ref: str, verifier_ref: str, verified_at: datetime,
    channel_ref: str, channel_kind: str,
    recognition_basis: Literal["PREVIOUSLY_RECOGNIZED", "INDEPENDENTLY_SUPPORTED"],
    mandate_kind: Literal["SYNTHETIC", "PRESENTED_OPERATIONAL"],
    mandate_documents: tuple[DocumentaryMaterial, ...],
    channel_recognition_documents: tuple[DocumentaryMaterial, ...],
    contrast_documents: tuple[DocumentaryMaterial, ...],
    observations: tuple[FlowMandateObservation, ...],
    purpose_scope: Literal["FLOW_INVENTORY_REVIEW_FOR_PROJECTION_ONLY"] =
        "FLOW_INVENTORY_REVIEW_FOR_PROJECTION_ONLY",
) -> FlowInventoryMandateVerification:
    if not isinstance(target, FinanceFlowCompletenessRecord):
        raise TypeError("Expected constructed flow-completeness target")
    for value in (verification_ref, company_scope, reviewer_ref, mandate_ref,
                  target_review_ref, verifier_ref, channel_ref, channel_kind): _reference(value)
    if not isinstance(verified_at, datetime) or verified_at.utcoffset() is None:
        raise ValueError("Aware verification time required")
    target_payload = target.to_payload()
    captured_company = target_payload["preparation"]["capture"]["finance_package"][
        "finance_input"]["snapshot"]["company_scope"]
    if company_scope != captured_company: raise ValueError("Company differs from target")
    groups = (("MANDATE_DOCUMENT", "mandate_documents", mandate_documents),
              ("CHANNEL_RECOGNITION_SUPPORT", "channel_recognition_documents", channel_recognition_documents),
              ("CONTRAST_SUPPORT", "contrast_documents", contrast_documents))
    all_refs, preserved, refs_by_origin = set(), {}, {}
    for origin, key, documents in groups:
        if type(documents) is not tuple or not documents:
            raise ValueError("Each mandate support origin requires documents")
        values, refs = [], set()
        for document in documents:
            if not isinstance(document, DocumentaryMaterial): raise TypeError("Expected documentary material")
            document = DocumentaryMaterial.model_validate(document.model_dump(mode="python"))
            _reference(document.document_ref)
            if document.document_ref in all_refs: raise ValueError("Duplicate or colliding document reference")
            all_refs.add(document.document_ref); refs.add(document.document_ref)
            values.append(dict(document_ref=document.document_ref,
                content_base64=base64.b64encode(document.content).decode("ascii"),
                sha256=sha256(document.content).hexdigest()))
        preserved[key] = values; refs_by_origin[origin] = refs
    if type(observations) is not tuple: raise TypeError("Explicit observation tuple required")
    entries, seen = [], set()
    for observation in observations:
        if not isinstance(observation, FlowMandateObservation): raise TypeError("Expected mandate observation")
        observation = FlowMandateObservation.model_validate(observation.model_dump(mode="python"))
        _reference(observation.note)
        if observation.condition in seen: raise ValueError("Duplicate condition")
        seen.add(observation.condition)
        if observation.outcome != "CONFLICT_REPORTED" and not observation.locators:
            raise ValueError("Confirmed or not-confirmed outcome requires support")
        for locator in observation.locators:
            _reference(locator.document_ref); _reference(locator.section)
            if locator.document_ref not in refs_by_origin[locator.origin]:
                raise ValueError("Locator does not belong to declared origin")
        entries.append(observation.model_dump(mode="json"))
    pending = [condition for condition in CONDITIONS if condition not in seen]
    outcomes = {item["outcome"] for item in entries}
    result = ("NO_ACREDITADO" if "NOT_CONFIRMED_BY_CONTRAST" in outcomes else
              "INCONCLUYENTE" if pending or "CONFLICT_REPORTED" in outcomes else
              "ACREDITADO_POR_CONTRASTE")
    payload = dict(schema_version="FLOW-INVENTORY-MANDATE-01/v0.1", purpose_scope=purpose_scope,
        target=target_payload, target_fingerprint=target.fingerprint, verification_ref=verification_ref,
        company_scope=company_scope, reviewer_ref=reviewer_ref, mandate_ref=mandate_ref,
        target_review_ref=target_review_ref, verifier_ref=verifier_ref,
        verified_at=verified_at.isoformat(), channel_ref=channel_ref, channel_kind=channel_kind,
        recognition_basis=recognition_basis, mandate_kind=mandate_kind, **preserved,
        observations=entries, condition_inventory=list(CONDITIONS), pending_conditions=pending,
        verification_outcome=result, assurance_scope="BOUND_PRESENTED_FLOW_MANDATE_CONTRAST_ONLY")
    record = object.__new__(FlowInventoryMandateVerification)
    object.__setattr__(record, "_material", json.dumps(payload, ensure_ascii=False,
        sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"))
    return record


def validate_flow_mandate_for_target(record: FlowInventoryMandateVerification,
    target: FinanceFlowCompletenessRecord) -> None:
    if not isinstance(record, FlowInventoryMandateVerification) or not isinstance(target, FinanceFlowCompletenessRecord):
        raise TypeError("Expected constructed mandate and target")
    payload = record.to_payload()
    if payload["target"] != target.to_payload() or payload["target_fingerprint"] != target.fingerprint:
        raise ValueError("Flow mandate belongs to different target")
