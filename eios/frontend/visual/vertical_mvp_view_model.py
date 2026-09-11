"""Pure presentation mapping for the Vertical MVP support result.

This adapter consumes only the payload already produced by the U1 application
boundary. It does not execute capabilities, evaluate rules, recalculate CRC, or
create decision authority.
"""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any


def build_vertical_mvp_view_model(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    """Create a presentation-only copy of an existing Vertical MVP UI payload."""
    if not isinstance(payload, Mapping):
        raise TypeError("se requiere un payload contractual de Vertical MVP")

    execution = payload.get("execution")
    if not isinstance(execution, Mapping):
        raise ValueError("execution debe ser un Mapping")

    rules = payload.get("rules")
    if rules is not None and not isinstance(rules, Mapping):
        raise ValueError("rules debe ser null o un Mapping")

    view: dict[str, Any] = {
        "execution_status": execution.get("status"),
        "policy_version": execution.get("policy_version"),
        "failure_reason": execution.get("failure_reason"),
        "unresolved_items": deepcopy(execution.get("unresolved_items", [])),
        "capabilities": deepcopy(execution.get("capabilities", [])),
        "rules_available": rules is not None,
        "rule_coverage": None,
        "crc_support_result": None,
        "assessments": None,
        "rule_trace_references": None,
    }

    if rules is None:
        return view

    view["rule_coverage"] = {
        "executed_rule_ids": deepcopy(rules.get("executed_rule_ids", [])),
        "omitted_rule_ids": deepcopy(rules.get("omitted_rule_ids", [])),
    }
    view["crc_support_result"] = {
        "consolidated_result": rules.get("consolidated_result"),
        "dominant_reason": rules.get("dominant_reason"),
        "relevant_factors": deepcopy(rules.get("relevant_factors", [])),
        "conflicts": deepcopy(rules.get("conflicts", [])),
    }
    view["assessments"] = deepcopy(rules.get("assessments", []))
    view["rule_trace_references"] = deepcopy(rules.get("trace_references", []))
    return view


__all__ = ["build_vertical_mvp_view_model"]
