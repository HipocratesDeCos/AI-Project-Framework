from datetime import date
from decimal import Decimal
from inspect import signature

import pytest

from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.mvp_execution import run_mvp_execution
from eios.core.orchestration import O1ExecutionStatus
from eios.core.price_integration import build_provenanced_price_invoker
from eios.pricing.models import PriceIntelligenceAssessmentContext, PriceIntelligenceInput
from eios.pricing.sufficiency import SufficiencyObservation


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-PRICE-CTX",
        scenario_id="S-PRICE-CTX",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-PRICE-CTX",
        scenario_id="S-PRICE-CTX",
        article_id="ART-1",
        supplier_id="SUP-1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=date(2026, 9, 12),
    )


def _payload() -> PriceIntelligenceInput:
    return PriceIntelligenceInput(
        decision_context=_context(),
        purchase_operation=_purchase(),
        references=(),
        evidence_validations=(),
        normalization_basis=None,
        economic_basis_evidence=(),
        methodology_version="price-v1",
    )


def _assessment_context() -> PriceIntelligenceAssessmentContext:
    return PriceIntelligenceAssessmentContext(
        sufficiency=SufficiencyObservation(),
    )


def _invoker():
    return build_provenanced_price_invoker(
        payload=_payload(),
        assessment_context=_assessment_context(),
    )


def test_matching_full_price_input_executes_through_invoker() -> None:
    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-PRICE-CTX-1",
        price_invoker=_invoker(),
    )

    capability = outcome.capability_results[0]
    assert capability.capability == "PRICE"
    assert capability.status == O1ExecutionStatus.NOT_EVALUABLE
    assert capability.result_available is False
    assert capability.unresolved_items == ("PRICE_NOT_JUSTIFIABLE",)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("decision_id", "D-OTHER"),
        ("scenario_id", "S-OTHER"),
        ("rules_version", "rules-other"),
        ("parameters_version", "params-other"),
        ("data_snapshot_id", "snapshot-other"),
    ),
)
def test_price_invoker_rejects_any_foreign_decision_context_field(
    field: str,
    value: str,
) -> None:
    foreign = _context().model_copy(update={field: value})

    with pytest.raises(ValueError, match=field):
        _invoker()(_purchase(), foreign)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("article_id", "ART-OTHER"),
        ("supplier_id", "SUP-OTHER"),
        ("quantity", Decimal("11")),
        ("unit_price", Decimal("6")),
        ("operation_date", date(2026, 9, 11)),
    ),
)
def test_price_invoker_rejects_foreign_purchase_even_when_ids_match(
    field: str,
    value,
) -> None:
    foreign = _purchase().model_copy(update={field: value})

    with pytest.raises(ValueError, match=field):
        _invoker()(foreign, _context())


def test_price_invoker_freezes_complete_input_snapshot() -> None:
    payload = _payload()
    invoker = build_provenanced_price_invoker(
        payload=payload,
        assessment_context=_assessment_context(),
    )

    payload.purchase_operation.article_id = "MUTATED-LATER"
    payload.decision_context.parameters_version = "MUTATED-LATER"

    capability = invoker(_purchase(), _context())

    assert capability.capability == "PRICE"
    assert capability.status == O1ExecutionStatus.NOT_EVALUABLE


def test_price_builder_requires_typed_physical_inputs() -> None:
    with pytest.raises(TypeError, match="PriceIntelligenceInput"):
        build_provenanced_price_invoker(
            payload=object(),
            assessment_context=_assessment_context(),
        )

    with pytest.raises(TypeError, match="PriceIntelligenceAssessmentContext"):
        build_provenanced_price_invoker(
            payload=_payload(),
            assessment_context=object(),
        )


def test_mvp_execution_public_signature_has_no_detached_price_result() -> None:
    parameters = signature(run_mvp_execution).parameters

    assert "price_result" not in parameters
    assert "price_invoker" in parameters


def test_old_price_result_keyword_is_rejected() -> None:
    with pytest.raises(TypeError, match="price_result"):
        run_mvp_execution(
            purchase=_purchase(),
            context=_context(),
            policy_version="MVP-PRICE-CTX-1",
            price_result=object(),
        )
