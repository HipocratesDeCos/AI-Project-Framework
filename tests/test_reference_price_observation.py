"""Same-invocation PRICE observation, bounded to the synthetic terminal."""
import pytest
from decimal import Decimal

from examples.reference_business_case_001 import (
    _bundle, _runtime, _provenanced_price_invoker,
    execute_reference_business_case_with_price_observation,
)
from eios.core.reference_price_observation import _close_reference_price_observation


@pytest.mark.parametrize("variant", ["negative", "qtg-eligible"])
def test_reference_price_observation_matches_terminal_without_changing_it(variant):
    execution, observation = execute_reference_business_case_with_price_observation(
        variant=variant,
    )
    terminal, seen = execution.to_payload(), observation.to_payload()
    assert seen["terminal_fingerprint"] == terminal["terminal_fingerprint"]
    assert seen["reference_case_id"] == terminal["reference_case_id"]
    assert seen["price_execution"] == terminal["execution_outcome"]["capability_results"][0]
    assert Decimal(seen["price_result"]["pr_value"]) == Decimal("20.25")
    assert seen["price_result"]["currency"] == "EUR"
    assert seen["material_nature"] == "SYNTHETIC"
    assert seen["operational_path"] == "FORBIDDEN"
    assert seen["decision_authority"] is False


def test_price_observer_is_single_use_and_rejects_foreign_runtime():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    observer = _provenanced_price_invoker(
        purchase, context, observed=True, reference_case_id="REF-BUSINESS-001",
    )
    with pytest.raises(ValueError, match="unavailable"):
        observer.capture()
    foreign = purchase.model_copy(update={"supplier_id": "FOREIGN"})
    with pytest.raises(ValueError, match="PurchaseOperation"):
        observer(foreign, context)
    with pytest.raises(ValueError, match="unavailable"):
        observer.capture()
    with pytest.raises(ValueError, match="single-use"):
        observer(purchase, context)


def test_price_observer_produces_once_and_requires_matching_case(monkeypatch):
    import eios.core.price_integration as integration
    original = integration.run_price_intelligence
    calls = []

    def counted(*args):
        calls.append(1)
        return original(*args)

    monkeypatch.setattr(integration, "run_price_intelligence", counted)
    execution, observation = execute_reference_business_case_with_price_observation(
        variant="negative",
    )
    assert len(calls) == 1
    assert observation.to_payload()["price_result"]["pr_status"] == "PR_AVAILABLE"

    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    foreign = _provenanced_price_invoker(
        purchase, context, observed=True,
        reference_case_id="REF-BUSINESS-001-QTG-ELIGIBLE",
    )
    foreign(purchase, context)
    with pytest.raises(ValueError, match="case identity"):
        _close_reference_price_observation(execution=execution, price_invoker=foreign)


@pytest.mark.parametrize("sufficiency,pr_status,expected_execution", [
    ("LIMITED", "PR_LIMITED", "COMPLETED"),
    ("NOT_JUSTIFIABLE", "PR_NOT_JUSTIFIABLE", "NOT_EVALUABLE"),
])
def test_observer_preserves_price_quality_states(
    monkeypatch, sufficiency, pr_status, expected_execution,
):
    import eios.core.price_integration as integration
    from eios.pricing.models import PriceIntelligenceResult

    original = integration.run_price_intelligence

    def variant(*args):
        data = original(*args).model_dump(mode="python")
        data["sufficiency_status"] = sufficiency
        data["pr_status"] = pr_status
        if pr_status == "PR_NOT_JUSTIFIABLE":
            data["pr_value"] = None
            data["reference_set"] = ()
            data["counts"]["n_selected"] = 0
        return PriceIntelligenceResult.model_validate(data)

    monkeypatch.setattr(integration, "run_price_intelligence", variant)
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    observer = _provenanced_price_invoker(
        purchase, context, observed=True, reference_case_id="REF-BUSINESS-001",
    )
    capability = observer(purchase, context)
    assert capability.status.value == expected_execution
    assert observer.capture().result.pr_status == pr_status
    assert (observer.capture().result.pr_value is None) == (
        pr_status == "PR_NOT_JUSTIFIABLE"
    )
