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
from .models import DecisionContext, Evidence, PurchaseOperation
from .projection_mock_dataset import ProjectionMockDataset
from .required_installment_coverage import (
    RequiredInstallment, RequiredInstallmentCalendar, RequiredInstallmentCoverage,
    check_required_installment_coverage,
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


class _PaymentDocument(_StrictModel):
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
    external_review_ref: str | None
    documents: list[_PaymentDocument]
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


def _verified_binary(document: _PaymentDocument, index: int) -> bytes:
    field = f"documents[{index}].content_base64"
    try:
        content = base64.b64decode(document.content_base64, validate=True)
    except (ValueError, UnicodeEncodeError) as exc:
        raise ValueError(f"{field} must be strict standard base64") from exc
    canonical = base64.b64encode(content).decode("ascii")
    if canonical != document.content_base64:
        raise ValueError(f"{field} must use canonical base64 representation")
    if sha256(content).hexdigest() != document.sha256:
        raise ValueError(f"documents[{index}].sha256 does not match decoded content")
    return content


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
            external_review_ref=payment_data.external_review_ref,
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


__all__: tuple[str, ...] = ()
