"""Authorized non-scoring Supplier Risk / Value external assessment layer."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.core.orchestration import CapabilityExecution, O1ExecutionStatus
from eios.core.observed_invocation import SingleUseObservedInvoker
from eios.core.validation import validate_evidence

from .models import SupplierEvidenceResult


RiskDimension = Literal[
    "RELIABILITY",
    "COMPLIANCE",
    "AVAILABILITY",
    "CONCENTRATION",
    "CRITICAL_SIGNAL",
]
RiskState = Literal["FAVORABLE", "ADVERSE", "NOT_DETERMINABLE", "CONFLICTING"]

ValueDimension = Literal[
    "PRICE",
    "PAYMENT_TERM",
    "COMMERCIAL_CONDITIONS",
    "RELIABILITY",
    "AVAILABILITY",
]
ValueState = Literal[
    "BETTER",
    "EQUIVALENT",
    "WORSE",
    "NOT_DETERMINABLE",
    "CONFLICTING",
]


class _Frozen(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class SupplierRiskDimensionAssessment(_Frozen):
    supplier_id: str = Field(min_length=1, max_length=128)
    dimension: RiskDimension
    state: RiskState
    authority_ref: str = Field(min_length=1, max_length=256)
    methodology_ref: str = Field(min_length=1, max_length=256)
    assessment_ref: str = Field(min_length=1, max_length=256)
    evidence_refs: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_refs(self) -> "SupplierRiskDimensionAssessment":
        if len(self.evidence_refs) != len(set(self.evidence_refs)):
            raise ValueError("evidence_refs no puede contener duplicados")
        if len(self.trace_refs) != len(set(self.trace_refs)):
            raise ValueError("trace_refs no puede contener duplicados")
        if not self.evidence_refs:
            raise ValueError("evidence_refs no puede estar vacío")
        if not self.trace_refs:
            raise ValueError("trace_refs no puede estar vacío")
        return self


class SupplierValueDimensionAssessment(_Frozen):
    supplier_id: str = Field(min_length=1, max_length=128)
    comparison_supplier_id: str | None = Field(default=None, min_length=1, max_length=128)
    dimension: ValueDimension
    state: ValueState
    authority_ref: str = Field(min_length=1, max_length=256)
    methodology_ref: str = Field(min_length=1, max_length=256)
    assessment_ref: str = Field(min_length=1, max_length=256)
    evidence_refs: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_value(self) -> "SupplierValueDimensionAssessment":
        if self.comparison_supplier_id == self.supplier_id:
            raise ValueError("un proveedor no puede compararse consigo mismo")
        if self.state in {"BETTER", "EQUIVALENT", "WORSE"} and self.comparison_supplier_id is None:
            raise ValueError("BETTER/EQUIVALENT/WORSE requieren comparison_supplier_id")
        if len(self.evidence_refs) != len(set(self.evidence_refs)):
            raise ValueError("evidence_refs no puede contener duplicados")
        if len(self.trace_refs) != len(set(self.trace_refs)):
            raise ValueError("trace_refs no puede contener duplicados")
        if not self.evidence_refs:
            raise ValueError("evidence_refs no puede estar vacío")
        if not self.trace_refs:
            raise ValueError("trace_refs no puede estar vacío")
        return self


class SupplierRiskValueResult(_Frozen):
    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    article_id: str = Field(min_length=1, max_length=128)
    current_supplier_id: str = Field(min_length=1, max_length=128)
    risk_dimensions: tuple[SupplierRiskDimensionAssessment, ...] = ()
    value_dimensions: tuple[SupplierValueDimensionAssessment, ...] = ()
    unresolved_items: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()


def _validate_identity(
    purchase: PurchaseOperation,
    context: DecisionContext,
    supplier_result: SupplierEvidenceResult,
) -> set[str]:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    identity = supplier_result.identity
    checks = (
        (identity.decision_id, context.decision_id, "decision_id"),
        (identity.scenario_id, context.scenario_id, "scenario_id"),
        (identity.rules_version, context.rules_version, "rules_version"),
        (identity.parameters_version, context.parameters_version, "parameters_version"),
        (identity.data_snapshot_id, context.data_snapshot_id, "data_snapshot_id"),
        (identity.article_id, purchase.article_id, "article_id"),
        (identity.evaluation_date, purchase.operation_date, "evaluation_date"),
        (supplier_result.current_supplier_id, purchase.supplier_id, "supplier_id"),
    )
    for actual, expected, label in checks:
        if actual != expected:
            raise ValueError(f"SupplierEvidenceResult incompatible en {label}")
    return {
        supplier_result.current_supplier_id,
        *(item.supplier_id for item in supplier_result.candidates),
    }


def _validated_evidence(evidences: tuple[Evidence, ...]) -> dict[str, Evidence]:
    by_id = {item.evidence_id: item for item in evidences}
    if len(by_id) != len(evidences):
        raise ValueError("evidence_id duplicado")
    return by_id


def _validate_external_assessment(item, by_id: dict[str, Evidence]) -> None:
    if not any(
        evidence.state == "DEMONSTRATED"
        and evidence.demonstration_ref == item.authority_ref
        and validate_evidence(evidence).status == "VALID"
        for evidence in by_id.values()
    ):
        raise ValueError("authority_ref no demostrada")
    for evidence_id in item.evidence_refs:
        evidence = by_id.get(evidence_id)
        if (
            evidence is None
            or evidence.state != "DEMONSTRATED"
            or validate_evidence(evidence).status != "VALID"
        ):
            raise ValueError("evidence_ref no demostrada")


def produce_supplier_risk_value(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    supplier_result: SupplierEvidenceResult,
    risk_assessments: tuple[SupplierRiskDimensionAssessment, ...],
    value_assessments: tuple[SupplierValueDimensionAssessment, ...],
    evidences: tuple[Evidence, ...],
) -> SupplierRiskValueResult:
    allowed_suppliers = _validate_identity(purchase, context, supplier_result)
    by_id = _validated_evidence(evidences)

    risk_keys = tuple((x.supplier_id, x.dimension) for x in risk_assessments)
    if len(risk_keys) != len(set(risk_keys)):
        raise ValueError("dimensión Risk duplicada para supplier_id")

    value_keys = tuple(
        (x.supplier_id, x.comparison_supplier_id, x.dimension)
        for x in value_assessments
    )
    if len(value_keys) != len(set(value_keys)):
        raise ValueError("dimensión Value duplicada para supplier/comparison/dimension")

    for item in (*risk_assessments, *value_assessments):
        if item.supplier_id not in allowed_suppliers:
            raise ValueError("assessment pertenece a supplier_id fuera del conjunto evaluado")
        comparison = getattr(item, "comparison_supplier_id", None)
        if comparison is not None and comparison not in allowed_suppliers:
            raise ValueError("comparison_supplier_id fuera del conjunto evaluado")
        _validate_external_assessment(item, by_id)

    risks = tuple(sorted(
        risk_assessments,
        key=lambda x: (x.supplier_id, x.dimension, x.assessment_ref),
    ))
    values = tuple(sorted(
        value_assessments,
        key=lambda x: (
            x.supplier_id,
            x.comparison_supplier_id or "",
            x.dimension,
            x.assessment_ref,
        ),
    ))

    unresolved = tuple(sorted({
        f"RISK:{x.supplier_id}:{x.dimension}:{x.state}"
        for x in risks
        if x.state in {"NOT_DETERMINABLE", "CONFLICTING"}
    } | {
        f"VALUE:{x.supplier_id}:{x.comparison_supplier_id or 'none'}:{x.dimension}:{x.state}"
        for x in values
        if x.state in {"NOT_DETERMINABLE", "CONFLICTING"}
    }))
    evidence_refs = tuple(sorted({
        ref for item in (*risks, *values) for ref in item.evidence_refs
    }))
    trace_refs = tuple(sorted({
        ref for item in (*risks, *values) for ref in item.trace_refs
    }))

    return SupplierRiskValueResult(
        decision_id=context.decision_id,
        scenario_id=context.scenario_id,
        article_id=purchase.article_id,
        current_supplier_id=purchase.supplier_id,
        risk_dimensions=risks,
        value_dimensions=values,
        unresolved_items=unresolved,
        evidence_refs=evidence_refs,
        trace_refs=trace_refs,
    )


SupplierRiskValueInvoker = Callable[[PurchaseOperation, DecisionContext], CapabilityExecution]


@dataclass(frozen=True)
class SupplierRiskValueInvocationCapture:
    result: SupplierRiskValueResult
    capability: CapabilityExecution


def _frozen_sources(supplier_result, risk_assessments, value_assessments, evidences):
    return (
        supplier_result.model_copy(deep=True),
        tuple(item.model_copy(deep=True) for item in risk_assessments),
        tuple(item.model_copy(deep=True) for item in value_assessments),
        tuple(item.model_copy(deep=True) for item in evidences),
    )


def _produce_bound(purchase, context, supplier_snapshot, risk_snapshot,
                   value_snapshot, evidence_snapshot):
    return produce_supplier_risk_value(
        purchase=purchase.model_copy(deep=True),
        context=context.model_copy(deep=True),
        supplier_result=supplier_snapshot.model_copy(deep=True),
        risk_assessments=tuple(item.model_copy(deep=True) for item in risk_snapshot),
        value_assessments=tuple(item.model_copy(deep=True) for item in value_snapshot),
        evidences=tuple(item.model_copy(deep=True) for item in evidence_snapshot),
    )


def _adapt_result(result: SupplierRiskValueResult) -> CapabilityExecution:
    status = (O1ExecutionStatus.PARTIALLY_COMPLETED if result.unresolved_items
              else O1ExecutionStatus.COMPLETED)
    return CapabilityExecution(
        capability="SUPPLIER_RISK_VALUE", status=status, result_available=True,
        trace_references=result.trace_refs, unresolved_items=result.unresolved_items,
    )


class ObservedSupplierRiskValueInvoker(SingleUseObservedInvoker[
    SupplierRiskValueResult, SupplierRiskValueInvocationCapture
]):
    """One-shot reference capture with complete frozen purchase identity."""

    def __init__(self, *, reference_case_id: str, purchase: PurchaseOperation,
                 supplier_result: SupplierEvidenceResult,
                 risk_assessments: tuple[SupplierRiskDimensionAssessment, ...],
                 value_assessments: tuple[SupplierValueDimensionAssessment, ...],
                 evidences: tuple[Evidence, ...]) -> None:
        self._purchase = purchase.model_copy(deep=True)
        self._sources = _frozen_sources(
            supplier_result, risk_assessments, value_assessments, evidences,
        )
        super().__init__(
            label="SUPPLIER_RISK_VALUE", reference_case_id=reference_case_id,
            producer=self._produce, adapter=_adapt_result,
            capture_factory=SupplierRiskValueInvocationCapture,
        )

    def _produce(self, purchase: PurchaseOperation,
                 context: DecisionContext) -> SupplierRiskValueResult:
        mismatches = tuple(field for field in PurchaseOperation.model_fields
                           if getattr(self._purchase, field) != getattr(purchase, field))
        if mismatches:
            raise ValueError("Observed supplier purchase mismatch: " + ", ".join(mismatches))
        identity = self._sources[0].identity
        context_mismatches = tuple(field for field in (
            "decision_id", "scenario_id", "rules_version", "parameters_version",
            "data_snapshot_id",
        ) if getattr(identity, field) != getattr(context, field))
        if context_mismatches:
            raise ValueError("Observed supplier context mismatch: "
                             + ", ".join(context_mismatches))
        return _produce_bound(purchase, context, *self._sources)

    def source_payload(self) -> dict:
        supplier, risks, values, evidences = self._sources
        return {
            "purchase": self._purchase.model_dump(mode="json"),
            "supplier_result": supplier.model_dump(mode="json"),
            "risk_assessments": [x.model_dump(mode="json") for x in risks],
            "value_assessments": [x.model_dump(mode="json") for x in values],
            "evidences": [x.model_dump(mode="json") for x in evidences],
        }


def build_reference_observed_supplier_risk_value_invoker(
    *, reference_case_id: str, purchase: PurchaseOperation,
    supplier_result: SupplierEvidenceResult,
    risk_assessments: tuple[SupplierRiskDimensionAssessment, ...],
    value_assessments: tuple[SupplierValueDimensionAssessment, ...],
    evidences: tuple[Evidence, ...],
) -> ObservedSupplierRiskValueInvoker:
    return ObservedSupplierRiskValueInvoker(
        reference_case_id=reference_case_id, purchase=purchase,
        supplier_result=supplier_result, risk_assessments=risk_assessments,
        value_assessments=value_assessments, evidences=evidences,
    )


def build_provenanced_supplier_risk_value_invoker(
    *,
    supplier_result: SupplierEvidenceResult,
    risk_assessments: tuple[SupplierRiskDimensionAssessment, ...],
    value_assessments: tuple[SupplierValueDimensionAssessment, ...],
    evidences: tuple[Evidence, ...],
) -> SupplierRiskValueInvoker:
    supplier_snapshot, risk_snapshot, value_snapshot, evidence_snapshot = _frozen_sources(
        supplier_result, risk_assessments, value_assessments, evidences,
    )

    def invoke(purchase: PurchaseOperation, context: DecisionContext) -> CapabilityExecution:
        result = _produce_bound(purchase, context, supplier_snapshot, risk_snapshot,
                                value_snapshot, evidence_snapshot)
        return _adapt_result(result)

    return invoke


__all__ = [
    "RiskDimension",
    "RiskState",
    "SupplierRiskDimensionAssessment",
    "SupplierRiskValueInvoker",
    "SupplierRiskValueResult",
    "SupplierValueDimensionAssessment",
    "ValueDimension",
    "ValueState",
    "build_provenanced_supplier_risk_value_invoker",
    "ObservedSupplierRiskValueInvoker",
    "SupplierRiskValueInvocationCapture",
    "build_reference_observed_supplier_risk_value_invoker",
    "produce_supplier_risk_value",
]
