"""Pure presentation mapping for the U1.1 visual frontend."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def _dump(value: Any) -> Mapping[str, Any]:
    if not hasattr(value, "model_dump"):
        raise TypeError("se requiere un modelo contractual")
    return value.model_dump(mode="json")


def build_view_model(support_package: Any) -> Mapping[str, Any]:
    """Create a presentation-only copy of an existing O1 support package."""
    data = dict(_dump(support_package))
    context = dict(data.get("execution_context", {}))
    return {
        "execution_status": data.get("execution_status"),
        "capability_results": data.get("capability_results", []),
        "evidence_status": data.get("evidence_status", []),
        "trace_references": data.get("trace_references", []),
        "unresolved_items": data.get("unresolved_items", []),
        "identity": {
            key: context[key]
            for key in (
                "execution_id",
                "decision_id",
                "scenario_id",
                "rules_version",
                "parameters_version",
                "data_snapshot_id",
            )
            if key in context
        },
    }
