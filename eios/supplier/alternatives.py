"""Explicit PROV supplier-alternative carriers authorized by EIOS.

This module materializes only the contracts required by R-PROV-001 and
R-PROV-002. It does not derive supplier preference, significance, ranking,
scoring, recommendation or provider selection.
"""
from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from eios.core.models import PurchaseOperation

from .models import SupplierEvidenceResult


SupplierAlternativeSetCoverageState = Literal[
    "COMPLETE",
    "PARTIAL",
    "NOT_DETERMINABLE",
]
SupplierAlternativeOpportunityState = Literal[
    "POTENTIALLY_BETTER",
    "NOT_POTENTIALLY_BETTER",
    "NOT_DETERMINABLE",
]
SupplierAlternativeComparabilityState = Literal[
    "COMPARABLE",
    "NOT_COMPARABLE",
    "NOT_DETERMINABLE",
]
SupplierAlternativeSignificantImprovementState = Literal[
    "SIGNIFICANT_IMPROVEMENT",
    "NO_SIGNIFICANT_IMPROVEMENT",
    "NOT_DETERMINABLE",
]
SupplierAlternativeDimension = Literal[
    "PRICE",
    "PAYMENT_TERM",
    "COMMERCIAL_CONDITIONS",
    "RELIABILITY",
    "AVAILABILITY",
]

PROV_COVERAGE_EVIDENCE_SOURCE_TYPE = "SupplierAlternativeSetCoverageEvidence"
PROV_OPPORTUNITY_EVIDENCE_SOURCE_TYPE = "SupplierAlternativeOpportunityEvidence"
PROV_COMPARABILITY_EVIDENCE_SOURCE_TYPE = "SupplierAlternativeComparabilityEvidence"
PROV_SIGNIFICANT_IMPROVEMENT_EVIDENCE_SOURCE_TYPE = (
    "SupplierAlternativeSignificantImprovementEvidence"
)


class _FrozenCarrier(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


def _validate_unique_refs(values: tuple[str, ...], field: str) -> None:
    if any(not value.strip() for value in values):
        raise ValueError(f"{field} no puede contener referencias vacías")
    if len(values) != len(set(values)):
        raise ValueError(f"{field} no puede contener duplicados")


class SupplierAlternativeSetCoverage(_FrozenCarrier):
    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    article_id: str = Field(min_length=1, max_length=128)
    purchase_operation_ref: str = Field(min_length=1, max_length=256)
    supplier_evidence_ref: str = Field(min_length=1, max_length=256)
    state: SupplierAlternativeSetCoverageState
    authority_ref: str = Field(min_length=1, max_length=256)
    methodology_ref: str = Field(min_length=1, max_length=256)
    evidence_ids: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_coverage(self) -> "SupplierAlternativeSetCoverage":
        _validate_unique_refs(self.evidence_ids, "evidence_ids")
        _validate_unique_refs(self.trace_refs, "trace_refs")
        if self.state == "COMPLETE" and not self.evidence_ids:
            raise ValueError("COMPLETE requiere evidencia explícita de cobertura")
        return self


class _CandidateDetermination(_FrozenCarrier):
    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    article_id: str = Field(min_length=1, max_length=128)
    purchase_operation_ref: str = Field(min_length=1, max_length=256)
    candidate_id: str = Field(min_length=1, max_length=128)
    supplier_id: str = Field(min_length=1, max_length=128)
    supplier_evidence_ref: str = Field(min_length=1, max_length=256)
    authority_ref: str = Field(min_length=1, max_length=256)
    methodology_ref: str = Field(min_length=1, max_length=256)
    evidence_ids: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_binding_refs(self) -> "_CandidateDetermination":
        _validate_unique_refs(self.evidence_ids, "evidence_ids")
        _validate_unique_refs(self.trace_refs, "trace_refs")
        return self


class SupplierAlternativeOpportunityDetermination(_CandidateDetermination):
    state: SupplierAlternativeOpportunityState

    @model_validator(mode="after")
    def validate_state_evidence(self) -> "SupplierAlternativeOpportunityDetermination":
        if self.state != "NOT_DETERMINABLE" and not self.evidence_ids:
            raise ValueError(f"{self.state} requiere evidencia explícita")
        return self


class SupplierAlternativeComparabilityDetermination(_CandidateDetermination):
    state: SupplierAlternativeComparabilityState

    @model_validator(mode="after")
    def validate_state_evidence(self) -> "SupplierAlternativeComparabilityDetermination":
        if self.state != "NOT_DETERMINABLE" and not self.evidence_ids:
            raise ValueError(f"{self.state} requiere evidencia explícita")
        return self


class SupplierAlternativeSignificantImprovementDetermination(_CandidateDetermination):
    state: SupplierAlternativeSignificantImprovementState
    dimensions: tuple[SupplierAlternativeDimension, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_state_evidence(
        self,
    ) -> "SupplierAlternativeSignificantImprovementDetermination":
        if len(self.dimensions) != len(set(self.dimensions)):
            raise ValueError("dimensions no puede contener duplicados")
        if self.state != "NOT_DETERMINABLE" and not self.evidence_ids:
            raise ValueError(f"{self.state} requiere evidencia explícita")
        return self


def _model_ref(prefix: str, model: BaseModel) -> str:
    payload = json.dumps(
        model.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"{prefix}:{hashlib.sha256(payload).hexdigest()}"


def supplier_alternative_purchase_operation_ref(
    purchase: PurchaseOperation,
) -> str:
    if not isinstance(purchase, PurchaseOperation):
        raise TypeError("purchase debe ser PurchaseOperation")
    return _model_ref("prov_purchase", purchase)


def supplier_evidence_result_ref(result: SupplierEvidenceResult) -> str:
    if not isinstance(result, SupplierEvidenceResult):
        raise TypeError("result debe ser SupplierEvidenceResult")
    return _model_ref("supplier_evidence", result)


def supplier_alternative_coverage_ref(
    coverage: SupplierAlternativeSetCoverage,
) -> str:
    if not isinstance(coverage, SupplierAlternativeSetCoverage):
        raise TypeError("coverage debe ser SupplierAlternativeSetCoverage")
    return _model_ref("prov_coverage", coverage)


def supplier_alternative_opportunity_ref(
    determination: SupplierAlternativeOpportunityDetermination,
) -> str:
    if not isinstance(determination, SupplierAlternativeOpportunityDetermination):
        raise TypeError(
            "determination debe ser SupplierAlternativeOpportunityDetermination"
        )
    return _model_ref("prov_opportunity", determination)


def supplier_alternative_comparability_ref(
    determination: SupplierAlternativeComparabilityDetermination,
) -> str:
    if not isinstance(determination, SupplierAlternativeComparabilityDetermination):
        raise TypeError(
            "determination debe ser SupplierAlternativeComparabilityDetermination"
        )
    return _model_ref("prov_comparability", determination)


def supplier_alternative_significant_improvement_ref(
    determination: SupplierAlternativeSignificantImprovementDetermination,
) -> str:
    if not isinstance(
        determination, SupplierAlternativeSignificantImprovementDetermination
    ):
        raise TypeError(
            "determination debe ser SupplierAlternativeSignificantImprovementDetermination"
        )
    return _model_ref("prov_significant_improvement", determination)


__all__ = [
    "PROV_COMPARABILITY_EVIDENCE_SOURCE_TYPE",
    "PROV_COVERAGE_EVIDENCE_SOURCE_TYPE",
    "PROV_OPPORTUNITY_EVIDENCE_SOURCE_TYPE",
    "PROV_SIGNIFICANT_IMPROVEMENT_EVIDENCE_SOURCE_TYPE",
    "SupplierAlternativeComparabilityDetermination",
    "SupplierAlternativeComparabilityState",
    "SupplierAlternativeDimension",
    "SupplierAlternativeOpportunityDetermination",
    "SupplierAlternativeOpportunityState",
    "SupplierAlternativeSetCoverage",
    "SupplierAlternativeSetCoverageState",
    "SupplierAlternativeSignificantImprovementDetermination",
    "SupplierAlternativeSignificantImprovementState",
    "supplier_alternative_comparability_ref",
    "supplier_alternative_coverage_ref",
    "supplier_alternative_opportunity_ref",
    "supplier_alternative_purchase_operation_ref",
    "supplier_alternative_significant_improvement_ref",
    "supplier_evidence_result_ref",
]
