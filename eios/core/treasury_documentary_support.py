"""Bind presented treasury support without certifying availability or quality."""
import base64
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .documentary_payment_capture import DocumentaryMaterial, DocumentaryLocator
from .documentary_payment_review import _reference
from .finance_quality_preparation import FinanceQualityPreparation

CONDITIONS = ("SOURCE_CORRESPONDENCE", "ECONOMIC_CUTOFF", "AMOUNT_SUPPORT",
              "AVAILABILITY", "RESTRICTIONS", "SOURCE_SUFFICIENCY")


class TreasuryDeclaration(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    documentary_company: str | None = None
    currency: str | None = None
    economic_date: date | None = None
    available_amount: Decimal | None = Field(default=None, ge=0, allow_inf_nan=False)
    locators: tuple[DocumentaryLocator, ...] = Field(min_length=1)


class TreasuryObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    condition: Literal["SOURCE_CORRESPONDENCE", "ECONOMIC_CUTOFF", "AMOUNT_SUPPORT",
                       "AVAILABILITY", "RESTRICTIONS", "SOURCE_SUFFICIENCY"]
    outcome: Literal["DECLARED_CONSISTENT", "DECLARED_INCONSISTENT", "NOT_ESTABLISHED"]
    note: str = Field(min_length=1)
    locators: tuple[DocumentaryLocator, ...] = ()


@dataclass(frozen=True, init=False)
class TreasuryDocumentarySupport:
    _material: bytes

    def __init__(self):
        raise TypeError("Use build_treasury_documentary_support")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()

    def document_bytes(self, reference: str) -> bytes:
        for document in self.to_payload()["documents"]:
            if document["document_ref"] == reference:
                return base64.b64decode(document["content_base64"], validate=True)
        raise KeyError(reference)


def build_treasury_documentary_support(
    *, preparation: FinanceQualityPreparation, record_ref: str,
    target_company_scope: str, case_kind: Literal["SYNTHETIC", "PRESENTED_OPERATIONAL"],
    documents: tuple[DocumentaryMaterial, ...], declaration: TreasuryDeclaration,
    observations: tuple[TreasuryObservation, ...] = (),
    reviewer_ref: str | None = None, reviewed_at: datetime | None = None,
) -> TreasuryDocumentarySupport:
    if not isinstance(preparation, FinanceQualityPreparation):
        raise TypeError("Expected constructed financial preparation")
    _reference(record_ref)
    _reference(target_company_scope)
    if case_kind not in ("SYNTHETIC", "PRESENTED_OPERATIONAL"):
        raise ValueError("Explicit support nature required")
    material = preparation.to_payload()
    snapshot = material["capture"]["finance_package"]["finance_input"]["snapshot"]
    if target_company_scope != snapshot["company_scope"]:
        raise ValueError("Target company differs from captured snapshot")
    if (reviewer_ref is None) != (reviewed_at is None):
        raise ValueError("Reviewer and time must be presented together")
    if reviewer_ref is not None:
        _reference(reviewer_ref)
        if not isinstance(reviewed_at, datetime) or reviewed_at.utcoffset() is None:
            raise ValueError("Aware review time required")
    if type(documents) is not tuple or not documents:
        raise ValueError("Nonempty document tuple required")
    preserved, refs = [], set()
    for document in documents:
        if not isinstance(document, DocumentaryMaterial):
            raise TypeError("Expected documentary material")
        document = DocumentaryMaterial.model_validate(document.model_dump(mode="python"))
        _reference(document.document_ref)
        if document.document_ref in refs:
            raise ValueError("Duplicate document reference")
        refs.add(document.document_ref)
        preserved.append(dict(document_ref=document.document_ref,
            content_base64=base64.b64encode(document.content).decode("ascii"),
            sha256=sha256(document.content).hexdigest()))
    if not isinstance(declaration, TreasuryDeclaration):
        raise TypeError("Expected treasury declaration")
    declaration = TreasuryDeclaration.model_validate(declaration.model_dump(mode="python"))
    for value in (declaration.documentary_company, declaration.currency):
        if value is not None:
            _reference(value)

    def validate_locators(locators):
        for locator in locators:
            _reference(locator.document_ref)
            _reference(locator.section)
            if locator.document_ref not in refs:
                raise ValueError("Locator refers to unpreserved document")

    validate_locators(declaration.locators)
    if type(observations) is not tuple:
        raise TypeError("Expected observation tuple")
    findings, seen = [], set()
    for observation in observations:
        if not isinstance(observation, TreasuryObservation):
            raise TypeError("Expected treasury observation")
        observation = TreasuryObservation.model_validate(observation.model_dump(mode="python"))
        _reference(observation.note)
        if observation.condition in seen:
            raise ValueError("Duplicate condition")
        seen.add(observation.condition)
        if observation.outcome == "DECLARED_CONSISTENT" and not observation.locators:
            raise ValueError("Consistent declaration requires support locators")
        validate_locators(observation.locators)
        findings.append(observation.model_dump(mode="json"))
    expected_amount = snapshot["available_treasury"]
    comparisons = dict(
        amount_matches=(declaration.available_amount == Decimal(str(expected_amount)))
            if declaration.available_amount is not None and expected_amount is not None else None,
        currency_matches=declaration.currency == snapshot["currency"] if declaration.currency is not None else None,
        economic_date_matches=declaration.economic_date.isoformat() == snapshot["as_of_date"]
            if declaration.economic_date is not None else None)
    payload = dict(schema_version="FIN-TREASURY-SUPPORT-01/v0.1",
        preparation=material, preparation_fingerprint=preparation.fingerprint,
        record_ref=record_ref, target_company_scope=target_company_scope, case_kind=case_kind,
        documents=preserved, declaration=declaration.model_dump(mode="json"),
        observations=findings, condition_inventory=list(CONDITIONS),
        pending_controls=[condition for condition in CONDITIONS if condition not in seen],
        technical_comparisons=comparisons, reviewer_ref=reviewer_ref,
        reviewed_at=reviewed_at.isoformat() if reviewed_at else None,
        assurance_scope="BOUND_PRESENTED_DECLARATIONS_ONLY")
    result = object.__new__(TreasuryDocumentarySupport)
    object.__setattr__(result, "_material", json.dumps(payload, ensure_ascii=False,
        sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"))
    return result


def validate_treasury_support_for_preparation(
    support: TreasuryDocumentarySupport, preparation: FinanceQualityPreparation,
) -> None:
    if not isinstance(support, TreasuryDocumentarySupport) or not isinstance(preparation, FinanceQualityPreparation):
        raise TypeError("Expected constructed support and preparation")
    payload = support.to_payload()
    if payload["preparation"] != preparation.to_payload() or payload["preparation_fingerprint"] != preparation.fingerprint:
        raise ValueError("Treasury support belongs to different preparation")
