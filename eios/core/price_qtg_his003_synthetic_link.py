"""Synthetic-only correspondence of QTG material and PRICE/HIS003 sources.

No QTG receipt, historical observation, or price is accepted as a detached
decision result. This module DOES NOT produce an O1 operational admission.
"""
from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict

from .models import DecisionContext, Evidence, PurchaseOperation, Rule
from .price_his003_reconciliation import (
    HistoricalReferenceSourceBundle, PriceHistoryReconciliation,
    reconcile_price_and_his003,
)
from .projection_material_envelope import ProjectionMaterialEnvelope
from .projection_quality_consumer import (
    ProjectionQualityConsumption, validate_projection_quality_consumption,
)
from .projection_quality_producer import ProjectionQualityReceipt
from eios.pricing.company_coverage import PriceCompanyCoverageProfile
from eios.pricing.models import (
    PriceIntelligenceInput, PriceIntelligenceAssessmentContext,
)


class SyntheticPriceHistoryQTGLink(BaseModel):
    """Non-operational evidence correspondence; never buying authorization."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal["PRICE-HIS003-QTG-SYNTHETIC-LINK/v0.1"] = (
        "PRICE-HIS003-QTG-SYNTHETIC-LINK/v0.1"
    )
    company_id: str
    envelope_fingerprint: str
    receipt_fingerprint: str
    consumption_fingerprint: str
    purchase_fingerprint: str
    context_fingerprint: str
    qtg_quality_status: Literal["APTO", "APTO_CON_ADVERTENCIAS", "NO_APTO"]
    qtg_quality_confidence: Literal["ALTA", "MEDIA", "BAJA"]
    price_history: PriceHistoryReconciliation
    execution_mode: Literal["SYNTHETIC_TEST"] = "SYNTHETIC_TEST"
    consumption_scope: Literal["TEST_ONLY"] = "TEST_ONLY"
    operational_path: Literal["FORBIDDEN"] = "FORBIDDEN"
    decision_authority: Literal[False] = False


def _digest(model: BaseModel) -> str:
    return hashlib.sha256(
        json.dumps(
            model.model_dump(mode="json"), sort_keys=True, ensure_ascii=False,
            separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _runtime(envelope: ProjectionMaterialEnvelope) -> tuple[
    PurchaseOperation, DecisionContext, str,
]:
    try:
        package = envelope.to_payload()["preparation"]["payload"]["capture"][
            "finance_package"
        ]["decision_input_package"]
        return (
            PurchaseOperation.model_validate(package["purchase"]),
            DecisionContext.model_validate(package["context"]),
            package["company_id"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("QTG envelope lacks a valid company-bound DIP") from exc


def link_synthetic_qtg_price_his003(
    *,
    envelope: ProjectionMaterialEnvelope,
    receipt: ProjectionQualityReceipt,
    consumption: ProjectionQualityConsumption,
    payload: PriceIntelligenceInput,
    assessment_context: PriceIntelligenceAssessmentContext,
    profile: PriceCompanyCoverageProfile,
    expected_company_id: str,
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    historical_sources: tuple[HistoricalReferenceSourceBundle, ...],
) -> SyntheticPriceHistoryQTGLink:
    """Replay both producers under one synthetic QTG-validated DIP identity.

    Important: a synthetic QTG APTO never proves PRICE/HIS003 comparability,
    nor provides decision authority; a NO_APTO remains visible as NO_APTO.
    """
    if not isinstance(envelope, ProjectionMaterialEnvelope):
        raise TypeError("Expected ProjectionMaterialEnvelope")
    if not isinstance(receipt, ProjectionQualityReceipt):
        raise TypeError("Expected ProjectionQualityReceipt")
    if not isinstance(consumption, ProjectionQualityConsumption):
        raise TypeError("Expected ProjectionQualityConsumption")
    if not isinstance(purchase, PurchaseOperation):
        raise TypeError("Expected PurchaseOperation")
    if not isinstance(context, DecisionContext):
        raise TypeError("Expected DecisionContext")

    # Existing QTG producer/consumer recompute the exact material and receipt.
    # Synthetic receipt promotion to OPERATIONAL is intentionally impossible.
    validate_projection_quality_consumption(
        consumption=consumption, receipt=receipt, envelope=envelope,
        execution_mode="SYNTHETIC_TEST", consumption_scope="TEST_ONLY",
    )
    qtg = consumption.to_payload()
    if (
        qtg.get("execution_mode") != "SYNTHETIC_TEST"
        or qtg.get("consumption_scope") != "TEST_ONLY"
        or qtg.get("operational_effect") is not False
        or qtg.get("decision_authority") is not False
    ):
        raise ValueError("QTG synthetic non-operational scope mismatch")

    expected_purchase, expected_context, company_id = _runtime(envelope)
    if not isinstance(company_id, str) or not company_id.strip():
        raise ValueError("QTG DIP company scope is missing")
    if expected_purchase != purchase:
        raise ValueError("PRICE/HIS003 purchase differs from QTG DIP purchase")
    if expected_context != context:
        raise ValueError("PRICE/HIS003 context differs from QTG DIP context")
    if company_id != expected_company_id or profile.company_id != company_id:
        raise ValueError("PRICE/HIS003 company scope differs from QTG DIP company")

    # No detached HIS003 verdict, price result or QTG status is accepted.
    history = reconcile_price_and_his003(
        payload=payload, assessment_context=assessment_context,
        profile=profile, expected_company_id=company_id,
        purchase=purchase, context=context, rule=rule,
        historical_sources=historical_sources,
    )
    quality = qtg["functional_quality_result"]
    return SyntheticPriceHistoryQTGLink(
        company_id=company_id,
        envelope_fingerprint=envelope.fingerprint,
        receipt_fingerprint=receipt.fingerprint,
        consumption_fingerprint=consumption.fingerprint,
        purchase_fingerprint=_digest(purchase),
        context_fingerprint=_digest(context),
        qtg_quality_status=quality["status"],
        qtg_quality_confidence=quality["confidence"],
        price_history=history,
    )


__all__ = ["SyntheticPriceHistoryQTGLink", "link_synthetic_qtg_price_his003"]
