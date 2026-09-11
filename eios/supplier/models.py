"""Physical Supplier Evidence Core contracts for EIOS Capa 5.

This module implements the closed Supplier Evidence Core methodology v0.3 and
technical contract v0.3.3. It owns factual supplier evidence only; supplier
scoring, ranking, R-PROV rules, CRC and final purchase authority remain outside
this package.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from eios.core.models import DecisionContext, PurchaseOperation

SUPPLIER_EVIDENCE_METHODOLOGY_VERSION = "0.3"

CandidateEvidenceState = Literal[
    "CURRENT_OPERATION_DEMONSTRATED",
    "REFERENCE_ONLY",
    "GAP",
    "CONFLICTING_DATA",
]
CandidateResolutionState = Literal[
    "EVIDENCED_CANDIDATE",
    "NOT_EVIDENCED",
    "CONFLICTING_DATA",
]
ObservationState = Literal["KNOWN", "NOT_EVIDENCED", "CONFLICTING_DATA"]
StructuralComparabilityState = Literal[
    "STRUCTURALLY_COMPARABLE",
    "NOT_STRUCTURALLY_COMPARABLE",
    "UNKNOWN",
]
ExternalMetricUsageState = Literal[
    "AUTHORIZED_EXTERNAL_METRIC",
    "CONTEXT_ONLY_METRIC",
]
IssueType = Literal["MISSING_DATA", "CONTRADICTION"]
SupplierItemType = Literal["CANDIDATE", "OBSERVATION", "METRIC", "COMPARISON"]
SupplierDimension = Literal[
    "PRICE_REFERENCE",
    "PAYMENT_TERM",
    "COMMERCIAL_CONDITION",
    "DELIVERY_DATE",
    "LEAD_TIME",
    "AVAILABILITY",
    "QUALITY_REFERENCE",
    "RELIABILITY_REFERENCE",
    "OTHER_EVIDENCED_CONDITION",
]
ObservationValueKind = Literal["DECIMAL", "TEXT", "DATE", "INTEGER", "BOOLEAN"]


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)


def _finite(value: Decimal | None, field: str) -> Decimal | None:
    if value is not None and not value.is_finite():
        raise ValueError(f"{field} debe ser finito")
    return value


def _unique(values: tuple[str, ...], field: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"{field} no puede contener duplicados")


def _has_contradiction(issues: tuple["SupplierDataIssueRef", ...]) -> bool:
    return any(issue.issue_type == "CONTRADICTION" for issue in issues)


class SupplierDataIssueRef(FrozenModel):
    issue_id: str = Field(min_length=1, max_length=128)
    issue_type: IssueType
    issue_record_ref: str = Field(min_length=1, max_length=256)
    evidence_refs: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_issue(self) -> "SupplierDataIssueRef":
        _unique(self.evidence_refs, "evidence_refs")
        _unique(self.trace_refs, "trace_refs")
        if self.issue_type == "CONTRADICTION" and len(self.evidence_refs) < 2:
            raise ValueError("CONTRADICTION requiere al menos dos evidence_refs distintas")
        return self


class SupplierItemRef(FrozenModel):
    item_type: SupplierItemType
    item_id: str = Field(min_length=1, max_length=128)


class SupplierResultIdentity(FrozenModel):
    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    rules_version: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    company_scope: str = Field(min_length=1, max_length=128)
    article_id: str = Field(min_length=1, max_length=128)
    evaluation_date: date
    methodology_version: Literal["0.3"] = SUPPLIER_EVIDENCE_METHODOLOGY_VERSION


class SupplierCandidateEvidence(FrozenModel):
    candidate_id: str = Field(min_length=1, max_length=128)
    supplier_id: str = Field(min_length=1, max_length=128)
    object_id: str = Field(min_length=1, max_length=128)
    state: CandidateEvidenceState
    evidence_id: str | None = Field(default=None, min_length=1, max_length=128)
    source_ref: str | None = Field(default=None, min_length=1, max_length=256)
    captured_at: date | None = None
    applicability_ref: str | None = Field(default=None, min_length=1, max_length=256)
    valid_from: date | None = None
    valid_to: date | None = None
    issue_refs: tuple[SupplierDataIssueRef, ...] = ()
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_candidate(self) -> "SupplierCandidateEvidence":
        _unique(self.trace_refs, "trace_refs")
        if self.valid_from and self.valid_to and self.valid_to < self.valid_from:
            raise ValueError("valid_to no puede ser anterior a valid_from")
        if self.state == "CURRENT_OPERATION_DEMONSTRATED":
            if not all((self.evidence_id, self.source_ref, self.captured_at, self.applicability_ref)):
                raise ValueError("CURRENT_OPERATION_DEMONSTRATED requiere evidencia, fuente, captura y aplicabilidad")
            if _has_contradiction(self.issue_refs):
                raise ValueError("CURRENT_OPERATION_DEMONSTRATED no admite contradicción no resuelta")
        elif self.state == "REFERENCE_ONLY":
            if not all((self.evidence_id, self.source_ref, self.captured_at)):
                raise ValueError("REFERENCE_ONLY requiere evidencia, fuente y captura")
        elif self.state == "GAP":
            if self.applicability_ref is not None:
                raise ValueError("GAP no puede publicar applicability_ref actual")
        elif self.state == "CONFLICTING_DATA":
            if not _has_contradiction(self.issue_refs):
                raise ValueError("CONFLICTING_DATA requiere SupplierDataIssueRef CONTRADICTION")
            if self.applicability_ref is not None:
                raise ValueError("CONFLICTING_DATA no puede publicar applicability_ref determinado")
        return self


class CandidateResolution(FrozenModel):
    candidate_id: str = Field(min_length=1, max_length=128)
    supplier_id: str = Field(min_length=1, max_length=128)
    state: CandidateResolutionState
    evidence_refs: tuple[str, ...] = ()
    issue_refs: tuple[SupplierDataIssueRef, ...] = ()
    trace_refs: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()


class SupplierObservation(FrozenModel):
    observation_id: str = Field(min_length=1, max_length=128)
    supplier_id: str = Field(min_length=1, max_length=128)
    candidate_id: str | None = Field(default=None, min_length=1, max_length=128)
    object_id: str = Field(min_length=1, max_length=128)
    dimension: SupplierDimension
    state: ObservationState
    value_kind: ObservationValueKind
    value_decimal: Decimal | None = None
    value_text: str | None = Field(default=None, min_length=1, max_length=512)
    value_date: date | None = None
    value_integer: int | None = None
    value_boolean: bool | None = None
    unit: str | None = Field(default=None, min_length=1, max_length=64)
    semantic_ref: str = Field(min_length=1, max_length=256)
    source_ref: str | None = Field(default=None, min_length=1, max_length=256)
    evidence_id: str | None = Field(default=None, min_length=1, max_length=128)
    captured_at: date | None = None
    valid_from: date | None = None
    valid_to: date | None = None
    issue_refs: tuple[SupplierDataIssueRef, ...] = ()
    trace_refs: tuple[str, ...] = ()

    @field_validator("value_integer", "value_decimal", mode="before")
    @classmethod
    def reject_bool_as_numeric(cls, value):
        if isinstance(value, bool):
            raise ValueError("bool no puede utilizarse como valor numérico")
        return value

    @field_validator("value_boolean", mode="before")
    @classmethod
    def require_real_bool(cls, value):
        if value is not None and type(value) is not bool:
            raise ValueError("value_boolean requiere bool real")
        return value

    @field_validator("value_decimal")
    @classmethod
    def validate_decimal(cls, value: Decimal | None) -> Decimal | None:
        return _finite(value, "value_decimal")

    @model_validator(mode="after")
    def validate_observation(self) -> "SupplierObservation":
        _unique(self.trace_refs, "trace_refs")
        if self.valid_from and self.valid_to and self.valid_to < self.valid_from:
            raise ValueError("valid_to no puede ser anterior a valid_from")

        values = {
            "DECIMAL": self.value_decimal,
            "TEXT": self.value_text,
            "DATE": self.value_date,
            "INTEGER": self.value_integer,
            "BOOLEAN": self.value_boolean,
        }
        present = [name for name, value in values.items() if value is not None]
        if self.state == "KNOWN":
            if present != [self.value_kind]:
                raise ValueError("KNOWN requiere exactamente el value_* correspondiente a value_kind")
            if not all((self.source_ref, self.evidence_id, self.captured_at)):
                raise ValueError("Observation KNOWN requiere fuente, evidencia y captura")
        elif present:
            raise ValueError("Una observación no KNOWN no puede publicar value_*")

        if self.state == "CONFLICTING_DATA" and not _has_contradiction(self.issue_refs):
            raise ValueError("Observation CONFLICTING_DATA requiere contradicción")
        if self.value_kind in {"DATE", "TEXT", "BOOLEAN"} and self.unit is not None:
            raise ValueError("DATE/TEXT/BOOLEAN requieren unit=None")
        return self


class SupplierHistoricalFact(FrozenModel):
    fact_id: str = Field(min_length=1, max_length=128)
    supplier_id: str = Field(min_length=1, max_length=128)
    event_type: str = Field(min_length=1, max_length=128)
    event_date: date
    captured_at: date
    scope_ref: str = Field(min_length=1, max_length=256)
    source_ref: str = Field(min_length=1, max_length=256)
    evidence_id: str = Field(min_length=1, max_length=128)
    trace_refs: tuple[str, ...] = ()


class SupplierSignal(FrozenModel):
    signal_id: str = Field(min_length=1, max_length=128)
    supplier_id: str = Field(min_length=1, max_length=128)
    signal_type: str = Field(min_length=1, max_length=128)
    observed_at: date
    captured_at: date
    scope_ref: str = Field(min_length=1, max_length=256)
    source_ref: str = Field(min_length=1, max_length=256)
    evidence_id: str = Field(min_length=1, max_length=128)
    trace_refs: tuple[str, ...] = ()


class ExternalSupplierMetric(FrozenModel):
    metric_id: str = Field(min_length=1, max_length=128)
    supplier_id: str = Field(min_length=1, max_length=128)
    metric_name: str = Field(min_length=1, max_length=128)
    data_state: ObservationState
    value: Decimal | None = None
    unit: str = Field(min_length=1, max_length=64)
    scope_ref: str = Field(min_length=1, max_length=256)
    period_start: date | None = None
    period_end: date | None = None
    methodology_ref: str | None = Field(default=None, min_length=1, max_length=256)
    source_ref: str | None = Field(default=None, min_length=1, max_length=256)
    captured_at: date | None = None
    usage_state: ExternalMetricUsageState
    usage_authority_ref: str | None = Field(default=None, min_length=1, max_length=256)
    issue_refs: tuple[SupplierDataIssueRef, ...] = ()
    trace_refs: tuple[str, ...] = ()

    @field_validator("value", mode="before")
    @classmethod
    def reject_bool_metric(cls, value):
        if isinstance(value, bool):
            raise ValueError("bool no puede utilizarse como métrica Decimal")
        return value

    @field_validator("value")
    @classmethod
    def validate_value(cls, value: Decimal | None) -> Decimal | None:
        return _finite(value, "metric.value")

    @model_validator(mode="after")
    def validate_metric(self) -> "ExternalSupplierMetric":
        if self.period_start and self.period_end and self.period_end < self.period_start:
            raise ValueError("period_end no puede ser anterior a period_start")
        if self.data_state == "KNOWN":
            if self.value is None or not all((self.period_start, self.period_end, self.methodology_ref, self.source_ref, self.captured_at)):
                raise ValueError("Metric KNOWN requiere valor, periodo, metodología, fuente y captura")
        elif self.value is not None:
            raise ValueError("Metric no KNOWN no puede publicar value")
        if self.data_state == "CONFLICTING_DATA" and not _has_contradiction(self.issue_refs):
            raise ValueError("Metric CONFLICTING_DATA requiere contradicción")
        if self.usage_state == "AUTHORIZED_EXTERNAL_METRIC":
            if self.data_state != "KNOWN" or not self.usage_authority_ref:
                raise ValueError("AUTHORIZED_EXTERNAL_METRIC requiere dato KNOWN y usage_authority_ref")
        return self


class StructuralComparisonRequest(FrozenModel):
    comparison_id: str = Field(min_length=1, max_length=128)
    current_observation_id: str = Field(min_length=1, max_length=128)
    candidate_observation_id: str = Field(min_length=1, max_length=128)
    comparison_authority_ref: str | None = Field(default=None, min_length=1, max_length=256)


class StructuralComparisonResult(FrozenModel):
    comparison_id: str = Field(min_length=1, max_length=128)
    current_observation_id: str = Field(min_length=1, max_length=128)
    candidate_observation_id: str = Field(min_length=1, max_length=128)
    current_dimension: SupplierDimension
    candidate_dimension: SupplierDimension
    state: StructuralComparabilityState
    difference_decimal: Decimal | None = None
    comparison_authority_ref: str | None = None
    issue_refs: tuple[SupplierDataIssueRef, ...] = ()
    limitations: tuple[str, ...] = ()

    @field_validator("difference_decimal")
    @classmethod
    def validate_difference(cls, value: Decimal | None) -> Decimal | None:
        return _finite(value, "difference_decimal")

    @model_validator(mode="after")
    def validate_difference_state(self) -> "StructuralComparisonResult":
        if self.difference_decimal is not None and self.state != "STRUCTURALLY_COMPARABLE":
            raise ValueError("Solo una comparación estructural compatible puede publicar difference_decimal")
        if self.state == "STRUCTURALLY_COMPARABLE" and self.current_dimension != self.candidate_dimension:
            raise ValueError("STRUCTURALLY_COMPARABLE requiere dimensiones iguales")
        return self


class SupplierEvidenceInput(FrozenModel):
    context: DecisionContext
    purchase_operation: PurchaseOperation
    company_scope: str = Field(min_length=1, max_length=128)
    evaluation_date: date
    methodology_version: Literal["0.3"] = SUPPLIER_EVIDENCE_METHODOLOGY_VERSION
    candidates: tuple[SupplierCandidateEvidence, ...] = ()
    observations: tuple[SupplierObservation, ...] = ()
    historical_facts: tuple[SupplierHistoricalFact, ...] = ()
    external_metrics: tuple[ExternalSupplierMetric, ...] = ()
    signals: tuple[SupplierSignal, ...] = ()
    comparison_requests: tuple[StructuralComparisonRequest, ...] = ()

    @model_validator(mode="after")
    def validate_envelope(self) -> "SupplierEvidenceInput":
        if self.context.decision_id != self.purchase_operation.decision_id:
            raise ValueError("DecisionContext y PurchaseOperation deben compartir decision_id")
        if self.context.scenario_id != self.purchase_operation.scenario_id:
            raise ValueError("DecisionContext y PurchaseOperation deben compartir scenario_id")

        def ensure_unique(items, attr: str) -> None:
            values = [getattr(item, attr) for item in items]
            if len(values) != len(set(values)):
                raise ValueError(f"{attr} duplicado")

        ensure_unique(self.candidates, "candidate_id")
        ensure_unique(self.observations, "observation_id")
        ensure_unique(self.historical_facts, "fact_id")
        ensure_unique(self.external_metrics, "metric_id")
        ensure_unique(self.signals, "signal_id")
        ensure_unique(self.comparison_requests, "comparison_id")

        current_supplier = self.purchase_operation.supplier_id
        article_id = self.purchase_operation.article_id
        candidates = {candidate.candidate_id: candidate for candidate in self.candidates}
        allowed_suppliers = {current_supplier, *(c.supplier_id for c in self.candidates)}

        for candidate in self.candidates:
            if candidate.supplier_id == current_supplier:
                raise ValueError("Un candidato alternativo no puede ser el proveedor actual")
            if candidate.object_id != article_id:
                raise ValueError("El candidato debe referir al article_id de la operación")
            if candidate.captured_at and candidate.captured_at > self.evaluation_date:
                raise ValueError("candidate.captured_at no puede ser posterior a evaluation_date")
            if candidate.state == "CURRENT_OPERATION_DEMONSTRATED":
                if candidate.valid_from and candidate.valid_from > self.evaluation_date:
                    raise ValueError("El candidato demostrado aún no está vigente")
                if candidate.valid_to and candidate.valid_to < self.evaluation_date:
                    raise ValueError("El candidato demostrado está expirado")

        observations = {item.observation_id: item for item in self.observations}
        for item in self.observations:
            if item.object_id != article_id:
                raise ValueError("La observación debe referir al article_id de la operación")
            if item.captured_at and item.captured_at > self.evaluation_date:
                raise ValueError("observation.captured_at no puede ser posterior a evaluation_date")
            if item.candidate_id is None:
                if item.supplier_id != current_supplier:
                    raise ValueError("Una observación sin candidate_id debe pertenecer al proveedor actual")
            else:
                candidate = candidates.get(item.candidate_id)
                if candidate is None:
                    raise ValueError("La observación referencia un candidate_id inexistente")
                if item.supplier_id != candidate.supplier_id:
                    raise ValueError("La observación y su candidato deben compartir supplier_id")

        for fact in self.historical_facts:
            if fact.supplier_id not in allowed_suppliers:
                raise ValueError("Historical fact pertenece a proveedor ajeno al conjunto evaluado")
            if fact.event_date > self.evaluation_date or fact.captured_at > self.evaluation_date:
                raise ValueError("Historical fact no puede ser futuro respecto de evaluation_date")

        for signal in self.signals:
            if signal.supplier_id not in allowed_suppliers:
                raise ValueError("Signal pertenece a proveedor ajeno al conjunto evaluado")
            if signal.observed_at > self.evaluation_date or signal.captured_at > self.evaluation_date:
                raise ValueError("Signal no puede ser futuro respecto de evaluation_date")

        for metric in self.external_metrics:
            if metric.supplier_id not in allowed_suppliers:
                raise ValueError("Metric pertenece a proveedor ajeno al conjunto evaluado")
            if metric.captured_at and metric.captured_at > self.evaluation_date:
                raise ValueError("metric.captured_at no puede ser posterior a evaluation_date")
            if metric.period_end and metric.period_end > self.evaluation_date:
                raise ValueError("metric.period_end no puede ser posterior a evaluation_date")

        for request in self.comparison_requests:
            current = observations.get(request.current_observation_id)
            candidate_obs = observations.get(request.candidate_observation_id)
            if current is None or candidate_obs is None:
                raise ValueError("Comparison request referencia observation_id inexistente")
            if current.observation_id == candidate_obs.observation_id:
                raise ValueError("Una comparación no puede enfrentar una observación consigo misma")
            if current.candidate_id is not None or current.supplier_id != current_supplier:
                raise ValueError("current_observation debe pertenecer al proveedor actual")
            if candidate_obs.candidate_id is None or candidate_obs.candidate_id not in candidates:
                raise ValueError("candidate_observation debe pertenecer a un candidato existente")
        return self


class SupplierEvidenceResult(FrozenModel):
    identity: SupplierResultIdentity
    current_supplier_id: str = Field(min_length=1, max_length=128)
    candidates: tuple[SupplierCandidateEvidence, ...] = ()
    candidate_resolutions: tuple[CandidateResolution, ...] = ()
    observations: tuple[SupplierObservation, ...] = ()
    historical_facts: tuple[SupplierHistoricalFact, ...] = ()
    external_metrics: tuple[ExternalSupplierMetric, ...] = ()
    signals: tuple[SupplierSignal, ...] = ()
    structural_comparisons: tuple[StructuralComparisonResult, ...] = ()
    unresolved_items: tuple[SupplierItemRef, ...] = ()
    conflicting_items: tuple[SupplierItemRef, ...] = ()
    limitations: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_candidate_alignment(self) -> "SupplierEvidenceResult":
        if tuple(item.candidate_id for item in self.candidates) != tuple(
            item.candidate_id for item in self.candidate_resolutions
        ):
            raise ValueError("candidates y candidate_resolutions deben permanecer alineados")
        return self


__all__ = [
    "CandidateEvidenceState",
    "CandidateResolution",
    "CandidateResolutionState",
    "ExternalMetricUsageState",
    "ExternalSupplierMetric",
    "IssueType",
    "ObservationState",
    "ObservationValueKind",
    "StructuralComparabilityState",
    "StructuralComparisonRequest",
    "StructuralComparisonResult",
    "SupplierCandidateEvidence",
    "SupplierDataIssueRef",
    "SupplierDimension",
    "SupplierEvidenceInput",
    "SupplierEvidenceResult",
    "SupplierHistoricalFact",
    "SupplierItemRef",
    "SupplierItemType",
    "SupplierObservation",
    "SupplierResultIdentity",
    "SupplierSignal",
    "SUPPLIER_EVIDENCE_METHODOLOGY_VERSION",
]
