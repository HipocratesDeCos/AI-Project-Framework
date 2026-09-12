"""Adapt closed O2 scenario coordination into one Vertical MVP capability.

This module is descriptive only. It does not execute scenarios, interpret
analytical content, rank alternatives, or make a business decision.
"""
from __future__ import annotations

from .models import DecisionContext
from .o2 import O2ScenarioStatus, O2SupportPackage
from .orchestration import CapabilityExecution, O1ExecutionStatus


_STATUS_MAP = {
    O2ScenarioStatus.READY: O1ExecutionStatus.READY,
    O2ScenarioStatus.RUNNING: O1ExecutionStatus.RUNNING,
    O2ScenarioStatus.COMPLETED: O1ExecutionStatus.COMPLETED,
    O2ScenarioStatus.BLOCKED: O1ExecutionStatus.BLOCKED,
    O2ScenarioStatus.PARTIALLY_COMPLETED: O1ExecutionStatus.PARTIALLY_COMPLETED,
    O2ScenarioStatus.NOT_EVALUABLE: O1ExecutionStatus.NOT_EVALUABLE,
    O2ScenarioStatus.FAILED: O1ExecutionStatus.FAILED,
}


def validate_scenario_coordination_context(
    result: O2SupportPackage,
    context: DecisionContext,
) -> None:
    """Reject an O2 package that belongs to a different execution context."""
    execution = result.execution_context
    if execution.decision_id != context.decision_id:
        raise ValueError("O2 decision_id incoherente con DecisionContext")
    if execution.rules_version != context.rules_version:
        raise ValueError("O2 rules_version incoherente con DecisionContext")
    if execution.parameters_version != context.parameters_version:
        raise ValueError("O2 parameters_version incoherente con DecisionContext")
    if execution.data_snapshot_id != context.data_snapshot_id:
        raise ValueError("O2 data_snapshot_id incoherente con DecisionContext")


def adapt_scenario_coordination(result: O2SupportPackage) -> CapabilityExecution:
    """Represent an already-built O2 package in the O1 execution envelope."""
    if not result.scenarios:
        raise ValueError("SCENARIO_COORDINATION requiere escenarios O2")

    statuses = tuple(item.status for item in result.scenarios)
    failed_ids = tuple(
        sorted(item.scenario_id for item in result.scenarios if item.status == O2ScenarioStatus.FAILED)
    )

    if failed_ids:
        status = O1ExecutionStatus.FAILED
    elif all(item == O2ScenarioStatus.COMPLETED for item in statuses):
        status = O1ExecutionStatus.COMPLETED
    elif len(set(statuses)) == 1:
        status = _STATUS_MAP[statuses[0]]
    else:
        status = O1ExecutionStatus.PARTIALLY_COMPLETED

    trace_references = tuple(
        sorted({ref for item in result.scenarios for ref in item.trace_references})
    )

    unresolved: set[str] = set()
    for item in result.scenarios:
        for unresolved_item in item.unresolved_items:
            unresolved.add(f"{item.scenario_id}:{unresolved_item}")
        if item.status != O2ScenarioStatus.COMPLETED and not item.unresolved_items:
            unresolved.add(f"{item.scenario_id}:{item.status.value}")

    failure_reason = None
    if failed_ids:
        failure_reason = "FAILED scenarios: " + ", ".join(failed_ids)

    return CapabilityExecution(
        capability="SCENARIO_COORDINATION",
        status=status,
        result_available=status == O1ExecutionStatus.COMPLETED,
        trace_references=trace_references,
        unresolved_items=tuple(sorted(unresolved)),
        failure_reason=failure_reason,
    )


__all__ = ["adapt_scenario_coordination", "validate_scenario_coordination_context"]
