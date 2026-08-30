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
    scenario_refs: Mapping[str, str | None]
    observations: Mapping[str, Mapping[str, Any]]
    differences: Mapping[str, tuple[Any, ...]]
    missing: Mapping[str, tuple[str, ...]]
    viability: Mapping[str, Any]
    viability_differences: tuple[Any, ...]
    consequence_observations: Mapping[str, Mapping[str, Any]]
    consequence_differences: Mapping[str, tuple[Any, ...]]
    traceability: Mapping[str, tuple[str, ...]]


def _differences(values: Sequence[Any]) -> tuple[Any, ...]:
    if len({repr(value) for value in values}) > 1:
        return tuple(values)
    return ()


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

    for key in keys:
        row: dict[str, Any] = {}
        absent: list[str] = []
        for alt in alternatives:
            if key in alt.values:
                row[alt.representation_ref] = alt.values[key]
            else:
                absent.append(alt.representation_ref)
        observations[key] = row
        diff = _differences(tuple(row.values()))
        if diff:
            differences[key] = diff
        if absent:
            missing[key] = tuple(absent)

    scenario_refs = {
        a.representation_ref: a.scenario_ref for a in alternatives
    }
    viability = {a.representation_ref: a.viability for a in alternatives}
    viability_diff = _differences(tuple(a.viability for a in alternatives))

    consequence_keys = sorted(
        {key for alt in alternatives for key in (alt.consequences or {})}
    )
    consequence_observations: dict[str, dict[str, Any]] = {}
    consequence_differences: dict[str, tuple[Any, ...]] = {}
    for key in consequence_keys:
        row = {
            a.representation_ref: (a.consequences or {})[key]
            for a in alternatives
            if key in (a.consequences or {})
        }
        consequence_observations[key] = row
        diff = _differences(tuple(row.values()))
        if diff:
            consequence_differences[key] = diff

    traces = {
        a.representation_ref: tuple(a.trace_refs)
        for a in alternatives
    }

    return Comparison(
        alternatives=refs,
        scenario_refs=scenario_refs,
        observations=observations,
        differences=differences,
        missing=missing,
        viability=viability,
        viability_differences=viability_diff,
        consequence_observations=consequence_observations,
        consequence_differences=consequence_differences,
        traceability=traces,
    )
