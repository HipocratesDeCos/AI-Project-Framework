"""Immutable receipt for presented manual mandate-verification observations."""
import base64
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt

from .documentary_payment_capture import DocumentaryMaterial
from .documentary_payment_review import _reference
from .treasury_contextual_assessment import TreasuryContextualAssessment

CONDITIONS = ("PERSON_IDENTITY", "COMPANY_RELATION", "GRANTOR_AUTHORITY",
              "TREASURY_SCOPE", "VALIDITY_AND_KNOWN_CHANGES", "TARGET_CONTEXT_BINDING")


class MandateVerificationLocator(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    origin: Literal["MANDATE_DOCUMENT", "CHANNEL_RECOGNITION_SUPPORT", "CONTRAST_SUPPORT"]
    document_ref: str = Field(min_length=1)
    page: StrictInt = Field(gt=0)
    section: str = Field(min_length=1)


class MandateVerificationObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    condition: Literal["PERSON_IDENTITY", "COMPANY_RELATION", "GRANTOR_AUTHORITY",
                       "TREASURY_SCOPE", "VALIDITY_AND_KNOWN_CHANGES", "TARGET_CONTEXT_BINDING"]
    outcome: Literal["CONFIRMED_BY_CONTRAST", "NOT_CONFIRMED_BY_CONTRAST", "CONFLICT_REPORTED"]
    note: str = Field(min_length=1)
    locators: tuple[MandateVerificationLocator, ...] = ()


@dataclass(frozen=True, init=False)
class TreasuryMandateVerification:
    _material: bytes

    def __init__(self):
        raise TypeError("Use build_treasury_mandate_verification")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()

    def document_bytes(self, origin: str, reference: str) -> bytes:
        key = {"MANDATE_DOCUMENT": "mandate_documents",
               "CHANNEL_RECOGNITION_SUPPORT": "channel_recognition_documents",
               "CONTRAST_SUPPORT": "contrast_documents"}.get(origin)
        if key:
            for document in self.to_payload()[key]:
                if document["document_ref"] == reference:
                    return base64.b64decode(document["content_base64"], validate=True)
        raise KeyError((origin, reference))


def build_treasury_mandate_verification(*, target: TreasuryContextualAssessment,
    verification_ref: str, company_scope: str, reviewer_ref: str, mandate_ref: str,
    target_review_ref: str, verifier_ref: str, verified_at: datetime,
    channel_ref: str, channel_kind: str,
    recognition_basis: Literal["PREVIOUSLY_RECOGNIZED", "INDEPENDENTLY_SUPPORTED"],
    mandate_kind: Literal["SYNTHETIC", "PRESENTED_OPERATIONAL"],
    mandate_documents: tuple[DocumentaryMaterial, ...],
    channel_recognition_documents: tuple[DocumentaryMaterial, ...],
    contrast_documents: tuple[DocumentaryMaterial, ...],
    observations: tuple[MandateVerificationObservation, ...],
    purpose_scope: Literal["TREASURY_REVIEW_FOR_DOCUMENTARY_CUTOFF_PILOT"] = "TREASURY_REVIEW_FOR_DOCUMENTARY_CUTOFF_PILOT",
) -> TreasuryMandateVerification:
    if not isinstance(target, TreasuryContextualAssessment):
        raise TypeError("Expected constructed contextual target")
    for value in (verification_ref, company_scope, reviewer_ref, mandate_ref, target_review_ref,
                  verifier_ref, channel_ref, channel_kind):
        _reference(value)
    if not isinstance(verified_at, datetime) or verified_at.utcoffset() is None:
        raise ValueError("Aware verification time required")
    target_payload = target.to_payload()
    captured_company = target_payload["preparation"]["capture"]["finance_package"]["finance_input"]["snapshot"]["company_scope"]
    if company_scope != captured_company:
        raise ValueError("Company differs from contextual target")
    groups = (("MANDATE_DOCUMENT", "mandate_documents", mandate_documents),
              ("CHANNEL_RECOGNITION_SUPPORT", "channel_recognition_documents", channel_recognition_documents),
              ("CONTRAST_SUPPORT", "contrast_documents", contrast_documents))
    all_refs, preserved = set(), {}
    for origin, key, documents in groups:
        if type(documents) is not tuple or not documents:
            raise ValueError("Each verification support origin requires documents")
        values = []
        for document in documents:
            if not isinstance(document, DocumentaryMaterial):
                raise TypeError("Expected documentary material")
            document = DocumentaryMaterial.model_validate(document.model_dump(mode="python"))
            _reference(document.document_ref)
            if document.document_ref in all_refs:
                raise ValueError("Duplicate or colliding document reference")
            all_refs.add(document.document_ref)
            values.append(dict(document_ref=document.document_ref,
                content_base64=base64.b64encode(document.content).decode("ascii"),
                sha256=sha256(document.content).hexdigest()))
        preserved[key] = values
    refs_by_origin = {origin: {d.document_ref for d in documents} for origin, _, documents in groups}
    if type(observations) is not tuple:
        raise TypeError("Explicit observation tuple required")
    entries, seen = [], set()
    for observation in observations:
        if not isinstance(observation, MandateVerificationObservation):
            raise TypeError("Expected mandate verification observation")
        observation = MandateVerificationObservation.model_validate(observation.model_dump(mode="python"))
        _reference(observation.note)
        if observation.condition in seen:
            raise ValueError("Duplicate condition")
        seen.add(observation.condition)
        if observation.outcome != "CONFLICT_REPORTED" and not observation.locators:
            raise ValueError("Confirmed or not-confirmed outcome requires support")
        for locator in observation.locators:
            _reference(locator.document_ref); _reference(locator.section)
            if locator.document_ref not in refs_by_origin[locator.origin]:
                raise ValueError("Locator does not belong to declared origin")
        entries.append(observation.model_dump(mode="json"))
    pending = [condition for condition in CONDITIONS if condition not in seen]
    outcomes = {entry["outcome"] for entry in entries}
    if "NOT_CONFIRMED_BY_CONTRAST" in outcomes:
        result = "NO_ACREDITADO"
    elif pending or "CONFLICT_REPORTED" in outcomes:
        result = "INCONCLUYENTE"
    else:
        result = "ACREDITADO_POR_CONTRASTE"
    payload = dict(schema_version="TREASURY-MANDATE-RECORD-01/v0.1",
        purpose_scope=purpose_scope, target=target_payload, target_fingerprint=target.fingerprint,
        verification_ref=verification_ref, company_scope=company_scope, reviewer_ref=reviewer_ref,
        mandate_ref=mandate_ref, target_review_ref=target_review_ref, verifier_ref=verifier_ref,
        verified_at=verified_at.isoformat(), channel_ref=channel_ref, channel_kind=channel_kind,
        recognition_basis=recognition_basis, mandate_kind=mandate_kind, **preserved,
        observations=entries, condition_inventory=list(CONDITIONS), pending_conditions=pending,
        verification_outcome=result, assurance_scope="BOUND_PRESENTED_MANUAL_CONTRAST_ONLY")
    record = object.__new__(TreasuryMandateVerification)
    object.__setattr__(record, "_material", json.dumps(payload, ensure_ascii=False,
        sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"))
    return record


def validate_mandate_verification_for_target(record: TreasuryMandateVerification,
    target: TreasuryContextualAssessment) -> None:
    if not isinstance(record, TreasuryMandateVerification) or not isinstance(target, TreasuryContextualAssessment):
        raise TypeError("Expected constructed verification and contextual target")
    payload = record.to_payload()
    if payload["target"] != target.to_payload() or payload["target_fingerprint"] != target.fingerprint:
        raise ValueError("Mandate verification belongs to different target")
