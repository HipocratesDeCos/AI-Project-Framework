from dataclasses import FrozenInstanceError, replace
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from hashlib import sha256
import inspect
import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from eios.core.decision_input_package import DecisionInputPackage, build_decision_input_package
from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.finance.models import FinancialSnapshot
from eios.parameters.center import Configuration, ParameterConfigurationCenter, ParameterConfigurationError, ParameterDefinition


@pytest.fixture
def inputs():
    now = datetime(2026, 9, 17, 10, tzinfo=timezone.utc)
    configuration = Configuration(1, "P-FIN-001", "company", "30", "integer", "días",
                                  now - timedelta(days=1), None, now, now)
    calls = []
    configs = {"P-FIN-001": configuration}

    def get_at(company_id, parameter_id, effective_at):
        calls.append((company_id, parameter_id, effective_at))
        return configs.get(parameter_id)

    centre = ParameterConfigurationCenter(
        SimpleNamespace(get_parameter=lambda pid: ParameterDefinition(pid) if pid in {"P-FIN-001", "P-FIN-002"} else None),
        SimpleNamespace(can_modify=lambda *args: False),
        SimpleNamespace(get_at=get_at),
    )
    kwargs = dict(
        purchase=PurchaseOperation(decision_id="d", scenario_id="s", article_id="a", supplier_id="p",
                                   quantity=Decimal("2"), unit_price=Decimal("12.50"), operation_date=date(2026, 9, 16)),
        context=DecisionContext(decision_id="d", scenario_id="s", rules_version="r", parameters_version="v", data_snapshot_id="snap"),
        evidence=(Evidence(evidence_id="e", source_type="offer", source_ref="offer:1", captured_at=date(2026, 9, 10), state="GAP"),),
        financial_snapshot=FinancialSnapshot(company_scope="company", as_of_date=date(2026, 9, 15), data_snapshot_id="snap", currency="EUR",
                                             available_treasury=Decimal("100"), treasury_evidence_ref="erp:treasury"),
        company_id="company", effective_at=now,
        requested_parameter_ids=("P-FIN-001", "P-FIN-002"), center=centre,
    )
    return kwargs, configs, calls


def test_capture_partition_roundtrip_and_exact_canonical_identity(inputs):
    kwargs, configs, calls = inputs
    package = build_decision_input_package(**kwargs)
    assert package.purchase == kwargs["purchase"]
    assert package.context == kwargs["context"]
    assert package.company_id == kwargs["company_id"]
    assert package.effective_at == kwargs["effective_at"]
    assert package.requested_parameter_ids == kwargs["requested_parameter_ids"]
    assert package.evidence == kwargs["evidence"]
    assert package.financial_snapshot == kwargs["financial_snapshot"]
    assert package.configurations[0].configuration == configs["P-FIN-001"]
    assert package.configurations[0].parameters_version == "v"
    assert package.missing_parameter_ids == ("P-FIN-002",)
    assert [call[1] for call in calls] == ["P-FIN-001", "P-FIN-002"]
    payload = package.to_payload()
    assert payload["schema_version"] == "DIP-AGG-01/v0.1"
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    assert package.fingerprint == sha256(canonical).hexdigest()
    assert package.fingerprint == build_decision_input_package(**kwargs).fingerprint
    assert package.evidence[0].state == "GAP"
    assert package.financial_snapshot.as_of_date != package.purchase.operation_date
    assert package.financial_snapshot.as_of_date != kwargs["effective_at"].date()


def test_mutation_cannot_change_capture_or_consumer_copies(inputs):
    kwargs, _, _ = inputs
    package = build_decision_input_package(**kwargs)
    original = package.to_payload()
    fingerprint = package.fingerprint
    kwargs["purchase"].quantity = Decimal("999")
    kwargs["context"].parameters_version = "changed"
    kwargs["evidence"][0].source_ref = "changed"
    package.purchase.quantity = Decimal("888")
    package.context.parameters_version = "changed-again"
    package.evidence[0].source_ref = "changed-again"
    package.to_payload()["configurations"].clear()
    assert package.to_payload() == original
    assert package.fingerprint == fingerprint
    with pytest.raises(FrozenInstanceError):
        package._material = b"{}"
    with pytest.raises(TypeError):
        DecisionInputPackage()


def test_capture_precedes_external_reads(inputs):
    kwargs, configs, _ = inputs
    def malicious_read(company_id, pid, at):
        kwargs["purchase"].quantity = Decimal("999")
        kwargs["context"].parameters_version = "tampered"
        kwargs["evidence"][0].state = "DEMONSTRATED"
        return configs.get(pid)
    kwargs["center"]._repository.get_at = malicious_read
    package = build_decision_input_package(**kwargs)
    assert package.purchase.quantity == Decimal("2")
    assert package.context.parameters_version == "v"
    assert package.evidence[0].state == "GAP"


@pytest.mark.parametrize("component,field,value", [
    ("purchase", "decision_id", "other"), ("purchase", "scenario_id", "other"),
    ("financial_snapshot", "company_scope", "other"),
    ("financial_snapshot", "data_snapshot_id", "other"),
])
def test_reject_scope_mismatch_before_read(inputs, component, field, value):
    kwargs, _, calls = inputs
    kwargs[component] = kwargs[component].model_copy(update={field: value})
    with pytest.raises(ValueError):
        build_decision_input_package(**kwargs)
    assert calls == []


@pytest.mark.parametrize("component,field,value", [
    ("purchase", "quantity", Decimal("-1")), ("context", "rules_version", ""),
    ("financial_snapshot", "available_treasury", Decimal("-1")),
])
def test_revalidate_models_bypassing_validation(inputs, component, field, value):
    kwargs, _, calls = inputs
    data = kwargs[component].model_dump()
    data[field] = value
    kwargs[component] = type(kwargs[component]).model_construct(**data)
    with pytest.raises(ValidationError):
        build_decision_input_package(**kwargs)
    assert calls == []


def test_revalidate_invalid_demonstrated_evidence(inputs):
    kwargs, _, calls = inputs
    kwargs["evidence"] = (kwargs["evidence"][0].model_copy(update={"state": "DEMONSTRATED"}),)
    with pytest.raises(ValidationError):
        build_decision_input_package(**kwargs)
    assert calls == []


@pytest.mark.parametrize("field,value", [
    ("company_id", "other"), ("parameter_id", "P-FIN-002"),
    ("value", 30), ("configuration_id", True), ("unit", 1),
    ("created_at", "2026-09-17"), ("valid_to", "invalid"),
])
def test_revalidate_centre_results(inputs, field, value):
    kwargs, configs, _ = inputs
    configs["P-FIN-001"] = replace(configs["P-FIN-001"], **{field: value})
    with pytest.raises((ValueError, TypeError)):
        build_decision_input_package(**kwargs)


@pytest.mark.parametrize("kind", ["future", "expired", "incompatible_timezone"])
def test_validity_errors_are_technical(inputs, kind):
    kwargs, configs, _ = inputs
    config = configs["P-FIN-001"]
    if kind == "future":
        config = replace(config, valid_from=kwargs["effective_at"] + timedelta(seconds=1))
    elif kind == "expired":
        config = replace(config, valid_to=kwargs["effective_at"])
    else:
        config = replace(config, valid_from=config.valid_from.replace(tzinfo=None))
    configs["P-FIN-001"] = config
    with pytest.raises(ParameterConfigurationError) as caught:
        build_decision_input_package(**kwargs)
    assert caught.value.code == "INVALID_VALIDITY"


def test_unknown_parameter_and_repository_failure_are_not_absence(inputs):
    kwargs, _, calls = inputs
    with pytest.raises(ParameterConfigurationError) as caught:
        build_decision_input_package(**{**kwargs, "requested_parameter_ids": ("unknown",)})
    assert caught.value.code == "PARAMETER_NOT_FOUND"
    assert calls == []
    def unavailable(*args):
        raise RuntimeError("repository unavailable")
    kwargs["center"]._repository.get_at = unavailable
    with pytest.raises(RuntimeError, match="repository unavailable"):
        build_decision_input_package(**kwargs)


@pytest.mark.parametrize("override", [
    {"requested_parameter_ids": ("P-FIN-001", "P-FIN-001")},
    {"requested_parameter_ids": (" P-FIN-001",)},
    {"requested_parameter_ids": ("",)}, {"company_id": "company "},
])
def test_invalid_selection(inputs, override):
    kwargs, _, calls = inputs
    with pytest.raises(ValueError):
        build_decision_input_package(**{**kwargs, **override})
    assert calls == []


def test_duplicate_evidence_and_explicit_empty_capture(inputs):
    kwargs, _, calls = inputs
    with pytest.raises(ValueError, match="Duplicate evidence"):
        build_decision_input_package(**{**kwargs, "evidence": kwargs["evidence"] * 2})
    assert calls == []
    package = build_decision_input_package(**{**kwargs, "financial_snapshot": None, "evidence": (), "requested_parameter_ids": ()})
    assert package.financial_snapshot is None
    assert package.evidence == package.configurations == package.missing_parameter_ids == ()
    assert calls == []


@pytest.mark.parametrize("family", ["purchase", "context", "evidence", "finance", "configuration", "selection", "instant", "absence"])
def test_fingerprint_sensitive_to_each_material_family(inputs, family):
    kwargs, configs, _ = inputs
    original = build_decision_input_package(**kwargs).fingerprint
    if family == "purchase":
        kwargs["purchase"].unit_price += Decimal("1")
    elif family == "context":
        kwargs["context"].rules_version = "r2"
    elif family == "evidence":
        kwargs["evidence"][0].source_ref = "offer:2"
    elif family == "finance":
        kwargs["financial_snapshot"] = kwargs["financial_snapshot"].model_copy(update={"available_treasury": Decimal("200")})
    elif family == "configuration":
        configs["P-FIN-001"] = replace(configs["P-FIN-001"], value="40")
    elif family == "selection":
        kwargs["requested_parameter_ids"] = tuple(reversed(kwargs["requested_parameter_ids"]))
    elif family == "instant":
        kwargs["effective_at"] += timedelta(seconds=1)
    else:
        configs.pop("P-FIN-001")
    assert build_decision_input_package(**kwargs).fingerprint != original


def test_no_opaque_configuration_or_quality_passthrough(inputs):
    kwargs, _, _ = inputs
    parameters = inspect.signature(build_decision_input_package).parameters
    assert "configurations" not in parameters
    assert "quality_invoker" not in parameters
    assert "quality_result" not in parameters
    with pytest.raises(TypeError):
        build_decision_input_package(**kwargs, configurations=())


@pytest.mark.parametrize("field,value", [("parameters_version", "other"), ("effective_at", datetime(2026, 9, 18, tzinfo=timezone.utc))])
def test_resolution_binding_is_rechecked(inputs, monkeypatch, field, value):
    import eios.core.decision_input_package as module
    kwargs, _, _ = inputs
    original = module.resolve_configuration_for_context
    def wrong_binding(*args):
        return replace(original(*args), **{field: value})
    monkeypatch.setattr(module, "resolve_configuration_for_context", wrong_binding)
    with pytest.raises(ValueError, match="binding mismatch"):
        build_decision_input_package(**kwargs)


def test_offset_representation_preserved_without_claiming_time_equivalence(inputs):
    kwargs, _, _ = inputs
    first = build_decision_input_package(**kwargs)
    kwargs["effective_at"] = kwargs["effective_at"].astimezone(timezone(timedelta(hours=2)))
    second = build_decision_input_package(**kwargs)
    assert first.configurations[0].effective_at == second.configurations[0].effective_at
    assert first.to_payload()["effective_at"] != second.to_payload()["effective_at"]
    assert first.fingerprint != second.fingerprint
