from datetime import date

import pytest

from eios.core.models import DecisionContext, PurchaseOperation
from eios.frontend.application_boundary import (
    FrontendBoundaryError,
    build_decision_context,
    build_purchase_operation,
    present_support_package,
)


def operation_payload():
    return {
        "decision_id": "D-001",
        "scenario_id": "S-001",
        "article_id": "A-001",
        "supplier_id": "SUP-001",
        "quantity": 10,
        "unit_price": 25.0,
        "currency": "EUR",
        "operation_date": date(2026, 9, 2),
    }


def context_payload():
    return {
        "decision_id": "D-001",
        "scenario_id": "S-001",
        "rules_version": "R1",
        "parameters_version": "P1",
        "data_snapshot_id": "SNAP-001",
    }


def test_build_purchase_operation_uses_canonical_model():
    result = build_purchase_operation(operation_payload())
    assert isinstance(result, PurchaseOperation)
    assert result.decision_id == "D-001"


def test_build_context_uses_canonical_model():
    result = build_decision_context(context_payload())
    assert isinstance(result, DecisionContext)
    assert result.rules_version == "R1"


@pytest.mark.parametrize("field", ["decision_version", "decision_fingerprint"])
def test_forbidden_parallel_identity_fields_are_rejected(field):
    payload = operation_payload()
    payload[field] = "FORBIDDEN"
    with pytest.raises(FrontendBoundaryError, match="campos no autorizados"):
        build_purchase_operation(payload)


def test_invalid_operation_is_boundary_error():
    payload = operation_payload()
    payload["quantity"] = "not-a-number"
    with pytest.raises(FrontendBoundaryError, match="entrada de operación no válida"):
        build_purchase_operation(payload)


def test_invalid_context_is_boundary_error():
    payload = context_payload()
    payload.pop("rules_version")
    with pytest.raises(FrontendBoundaryError, match="contexto de decisión no válido"):
        build_decision_context(payload)


def test_support_package_is_presented_without_recalculation():
    class Package:
        def model_dump(self, mode="json"):
            return {"execution_status": "COMPLETED", "capability_results": {}}

    result = present_support_package(Package())
    assert result["execution_status"] == "COMPLETED"


def test_non_package_is_rejected():
    with pytest.raises(FrontendBoundaryError, match="paquete O1 no válido"):
        present_support_package(object())
