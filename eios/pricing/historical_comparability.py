"""HIS003 commercial-comparability carrier and deterministic aggregator."""
from __future__ import annotations

import hashlib
import json
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.core.validation import validate_evidence
from eios.pricing.historical_reference import historical_reference_purchase_ref
from eios.pricing.models import PriceReference


HistoricalComparabilityDimension = Literal[
    "QUANTITY",
    "SUPPLIER",
    "COMMERCIAL_CONDITIONS",
    "DISCOUNTS",
    "RAPPELS",
    "PAYMENT_TERM",
    "ARTICLE_CHARACTERISTICS",
]
HistoricalComparabilityDimensionState = Literal[
    "EQUIVALENT",
    "MATERIALLY_DIFFERENT",
    "NOT_DETERMINABLE",
    "NOT_APPLICABLE",
]
HistoricalCommercialComparabilityState = Literal[
    "COMPARABLE",
    "NON_COMPARABLE",
    "NOT_DETERMINABLE",
]

HIS003_DIMENSION_EVIDENCE_SOURCE_TYPE = (
    "HistoricalCommercialComparabilityDimensionEvidence"
)
HIS003_AUTHORITY_REF = (
    "01_Modelo/HIS003_Commercial_Comparability_Authority_v0.1.md"
)
HIS003_METHODOLOGY_REF = (
    "08_Implementacion/R_HIS_003_Provenance_Safe_Core_Technical_Contract_v0.1.md"
)
HIS003_REQUIRED_DIMENSIONS = (
    "QUANTITY",
    "SUPPLIER",
    "COMMERCIAL_CONDITIONS",
    "DISCOUNTS",
    "RAPPELS",
    "PAYMENT_TERM",
    "ARTICLE_CHARACTERISTICS",
)


class HistoricalComparabilityDimensionAuthority(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    dimension: HistoricalComparabilityDimension
    authority_ref: str = Field(min_length=1, max_length=256)
    methodology_ref: str = Field(min_length=1, max_length=256)
    version: str = Field(min_length=1, max_length=64)


class HistoricalComparabilityDimensionDetermination(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    dimension: HistoricalComparabilityDimension
    state: HistoricalComparabilityDimensionState
    authority: HistoricalComparabilityDimensionAuthority
    evidence_ids: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = Field(min_length=1)
    reason: str | None = Field(default=None, min_length=1, max_length=256)

    @model_validator(mode="after")
    def validate_payload(self) -> "HistoricalComparabilityDimensionDetermination":
        if self.authority.dimension != self.dimension:
            raise ValueError("authority.dimension debe coincidir con dimension")
        if len(self.evidence_ids) != len(set(self.evidence_ids)):
            raise ValueError("evidence_ids no puede contener duplicados")
        if len(self.trace_refs) != len(set(self.trace_refs)):
            raise ValueError("trace_refs no puede contener duplicados")
        if any(not item.strip() for item in self.evidence_ids + self.trace_refs):
            raise ValueError("evidence_ids/trace_refs no pueden contener valores vacíos")

        if self.state in {
            "EQUIVALENT",
            "MATERIALLY_DIFFERENT",
            "NOT_APPLICABLE",
        } and not self.evidence_ids:
            raise ValueError(
                f"{self.state} requiere evidencia explícita de la dimensión"
            )
        if self.state == "NOT_DETERMINABLE" and self.reason is None:
            raise ValueError("NOT_DETERMINABLE requiere reason explícito")
        return self


class HistoricalCommercialComparabilityObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    article_id: str = Field(min_length=1, max_length=128)
    purchase_operation_ref: str = Field(min_length=1, max_length=128)
    reference_id: str = Field(min_length=1, max_length=128)
    reference_transaction_id: str = Field(min_length=1, max_length=128)
    evaluation_date: date
    reference_date: date
    state: HistoricalCommercialComparabilityState
    dimension_assessments: tuple[HistoricalComparabilityDimensionDetermination, ...]
    authority_ref: str = Field(min_length=1, max_length=256)
    methodology_ref: str = Field(min_length=1, max_length=256)
    evidence_ids: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_dimensions_and_state(self) -> "HistoricalCommercialComparabilityObservation":
        dimensions = tuple(item.dimension for item in self.dimension_assessments)
        if len(dimensions) != len(set(dimensions)):
            raise ValueError("dimension_assessments contiene dimensiones duplicadas")
        if set(dimensions) != set(HIS003_REQUIRED_DIMENSIONS):
            raise ValueError("HIS003 requiere exactamente las siete dimensiones autorizadas")
        if self.reference_date > self.evaluation_date:
            raise ValueError("reference_date no puede ser futura respecto a evaluation_date")
        expected = aggregate_historical_comparability(self.dimension_assessments)
        if self.state != expected:
            raise ValueError("state no coincide con la agregación HIS003 autorizada")
        if len(self.evidence_ids) != len(set(self.evidence_ids)):
            raise ValueError("evidence_ids agregados no pueden contener duplicados")
        if len(self.trace_refs) != len(set(self.trace_refs)):
            raise ValueError("trace_refs agregados no pueden contener duplicados")
        return self


def historical_comparability_dimension_ref(
    determination: HistoricalComparabilityDimensionDetermination,
) -> str:
    if not isinstance(determination, HistoricalComparabilityDimensionDetermination):
        raise TypeError(
            "determination debe ser HistoricalComparabilityDimensionDetermination"
        )
    payload = json.dumps(
        determination.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"his003_dimension:{hashlib.sha256(payload).hexdigest()}"


def historical_comparability_reference_ref(reference: PriceReference) -> str:
    if not isinstance(reference, PriceReference):
        raise TypeError("reference debe ser PriceReference")
    payload = json.dumps(
        reference.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"his003_reference:{hashlib.sha256(payload).hexdigest()}"


def aggregate_historical_comparability(
    determinations: tuple[HistoricalComparabilityDimensionDetermination, ...],
) -> HistoricalCommercialComparabilityState:
    dimensions = tuple(item.dimension for item in determinations)
    if len(dimensions) != len(set(dimensions)):
        raise ValueError("determinaciones HIS003 duplicadas")
    if set(dimensions) != set(HIS003_REQUIRED_DIMENSIONS):
        raise ValueError("HIS003 requiere exactamente las siete dimensiones")

    if any(item.state == "MATERIALLY_DIFFERENT" for item in determinations):
        return "NON_COMPARABLE"
    if all(item.state in {"EQUIVALENT", "NOT_APPLICABLE"} for item in determinations):
        return "COMPARABLE"
    return "NOT_DETERMINABLE"


def _validate_dimension_evidence(
    *,
    determination: HistoricalComparabilityDimensionDetermination,
    evidence_by_id: dict[str, Evidence],
    evaluation_date: date,
) -> None:
    expected_ref = historical_comparability_dimension_ref(determination)
    for evidence_id in determination.evidence_ids:
        evidence = evidence_by_id.get(evidence_id)
        if evidence is None:
            raise ValueError(
                f"HIS003 evidence_id desconocido para {determination.dimension}: {evidence_id}"
            )
        if evidence.source_type != HIS003_DIMENSION_EVIDENCE_SOURCE_TYPE:
            raise ValueError("HIS003 dimension evidence source_type incompatible")
        if evidence.captured_at != evaluation_date:
            raise ValueError("HIS003 dimension evidence usa otra evaluation_date")
        if evidence.state == "DEMONSTRATED":
            if evidence.demonstration_ref != expected_ref:
                raise ValueError(
                    "HIS003 dimension evidence no está vinculada a la determinación exacta"
                )
        elif determination.state != "NOT_DETERMINABLE":
            raise ValueError(
                "Una dimensión HIS003 determinada requiere evidencia DEMONSTRATED"
            )

    if determination.state in {
        "EQUIVALENT",
        "MATERIALLY_DIFFERENT",
        "NOT_APPLICABLE",
    }:
        if any(
            validate_evidence(evidence_by_id[evidence_id]).status != "VALID"
            for evidence_id in determination.evidence_ids
        ):
            raise ValueError(
                "Una dimensión HIS003 determinada requiere evidencia válida"
            )


def build_historical_commercial_comparability_observation(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    reference: PriceReference,
    dimension_determinations: tuple[
        HistoricalComparabilityDimensionDetermination, ...
    ],
    dimension_evidences: tuple[Evidence, ...],
) -> HistoricalCommercialComparabilityObservation:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    if reference.operation_date > purchase.operation_date:
        raise ValueError("La referencia histórica no puede ser futura")

    evidence_ids = tuple(item.evidence_id for item in dimension_evidences)
    if len(evidence_ids) != len(set(evidence_ids)):
        raise ValueError("dimension_evidences contiene evidence_id duplicados")
    evidence_by_id = {item.evidence_id: item for item in dimension_evidences}

    for determination in dimension_determinations:
        _validate_dimension_evidence(
            determination=determination,
            evidence_by_id=evidence_by_id,
            evaluation_date=purchase.operation_date,
        )

    state = aggregate_historical_comparability(dimension_determinations)
    used_evidence_ids = tuple(
        dict.fromkeys(
            evidence_id
            for determination in dimension_determinations
            for evidence_id in determination.evidence_ids
        )
    )
    trace_refs = tuple(
        dict.fromkeys(
            trace_ref
            for determination in dimension_determinations
            for trace_ref in determination.trace_refs
        )
    )

    return HistoricalCommercialComparabilityObservation(
        decision_id=context.decision_id,
        scenario_id=context.scenario_id,
        data_snapshot_id=context.data_snapshot_id,
        parameters_version=context.parameters_version,
        article_id=purchase.article_id,
        purchase_operation_ref=historical_reference_purchase_ref(purchase),
        reference_id=historical_comparability_reference_ref(reference),
        reference_transaction_id=reference.source_transaction_id,
        evaluation_date=purchase.operation_date,
        reference_date=reference.operation_date,
        state=state,
        dimension_assessments=dimension_determinations,
        authority_ref=HIS003_AUTHORITY_REF,
        methodology_ref=HIS003_METHODOLOGY_REF,
        evidence_ids=used_evidence_ids,
        trace_refs=trace_refs,
    )


__all__ = [
    "HIS003_AUTHORITY_REF",
    "HIS003_DIMENSION_EVIDENCE_SOURCE_TYPE",
    "HIS003_METHODOLOGY_REF",
    "HIS003_REQUIRED_DIMENSIONS",
    "HistoricalCommercialComparabilityObservation",
    "HistoricalCommercialComparabilityState",
    "HistoricalComparabilityDimension",
    "HistoricalComparabilityDimensionAuthority",
    "HistoricalComparabilityDimensionDetermination",
    "HistoricalComparabilityDimensionState",
    "aggregate_historical_comparability",
    "build_historical_commercial_comparability_observation",
    "historical_comparability_dimension_ref",
    "historical_comparability_reference_ref",
]
