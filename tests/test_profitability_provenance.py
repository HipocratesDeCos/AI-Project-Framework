from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from eios.core.models import DecisionContext, PurchaseOperation
from eios.profitability import (
    AuthorizedCostBasis,
    AuthorizedSaleBasis,
    ProfitabilityInput,
    ProfitabilityProvenanceError,
    ProvenancedProfitabilityExecution,
    calculate_profitability,
    run_provenanced_profitability,
    validate_provenanced_profitability_execution,
)


EVAL_DATE = date(2026, 9, 20)


def _context():
    return DecisionContext(
        decision_id="DEC-MGE-PROV-001",
        scenario_id="SCN-MGE-PROV-001",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snap-v1",
    )


def _purchase():
    return PurchaseOperation(
        decision_id="DEC-MGE-PROV-001",
        scenario_id="SCN-MGE-PROV-001",
        article_id="ART-001",
        supplier_id="SUP-001",
        quantity=Decimal("10"),
        unit_price=Decimal("5.0000"),
        currency="EUR",
        operation_date=EVAL_DATE,
    )


def _basis_common():
    return dict(
        state="KNOWN",
        decision_id="DEC-MGE-PROV-001",
        scenario_id="SCN-MGE-PROV-001",
        data_snapshot_id="snap-v1",
        company_scope="COMPANY-A",
        article_id="ART-001",
        evaluation_date=EVAL_DATE,
        currency="EUR",
        economic_basis_ref="BASIS:UNIT",
        authority_ref="MGE-AUTH-v0.1",
    )


def _sale():
    return AuthorizedSaleBasis(
        **_basis_common(),
        value=Decimal("100.0000"),
        source_ref="SALE-SRC-001",
        trace_refs=("TRACE-SALE",),
    )


def _cost():
    return AuthorizedCostBasis(
        **_basis_common(),
        value=Decimal("70.0000"),
        source_ref="COST-SRC-001",
        trace_refs=("TRACE-COST",),
    )


def _payload():
    return ProfitabilityInput(
        context=_context(),
        purchase_operation=_purchase(),
        company_scope="COMPANY-A",
        evaluation_date=EVAL_DATE,
        sale_basis=_sale(),
        cost_basis=_cost(),
        methodology_version="MGE-AUTH-v0.1",
    )


def test_provenanced_execution_matches_exact_core_result():
    payload = _payload()

    execution = run_provenanced_profitability(payload)

    assert type(execution) is ProvenancedProfitabilityExecution
    assert execution.profitability_result == calculate_profitability(
        execution.profitability_input
    )
    assert execution.profitability_result.margin_amount == Decimal("30.0000")
    assert execution.profitability_result.margin_percentage == Decimal("30.0")


def test_factory_reconstructs_deep_snapshot():
    payload = _payload()

    execution = run_provenanced_profitability(payload)

    assert execution.profitability_input is not payload
    assert execution.profitability_input.context is not payload.context
    assert execution.profitability_input.purchase_operation is not payload.purchase_operation
    assert execution.profitability_input.sale_basis is not payload.sale_basis
    assert execution.profitability_input.cost_basis is not payload.cost_basis


def test_external_nested_mutation_after_run_does_not_change_execution():
    payload = _payload()
    execution = run_provenanced_profitability(payload)

    payload.context.decision_id = "DEC-MUTATED"
    payload.purchase_operation.article_id = "ART-MUTATED"
    object.__setattr__(payload.sale_basis, "value", Decimal("999"))

    assert execution.profitability_input.context.decision_id == "DEC-MGE-PROV-001"
    assert execution.profitability_input.purchase_operation.article_id == "ART-001"
    assert execution.profitability_input.sale_basis.value == Decimal("100.0000")
    validate_provenanced_profitability_execution(execution)


def test_validator_accepts_valid_execution():
    execution = run_provenanced_profitability(_payload())

    validate_provenanced_profitability_execution(execution)


def test_factory_rejects_wrong_input_type():
    with pytest.raises(TypeError, match="ProfitabilityInput"):
        run_provenanced_profitability(object())


def test_validator_rejects_wrong_execution_type():
    with pytest.raises(TypeError, match="ProvenancedProfitabilityExecution"):
        validate_provenanced_profitability_execution(object())


def test_validator_rejects_tampered_result():
    execution = run_provenanced_profitability(_payload())
    tampered = execution.profitability_result.model_copy(
        update={"margin_amount": Decimal("999")}
    )
    object.__setattr__(execution, "profitability_result", tampered)

    with pytest.raises(ProfitabilityProvenanceError, match="recomputación"):
        validate_provenanced_profitability_execution(execution)


def test_validator_rejects_nested_context_mutation_inside_execution():
    execution = run_provenanced_profitability(_payload())
    execution.profitability_input.context.decision_id = "DEC-FORGED"

    with pytest.raises(ProfitabilityProvenanceError, match="revalidación"):
        validate_provenanced_profitability_execution(execution)


def test_validator_rejects_nested_purchase_mutation_inside_execution():
    execution = run_provenanced_profitability(_payload())
    execution.profitability_input.purchase_operation.article_id = "ART-FORGED"

    with pytest.raises(ProfitabilityProvenanceError, match="revalidación"):
        validate_provenanced_profitability_execution(execution)


def test_validator_rejects_internal_basis_mutation_inside_execution():
    execution = run_provenanced_profitability(_payload())
    object.__setattr__(
        execution.profitability_input.sale_basis,
        "decision_id",
        "DEC-FORGED",
    )

    with pytest.raises(ProfitabilityProvenanceError, match="revalidación"):
        validate_provenanced_profitability_execution(execution)


def test_validator_rejects_invalid_known_basis_mutation():
    execution = run_provenanced_profitability(_payload())
    object.__setattr__(execution.profitability_input.cost_basis, "source_ref", None)

    with pytest.raises(ProfitabilityProvenanceError, match="revalidación"):
        validate_provenanced_profitability_execution(execution)


def test_detached_result_is_not_an_execution():
    result = calculate_profitability(_payload())

    with pytest.raises(TypeError, match="ProvenancedProfitabilityExecution"):
        validate_provenanced_profitability_execution(result)


def test_execution_dataclass_is_frozen():
    execution = run_provenanced_profitability(_payload())

    with pytest.raises(Exception):
        execution.profitability_input = _payload()


def test_boundary_has_no_rules_price_tco_io_or_clock_dependencies():
    root = Path(__file__).parents[1]
    source = (
        root / "eios" / "profitability" / "provenance.py"
    ).read_text(encoding="utf-8")

    forbidden = (
        "eios.rules",
        "eios.pricing",
        "eios.tco",
        "crc",
        "requests",
        "httpx",
        "socket",
        "open(",
        "Path(",
        "date.today",
        "datetime.now",
    )
    for token in forbidden:
        assert token not in source
