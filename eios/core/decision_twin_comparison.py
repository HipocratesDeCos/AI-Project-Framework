"""Minimal structural comparison model for Decision Twin.

This module deliberately does not implement scoring, ranking, selection,
optimization, or business decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class AlternativeRepresentation:
    """Ephemeral representation of an alternative; no Alternative_ID."""

    representation_ref: str
    values: Mapping[str, Any]
    scenario_ref: str | None = None
    viability: Any = None
    consequences: Mapping[str, Any] | None = None
    trace_refs: Sequence[str] = ()


@dataclass(frozen=True)
class Comparison:
    """Descriptive comparison only."""

    alternatives: tuple[str, ...]
    observations: Mapping[str, Mapping[str, Any]]
    differences: Mapping[str, tuple[Any, ...]]
    missing: Mapping[str, tuple[str, ...]]
    traceability: Mapping[str, tuple[str, ...]]


def compare(alternatives: Sequence[AlternativeRepresentation]) -> Comparison:
    """Compare two or more representations without inferring preference."""
    if len(alternatives) < 2:
        raise ValueError("comparison requires at least two alternatives")

    refs = tuple(a.representation_ref for a in alternatives)
    if len(set(refs)) != len(refs):
        raise ValueError("representation_ref must be unique within a comparison")

    keys = sorted({key for alt in alternatives for key in alt.values})
    observations: dict[str, dict[str, Any]] = {}
    differences: dict[str, tuple[Any, ...]] = {}
    missing: dict[str, tuple[str, ...]] = {}
    traces: dict[str, tuple[str, ...]] = {}

    for key in keys:
        row: dict[str, Any] = {}
        absent: list[str] = []
        for alt in alternatives:
            if key in alt.values:
                row[alt.representation_ref] = alt.values[key]
            else:
                absent.append(alt.representation_ref)
        observations[key] = row
        values = tuple(row.values())
        if len(set(map(repr, values))) > 1:
            differences[key] = values
        if absent:
            missing[key] = tuple(absent)

    for alt in alternatives:
        traces[alt.representation_ref] = tuple(alt.trace_refs)

    return Comparison(
        alternatives=refs,
        observations=observations,
        differences=differences,
        missing=missing,
        traceability=traces,
    )
