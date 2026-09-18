from dataclasses import FrozenInstanceError
from hashlib import sha256
from datetime import timedelta

import pytest
from pydantic import ValidationError

from test_finance_decision_input_package import capture
from eios.core.finance_decision_input_package import build_finance_decision_input_package
from eios.core.documentary_payment_capture import (
    DocumentaryMaterial, DocumentaryLocator, DocumentaryPaymentBinding,
    DocumentaryPaymentCapture, build_documentary_payment_capture,
)


@pytest.fixture
def arguments(capture):
    kwargs, _, _ = capture
    package = build_finance_decision_input_package(**kwargs)
    document = DocumentaryMaterial(document_ref="doc", content=b"Synthetic documentary bytes")
    locator = DocumentaryLocator(document_ref="doc", page=2, section="Payment terms")
    binding = DocumentaryPaymentBinding(installment_ref="order/1", flow_id="payment", locators=(locator,))
    return dict(package=package, documents=(document,), bindings=(binding,),
                case_kind="SYNTHETIC", operation_ref="operation")


def test_capture_bytes_scope_and_independent_export(arguments):
    result = build_documentary_payment_capture(**arguments)
    payload = result.to_payload()
    assert result.document_bytes("doc") == arguments["documents"][0].content
    assert payload["documents"][0]["sha256"] == sha256(result.document_bytes("doc")).hexdigest()
    assert payload["finance_package"] == arguments["package"].to_payload()
    assert payload["external_review_ref"] is None
    assert payload["case_kind"] == "SYNTHETIC"
    payload["bindings"].clear()
    assert len(result.to_payload()["bindings"]) == 1
    with pytest.raises(FrozenInstanceError):
        result._material = b"forged"
    with pytest.raises(TypeError):
        DocumentaryPaymentCapture()
    with pytest.raises(KeyError):
        result.document_bytes("absent")


@pytest.mark.parametrize("flow_id", ["absent", "unknown"])
def test_invalid_flow_binding(arguments, flow_id):
    original = arguments["bindings"][0]
    arguments["bindings"] = (original.model_copy(update={"flow_id": flow_id}),)
    with pytest.raises(ValueError, match="PAYMENT"):
        build_documentary_payment_capture(**arguments)


def test_duplicate_flow_and_document(arguments):
    binding = arguments["bindings"][0]
    arguments["bindings"] = (binding, binding.model_copy(update={"installment_ref": "other"}))
    with pytest.raises(ValueError, match="Duplicate"):
        build_documentary_payment_capture(**arguments)
    arguments["bindings"] = ()
    arguments["documents"] *= 2
    with pytest.raises(ValueError, match="Duplicate"):
        build_documentary_payment_capture(**arguments)


@pytest.mark.parametrize("page", [0, -1, True])
def test_revalidation_of_bypassed_locator(arguments, page):
    original = arguments["bindings"][0]
    locator = original.locators[0].model_copy(update={"page": page})
    arguments["bindings"] = (original.model_copy(update={"locators": (locator,)}),)
    with pytest.raises(ValidationError):
        build_documentary_payment_capture(**arguments)


def test_missing_document(arguments):
    arguments["documents"] = ()
    with pytest.raises(ValueError, match="conserved"):
        build_documentary_payment_capture(**arguments)


def test_empty_association_no_evidence_upgrade(arguments):
    arguments["bindings"] = ()
    arguments["documents"] = ()
    arguments["case_kind"] = "PRESENTED_OPERATIONAL"
    result = build_documentary_payment_capture(**arguments)
    assert result.to_payload()["bindings"] == []
    assert result.to_payload()["finance_package"]["finance_input"]["cash_flows"][1]["evidence_state"] == "NOT_EVIDENCED"


def test_material_and_context_identity_sensitivity(arguments):
    original = build_documentary_payment_capture(**arguments)
    arguments["documents"] = (DocumentaryMaterial(document_ref="doc", content=b"Changed"),)
    changed = build_documentary_payment_capture(**arguments)
    assert original.fingerprint != changed.fingerprint
    arguments["operation_ref"] = "another"
    assert changed.fingerprint != build_documentary_payment_capture(**arguments).fingerprint


def test_capture_does_not_execute_engines(arguments, monkeypatch):
    import eios.finance.provenance as provenance
    import eios.quality.gate as gate
    def forbidden(*args, **kwargs):
        raise AssertionError("capture must not execute")
    monkeypatch.setattr(provenance, "run_provenanced_finance_basic", forbidden)
    monkeypatch.setattr(gate, "evaluate_quality", forbidden)
    build_documentary_payment_capture(**arguments)


def test_duplicate_installment_under_different_flow_ids(capture):
    kwargs, _, _ = capture
    finance = kwargs['finance_input']
    first = finance.cash_flows[0]
    second = first.model_copy(update={'flow_id': 'second', 'due_date': first.due_date + timedelta(days=90)})
    kwargs['finance_input'] = finance.model_copy(update={'cash_flows': (first, second)})
    package = build_finance_decision_input_package(**kwargs)
    locator = DocumentaryLocator(document_ref='doc', page=1, section='Terms')
    a = DocumentaryPaymentBinding(installment_ref='same', flow_id=first.flow_id, locators=(locator,))
    b = a.model_copy(update={'flow_id': second.flow_id})
    args = dict(package=package, documents=(DocumentaryMaterial(document_ref='doc', content=b'synthetic'),),
                bindings=(a, b), case_kind='SYNTHETIC', operation_ref='op')
    with pytest.raises(ValueError, match='Duplicate'):
        build_documentary_payment_capture(**args)
    args['bindings'] = (a, b.model_copy(update={'installment_ref': 'second-installment'}))
    result = build_documentary_payment_capture(**args)
    assert len(result.to_payload()['bindings']) == 2
    assert len(result.to_payload()['finance_package']['finance_input']['cash_flows']) == 2


@pytest.mark.parametrize('content', [b'', 'not bytes'])
def test_document_construct_bypass_rejected(arguments, content):
    arguments['documents'] = (DocumentaryMaterial.model_construct(document_ref='doc', content=content),)
    with pytest.raises(ValidationError):
        build_documentary_payment_capture(**arguments)
