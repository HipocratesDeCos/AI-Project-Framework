"""Private staged decoder for a future atomic synthetic semantic adapter."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from eios.finance.models import (
    CashFlow, ExternalLiquidityReference, FinanceBasicInput, FinancialSnapshot,
    WorkingCapitalInput,
)
from eios.parameters.center import (
    Configuration, ParameterConfigurationCenter, ParameterDefinition,
)
from .documentary_payment_capture import (
    DocumentaryLocator, DocumentaryMaterial, DocumentaryPaymentBinding,
    DocumentaryPaymentCapture, build_documentary_payment_capture,
)
from .finance_decision_input_package import (
    FinanceDecisionInputPackage, build_finance_decision_input_package,
)
from .finance_flow_completeness import (
    CapturedFlowAssessment, FinanceFlowCompletenessRecord, FlowInventoryCandidate,
    FlowInventoryLocator, FlowInventoryPerimeter,
    build_finance_flow_completeness_record,
)
from .finance_quality_preparation import (
    FinanceQualityPreparation, PresentedQualityCriteria,
    build_finance_quality_preparation,
)
from .flow_inventory_mandate import (
    FlowInventoryMandateVerification, FlowMandateLocator, FlowMandateObservation,
    build_flow_inventory_mandate_verification,
)
from .flow_inventory_review import (
    FlowInstallmentReviewFinding, FlowInventoryPersonalReview,
    FlowInventoryReviewFinding, build_flow_inventory_personal_review,
)
from .models import DecisionContext, Evidence, PurchaseOperation
from .projection_criteria_manifest import (
    AuthorizedProjectionCriterion, CriterionFunction, ProjectionCriteriaManifest,
    build_projection_criteria_manifest,
    validate_preparation_criteria_against_manifest,
)
from .projection_mock_dataset import ProjectionMockDataset
from .required_installment_coverage import (
    RequiredInstallment, RequiredInstallmentCalendar, RequiredInstallmentCoverage,
    check_required_installment_coverage,
)
from .treasury_contextual_assessment import (
    ContextualSupportLocator, TreasuryContextualAssessment,
    TreasuryContextualDeclaration, build_treasury_contextual_assessment,
)
from .treasury_documentary_support import (
    TreasuryDeclaration, TreasuryDocumentarySupport, TreasuryObservation,
    build_treasury_documentary_support,
)
from .treasury_mandate_verification import (
    MandateVerificationLocator, MandateVerificationObservation,
    TreasuryMandateVerification, build_treasury_mandate_verification,
)
from .treasury_personal_review import (
    TreasuryPersonalReview, TreasuryReviewFinding, build_treasury_personal_review,
)


class SyntheticSemanticAdapterError(ValueError):
    """Stable, non-documentary failure from one semantic component."""

    def __init__(self, code: str, component: str, message: str) -> None:
        self.code = code
        self.component = component
        super().__init__(f"{code} [{component}]: {message}")


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class _Purchase(_StrictModel):
    decision_id: str = Field(min_length=1)
    scenario_id: str = Field(min_length=1)
    article_id: str = Field(min_length=1)
    supplier_id: str = Field(min_length=1)
    quantity: str = Field(min_length=1)
    unit_price: str = Field(min_length=1)
    currency: Literal["EUR"]
    operation_date: str = Field(min_length=1)


class _Evidence(_StrictModel):
    evidence_id: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    source_ref: str = Field(min_length=1)
    captured_at: str = Field(min_length=1)
    state: Literal["DEMONSTRATED", "GAP"]
    demonstration_ref: str | None = None


class _Operation(_StrictModel):
    case_kind: Literal["SYNTHETIC"]
    purchase: _Purchase
    evidence: list[_Evidence]


class _Context(_StrictModel):
    case_kind: Literal["SYNTHETIC"]
    decision_id: str = Field(min_length=1)
    scenario_id: str = Field(min_length=1)
    rules_version: str = Field(min_length=1)
    parameters_version: str = Field(min_length=1)
    data_snapshot_id: str = Field(min_length=1)


class _ExternalLiquidity(_StrictModel):
    value: str = Field(min_length=1)
    unit: str = Field(min_length=1)
    source_ref: str = Field(min_length=1)


class _Snapshot(_StrictModel):
    company_scope: str = Field(min_length=1)
    as_of_date: str = Field(min_length=1)
    data_snapshot_id: str = Field(min_length=1)
    currency: str = Field(min_length=3, max_length=3)
    available_treasury: str | None = None
    treasury_evidence_ref: str | None = None
    external_liquidity: _ExternalLiquidity | None = None


class _Flow(_StrictModel):
    flow_id: str = Field(min_length=1)
    flow_type: Literal["PAYMENT", "COLLECTION"]
    amount: str | None = None
    currency: str | None = None
    due_date: str | None = None
    due_date_evidenced: bool
    source_ref: str | None = None
    evidence_state: Literal["DEMONSTRATED", "NOT_EVIDENCED", "CONFLICTING_DATA"]


class _WorkingCapital(_StrictModel):
    company_scope: str = Field(min_length=1)
    as_of_date: str = Field(min_length=1)
    currency: str = Field(min_length=3, max_length=3)
    current_assets: str | None = None
    current_liabilities: str | None = None
    assets_source_ref: str | None = None
    liabilities_source_ref: str | None = None


class _Finance(_StrictModel):
    case_kind: Literal["SYNTHETIC"]
    company_id: str = Field(min_length=1)
    effective_at: str = Field(min_length=1)
    snapshot: _Snapshot
    cash_flows: list[_Flow]
    horizon_days: int = Field(gt=0)
    treasury_minimum: str | None = None
    working_capital_input: _WorkingCapital | None = None


class _Definition(_StrictModel):
    parameter_id: str = Field(min_length=1)
    value_type: str | None = None
    unit: str | None = None
    restricted: bool


class _Configuration(_StrictModel):
    configuration_id: int = Field(gt=0)
    parameter_id: str = Field(min_length=1)
    company_id: str = Field(min_length=1)
    value: str = Field(min_length=1)
    value_type: str | None = None
    unit: str | None = None
    valid_from: str = Field(min_length=1)
    valid_to: str | None = None
    created_at: str = Field(min_length=1)
    updated_at: str = Field(min_length=1)


class _Parameters(_StrictModel):
    case_kind: Literal["SYNTHETIC"]
    requested_parameter_ids: list[str] = Field(min_length=1)
    definitions: list[_Definition] = Field(min_length=1)
    configurations: list[_Configuration] = Field(min_length=1)


class _DocumentLocator(_StrictModel):
    document_ref: str = Field(min_length=1)
    page: int = Field(gt=0)
    section: str = Field(min_length=1)


class _BinaryDocument(_StrictModel):
    document_ref: str = Field(min_length=1)
    content_base64: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class _PaymentBinding(_StrictModel):
    installment_ref: str = Field(min_length=1)
    flow_id: str = Field(min_length=1)
    locators: list[_DocumentLocator] = Field(min_length=1)


class _PaymentDocuments(_StrictModel):
    case_kind: Literal["SYNTHETIC"]
    operation_ref: str = Field(min_length=1)
    order_ref: str = Field(min_length=1)
    order_version: str = Field(min_length=1)
    confirmation_ref: str = Field(min_length=1)
    documents: list[_BinaryDocument]
    bindings: list[_PaymentBinding]


class _RequiredInstallment(_StrictModel):
    installment_ref: str = Field(min_length=1)
    sequence: int = Field(gt=0)
    amount: str = Field(min_length=1)
    currency: str = Field(min_length=1)
    due_date: str = Field(min_length=1)
    locators: list[_DocumentLocator] = Field(min_length=1)


class _RequiredInstallmentCalendar(_StrictModel):
    case_kind: Literal["SYNTHETIC"]
    declaration_ref: str = Field(min_length=1)
    authority_ref: str = Field(min_length=1)
    operation_ref: str = Field(min_length=1)
    order_ref: str = Field(min_length=1)
    order_version: str = Field(min_length=1)
    confirmation_ref: str = Field(min_length=1)
    total_due: str = Field(min_length=1)
    currency: str = Field(min_length=1)
    installments: list[_RequiredInstallment] = Field(min_length=1)


class _PresentedCriterion(_StrictModel):
    reference: str = Field(min_length=1)
    version: str = Field(min_length=1)
    content_base64: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class _AuthorizedCriterion(_StrictModel):
    function: CriterionFunction
    reference: str = Field(min_length=1)
    version: str = Field(min_length=1)
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class _CriteriaManifest(_StrictModel):
    manifest_ref: str = Field(min_length=1)
    manifest_version: str = Field(min_length=1)
    authority_ref: str = Field(min_length=1)
    authorized_at: str = Field(min_length=1)
    criteria: list[_AuthorizedCriterion] = Field(min_length=1)


class _ProjectionCriteria(_StrictModel):
    case_kind: Literal["SYNTHETIC"]
    presented_criteria: list[_PresentedCriterion] = Field(min_length=1)
    manifest: _CriteriaManifest


TreasuryCondition = Literal[
    "SOURCE_CORRESPONDENCE", "ECONOMIC_CUTOFF", "AMOUNT_SUPPORT",
    "AVAILABILITY", "RESTRICTIONS", "SOURCE_SUFFICIENCY",
]
MandateCondition = Literal[
    "PERSON_IDENTITY", "COMPANY_RELATION", "GRANTOR_AUTHORITY",
    "TREASURY_SCOPE", "VALIDITY_AND_KNOWN_CHANGES", "TARGET_CONTEXT_BINDING",
]


class _TreasuryDeclaration(_StrictModel):
    documentary_company: str | None
    currency: str | None
    economic_date: str | None
    available_amount: str | None
    locators: list[_DocumentLocator] = Field(min_length=1)


class _TreasuryObservation(_StrictModel):
    condition: TreasuryCondition
    outcome: Literal[
        "DECLARED_CONSISTENT", "DECLARED_INCONSISTENT", "NOT_ESTABLISHED",
    ]
    note: str = Field(min_length=1)
    locators: list[_DocumentLocator]


class _TreasurySupport(_StrictModel):
    record_ref: str = Field(min_length=1)
    target_company_scope: str = Field(min_length=1)
    case_kind: Literal["SYNTHETIC"]
    documents: list[_BinaryDocument] = Field(min_length=1)
    declaration: _TreasuryDeclaration
    observations: list[_TreasuryObservation]
    reviewer_ref: str | None
    reviewed_at: str | None


class _ContextualSupportLocator(_StrictModel):
    origin: Literal["TREASURY_SUPPORT", "ADDITIONAL_ASSESSMENT_MATERIAL"]
    document_ref: str = Field(min_length=1)
    page: int = Field(gt=0)
    section: str = Field(min_length=1)


class _TreasuryContextualDeclaration(_StrictModel):
    condition: TreasuryCondition
    criterion_reference: str = Field(min_length=1)
    criterion_version: str = Field(min_length=1)
    applicability: Literal["APPLIES", "DOES_NOT_APPLY", "NOT_DETERMINED"]
    applicability_reason: str = Field(min_length=1)
    necessity: Literal[
        "NECESSARY_FOR_DETERMINED_PROJECTION",
        "RELEVANT_NOT_NECESSARY",
        "NOT_DETERMINED",
    ]
    necessity_reason: str = Field(min_length=1)
    impact_reason: str = Field(min_length=1)
    support_assessment: Literal[
        "DECLARED_SUFFICIENT", "DECLARED_INSUFFICIENT", "NOT_ESTABLISHED",
    ]
    support_reason: str = Field(min_length=1)
    observation_conditions: list[TreasuryCondition]
    support_locators: list[_ContextualSupportLocator]


class _TreasuryAssessment(_StrictModel):
    assessment_ref: str = Field(min_length=1)
    declarations: list[_TreasuryContextualDeclaration]
    additional_documents: list[_BinaryDocument]
    additional_case_kind: Literal["SYNTHETIC"] | None
    reviewer_ref: str | None
    reviewed_at: str | None


class _TreasuryMaterial(_StrictModel):
    case_kind: Literal["SYNTHETIC"]
    support: _TreasurySupport
    assessment: _TreasuryAssessment


class _MandateLocator(_StrictModel):
    origin: Literal[
        "MANDATE_DOCUMENT", "CHANNEL_RECOGNITION_SUPPORT", "CONTRAST_SUPPORT",
    ]
    document_ref: str = Field(min_length=1)
    page: int = Field(gt=0)
    section: str = Field(min_length=1)


class _MandateObservation(_StrictModel):
    condition: MandateCondition
    outcome: Literal[
        "CONFIRMED_BY_CONTRAST", "NOT_CONFIRMED_BY_CONTRAST", "CONFLICT_REPORTED",
    ]
    note: str = Field(min_length=1)
    locators: list[_MandateLocator]


class _TreasuryMandate(_StrictModel):
    case_kind: Literal["SYNTHETIC"]
    verification_ref: str = Field(min_length=1)
    company_scope: str = Field(min_length=1)
    reviewer_ref: str = Field(min_length=1)
    mandate_ref: str = Field(min_length=1)
    target_review_ref: str = Field(min_length=1)
    verifier_ref: str = Field(min_length=1)
    verified_at: str = Field(min_length=1)
    channel_ref: str = Field(min_length=1)
    channel_kind: str = Field(min_length=1)
    recognition_basis: Literal["PREVIOUSLY_RECOGNIZED", "INDEPENDENTLY_SUPPORTED"]
    mandate_kind: Literal["SYNTHETIC"]
    mandate_documents: list[_BinaryDocument] = Field(min_length=1)
    channel_recognition_documents: list[_BinaryDocument] = Field(min_length=1)
    contrast_documents: list[_BinaryDocument] = Field(min_length=1)
    observations: list[_MandateObservation]


class _TreasuryReviewFinding(_StrictModel):
    condition: TreasuryCondition
    outcome: Literal["CONFIRMED_BY_REVIEW", "NOT_CONFIRMED", "CONFLICT_REPORTED"]
    note: str = Field(min_length=1)
    locators: list[_DocumentLocator]


class _TreasuryReview(_StrictModel):
    case_kind: Literal["SYNTHETIC"]
    review_ref: str = Field(min_length=1)
    reviewer_ref: str = Field(min_length=1)
    reviewed_at: str = Field(min_length=1)
    findings: list[_TreasuryReviewFinding]
    previous_review_ref: str | None


FlowAssessmentState = Literal["ESTABLISHED", "NOT_ESTABLISHED", "CONFLICTING"]
FlowHorizonRelevance = Literal[
    "WITHIN_HORIZON", "AFTER_HORIZON", "NON_FUTURE",
    "NOT_ESTABLISHED", "CONFLICTING",
]
FlowReviewCondition = Literal[
    "PERIMETER_COVERAGE", "SOURCE_COVERAGE", "CAPTURED_FLOW_COVERAGE",
    "UNMATCHED_CANDIDATES", "HORIZON_CLASSIFICATION", "FLOW_ATTRIBUTE_SUPPORT",
    "ECONOMIC_DUPLICATION", "PURCHASE_PAYMENT_COHERENCE",
    "CONFLICTS_AND_LIMITATIONS",
]
FlowMandateCondition = Literal[
    "PERSON_IDENTITY", "COMPANY_RELATION", "GRANTOR_AUTHORITY",
    "FLOW_INVENTORY_SCOPE", "VALIDITY_AND_KNOWN_CHANGES", "TARGET_RECORD_BINDING",
]


class _FlowInventoryLocator(_StrictModel):
    origin: Literal["FLOW_INVENTORY_MATERIAL", "PAYMENT_CAPTURE"]
    document_ref: str = Field(min_length=1)
    page: int = Field(gt=0)
    section: str = Field(min_length=1)


class _FlowInventoryPerimeter(_StrictModel):
    perimeter_ref: str = Field(min_length=1)
    description: str = Field(min_length=1)
    company_scope: str = Field(min_length=1)
    as_of_date: str = Field(min_length=1)
    horizon_end: str = Field(min_length=1)
    currency: str = Field(min_length=3, max_length=3)
    source_refs: list[str] = Field(min_length=1)
    coverage_declaration: Literal[
        "DECLARED_COMPLETE", "DECLARED_INCOMPLETE", "NOT_ESTABLISHED",
    ]
    coverage_reason: str = Field(min_length=1)
    limitations: list[str]


class _FlowInventoryCandidate(_StrictModel):
    candidate_ref: str = Field(min_length=1)
    perimeter_ref: str = Field(min_length=1)
    declared_flow_type: Literal["PAYMENT", "COLLECTION", "NOT_ESTABLISHED"]
    captured_flow_id: str | None
    amount_assessment: FlowAssessmentState
    currency_assessment: FlowAssessmentState
    due_date_assessment: FlowAssessmentState
    economic_membership_assessment: FlowAssessmentState
    horizon_relevance: FlowHorizonRelevance
    economic_identity_ref: str | None
    locators: list[_FlowInventoryLocator] = Field(min_length=1)
    note: str = Field(min_length=1)


class _CapturedFlowAssessment(_StrictModel):
    flow_id: str = Field(min_length=1)
    candidate_refs: list[str]
    amount_assessment: FlowAssessmentState
    currency_assessment: FlowAssessmentState
    due_date_assessment: FlowAssessmentState
    economic_membership_assessment: FlowAssessmentState
    duplication_assessment: Literal[
        "DECLARED_UNIQUE", "POSSIBLE_DUPLICATE", "CONFLICTING", "NOT_ESTABLISHED",
    ]
    horizon_relevance: FlowHorizonRelevance
    criterion_reference: str = Field(min_length=1)
    criterion_version: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    locators: list[_FlowInventoryLocator] = Field(min_length=1)


class _FlowInventory(_StrictModel):
    case_kind: Literal["SYNTHETIC"]
    record_ref: str = Field(min_length=1)
    perimeters: list[_FlowInventoryPerimeter] = Field(min_length=1)
    documents: list[_BinaryDocument]
    candidates: list[_FlowInventoryCandidate]
    flow_assessments: list[_CapturedFlowAssessment]
    presenter_ref: str | None
    presented_at: str | None


class _FlowMandateLocator(_StrictModel):
    origin: Literal[
        "MANDATE_DOCUMENT", "CHANNEL_RECOGNITION_SUPPORT", "CONTRAST_SUPPORT",
    ]
    document_ref: str = Field(min_length=1)
    page: int = Field(gt=0)
    section: str = Field(min_length=1)


class _FlowMandateObservation(_StrictModel):
    condition: FlowMandateCondition
    outcome: Literal[
        "CONFIRMED_BY_CONTRAST", "NOT_CONFIRMED_BY_CONTRAST", "CONFLICT_REPORTED",
    ]
    note: str = Field(min_length=1)
    locators: list[_FlowMandateLocator]


class _FlowMandate(_StrictModel):
    case_kind: Literal["SYNTHETIC"]
    verification_ref: str = Field(min_length=1)
    company_scope: str = Field(min_length=1)
    reviewer_ref: str = Field(min_length=1)
    mandate_ref: str = Field(min_length=1)
    target_review_ref: str = Field(min_length=1)
    verifier_ref: str = Field(min_length=1)
    verified_at: str = Field(min_length=1)
    channel_ref: str = Field(min_length=1)
    channel_kind: str = Field(min_length=1)
    recognition_basis: Literal["PREVIOUSLY_RECOGNIZED", "INDEPENDENTLY_SUPPORTED"]
    mandate_kind: Literal["SYNTHETIC"]
    mandate_documents: list[_BinaryDocument] = Field(min_length=1)
    channel_recognition_documents: list[_BinaryDocument] = Field(min_length=1)
    contrast_documents: list[_BinaryDocument] = Field(min_length=1)
    observations: list[_FlowMandateObservation]


class _FlowInstallmentFinding(_StrictModel):
    installment_ref: str = Field(min_length=1)
    outcome: Literal["CONFIRMED_BY_REVIEW", "NOT_CONFIRMED", "CONFLICT_REPORTED"]
    note: str = Field(min_length=1)
    locators: list[_FlowInventoryLocator]
    flow_ids: list[str]


class _FlowReviewFinding(_StrictModel):
    condition: FlowReviewCondition
    outcome: Literal["CONFIRMED_BY_REVIEW", "NOT_CONFIRMED", "CONFLICT_REPORTED"]
    note: str = Field(min_length=1)
    locators: list[_FlowInventoryLocator]
    perimeter_refs: list[str]
    candidate_refs: list[str]
    flow_ids: list[str]
    installment_findings: list[_FlowInstallmentFinding]


class _FlowReview(_StrictModel):
    case_kind: Literal["SYNTHETIC"]
    review_ref: str = Field(min_length=1)
    reviewer_ref: str = Field(min_length=1)
    reviewed_at: str = Field(min_length=1)
    findings: list[_FlowReviewFinding]
    previous_review_ref: str | None


def _decimal(value: str | None, field: str) -> Decimal | None:
    if value is None:
        return None
    try:
        result = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field} must be a decimal string") from exc
    if not result.is_finite():
        raise ValueError(f"{field} must be finite")
    return result


def _date(value: str, field: str) -> date:
    try:
        result = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO date") from exc
    if result.isoformat() != value:
        raise ValueError(f"{field} must use canonical ISO date form")
    return result


def _datetime(value: str, field: str) -> datetime:
    try:
        result = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO datetime") from exc
    if result.utcoffset() is None or result.isoformat() != value:
        raise ValueError(f"{field} must be canonical and timezone-aware")
    return result


def _verified_base64(
    content_base64: str, expected_sha256: str, field: str,
) -> bytes:
    try:
        content = base64.b64decode(content_base64, validate=True)
    except (ValueError, UnicodeEncodeError) as exc:
        raise ValueError(f"{field} must be strict standard base64") from exc
    canonical = base64.b64encode(content).decode("ascii")
    if canonical != content_base64:
        raise ValueError(f"{field} must use canonical base64 representation")
    if sha256(content).hexdigest() != expected_sha256:
        raise ValueError(f"{field} sha256 does not match decoded content")
    return content


def _verified_binary(document: _BinaryDocument, index: int) -> bytes:
    return _verified_base64(
        document.content_base64, document.sha256,
        f"documents[{index}].content_base64",
    )


def _documentary_materials(
    documents: list[_BinaryDocument], field: str,
) -> tuple[DocumentaryMaterial, ...]:
    return tuple(
        DocumentaryMaterial(
            document_ref=item.document_ref,
            content=_verified_base64(
                item.content_base64, item.sha256,
                f"{field}[{index}].content_base64",
            ),
        )
        for index, item in enumerate(documents)
    )


def _decode(dataset: ProjectionMockDataset, component: str, model):
    try:
        raw = json.loads(dataset.component_bytes(component).decode("utf-8"))
        return model.model_validate(raw)
    except (UnicodeDecodeError, json.JSONDecodeError, ValidationError) as exc:
        raise SyntheticSemanticAdapterError(
            "INVALID_COMPONENT", component, "strict semantic schema rejected",
        ) from exc


class _Catalogue:
    def __init__(self, definitions: dict[str, ParameterDefinition]) -> None:
        self._definitions = definitions

    def get_parameter(self, parameter_id: str) -> ParameterDefinition | None:
        return self._definitions.get(parameter_id)


class _Repository:
    def __init__(self, configurations: dict[str, Configuration]) -> None:
        self._configurations = configurations

    def get_at(self, company_id: str, parameter_id: str,
               effective_at: datetime) -> Configuration | None:
        configuration = self._configurations.get(parameter_id)
        if configuration is None or configuration.company_id != company_id:
            return None
        return configuration

    def get_current(self, company_id: str, parameter_id: str):
        raise RuntimeError("synthetic parameter repository is effective-date only")

    def get_history(self, company_id: str, parameter_id: str):
        raise RuntimeError("synthetic parameter repository exposes no history")

    def has_overlapping_configuration(self, *args):
        raise RuntimeError("synthetic parameter repository is read-only")

    def apply_change_atomically(self, request):
        raise RuntimeError("synthetic parameter repository is read-only")


class _DenyAuthorization:
    def can_modify(self, company_id: str, parameter_id: str, actor: str) -> bool:
        return False


@dataclass(frozen=True)
class _SyntheticFoundation:
    dataset_fingerprint: str
    purchase: PurchaseOperation
    context: DecisionContext
    evidence: tuple[Evidence, ...]
    finance_input: FinanceBasicInput
    finance_package: FinanceDecisionInputPackage


@dataclass(frozen=True)
class _SyntheticStage3:
    dataset_fingerprint: str
    foundation: _SyntheticFoundation
    payment_capture: DocumentaryPaymentCapture
    required_installment_calendar: RequiredInstallmentCalendar
    required_installment_coverage: RequiredInstallmentCoverage


@dataclass(frozen=True)
class _SyntheticStage4:
    dataset_fingerprint: str
    stage3: _SyntheticStage3
    finance_quality_preparation: FinanceQualityPreparation
    criteria_manifest: ProjectionCriteriaManifest


@dataclass(frozen=True)
class _SyntheticStage5:
    dataset_fingerprint: str
    stage4: _SyntheticStage4
    treasury_support: TreasuryDocumentarySupport
    treasury_assessment: TreasuryContextualAssessment
    treasury_mandate: TreasuryMandateVerification
    treasury_review: TreasuryPersonalReview


@dataclass(frozen=True)
class _SyntheticStage6:
    dataset_fingerprint: str
    stage5: _SyntheticStage5
    flow_record: FinanceFlowCompletenessRecord
    flow_mandate: FlowInventoryMandateVerification
    flow_review: FlowInventoryPersonalReview


def _build_synthetic_foundation(dataset: ProjectionMockDataset) -> _SyntheticFoundation:
    """Build private S1-S2 material; never return the future public bundle."""
    if not isinstance(dataset, ProjectionMockDataset):
        raise TypeError("dataset must be a validated ProjectionMockDataset")
    try:
        operation = _decode(dataset, "operation", _Operation)
        context_data = _decode(dataset, "decision_context", _Context)
        finance = _decode(dataset, "finance_input", _Finance)
        parameters = _decode(dataset, "parameter_resolutions", _Parameters)

        purchase = PurchaseOperation(
            **operation.purchase.model_dump(exclude={"quantity", "unit_price", "operation_date"}),
            quantity=_decimal(operation.purchase.quantity, "purchase.quantity"),
            unit_price=_decimal(operation.purchase.unit_price, "purchase.unit_price"),
            operation_date=_date(operation.purchase.operation_date, "purchase.operation_date"),
        )
        context = DecisionContext(**context_data.model_dump(exclude={"case_kind"}))
        evidence = tuple(Evidence(
            **item.model_dump(exclude={"captured_at"}),
            captured_at=_date(item.captured_at, "evidence.captured_at"),
        ) for item in operation.evidence)

        external = finance.snapshot.external_liquidity
        snapshot = FinancialSnapshot(
            **finance.snapshot.model_dump(exclude={"as_of_date", "available_treasury", "external_liquidity"}),
            as_of_date=_date(finance.snapshot.as_of_date, "snapshot.as_of_date"),
            available_treasury=_decimal(finance.snapshot.available_treasury, "snapshot.available_treasury"),
            external_liquidity=None if external is None else ExternalLiquidityReference(
                **external.model_dump(exclude={"value"}),
                value=_decimal(external.value, "external_liquidity.value")),
        )
        flows = tuple(CashFlow(
            **item.model_dump(exclude={"amount", "due_date"}),
            amount=_decimal(item.amount, f"cash_flows.{item.flow_id}.amount"),
            due_date=None if item.due_date is None else _date(
                item.due_date, f"cash_flows.{item.flow_id}.due_date"),
        ) for item in finance.cash_flows)
        working_data = finance.working_capital_input
        working = None if working_data is None else WorkingCapitalInput(
            **working_data.model_dump(exclude={"as_of_date", "current_assets", "current_liabilities"}),
            as_of_date=_date(working_data.as_of_date, "working_capital.as_of_date"),
            current_assets=_decimal(working_data.current_assets, "working_capital.current_assets"),
            current_liabilities=_decimal(working_data.current_liabilities, "working_capital.current_liabilities"),
        )
        finance_input = FinanceBasicInput(
            context=context, snapshot=snapshot, cash_flows=flows,
            horizon_days=finance.horizon_days,
            treasury_minimum=_decimal(finance.treasury_minimum, "treasury_minimum"),
            working_capital_input=working,
        )

        definition_ids = [item.parameter_id for item in parameters.definitions]
        configuration_ids = [item.parameter_id for item in parameters.configurations]
        requested_ids = list(parameters.requested_parameter_ids)
        if (len(set(requested_ids)) != len(requested_ids)
                or len(set(definition_ids)) != len(definition_ids)
                or len(set(configuration_ids)) != len(configuration_ids)
                or set(requested_ids) != set(definition_ids)
                or set(requested_ids) != set(configuration_ids)):
            raise ValueError("parameter inventory must be exact and unique")
        definitions = {item.parameter_id: ParameterDefinition(**item.model_dump())
                       for item in parameters.definitions}
        configurations = {item.parameter_id: Configuration(
            **item.model_dump(exclude={"valid_from", "valid_to", "created_at", "updated_at"}),
            valid_from=_datetime(item.valid_from, "configuration.valid_from"),
            valid_to=None if item.valid_to is None else _datetime(item.valid_to, "configuration.valid_to"),
            created_at=_datetime(item.created_at, "configuration.created_at"),
            updated_at=_datetime(item.updated_at, "configuration.updated_at"),
        ) for item in parameters.configurations}
        center = ParameterConfigurationCenter(
            _Catalogue(definitions), _DenyAuthorization(), _Repository(configurations))
        package = build_finance_decision_input_package(
            purchase=purchase, context=context, evidence=evidence,
            finance_input=finance_input, company_id=finance.company_id,
            effective_at=_datetime(finance.effective_at, "effective_at"),
            requested_parameter_ids=tuple(parameters.requested_parameter_ids), center=center,
        )
    except SyntheticSemanticAdapterError:
        raise
    except (TypeError, ValueError) as exc:
        raise SyntheticSemanticAdapterError(
            "FOUNDATION_REJECTED", "S1-S2", str(exc)) from exc
    return _SyntheticFoundation(dataset.fingerprint, purchase, context, evidence,
                                finance_input, package)


def _build_synthetic_stage3(dataset: ProjectionMockDataset) -> _SyntheticStage3:
    """Build private S1-S3 material without exposing a partial public bundle."""
    foundation = _build_synthetic_foundation(dataset)
    payment_data = _decode(dataset, "payment_documents", _PaymentDocuments)
    calendar_data = _decode(
        dataset, "required_installment_calendar", _RequiredInstallmentCalendar)

    try:
        documents = tuple(
            DocumentaryMaterial(
                document_ref=item.document_ref,
                content=_verified_binary(item, index),
            )
            for index, item in enumerate(payment_data.documents)
        )
        bindings = tuple(
            DocumentaryPaymentBinding(
                installment_ref=item.installment_ref,
                flow_id=item.flow_id,
                locators=tuple(
                    DocumentaryLocator(**locator.model_dump())
                    for locator in item.locators
                ),
            )
            for item in payment_data.bindings
        )
        capture = build_documentary_payment_capture(
            package=foundation.finance_package,
            documents=documents,
            bindings=bindings,
            case_kind=payment_data.case_kind,
            operation_ref=payment_data.operation_ref,
            order_ref=payment_data.order_ref,
            order_version=payment_data.order_version,
            confirmation_ref=payment_data.confirmation_ref,
            external_review_ref=None,
        )
    except (TypeError, ValueError, ValidationError) as exc:
        raise SyntheticSemanticAdapterError(
            "PAYMENT_CAPTURE_REJECTED", "payment_documents", str(exc)) from exc

    try:
        calendar = RequiredInstallmentCalendar(
            declaration_ref=calendar_data.declaration_ref,
            authority_ref=calendar_data.authority_ref,
            case_kind=calendar_data.case_kind,
            operation_ref=calendar_data.operation_ref,
            order_ref=calendar_data.order_ref,
            order_version=calendar_data.order_version,
            confirmation_ref=calendar_data.confirmation_ref,
            total_due=_decimal(calendar_data.total_due, "required_calendar.total_due"),
            currency=calendar_data.currency,
            installments=tuple(
                RequiredInstallment(
                    installment_ref=item.installment_ref,
                    sequence=item.sequence,
                    amount=_decimal(
                        item.amount,
                        f"required_calendar.{item.installment_ref}.amount",
                    ),
                    currency=item.currency,
                    due_date=_date(
                        item.due_date,
                        f"required_calendar.{item.installment_ref}.due_date",
                    ),
                    locators=tuple(
                        DocumentaryLocator(**locator.model_dump())
                        for locator in item.locators
                    ),
                )
                for item in calendar_data.installments
            ),
        )
    except (TypeError, ValueError, ValidationError) as exc:
        raise SyntheticSemanticAdapterError(
            "INSTALLMENT_CALENDAR_REJECTED",
            "required_installment_calendar",
            str(exc),
        ) from exc

    try:
        coverage = check_required_installment_coverage(
            capture=capture, calendar=calendar)
    except (TypeError, ValueError, ValidationError) as exc:
        raise SyntheticSemanticAdapterError(
            "PAYMENT_COVERAGE_REJECTED", "S3", str(exc)) from exc

    return _SyntheticStage3(
        dataset_fingerprint=dataset.fingerprint,
        foundation=foundation,
        payment_capture=capture,
        required_installment_calendar=calendar,
        required_installment_coverage=coverage,
    )


def _build_synthetic_stage4(dataset: ProjectionMockDataset) -> _SyntheticStage4:
    """Build private S1-S4 material without evaluating any quality criterion."""
    stage3 = _build_synthetic_stage3(dataset)
    criteria_data = _decode(dataset, "projection_criteria", _ProjectionCriteria)

    try:
        presented = tuple(
            PresentedQualityCriteria(
                reference=item.reference,
                version=item.version,
                content=_verified_base64(
                    item.content_base64,
                    item.sha256,
                    f"presented_criteria[{index}].content_base64",
                ),
            )
            for index, item in enumerate(criteria_data.presented_criteria)
        )
        preparation = build_finance_quality_preparation(
            capture=stage3.payment_capture,
            calendar=stage3.required_installment_calendar,
            coverage=stage3.required_installment_coverage,
            criteria=presented,
            review=None,
            designation=None,
        )
    except (TypeError, ValueError, ValidationError) as exc:
        raise SyntheticSemanticAdapterError(
            "CRITERIA_PREPARATION_REJECTED", "projection_criteria", str(exc),
        ) from exc

    manifest_data = criteria_data.manifest
    try:
        manifest = build_projection_criteria_manifest(
            manifest_ref=manifest_data.manifest_ref,
            manifest_version=manifest_data.manifest_version,
            authority_ref=manifest_data.authority_ref,
            authorized_at=_datetime(
                manifest_data.authorized_at, "criteria_manifest.authorized_at"),
            criteria=tuple(
                AuthorizedProjectionCriterion(
                    function=item.function,
                    reference=item.reference,
                    version=item.version,
                    content_sha256=item.content_sha256,
                )
                for item in manifest_data.criteria
            ),
        )
    except (TypeError, ValueError, ValidationError) as exc:
        raise SyntheticSemanticAdapterError(
            "CRITERIA_MANIFEST_REJECTED", "projection_criteria", str(exc),
        ) from exc

    try:
        validate_preparation_criteria_against_manifest(preparation, manifest)
    except (TypeError, ValueError) as exc:
        raise SyntheticSemanticAdapterError(
            "CRITERIA_BINDING_REJECTED", "S4", str(exc),
        ) from exc

    return _SyntheticStage4(
        dataset_fingerprint=dataset.fingerprint,
        stage3=stage3,
        finance_quality_preparation=preparation,
        criteria_manifest=manifest,
    )


def _build_synthetic_stage5(dataset: ProjectionMockDataset) -> _SyntheticStage5:
    """Build private S1-S5 treasury material without evaluating quality."""
    stage4 = _build_synthetic_stage4(dataset)
    material_data = _decode(dataset, "treasury_material", _TreasuryMaterial)
    mandate_data = _decode(dataset, "treasury_mandate", _TreasuryMandate)
    review_data = _decode(dataset, "treasury_review", _TreasuryReview)

    support_data = material_data.support
    try:
        support = build_treasury_documentary_support(
            preparation=stage4.finance_quality_preparation,
            record_ref=support_data.record_ref,
            target_company_scope=support_data.target_company_scope,
            case_kind=support_data.case_kind,
            documents=_documentary_materials(
                support_data.documents, "treasury_support.documents"),
            declaration=TreasuryDeclaration(
                documentary_company=support_data.declaration.documentary_company,
                currency=support_data.declaration.currency,
                economic_date=None if support_data.declaration.economic_date is None
                    else _date(
                        support_data.declaration.economic_date,
                        "treasury_support.declaration.economic_date",
                    ),
                available_amount=_decimal(
                    support_data.declaration.available_amount,
                    "treasury_support.declaration.available_amount",
                ),
                locators=tuple(
                    DocumentaryLocator(**locator.model_dump())
                    for locator in support_data.declaration.locators
                ),
            ),
            observations=tuple(
                TreasuryObservation(
                    condition=item.condition,
                    outcome=item.outcome,
                    note=item.note,
                    locators=tuple(
                        DocumentaryLocator(**locator.model_dump())
                        for locator in item.locators
                    ),
                )
                for item in support_data.observations
            ),
            reviewer_ref=support_data.reviewer_ref,
            reviewed_at=None if support_data.reviewed_at is None else _datetime(
                support_data.reviewed_at, "treasury_support.reviewed_at"),
        )
    except (TypeError, ValueError, ValidationError) as exc:
        raise SyntheticSemanticAdapterError(
            "TREASURY_SUPPORT_REJECTED", "treasury_material", str(exc),
        ) from exc

    assessment_data = material_data.assessment
    manifest_entries = stage4.criteria_manifest.to_payload()["criteria"]
    treasury_entry = next(
        item for item in manifest_entries
        if item["function"] == "INITIAL_TREASURY_SUFFICIENCY"
    )
    try:
        for item in assessment_data.declarations:
            if (item.criterion_reference, item.criterion_version) != (
                treasury_entry["reference"], treasury_entry["version"]):
                raise ValueError(
                    "Treasury declaration must use INITIAL_TREASURY_SUFFICIENCY criterion")
        assessment = build_treasury_contextual_assessment(
            preparation=stage4.finance_quality_preparation,
            treasury_support=support,
            assessment_ref=assessment_data.assessment_ref,
            declarations=tuple(
                TreasuryContextualDeclaration(
                    condition=item.condition,
                    criterion_reference=item.criterion_reference,
                    criterion_version=item.criterion_version,
                    applicability=item.applicability,
                    applicability_reason=item.applicability_reason,
                    necessity=item.necessity,
                    necessity_reason=item.necessity_reason,
                    impact_reason=item.impact_reason,
                    support_assessment=item.support_assessment,
                    support_reason=item.support_reason,
                    observation_conditions=tuple(item.observation_conditions),
                    support_locators=tuple(
                        ContextualSupportLocator(**locator.model_dump())
                        for locator in item.support_locators
                    ),
                )
                for item in assessment_data.declarations
            ),
            additional_documents=_documentary_materials(
                assessment_data.additional_documents,
                "treasury_assessment.additional_documents",
            ),
            additional_case_kind=assessment_data.additional_case_kind,
            reviewer_ref=assessment_data.reviewer_ref,
            reviewed_at=None if assessment_data.reviewed_at is None else _datetime(
                assessment_data.reviewed_at, "treasury_assessment.reviewed_at"),
        )
    except (TypeError, ValueError, ValidationError) as exc:
        raise SyntheticSemanticAdapterError(
            "TREASURY_ASSESSMENT_REJECTED", "treasury_material", str(exc),
        ) from exc

    try:
        mandate = build_treasury_mandate_verification(
            target=assessment,
            verification_ref=mandate_data.verification_ref,
            company_scope=mandate_data.company_scope,
            reviewer_ref=mandate_data.reviewer_ref,
            mandate_ref=mandate_data.mandate_ref,
            target_review_ref=mandate_data.target_review_ref,
            verifier_ref=mandate_data.verifier_ref,
            verified_at=_datetime(
                mandate_data.verified_at, "treasury_mandate.verified_at"),
            channel_ref=mandate_data.channel_ref,
            channel_kind=mandate_data.channel_kind,
            recognition_basis=mandate_data.recognition_basis,
            mandate_kind=mandate_data.mandate_kind,
            mandate_documents=_documentary_materials(
                mandate_data.mandate_documents,
                "treasury_mandate.mandate_documents",
            ),
            channel_recognition_documents=_documentary_materials(
                mandate_data.channel_recognition_documents,
                "treasury_mandate.channel_recognition_documents",
            ),
            contrast_documents=_documentary_materials(
                mandate_data.contrast_documents,
                "treasury_mandate.contrast_documents",
            ),
            observations=tuple(
                MandateVerificationObservation(
                    condition=item.condition,
                    outcome=item.outcome,
                    note=item.note,
                    locators=tuple(
                        MandateVerificationLocator(**locator.model_dump())
                        for locator in item.locators
                    ),
                )
                for item in mandate_data.observations
            ),
        )
    except (TypeError, ValueError, ValidationError) as exc:
        raise SyntheticSemanticAdapterError(
            "TREASURY_MANDATE_REJECTED", "treasury_mandate", str(exc),
        ) from exc

    try:
        review = build_treasury_personal_review(
            assessment=assessment,
            mandate=mandate,
            review_ref=review_data.review_ref,
            reviewer_ref=review_data.reviewer_ref,
            reviewed_at=_datetime(
                review_data.reviewed_at, "treasury_review.reviewed_at"),
            findings=tuple(
                TreasuryReviewFinding(
                    condition=item.condition,
                    outcome=item.outcome,
                    note=item.note,
                    locators=tuple(
                        DocumentaryLocator(**locator.model_dump())
                        for locator in item.locators
                    ),
                )
                for item in review_data.findings
            ),
            previous_review_ref=review_data.previous_review_ref,
        )
    except (TypeError, ValueError, ValidationError) as exc:
        raise SyntheticSemanticAdapterError(
            "TREASURY_REVIEW_REJECTED", "treasury_review", str(exc),
        ) from exc

    return _SyntheticStage5(
        dataset_fingerprint=dataset.fingerprint,
        stage4=stage4,
        treasury_support=support,
        treasury_assessment=assessment,
        treasury_mandate=mandate,
        treasury_review=review,
    )


def _build_synthetic_stage6(dataset: ProjectionMockDataset) -> _SyntheticStage6:
    """Build private S1-S6 flow material without evaluating quality."""
    stage5 = _build_synthetic_stage5(dataset)
    inventory_data = _decode(dataset, "flow_inventory", _FlowInventory)
    mandate_data = _decode(dataset, "flow_mandate", _FlowMandate)
    review_data = _decode(dataset, "flow_review", _FlowReview)

    def flow_locator(item: _FlowInventoryLocator) -> FlowInventoryLocator:
        return FlowInventoryLocator(**item.model_dump())

    try:
        record = build_finance_flow_completeness_record(
            preparation=stage5.stage4.finance_quality_preparation,
            record_ref=inventory_data.record_ref,
            perimeters=tuple(
                FlowInventoryPerimeter(
                    perimeter_ref=item.perimeter_ref,
                    description=item.description,
                    company_scope=item.company_scope,
                    as_of_date=_date(
                        item.as_of_date,
                        f"flow_inventory.{item.perimeter_ref}.as_of_date",
                    ),
                    horizon_end=_date(
                        item.horizon_end,
                        f"flow_inventory.{item.perimeter_ref}.horizon_end",
                    ),
                    currency=item.currency,
                    source_refs=tuple(item.source_refs),
                    coverage_declaration=item.coverage_declaration,
                    coverage_reason=item.coverage_reason,
                    limitations=tuple(item.limitations),
                )
                for item in inventory_data.perimeters
            ),
            documents=_documentary_materials(
                inventory_data.documents, "flow_inventory.documents"),
            candidates=tuple(
                FlowInventoryCandidate(
                    candidate_ref=item.candidate_ref,
                    perimeter_ref=item.perimeter_ref,
                    declared_flow_type=item.declared_flow_type,
                    captured_flow_id=item.captured_flow_id,
                    amount_assessment=item.amount_assessment,
                    currency_assessment=item.currency_assessment,
                    due_date_assessment=item.due_date_assessment,
                    economic_membership_assessment=item.economic_membership_assessment,
                    horizon_relevance=item.horizon_relevance,
                    economic_identity_ref=item.economic_identity_ref,
                    locators=tuple(flow_locator(locator) for locator in item.locators),
                    note=item.note,
                )
                for item in inventory_data.candidates
            ),
            flow_assessments=tuple(
                CapturedFlowAssessment(
                    flow_id=item.flow_id,
                    candidate_refs=tuple(item.candidate_refs),
                    amount_assessment=item.amount_assessment,
                    currency_assessment=item.currency_assessment,
                    due_date_assessment=item.due_date_assessment,
                    economic_membership_assessment=item.economic_membership_assessment,
                    duplication_assessment=item.duplication_assessment,
                    horizon_relevance=item.horizon_relevance,
                    criterion_reference=item.criterion_reference,
                    criterion_version=item.criterion_version,
                    reason=item.reason,
                    locators=tuple(flow_locator(locator) for locator in item.locators),
                )
                for item in inventory_data.flow_assessments
            ),
            case_kind=inventory_data.case_kind,
            presenter_ref=inventory_data.presenter_ref,
            presented_at=None if inventory_data.presented_at is None else _datetime(
                inventory_data.presented_at, "flow_inventory.presented_at"),
        )
    except (TypeError, ValueError, ValidationError) as exc:
        raise SyntheticSemanticAdapterError(
            "FLOW_INVENTORY_REJECTED", "flow_inventory", str(exc),
        ) from exc

    try:
        mandate = build_flow_inventory_mandate_verification(
            target=record,
            verification_ref=mandate_data.verification_ref,
            company_scope=mandate_data.company_scope,
            reviewer_ref=mandate_data.reviewer_ref,
            mandate_ref=mandate_data.mandate_ref,
            target_review_ref=mandate_data.target_review_ref,
            verifier_ref=mandate_data.verifier_ref,
            verified_at=_datetime(
                mandate_data.verified_at, "flow_mandate.verified_at"),
            channel_ref=mandate_data.channel_ref,
            channel_kind=mandate_data.channel_kind,
            recognition_basis=mandate_data.recognition_basis,
            mandate_kind=mandate_data.mandate_kind,
            mandate_documents=_documentary_materials(
                mandate_data.mandate_documents,
                "flow_mandate.mandate_documents",
            ),
            channel_recognition_documents=_documentary_materials(
                mandate_data.channel_recognition_documents,
                "flow_mandate.channel_recognition_documents",
            ),
            contrast_documents=_documentary_materials(
                mandate_data.contrast_documents,
                "flow_mandate.contrast_documents",
            ),
            observations=tuple(
                FlowMandateObservation(
                    condition=item.condition,
                    outcome=item.outcome,
                    note=item.note,
                    locators=tuple(
                        FlowMandateLocator(**locator.model_dump())
                        for locator in item.locators
                    ),
                )
                for item in mandate_data.observations
            ),
        )
    except (TypeError, ValueError, ValidationError) as exc:
        raise SyntheticSemanticAdapterError(
            "FLOW_MANDATE_REJECTED", "flow_mandate", str(exc),
        ) from exc

    try:
        review = build_flow_inventory_personal_review(
            target=record,
            mandate=mandate,
            review_ref=review_data.review_ref,
            reviewer_ref=review_data.reviewer_ref,
            reviewed_at=_datetime(
                review_data.reviewed_at, "flow_review.reviewed_at"),
            findings=tuple(
                FlowInventoryReviewFinding(
                    condition=item.condition,
                    outcome=item.outcome,
                    note=item.note,
                    locators=tuple(
                        flow_locator(locator) for locator in item.locators),
                    perimeter_refs=tuple(item.perimeter_refs),
                    candidate_refs=tuple(item.candidate_refs),
                    flow_ids=tuple(item.flow_ids),
                    installment_findings=tuple(
                        FlowInstallmentReviewFinding(
                            installment_ref=installment.installment_ref,
                            outcome=installment.outcome,
                            note=installment.note,
                            locators=tuple(
                                flow_locator(locator)
                                for locator in installment.locators
                            ),
                            flow_ids=tuple(installment.flow_ids),
                        )
                        for installment in item.installment_findings
                    ),
                )
                for item in review_data.findings
            ),
            previous_review_ref=review_data.previous_review_ref,
        )
    except (TypeError, ValueError, ValidationError) as exc:
        raise SyntheticSemanticAdapterError(
            "FLOW_REVIEW_REJECTED", "flow_review", str(exc),
        ) from exc

    return _SyntheticStage6(
        dataset_fingerprint=dataset.fingerprint,
        stage5=stage5,
        flow_record=record,
        flow_mandate=mandate,
        flow_review=review,
    )


__all__: tuple[str, ...] = ()
