"""Canonical offered-payment-term adapter for PAG001 input preparation."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from eios.supplier.models import SupplierEvidenceResult, SupplierObservation


PaymentTermMeaning = Literal["OFFERED_PAYMENT_TERM_DAYS"]
OfferedPaymentTermState = Literal[
    "AVAILABLE",
    "NOT_EVIDENCED",
    "CONFLICTING_DATA",
    "NOT_DETERMINABLE",
]


class PaymentTermSemanticAuthority(BaseModel):
    """Explicit authority binding a semantic_ref to offered payment term in days."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    semantic_ref: str = Field(min_length=1, max_length=256)
    meaning: PaymentTermMeaning
    authority_ref: str = Field(min_length=1, max_length=256)
    methodology_ref: str = Field(min_length=1, max_length=256)
    version: str = Field(min_length=1, max_length=64)


class OfferedPaymentTermObservation(BaseModel):
    """Provenance-safe scalar carrier for the current supplier payment term."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    company_scope: str = Field(min_length=1, max_length=128)
    article_id: str = Field(min_length=1, max_length=128)
    supplier_id: str = Field(min_length=1, max_length=128)
    evaluation_date: object
    source_observation_id: str | None = Field(default=None, max_length=128)
    offered_payment_term_days: Decimal | None = None
    state: OfferedPaymentTermState
    source_ref: str | None = Field(default=None, max_length=256)
    evidence_id: str | None = Field(default=None, max_length=128)
    semantic_ref: str | None = Field(default=None, max_length=256)
    semantic_authority_ref: str | None = Field(default=None, max_length=256)
    authority_ref: str = Field(min_length=1, max_length=256)
    methodology_ref: str = Field(min_length=1, max_length=256)
    trace_refs: tuple[str, ...] = ()

    @field_validator("offered_payment_term_days")
    @classmethod
    def validate_days(cls, value: Decimal | None) -> Decimal | None:
        if value is not None:
            if not value.is_finite():
                raise ValueError("offered_payment_term_days debe ser finito")
            if value < 0:
                raise ValueError("offered_payment_term_days no puede ser negativo")
        return value

    @field_validator("trace_refs")
    @classmethod
    def unique_trace_refs(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("trace_refs no puede contener duplicados")
        if any(not item.strip() for item in value):
            raise ValueError("trace_refs no puede contener valores vacíos")
        return value

    @model_validator(mode="after")
    def validate_state_payload(self) -> "OfferedPaymentTermObservation":
        if self.state == "AVAILABLE":
            required = (
                self.source_observation_id,
                self.offered_payment_term_days,
                self.source_ref,
                self.evidence_id,
                self.semantic_ref,
                self.semantic_authority_ref,
            )
            if any(item is None for item in required):
                raise ValueError("AVAILABLE requiere carrier factual completo")
        elif self.offered_payment_term_days is not None:
            raise ValueError("un estado no AVAILABLE no puede publicar plazo ofrecido")
        return self


class PaymentTermObservationAdapter:
    """Adapt Supplier Evidence facts without inventing term semantics or precedence."""

    def __init__(self, *, authority_ref: str, methodology_ref: str) -> None:
        if not authority_ref.strip():
            raise ValueError("authority_ref no puede estar vacío")
        if not methodology_ref.strip():
            raise ValueError("methodology_ref no puede estar vacío")
        self._authority_ref = authority_ref
        self._methodology_ref = methodology_ref

    def adapt(
        self,
        supplier_result: SupplierEvidenceResult,
        semantic_authority: PaymentTermSemanticAuthority,
    ) -> OfferedPaymentTermObservation:
        identity = supplier_result.identity

        candidates = tuple(
            item
            for item in supplier_result.observations
            if item.candidate_id is None
            and item.supplier_id == supplier_result.current_supplier_id
            and item.object_id == identity.article_id
            and item.dimension == "PAYMENT_TERM"
        )

        if not candidates:
            return self._build(
                supplier_result,
                state="NOT_EVIDENCED",
                semantic_authority=semantic_authority,
            )

        if len(candidates) > 1:
            return self._build(
                supplier_result,
                state="CONFLICTING_DATA",
                semantic_authority=semantic_authority,
                trace_refs=self._collect_trace_refs(candidates),
            )

        observation = candidates[0]

        if observation.state == "CONFLICTING_DATA":
            return self._build(
                supplier_result,
                state="CONFLICTING_DATA",
                semantic_authority=semantic_authority,
                observation=observation,
            )

        if observation.state == "NOT_EVIDENCED":
            return self._build(
                supplier_result,
                state="NOT_EVIDENCED",
                semantic_authority=semantic_authority,
                observation=observation,
            )

        if not self._is_usable(observation, identity.evaluation_date, semantic_authority):
            return self._build(
                supplier_result,
                state="NOT_DETERMINABLE",
                semantic_authority=semantic_authority,
                observation=observation,
            )

        if observation.value_kind == "INTEGER":
            assert observation.value_integer is not None
            value = Decimal(observation.value_integer)
        else:
            assert observation.value_kind == "DECIMAL"
            assert observation.value_decimal is not None
            value = observation.value_decimal

        if not value.is_finite() or value < 0:
            return self._build(
                supplier_result,
                state="NOT_DETERMINABLE",
                semantic_authority=semantic_authority,
                observation=observation,
            )

        return self._build(
            supplier_result,
            state="AVAILABLE",
            semantic_authority=semantic_authority,
            observation=observation,
            offered_payment_term_days=value,
        )

    @staticmethod
    def _is_usable(
        observation: SupplierObservation,
        evaluation_date,
        semantic_authority: PaymentTermSemanticAuthority,
    ) -> bool:
        if observation.value_kind not in {"INTEGER", "DECIMAL"}:
            return False
        if observation.unit != "days":
            return False
        if observation.semantic_ref != semantic_authority.semantic_ref:
            return False
        if semantic_authority.meaning != "OFFERED_PAYMENT_TERM_DAYS":
            return False
        if not all((observation.source_ref, observation.evidence_id, observation.captured_at)):
            return False
        if observation.captured_at > evaluation_date:
            return False
        if observation.valid_from and observation.valid_from > evaluation_date:
            return False
        if observation.valid_to and observation.valid_to < evaluation_date:
            return False
        if any(issue.issue_type == "CONTRADICTION" for issue in observation.issue_refs):
            return False
        return True

    @staticmethod
    def _collect_trace_refs(
        observations: tuple[SupplierObservation, ...],
    ) -> tuple[str, ...]:
        values: list[str] = []
        for item in observations:
            values.extend(item.trace_refs)
            for issue in item.issue_refs:
                values.extend(issue.trace_refs)
        return tuple(dict.fromkeys(values))

    def _build(
        self,
        supplier_result: SupplierEvidenceResult,
        *,
        state: OfferedPaymentTermState,
        semantic_authority: PaymentTermSemanticAuthority,
        observation: SupplierObservation | None = None,
        offered_payment_term_days: Decimal | None = None,
        trace_refs: tuple[str, ...] | None = None,
    ) -> OfferedPaymentTermObservation:
        identity = supplier_result.identity
        obs_trace = observation.trace_refs if observation is not None else ()
        return OfferedPaymentTermObservation(
            decision_id=identity.decision_id,
            scenario_id=identity.scenario_id,
            data_snapshot_id=identity.data_snapshot_id,
            company_scope=identity.company_scope,
            article_id=identity.article_id,
            supplier_id=supplier_result.current_supplier_id,
            evaluation_date=identity.evaluation_date,
            source_observation_id=(
                observation.observation_id if observation is not None else None
            ),
            offered_payment_term_days=offered_payment_term_days,
            state=state,
            source_ref=observation.source_ref if observation is not None else None,
            evidence_id=observation.evidence_id if observation is not None else None,
            semantic_ref=observation.semantic_ref if observation is not None else None,
            semantic_authority_ref=semantic_authority.authority_ref,
            authority_ref=self._authority_ref,
            methodology_ref=self._methodology_ref,
            trace_refs=trace_refs if trace_refs is not None else obs_trace,
        )


__all__ = [
    "OfferedPaymentTermObservation",
    "OfferedPaymentTermState",
    "PaymentTermMeaning",
    "PaymentTermObservationAdapter",
    "PaymentTermSemanticAuthority",
]
