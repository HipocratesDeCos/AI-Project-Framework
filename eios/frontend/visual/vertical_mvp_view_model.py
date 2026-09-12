"""Pure presentation mapping for the Vertical MVP support result.

This adapter consumes only the payload already produced by the U1 application
boundary. It does not execute capabilities, evaluate rules, recalculate CRC,
recalculate scenario comparison, or create decision authority.
"""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any


_EXECUTION_KEYS = frozenset(
    {"status", "policy_version", "unresolved_items", "failure_reason", "capabilities"}
)
_RULE_KEYS = frozenset(
    {
        "executed_rule_ids",
        "omitted_rule_ids",
        "consolidated_result",
        "dominant_reason",
        "relevant_factors",
        "conflicts",
        "assessments",
        "trace_references",
    }
)
_SCENARIO_SUPPORT_KEYS = frozenset({"execution_context", "scenarios", "comparison"})
_SCENARIO_CONTEXT_KEYS = frozenset(
    {
        "execution_id",
        "decision_id",
        "rules_version",
        "parameters_version",
        "data_snapshot_id",
    }
)
_SCENARIO_RECORD_KEYS = frozenset(
    {
        "scenario_id",
        "status",
        "values",
        "trace_references",
        "unresolved_items",
        "failure_reason",
    }
)
_SCENARIO_COMPARISON_KEYS = frozenset(
    {
        "scenario_ids",
        "observations",
        "differences",
        "missing",
        "statuses",
        "unresolved_items",
        "traceability",
    }
)


def _require_keys(section: Mapping[str, Any], required: frozenset[str], name: str) -> None:
    missing = required.difference(section.keys())
    if missing:
        raise ValueError(f"{name} carece de claves contractuales: {', '.join(sorted(missing))}")


def _validate_scenario_support(section: Mapping[str, Any]) -> None:
    _require_keys(section, _SCENARIO_SUPPORT_KEYS, "scenario_support")

    context = section["execution_context"]
    if not isinstance(context, Mapping):
        raise ValueError("scenario_support.execution_context debe ser un Mapping")
    _require_keys(context, _SCENARIO_CONTEXT_KEYS, "scenario_support.execution_context")

    scenarios = section["scenarios"]
    if not isinstance(scenarios, (list, tuple)):
        raise ValueError("scenario_support.scenarios debe ser una secuencia de registros")
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, Mapping):
            raise ValueError(f"scenario_support.scenarios[{index}] debe ser un Mapping")
        _require_keys(
            scenario,
            _SCENARIO_RECORD_KEYS,
            f"scenario_support.scenarios[{index}]",
        )

    comparison = section["comparison"]
    if comparison is not None:
        if not isinstance(comparison, Mapping):
            raise ValueError("scenario_support.comparison debe ser null o un Mapping")
        _require_keys(
            comparison,
            _SCENARIO_COMPARISON_KEYS,
            "scenario_support.comparison",
        )


def build_vertical_mvp_view_model(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    """Create a presentation-only copy of an existing Vertical MVP UI payload."""
    if not isinstance(payload, Mapping):
        raise TypeError("se requiere un payload contractual de Vertical MVP")
    if "rules" not in payload:
        raise ValueError("payload carece de la clave contractual rules")
    if "scenario_support" not in payload:
        raise ValueError("payload carece de la clave contractual scenario_support")

    execution = payload.get("execution")
    if not isinstance(execution, Mapping):
        raise ValueError("execution debe ser un Mapping")
    _require_keys(execution, _EXECUTION_KEYS, "execution")

    rules = payload["rules"]
    if rules is not None and not isinstance(rules, Mapping):
        raise ValueError("rules debe ser null o un Mapping")

    scenario_support = payload["scenario_support"]
    if scenario_support is not None and not isinstance(scenario_support, Mapping):
        raise ValueError("scenario_support debe ser null o un Mapping")

    view: dict[str, Any] = {
        "execution_status": execution["status"],
        "policy_version": execution["policy_version"],
        "failure_reason": execution["failure_reason"],
        "unresolved_items": deepcopy(execution["unresolved_items"]),
        "capabilities": deepcopy(execution["capabilities"]),
        "rules_available": rules is not None,
        "rule_coverage": None,
        "crc_support_result": None,
        "assessments": None,
        "rule_trace_references": None,
        "scenario_support_available": scenario_support is not None,
        "scenario_execution_context": None,
        "scenario_records": None,
        "scenario_comparison": None,
    }

    if rules is not None:
        _require_keys(rules, _RULE_KEYS, "rules")
        view["rule_coverage"] = {
            "executed_rule_ids": deepcopy(rules["executed_rule_ids"]),
            "omitted_rule_ids": deepcopy(rules["omitted_rule_ids"]),
        }
        view["crc_support_result"] = {
            "consolidated_result": rules["consolidated_result"],
            "dominant_reason": rules["dominant_reason"],
            "relevant_factors": deepcopy(rules["relevant_factors"]),
            "conflicts": deepcopy(rules["conflicts"]),
        }
        view["assessments"] = deepcopy(rules["assessments"])
        view["rule_trace_references"] = deepcopy(rules["trace_references"])

    if scenario_support is not None:
        _validate_scenario_support(scenario_support)
        view["scenario_execution_context"] = deepcopy(
            scenario_support["execution_context"]
        )
        view["scenario_records"] = deepcopy(scenario_support["scenarios"])
        view["scenario_comparison"] = deepcopy(scenario_support["comparison"])

    return view


__all__ = ["build_vertical_mvp_view_model"]
