"""Recompute PRICE and HIS003 from one frozen, traceable historical source set.

This is a technical source-membership reconciliation. It does not turn HIS003
into a PRICE authority, QTG into a price gate, or any result into authorization
to buy. Each domain is evaluated using its own producer/contract.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from eios.core.models import (
    Assessment, DecisionContext, Evidence, PurchaseOperation, Rule,
)
from eios.pricing.company_coverage import (
    PriceCompanyCoverageProfile, run_price_intelligence_for_company,
)
from eios.pricing.historical_comparability import (
    HistoricalComparabilityDimensionDetermination,
    historical_comparability_reference_ref,
)
from eios.pricing.models import (
    PriceIntelligenceAssessmentContext, PriceIntelligenceInput,
    PriceIntelligenceResult,
)
from eios.rules.history_comparability import R_HIS_003, evaluate_r_his_003


class HistoricalReferenceSourceBundle(BaseModel):
    """Raw HIS003 sources, never a detached precomputed assessment."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    reference_id: str = Field(min_length=1, max_length=128)
    dimension_determinations: tuple[HistoricalComparabilityDimensionDetermination, ...]
    dimension_evidences: tuple[Evidence, ...]


class RecomputedHistoricalReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    transaction_id: str
    reference_fingerprint: str
    assessment: Assessment
    evidence_ids: tuple[str, ...]
    trace_refs: tuple[str, ...]


class PriceHistoryReconciliation(BaseModel):
    """Technical coexistence, not a global quality or purchasing verdict."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    scope: Literal["PRICE_HIS003_SOURCE_MEMBERSHIP_ONLY"] = (
        "PRICE_HIS003_SOURCE_MEMBERSHIP_ONLY"
    )
    price_result: PriceIntelligenceResult
    historical_references: tuple[RecomputedHistoricalReference, ...]
    qtg_status: Literal["NOT_ASSESSED"] = "NOT_ASSESSED"
    decision_authority: Literal[False] = False


def reconcile_price_and_his003(
    *,
    payload: PriceIntelligenceInput,
    assessment_context: PriceIntelligenceAssessmentContext,
    profile: PriceCompanyCoverageProfile,
    expected_company_id: str,
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    historical_sources: tuple[HistoricalReferenceSourceBundle, ...],
) -> PriceHistoryReconciliation:
    """Enforce exact common runtime, then independently reexecute both domains.

    The strict company PRICE admission is mandatory. HIS003 may report a
    material commercial difference, or be NOT_EVALUABLE; neither outcome is
    silently reinterpreted as an economic PRICE conversion or a QTG status.
    """
    if not isinstance(payload, PriceIntelligenceInput):
        raise TypeError("Expected PriceIntelligenceInput")
    if not isinstance(assessment_context, PriceIntelligenceAssessmentContext):
        raise TypeError("Expected PriceIntelligenceAssessmentContext")
    if not isinstance(profile, PriceCompanyCoverageProfile):
        raise TypeError("Expected PriceCompanyCoverageProfile")
    if not isinstance(purchase, PurchaseOperation):
        raise TypeError("Expected PurchaseOperation")
    if not isinstance(context, DecisionContext):
        raise TypeError("Expected DecisionContext")
    if not isinstance(rule, Rule):
        raise TypeError("Expected Rule")

    if payload.purchase_operation != purchase:
        raise ValueError("PRICE purchase does not match HIS003 runtime purchase")
    if payload.decision_context != context:
        raise ValueError("PRICE DecisionContext does not match HIS003 runtime")
    if rule.rule_id != R_HIS_003 or rule.version != context.rules_version or not rule.requires_evidence:
        raise ValueError("HIS003 rule identity/version/evidence requirement mismatch")

    reference_by_id = {
        ref.source_transaction_id: ref for ref in payload.references
    }
    if len(reference_by_id) != len(payload.references):
        raise ValueError("HIS003 reconciliation requires unique PRICE reference IDs")

    source_by_id: dict[str, HistoricalReferenceSourceBundle] = {}
    for source in historical_sources:
        if not isinstance(source, HistoricalReferenceSourceBundle):
            raise TypeError("Expected HistoricalReferenceSourceBundle")
        if source.reference_id in source_by_id:
            raise ValueError("Duplicate HIS003 source reference: " + source.reference_id)
        source_by_id[source.reference_id] = source
    if set(source_by_id) != set(reference_by_id):
        raise ValueError("PRICE/HIS003 historical reference set mismatch")

    histories: list[RecomputedHistoricalReference] = []
    for reference_id, reference in reference_by_id.items():
        if reference.article_identity != purchase.article_id:
            raise ValueError("HIS003 reference article differs from PRICE purchase")
        source = source_by_id[reference_id]
        assessment = evaluate_r_his_003(
            purchase=purchase.model_copy(deep=True),
            context=context.model_copy(deep=True),
            rule=rule.model_copy(deep=True),
            reference=reference.model_copy(deep=True),
            dimension_determinations=tuple(
                item.model_copy(deep=True) for item in source.dimension_determinations
            ),
            dimension_evidences=tuple(
                item.model_copy(deep=True) for item in source.dimension_evidences
            ),
        )
        histories.append(RecomputedHistoricalReference(
            transaction_id=reference_id,
            reference_fingerprint=historical_comparability_reference_ref(reference),
            assessment=assessment,
            evidence_ids=tuple(assessment.evidence_ids),
            trace_refs=tuple(dict.fromkeys(
                trace
                for item in source.dimension_determinations
                for trace in item.trace_refs
            )),
        ))

    # Complete HIS003 source validation before computing PRICE. An invalid
    # or forged history cannot trigger an otherwise valid price calculation.
    price_result = run_price_intelligence_for_company(
        payload.model_copy(deep=True),
        assessment_context.model_copy(deep=True),
        profile.model_copy(deep=True),
        expected_company_id=expected_company_id,
    )

    return PriceHistoryReconciliation(
        price_result=price_result,
        historical_references=tuple(histories),
    )


__all__ = [
    "HistoricalReferenceSourceBundle",
    "PriceHistoryReconciliation",
    "RecomputedHistoricalReference",
    "reconcile_price_and_his003",
]
