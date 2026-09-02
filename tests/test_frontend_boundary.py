from datetime import date

import pytest

from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.orchestration import CapabilityExecution, DecisionSupportPackage, O1ExecutionContext, O1ExecutionStatus
from eios.frontend.application_boundary import FrontendBoundaryError, build_decision_context, build_purchase_operation, present_support_package


def operation_payload():
    return {"decision_id":"D-001","scenario_id":"S-001","article_id":"A-001","supplier_id":"SUP-001","quantity":10,"unit_price":25.0,"currency":"EUR","operation_date":date(2026,9,2)}


def context_payload():
    return {"decision_id":"D-001","scenario_id":"S-001","rules_version":"R1","parameters_version":"P1","data_snapshot_id":"SNAP-001"}


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
    payload = operation_payload(); payload[field] = "FORBIDDEN"
    with pytest.raises(FrontendBoundaryError, match="campos no autorizados"):
        build_purchase_operation(payload)


def test_invalid_operation_is_boundary_error():
    payload = operation_payload(); payload["quantity"] = "not-a-number"
    with pytest.raises(FrontendBoundaryError, match="entrada de operación no válida"):
        build_purchase_operation(payload)


def test_invalid_context_is_boundary_error():
    payload = context_payload(); payload.pop("rules_version")
    with pytest.raises(FrontendBoundaryError, match="contexto de decisión no válido"):
        build_decision_context(payload)


def package_for(status):
    context = O1ExecutionContext.from_context(DecisionContext(**context_payload()))
    kwargs = {}
    if status == O1ExecutionStatus.FAILED:
        kwargs["failure_reason"] = "technical failure"
    result_available = status not in {O1ExecutionStatus.READY,O1ExecutionStatus.RUNNING,O1ExecutionStatus.NOT_EVALUABLE}
    capability = CapabilityExecution(capability="C0",status=status,result_available=result_available,**kwargs)
    return DecisionSupportPackage(execution_context=context,execution_status=status,capability_results=(capability,))


@pytest.mark.parametrize("status", list(O1ExecutionStatus))
def test_support_package_preserves_technical_state(status):
    presented = present_support_package(package_for(status))
    assert presented["execution_status"] == status.value


def test_support_package_preserves_limitations_and_traceability():
    context = O1ExecutionContext.from_context(DecisionContext(**context_payload()))
    capability = CapabilityExecution(capability="C0",status=O1ExecutionStatus.PARTIALLY_COMPLETED,result_available=True,trace_references=("trace-1",),unresolved_items=("pending-evidence",))
    package = DecisionSupportPackage(execution_context=context,execution_status=O1ExecutionStatus.PARTIALLY_COMPLETED,capability_results=(capability,),evidence_status=("VALIDATED",),version_context=("R1","P1","SNAP-001"),trace_references=("trace-1",),unresolved_items=("pending-evidence",))
    presented = present_support_package(package)
    assert presented["evidence_status"] == ["VALIDATED"]
    assert presented["trace_references"] == ["trace-1"]
    assert presented["version_context"] == ["R1","P1","SNAP-001"]
    assert presented["unresolved_items"] == ["pending-evidence"]


def test_support_package_presentation_does_not_mutate_source():
    package = package_for(O1ExecutionStatus.COMPLETED)
    before = package.model_dump(mode="json")
    presented = present_support_package(package)
    presented["execution_status"] = "NO_COMPRAR"
    assert package.model_dump(mode="json") == before


def test_non_package_is_rejected():
    with pytest.raises(FrontendBoundaryError, match="paquete O1 no válido"):
        present_support_package(object())
