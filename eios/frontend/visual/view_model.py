"""Pure presentation mapping for the U1.1 visual frontend."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def _dump(value: Any) -> Mapping[str, Any]:
    if not hasattr(value, "model_dump"):
        raise TypeError("se requiere un modelo contractual")
    return value.model_dump(mode="json")


def build_view_model(support_package: Any) -> Mapping[str, Any]:
    """Create a presentation-only copy of an existing support package.

    No calculations, decisions, rankings or engine calls are performed.
    """
    data = dict(_dump(support_package))
    return {
        "execution": data.get("execution", {}),
        "result": data.get("result", data.get("assessment", {})),
        "evidence": data.get("evidence", []),
        "trace": data.get("trace", data.get("trace_references", [])),
        "scenarios": data.get("scenarios", []),
        "limitations": data.get("limitations", []),
        "identity": {
            key: data.get(key)
            for key in (
                "decision_id",
                "scenario_id",
                "execution_id",
                "rules_version",
                "parameters_version",
                "data_snapshot_id",
            )
            if key in data
        },
    }
