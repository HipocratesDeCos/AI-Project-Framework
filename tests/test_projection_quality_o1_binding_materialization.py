import inspect

import pytest

from test_finance_decision_input_package import capture  # noqa: F401
from test_finance_quality_preparation import prepared_args  # noqa: F401
from test_required_installment_coverage import material  # noqa: F401
from test_projection_material_envelope import envelope_parts  # noqa: F401

import eios.core.projection_quality_o1_binding as binding
from eios.core.mvp_execution import MVP_CAPABILITY_ORDER, run_mvp_execution
from eios.core.projection_material_envelope import build_projection_material_envelope
from eios.core.projection_quality_consumer import consume_projection_quality
from eios.core.projection_quality_producer import produce_projection_quality


def _synthetic_chain(parts):
    envelope = build_projection_material_envelope(**parts["envelope_args"])
    receipt = produce_projection_quality(
        envelope=envelope,
        execution_mode="SYNTHETIC_TEST",
    )
    consumption = consume_projection_quality(
        receipt=receipt,
        envelope=envelope,
        execution_mode="SYNTHETIC_TEST",
        consumption_scope="TEST_ONLY",
    )
    dip = envelope.to_payload()["preparation"]["payload"]["capture"][
        "finance_package"
    ]["decision_input_package"]
    from eios.core.models import DecisionContext, PurchaseOperation
    purchase = PurchaseOperation.model_validate(dip["purchase"])
    context = DecisionContext.model_validate(dip["context"])
    return envelope, receipt, consumption, purchase, context


def test_bound_input_rejects_synthetic_consumption(envelope_parts):
    envelope, receipt, consumption, purchase, context = _synthetic_chain(
        envelope_parts
    )
    with pytest.raises(ValueError):
        binding.build_projection_quality_o1_input_binding(
            consumption=consumption,
            receipt=receipt,
            envelope=envelope,
            purchase=purchase,
            context=context,
            policy_version="O1-POLICY-v1",
        )


def test_facade_rejects_synthetic_before_o1_is_called(envelope_parts, monkeypatch):
    envelope, receipt, consumption, purchase, context = _synthetic_chain(
        envelope_parts
    )
    calls = []

    def forbidden_call(**kwargs):
        calls.append(kwargs)
        raise AssertionError("O1 must not run for synthetic QTG consumption")

    monkeypatch.setattr(binding, "run_mvp_execution", forbidden_call)

    with pytest.raises(ValueError):
        binding.run_mvp_execution_with_projection_quality_binding(
            consumption=consumption,
            receipt=receipt,
            envelope=envelope,
            purchase=purchase,
            context=context,
            policy_version="O1-POLICY-v1",
            rules_invoker=lambda *_: None,
        )
    assert calls == []


def test_binding_facade_invoker_signature_matches_mvp_execution():
    base = inspect.signature(run_mvp_execution).parameters
    facade = inspect.signature(
        binding.run_mvp_execution_with_projection_quality_binding
    ).parameters

    specialized = {"consumption", "receipt", "envelope"}
    assert set(facade) - specialized == set(base)

    invoker_names = {name for name in base if name.endswith("_invoker")}
    assert invoker_names <= set(facade)
    assert "quality_invoker" not in facade
    assert "qtg_invoker" not in facade


def test_qtg_remains_outside_generic_runtime_invokers():
    params = inspect.signature(run_mvp_execution).parameters
    assert "quality_invoker" not in params
    assert "qtg_invoker" not in params
    assert "QTG" in MVP_CAPABILITY_ORDER


def test_no_public_posthoc_terminal_closer_exists():
    public = {
        name
        for name in dir(binding)
        if not name.startswith("_")
    }
    forbidden = {
        "close_projection_quality_o1_binding",
        "close_bound_execution",
        "bind_execution_outcome",
        "build_bound_terminal_outcome",
    }
    assert public.isdisjoint(forbidden)


def test_policy_identifier_rejects_blank_before_any_execution(envelope_parts):
    envelope, receipt, consumption, purchase, context = _synthetic_chain(
        envelope_parts
    )
    with pytest.raises(ValueError, match="policy_version"):
        binding.build_projection_quality_o1_input_binding(
            consumption=consumption,
            receipt=receipt,
            envelope=envelope,
            purchase=purchase,
            context=context,
            policy_version=" ",
        )


def test_no_positive_operational_fixture_is_created_by_binding_module():
    source = inspect.getsource(binding)
    assert "case_kind=" not in source
    assert "PRESENTED_OPERATIONAL" not in source
    assert "execution_mode=\"OPERATIONAL\"" in source
    assert "consumption_scope=\"OPERATIONAL\"" in source
