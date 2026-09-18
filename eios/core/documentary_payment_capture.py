"""Immutable capture of declared documentary associations, not a trust seal."""
from __future__ import annotations

import base64
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBytes, StrictInt

from .finance_decision_input_package import FinanceDecisionInputPackage


class DocumentaryMaterial(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    document_ref: str = Field(min_length=1)
    content: StrictBytes = Field(min_length=1)


class DocumentaryLocator(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    document_ref: str = Field(min_length=1)
    page: StrictInt = Field(gt=0)
    section: str = Field(min_length=1)


class DocumentaryPaymentBinding(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    installment_ref: str = Field(min_length=1)
    flow_id: str = Field(min_length=1)
    locators: tuple[DocumentaryLocator, ...] = Field(min_length=1)


@dataclass(frozen=True, init=False)
class DocumentaryPaymentCapture:
    _material: bytes

    def __init__(self):
        raise TypeError("Use build_documentary_payment_capture")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()

    def document_bytes(self, document_ref: str) -> bytes:
        for document in self.to_payload()["documents"]:
            if document["document_ref"] == document_ref:
                return base64.b64decode(document["content_base64"], validate=True)
        raise KeyError(document_ref)


def _identifier(value: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError("References must be nonempty without outer whitespace")


def build_documentary_payment_capture(
    *, package: FinanceDecisionInputPackage,
    documents: tuple[DocumentaryMaterial, ...],
    bindings: tuple[DocumentaryPaymentBinding, ...],
    case_kind: Literal["SYNTHETIC", "PRESENTED_OPERATIONAL"],
    operation_ref: str, order_ref: str | None = None,
    order_version: str | None = None, confirmation_ref: str | None = None,
    external_review_ref: str | None = None,
) -> DocumentaryPaymentCapture:
    """Preserve inputs without parsing documents, upgrading evidence or executing engines."""
    if not isinstance(package, FinanceDecisionInputPackage):
        raise TypeError("package must be FinanceDecisionInputPackage")
    if type(documents) is not tuple or type(bindings) is not tuple:
        raise TypeError("documents and bindings must be tuples")
    if case_kind not in {"SYNTHETIC", "PRESENTED_OPERATIONAL"}:
        raise ValueError("Explicit case nature required")
    for reference in (operation_ref, order_ref, order_version, confirmation_ref, external_review_ref):
        if reference is not None:
            _identifier(reference)
    _identifier(operation_ref)
    finance = package.finance_input  # Reconstructs/revalidates the captured model.
    base = package.decision_input_package
    purchase, context = base.purchase, base.context
    base.evidence  # Revalidate captured Evidence without elevating its state.
    payload = package.to_payload()
    if package.schema_version != "FIN-DIP-01/v0.1":
        raise ValueError("Unsupported financial capture schema")
    if payload["decision_input_package"] != base.to_payload():
        raise ValueError("Detached base capture")
    if finance.context != base.context or finance.snapshot != base.financial_snapshot:
        raise ValueError("Detached financial context/snapshot")
    if purchase.decision_id != context.decision_id or purchase.scenario_id != context.scenario_id:
        raise ValueError("Detached purchase context")
    docs = []
    document_refs = set()
    for document in documents:
        if not isinstance(document, DocumentaryMaterial):
            raise TypeError("Expected DocumentaryMaterial")
        document = DocumentaryMaterial.model_validate(document.model_dump(mode="python"))
        _identifier(document.document_ref)
        if document.document_ref in document_refs:
            raise ValueError("Duplicate document reference")
        document_refs.add(document.document_ref)
        docs.append(dict(document_ref=document.document_ref,
                         content_base64=base64.b64encode(document.content).decode("ascii"),
                         sha256=sha256(document.content).hexdigest()))
    flows = {flow.flow_id: flow for flow in finance.cash_flows}
    captured_bindings = []
    seen_flows, seen_installments = set(), set()
    for binding in bindings:
        if not isinstance(binding, DocumentaryPaymentBinding):
            raise TypeError("Expected DocumentaryPaymentBinding")
        binding = DocumentaryPaymentBinding.model_validate(binding.model_dump(mode="python"))
        _identifier(binding.flow_id)
        _identifier(binding.installment_ref)
        flow = flows.get(binding.flow_id)
        if flow is None or flow.flow_type != "PAYMENT":
            raise ValueError("Binding requires a captured PAYMENT")
        if binding.flow_id in seen_flows or binding.installment_ref in seen_installments:
            raise ValueError("Duplicate flow or declared installment")
        for locator in binding.locators:
            _identifier(locator.document_ref)
            _identifier(locator.section)
            if locator.document_ref not in document_refs:
                raise ValueError("Locator requires conserved document")
        seen_flows.add(binding.flow_id)
        seen_installments.add(binding.installment_ref)
        captured_bindings.append(binding.model_dump(mode="json"))
    capture_payload = dict(schema_version="DOC-PAY-CAP-01/v0.1", case_kind=case_kind,
        finance_package=payload, finance_package_fingerprint=package.fingerprint,
        operation_ref=operation_ref, order_ref=order_ref, order_version=order_version,
        confirmation_ref=confirmation_ref, external_review_ref=external_review_ref,
        scope="DECLARED_LISTED_INSTALLMENT_ASSOCIATIONS_ONLY", documents=docs,
        bindings=captured_bindings)
    material = json.dumps(capture_payload, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    result = object.__new__(DocumentaryPaymentCapture)
    object.__setattr__(result, "_material", material)
    return result
