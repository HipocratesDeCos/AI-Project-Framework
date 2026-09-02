"""Deterministic adapters from existing capability results to O1 execution records.

Adapters do not execute, recalculate, rank, approve, reject, or decide. They only
translate already-produced capability results into the operational O1 envelope.
"""
from __future__ import annotations

from .c0 import Assessment, Trace
from .orchestration import CapabilityExecution, O1ExecutionStatus
from .models import AssessmentStatus
from eios.pricing.models import PriceIntelligenceResult
from eios.tco.models import TCOResult
from eios.quality.gate import QualityTrustResult


def adapt_c0(assessments: tuple[Assessment, ...], traces: tuple[Trace, ...]) -> CapabilityExecution:
    if len(assessments) != len(traces):
        raise ValueError("C0 assessments y traces deben tener la misma cardinalidad")
    trace_refs = tuple(trace.trace_id for trace in traces)
    if not assessments:
        return CapabilityExecution(
            capability="C0",
            status=O1ExecutionStatus.NOT_EVALUABLE,
            result_available=False,
            trace_references=trace_refs,
            unresolved_items=("C0_NO_ASSESSMENTS",),
        )
    if any(item.status == "NOT_EVALUABLE" for item in assessments):
        return CapabilityExecution(
            capability="C0",
            status=O1ExecutionStatus.NOT_EVALUABLE,
            result_available=False,
            trace_references=trace_refs,
            unresolved_items=("C0_NOT_EVALUABLE",),
        )
    return CapabilityExecution(
        capability="C0",
        status=O1ExecutionStatus.COMPLETED,
        result_available=True,
        trace_references=trace_refs,
    )


def adapt_price(result: PriceIntelligenceResult) -> CapabilityExecution:
    if result.pr_status == "PR_NOT_JUSTIFIABLE":
        return CapabilityExecution(
            capability="PRICE",
            status=O1ExecutionStatus.NOT_EVALUABLE,
            result_available=False,
            trace_references=result.trace_references,
            unresolved_items=("PRICE_NOT_JUSTIFIABLE",),
        )
    return CapabilityExecution(
        capability="PRICE",
        status=O1ExecutionStatus.COMPLETED,
        result_available=True,
        trace_references=result.trace_references,
        unresolved_items=result.pr_limitations if result.pr_status == "PR_LIMITED" else (),
    )


def adapt_tco(result: TCOResult) -> CapabilityExecution:
    if result.complete:
        return CapabilityExecution(
            capability="TCO",
            status=O1ExecutionStatus.COMPLETED,
            result_available=True,
            unresolved_items=(),
        )
    return CapabilityExecution(
        capability="TCO",
        status=O1ExecutionStatus.PARTIALLY_COMPLETED,
        result_available=False,
        unresolved_items=result.unresolved_components or ("TCO_INCOMPLETE",),
    )


def adapt_qtg(result: QualityTrustResult) -> CapabilityExecution:
    return CapabilityExecution(
        capability="QTG",
        status=O1ExecutionStatus.COMPLETED,
        result_available=True,
        trace_references=tuple(
            ref for check in result.checks for ref in check.evidence_refs
        ),
    )


__all__ = ["adapt_c0", "adapt_price", "adapt_qtg", "adapt_tco"]
