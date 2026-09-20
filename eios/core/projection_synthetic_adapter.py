"""Public atomic adapter for validated PROJECTION_ONLY synthetic material."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from .documentary_payment_capture import DocumentaryPaymentCapture
from .finance_decision_input_package import FinanceDecisionInputPackage
from .finance_flow_completeness import FinanceFlowCompletenessRecord
from .finance_quality_preparation import FinanceQualityPreparation
from .flow_inventory_mandate import FlowInventoryMandateVerification
from .flow_inventory_review import FlowInventoryPersonalReview
from .projection_criteria_manifest import ProjectionCriteriaManifest
from .projection_material_envelope import (
    ProjectionMaterialEnvelope, build_projection_material_envelope,
)
from .projection_mock_dataset import ProjectionMockDataset
from .required_installment_coverage import (
    RequiredInstallmentCalendar, RequiredInstallmentCoverage,
)
from .treasury_contextual_assessment import TreasuryContextualAssessment
from .treasury_documentary_support import TreasuryDocumentarySupport
from .treasury_mandate_verification import TreasuryMandateVerification
from .treasury_personal_review import TreasuryPersonalReview
from ._projection_synthetic_foundation import (
    SyntheticSemanticAdapterError, _build_synthetic_stage6,
)


SCHEMA_VERSION = "EIOS-PROJECTION-ONLY-SYNTHETIC-BUNDLE-01/v0.1"


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _payload_hash(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


@dataclass(frozen=True, init=False)
class ProjectionOnlySyntheticMaterialBundle:
    """Complete synthetic translation; never a Finance or QTG result."""

    _dataset_fingerprint: str
    _finance_package: FinanceDecisionInputPackage
    _payment_capture: DocumentaryPaymentCapture
    _required_calendar: RequiredInstallmentCalendar
    _required_coverage: RequiredInstallmentCoverage
    _preparation: FinanceQualityPreparation
    _criteria_manifest: ProjectionCriteriaManifest
    _treasury_support: TreasuryDocumentarySupport
    _treasury_assessment: TreasuryContextualAssessment
    _treasury_mandate: TreasuryMandateVerification
    _treasury_review: TreasuryPersonalReview
    _flow_record: FinanceFlowCompletenessRecord
    _flow_mandate: FlowInventoryMandateVerification
    _flow_review: FlowInventoryPersonalReview
    _envelope: ProjectionMaterialEnvelope
    _material: bytes

    def __init__(self) -> None:
        raise TypeError("Use build_projection_only_synthetic_material_bundle")

    @property
    def dataset_fingerprint(self) -> str:
        return self._dataset_fingerprint

    @property
    def finance_package(self) -> FinanceDecisionInputPackage:
        return self._finance_package

    @property
    def payment_capture(self) -> DocumentaryPaymentCapture:
        return self._payment_capture

    @property
    def required_installment_calendar(self) -> RequiredInstallmentCalendar:
        return self._required_calendar

    @property
    def required_installment_coverage(self) -> RequiredInstallmentCoverage:
        return self._required_coverage

    @property
    def finance_quality_preparation(self) -> FinanceQualityPreparation:
        return self._preparation

    @property
    def criteria_manifest(self) -> ProjectionCriteriaManifest:
        return self._criteria_manifest

    @property
    def treasury_support(self) -> TreasuryDocumentarySupport:
        return self._treasury_support

    @property
    def treasury_assessment(self) -> TreasuryContextualAssessment:
        return self._treasury_assessment

    @property
    def treasury_mandate(self) -> TreasuryMandateVerification:
        return self._treasury_mandate

    @property
    def treasury_review(self) -> TreasuryPersonalReview:
        return self._treasury_review

    @property
    def flow_record(self) -> FinanceFlowCompletenessRecord:
        return self._flow_record

    @property
    def flow_mandate(self) -> FlowInventoryMandateVerification:
        return self._flow_mandate

    @property
    def flow_review(self) -> FlowInventoryPersonalReview:
        return self._flow_review

    @property
    def envelope(self) -> ProjectionMaterialEnvelope:
        return self._envelope

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()

    def to_payload(self) -> dict:
        return json.loads(self._material)


def build_projection_only_synthetic_material_bundle(
    dataset: ProjectionMockDataset,
) -> ProjectionOnlySyntheticMaterialBundle:
    """Translate one validated synthetic dataset atomically through S1-S7."""
    if not isinstance(dataset, ProjectionMockDataset):
        raise TypeError("dataset must be a validated ProjectionMockDataset")

    stage6 = _build_synthetic_stage6(dataset)
    stage5 = stage6.stage5
    stage4 = stage5.stage4
    stage3 = stage4.stage3
    foundation = stage3.foundation

    try:
        envelope = build_projection_material_envelope(
            preparation=stage4.finance_quality_preparation,
            criteria_manifest=stage4.criteria_manifest,
            treasury_support=stage5.treasury_support,
            treasury_assessment=stage5.treasury_assessment,
            treasury_mandate=stage5.treasury_mandate,
            treasury_review=stage5.treasury_review,
            flow_record=stage6.flow_record,
            flow_mandate=stage6.flow_mandate,
            flow_review=stage6.flow_review,
        )
    except (TypeError, ValueError) as exc:
        raise SyntheticSemanticAdapterError(
            "ENVELOPE_REJECTED", "S7", str(exc),
        ) from exc

    envelope_payload = envelope.to_payload()
    if not envelope_payload["recomputed_membership"]["contains_synthetic_material"]:
        raise SyntheticSemanticAdapterError(
            "SYNTHETIC_NATURE_REJECTED", "S7",
            "final envelope must preserve synthetic material nature",
        )

    dataset_payload = dataset.to_payload()
    intermediate_fingerprints = {
        "finance_package": foundation.finance_package.fingerprint,
        "payment_capture": stage3.payment_capture.fingerprint,
        "required_installment_calendar_payload": _payload_hash(
            stage3.required_installment_calendar.model_dump(mode="json")
        ),
        "required_installment_coverage": stage3.required_installment_coverage.fingerprint,
        "finance_quality_preparation": stage4.finance_quality_preparation.fingerprint,
        "criteria_manifest": stage4.criteria_manifest.fingerprint,
        "treasury_support": stage5.treasury_support.fingerprint,
        "treasury_assessment": stage5.treasury_assessment.fingerprint,
        "treasury_mandate": stage5.treasury_mandate.fingerprint,
        "treasury_review": stage5.treasury_review.fingerprint,
        "flow_record": stage6.flow_record.fingerprint,
        "flow_mandate": stage6.flow_mandate.fingerprint,
        "flow_review": stage6.flow_review.fingerprint,
    }
    material = _canonical({
        "schema_version": SCHEMA_VERSION,
        "profile": "PROJECTION_ONLY",
        "case_kind": "SYNTHETIC",
        "effect_scope": "NO_OPERATIONAL_EFFECT",
        "dataset_id": dataset_payload["dataset_id"],
        "dataset_fingerprint": dataset.fingerprint,
        "envelope_fingerprint": envelope.fingerprint,
        "intermediate_fingerprints": intermediate_fingerprints,
        "assurance_scope": "ATOMIC_SYNTHETIC_MATERIAL_TRANSLATION_ONLY",
    })

    result = object.__new__(ProjectionOnlySyntheticMaterialBundle)
    object.__setattr__(result, "_dataset_fingerprint", dataset.fingerprint)
    object.__setattr__(result, "_finance_package", foundation.finance_package)
    object.__setattr__(result, "_payment_capture", stage3.payment_capture)
    object.__setattr__(result, "_required_calendar", stage3.required_installment_calendar)
    object.__setattr__(result, "_required_coverage", stage3.required_installment_coverage)
    object.__setattr__(result, "_preparation", stage4.finance_quality_preparation)
    object.__setattr__(result, "_criteria_manifest", stage4.criteria_manifest)
    object.__setattr__(result, "_treasury_support", stage5.treasury_support)
    object.__setattr__(result, "_treasury_assessment", stage5.treasury_assessment)
    object.__setattr__(result, "_treasury_mandate", stage5.treasury_mandate)
    object.__setattr__(result, "_treasury_review", stage5.treasury_review)
    object.__setattr__(result, "_flow_record", stage6.flow_record)
    object.__setattr__(result, "_flow_mandate", stage6.flow_mandate)
    object.__setattr__(result, "_flow_review", stage6.flow_review)
    object.__setattr__(result, "_envelope", envelope)
    object.__setattr__(result, "_material", material)
    return result


__all__ = [
    "ProjectionOnlySyntheticMaterialBundle",
    "SCHEMA_VERSION",
    "SyntheticSemanticAdapterError",
    "build_projection_only_synthetic_material_bundle",
]
