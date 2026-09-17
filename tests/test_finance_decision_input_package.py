from dataclasses import FrozenInstanceError, replace
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from eios.core.finance_decision_input_package import FinanceDecisionInputPackage, build_finance_decision_input_package
from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.finance.models import CashFlow, FinanceBasicInput, FinancialSnapshot, WorkingCapitalInput
from eios.parameters.center import Configuration, ParameterConfigurationCenter, ParameterDefinition


@pytest.fixture
def capture():
    now = datetime(2026, 9, 17, 10, tzinfo=timezone.utc)
    context = DecisionContext(decision_id="d", scenario_id="s", rules_version="r", parameters_version="v", data_snapshot_id="snap")
    configurations = {}
    for number, pid, value, unit in [(1, "P-FIN-001", "30", "días"), (2, "P-FIN-002", "100", "€")]:
        configurations[pid] = Configuration(number, pid, "company", value, "numeric", unit, now - timedelta(days=1), None, now, now)
    calls = []
    def get_at(company, pid, instant):
        calls.append((company, pid, instant))
        return configurations.get(pid)
    center = ParameterConfigurationCenter(
        SimpleNamespace(get_parameter=lambda pid: ParameterDefinition(pid) if pid in {"P-FIN-001", "P-FIN-002", "P-FIN-004"} else None),
        SimpleNamespace(can_modify=lambda *args: False), SimpleNamespace(get_at=get_at),
    )
    snapshot = FinancialSnapshot(company_scope="company", as_of_date=now.date(), data_snapshot_id="snap", currency="EUR",
                                 available_treasury=Decimal("1000"), treasury_evidence_ref="erp:treasury")
    flows = (
        CashFlow(flow_id="payment", flow_type="PAYMENT", amount=Decimal("200"), currency="EUR", due_date=now.date() + timedelta(days=3), source_ref="erp:payment", evidence_state="DEMONSTRATED"),
        CashFlow(flow_id="unknown", flow_type="COLLECTION", evidence_state="NOT_EVIDENCED"),
    )
    working = WorkingCapitalInput(company_scope="company", as_of_date=now.date(), currency="EUR", current_assets=Decimal("400"), assets_source_ref="ledger:assets")
    finance = FinanceBasicInput(context=context.model_copy(deep=True), snapshot=snapshot, cash_flows=flows, horizon_days=30, treasury_minimum=Decimal("100"), working_capital_input=working)
    kwargs = dict(purchase=PurchaseOperation(decision_id="d", scenario_id="s", article_id="a", supplier_id="p", quantity=1, unit_price=200, operation_date=now.date()),
                  context=context, evidence=(Evidence(evidence_id="e", source_type="offer", source_ref="offer:1", captured_at=now.date(), state="GAP"),),
                  finance_input=finance, company_id="company", effective_at=now,
                  requested_parameter_ids=("P-FIN-001", "P-FIN-002", "P-FIN-004"), center=center)
    return kwargs, configurations, calls


def test_complete_capture_and_parameter_bindings(capture):
    kwargs, configs, calls = capture
    package = build_finance_decision_input_package(**kwargs)
    assert package.schema_version == "FIN-DIP-01/v0.1"
    assert package.finance_input == kwargs["finance_input"]
    assert package.decision_input_package.financial_snapshot == package.finance_input.snapshot
    assert package.horizon_resolution.configuration == configs["P-FIN-001"]
    assert package.treasury_minimum_resolution.configuration == configs["P-FIN-002"]
    assert package.decision_input_package.missing_parameter_ids == ("P-FIN-004",)
    assert len(calls) == 3
    assert package.fingerprint == build_finance_decision_input_package(**kwargs).fingerprint
    assert set(package.to_payload()) == {"schema_version", "decision_input_package", "finance_input"}
    assert len(package.finance_input.cash_flows) == 2
    assert package.finance_input.cash_flows[1].currency is None


@pytest.mark.parametrize("field,value", [("decision_id", "other"), ("scenario_id", "other"), ("rules_version", "other"), ("parameters_version", "other"), ("data_snapshot_id", "other")])
def test_all_context_fields_must_match(capture, field, value):
    kwargs, _, calls = capture
    kwargs["context"] = kwargs["context"].model_copy(update={field: value})
    with pytest.raises(ValueError):
        build_finance_decision_input_package(**kwargs)
    assert calls == []


@pytest.mark.parametrize("pid", ["P-FIN-001", "P-FIN-002"])
def test_required_configuration_omitted_or_unavailable(capture, pid):
    kwargs, configs, calls = capture
    kwargs["requested_parameter_ids"] = tuple(item for item in kwargs["requested_parameter_ids"] if item != pid)
    with pytest.raises(ValueError, match="explicit"):
        build_finance_decision_input_package(**kwargs)
    assert calls == []
    kwargs["requested_parameter_ids"] = ("P-FIN-001", "P-FIN-002")
    configs.pop(pid)
    with pytest.raises(ValueError, match="unavailable"):
        build_finance_decision_input_package(**kwargs)


@pytest.mark.parametrize("pid,field,value", [
    ("P-FIN-001", "value", "0"), ("P-FIN-001", "value", "30.5"),
    ("P-FIN-001", "value", "31"), ("P-FIN-001", "value", "NaN"),
    ("P-FIN-001", "unit", "days"), ("P-FIN-002", "value", "99"),
    ("P-FIN-002", "value", "-1"), ("P-FIN-002", "value", "Infinity"),
    ("P-FIN-002", "value", "unknown"), ("P-FIN-002", "unit", "USD"),
])
def test_no_raw_horizon_or_minimum_binding(capture, pid, field, value):
    kwargs, configs, _ = capture
    configs[pid] = replace(configs[pid], **{field: value})
    with pytest.raises(ValueError):
        build_finance_decision_input_package(**kwargs)


def test_euro_minimum_not_bound_to_another_currency(capture):
    kwargs, _, _ = capture
    finance = kwargs["finance_input"]
    kwargs["finance_input"] = finance.model_copy(update={"snapshot": finance.snapshot.model_copy(update={"currency": "USD"})})
    with pytest.raises(ValueError, match="minimum/unit"):
        build_finance_decision_input_package(**kwargs)


def test_none_minimum_not_hydrated_and_zero_not_overruled(capture):
    kwargs, configs, _ = capture
    finance = kwargs["finance_input"]
    kwargs["finance_input"] = finance.model_copy(update={"treasury_minimum": None})
    package = build_finance_decision_input_package(**kwargs)
    assert package.finance_input.treasury_minimum is None
    assert package.treasury_minimum_resolution is None
    assert "P-FIN-002" in [item.parameter_id for item in package.decision_input_package.configurations]
    without_minimum = build_finance_decision_input_package(**{**kwargs, "requested_parameter_ids": ("P-FIN-001",)})
    assert without_minimum.finance_input.treasury_minimum is None
    assert without_minimum.treasury_minimum_resolution is None
    configs["P-FIN-002"] = replace(configs["P-FIN-002"], value="0")
    kwargs["finance_input"] = finance.model_copy(update={"treasury_minimum": Decimal("0")})
    assert build_finance_decision_input_package(**kwargs).finance_input.treasury_minimum == 0


def test_financial_none_fields_conflicts_and_incompatibility_preserved(capture):
    kwargs, _, _ = capture
    finance = kwargs["finance_input"]
    conflicting = CashFlow(flow_id="conflict", flow_type="PAYMENT", evidence_state="CONFLICTING_DATA")
    working = finance.working_capital_input.model_copy(update={"company_scope": "another-company"})
    kwargs["finance_input"] = finance.model_copy(update={"cash_flows": (conflicting,), "working_capital_input": working})
    package = build_finance_decision_input_package(**kwargs)
    assert package.finance_input.cash_flows[0].amount is None
    assert package.finance_input.cash_flows[0].evidence_state == "CONFLICTING_DATA"
    assert package.finance_input.working_capital_input.company_scope == "another-company"


def test_revalidation_and_snapshot_date(capture):
    kwargs, _, calls = capture
    finance = kwargs["finance_input"]
    kwargs["finance_input"] = finance.model_copy(update={"horizon_days": -1})
    with pytest.raises(ValidationError):
        build_finance_decision_input_package(**kwargs)
    assert calls == []
    kwargs["finance_input"] = finance
    kwargs["effective_at"] += timedelta(days=1)
    with pytest.raises(ValueError, match="snapshot date"):
        build_finance_decision_input_package(**kwargs)
    assert calls == []


def test_capture_and_consumer_copies_are_independent(capture):
    kwargs, _, _ = capture
    package = build_finance_decision_input_package(**kwargs)
    payload = package.to_payload()
    fingerprint = package.fingerprint
    kwargs["finance_input"].context.parameters_version = "mutated"
    object.__setattr__(kwargs["finance_input"].cash_flows[0], "amount", Decimal("999"))
    package.finance_input.context.parameters_version = "consumer-mutation"
    package.to_payload()["finance_input"]["cash_flows"].clear()
    assert package.to_payload() == payload
    assert package.fingerprint == fingerprint
    with pytest.raises(FrozenInstanceError):
        package._material = b"{}"
    with pytest.raises(TypeError):
        FinanceDecisionInputPackage()


def test_capture_precedes_reads_and_errors_propagate(capture):
    kwargs, configs, _ = capture
    def mutating_read(company, pid, instant):
        kwargs["finance_input"].context.parameters_version = "mutated"
        object.__setattr__(kwargs["finance_input"].cash_flows[0], "amount", Decimal("999"))
        return configs.get(pid)
    kwargs["center"]._repository.get_at = mutating_read
    package = build_finance_decision_input_package(**kwargs)
    assert package.finance_input.context.parameters_version == "v"
    assert package.finance_input.cash_flows[0].amount == 200
    kwargs["finance_input"] = package.finance_input
    def unavailable(*args):
        raise RuntimeError("unavailable")
    kwargs["center"]._repository.get_at = unavailable
    with pytest.raises(RuntimeError, match="unavailable"):
        build_finance_decision_input_package(**kwargs)


@pytest.mark.parametrize("family", ["flow", "working_capital", "minimum", "horizon"])
def test_identity_covers_full_financial_material(capture, family):
    kwargs, configs, _ = capture
    first = build_finance_decision_input_package(**kwargs).fingerprint
    finance = kwargs["finance_input"]
    if family == "flow":
        flows = (finance.cash_flows[0].model_copy(update={"source_ref": "other-source"}), finance.cash_flows[1])
        kwargs["finance_input"] = finance.model_copy(update={"cash_flows": flows})
    elif family == "working_capital":
        kwargs["finance_input"] = finance.model_copy(update={"working_capital_input": None})
    elif family == "minimum":
        configs["P-FIN-002"] = replace(configs["P-FIN-002"], value="200")
        kwargs["finance_input"] = finance.model_copy(update={"treasury_minimum": Decimal("200")})
    else:
        configs["P-FIN-001"] = replace(configs["P-FIN-001"], value="31")
        kwargs["finance_input"] = finance.model_copy(update={"horizon_days": 31})
    assert build_finance_decision_input_package(**kwargs).fingerprint != first


def test_no_analytics_qtg_or_purchase_payment_inference(capture, monkeypatch):
    import eios.finance.engine as engine
    import eios.finance.provenance as provenance
    import eios.quality.gate as gate
    def forbidden(*args, **kwargs):
        raise AssertionError("must not execute during input capture")
    monkeypatch.setattr(engine, "calculate_finance_basic", forbidden)
    monkeypatch.setattr(provenance, "run_provenanced_finance_basic", forbidden)
    monkeypatch.setattr(gate, "evaluate_quality", forbidden)
    kwargs, _, _ = capture
    kwargs["finance_input"] = kwargs["finance_input"].model_copy(update={"cash_flows": ()})
    assert build_finance_decision_input_package(**kwargs).finance_input.cash_flows == ()


def test_captured_inputs_remain_compatible_with_closed_finance_boundary(capture):
    from eios.finance.provenance import run_provenanced_finance_basic
    kwargs, _, _ = capture
    package = build_finance_decision_input_package(**kwargs)
    execution = run_provenanced_finance_basic(package.finance_input, package.horizon_resolution)
    assert execution.finance_input == package.finance_input
    assert execution.finance_result.projection.status == "NOT_EVIDENCED"
    assert execution.finance_result.projection.financial_capacity_forecast is None
