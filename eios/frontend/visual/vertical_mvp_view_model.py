"""Pure presentation mapping for the Vertical MVP support result.

This adapter consumes only the payload already produced by the U1 application
boundary. It does not execute capabilities, evaluate rules, recalculate CRC, or
create decision authority.
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


def _require_keys(section: Mapping[str, Any], required: frozenset[str], name: str) -> None:
    missing = required.difference(section.keys())
    if missing:
        raise ValueError(f"{name} carece de claves contractuales: {', '.join(sorted(missing))}")


def build_vertical_mvp_view_model(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    """Create a presentation-only copy of an existing Vertical MVP UI payload."""
    if not isinstance(payload, Mapping):
        raise TypeError("se requiere un payload contractual de Vertical MVP")
    if "rules" not in payload:
        raise ValueError("payload carece de la clave contractual rules")

    execution = payload.get("execution")
    if not isinstance(execution, Mapping):
        raise ValueError("execution debe ser un Mapping")
    _require_keys(execution, _EXECUTION_KEYS, "execution")

    rules = payload["rules"]
    if rules is not None and not isinstance(rules, Mapping):
        raise ValueError("rules debe ser null o un Mapping")

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
    }

    if rules is None:
        return view

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
    return view


__all__ = ["build_vertical_mvp_view_model"]
