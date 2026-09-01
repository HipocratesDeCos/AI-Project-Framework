"""Structural, non-decisional comparison engine for Decision Twin."""
from __future__ import annotations

from typing import Any

from .decision_twin import (
    AlternativeRepresentation,
    ComparisonObservation,
    DecisionTwinComparison,
    DecisionTwinComparisonInput,
)


def _attributes(alternative: AlternativeRepresentation) -> dict[str, Any]:
    """Expose only already-authorized values; no source calculation is performed."""
    values: dict[str, Any] = {}
    if alternative.viability is not None:
        values["viability"] = alternative.viability
    values["results"] = alternative.results
    values["conditions"] = alternative.conditions
    values["consequences"] = alternative.consequences
    values["risk_refs"] = alternative.risk_refs
    return values


def compare_alternatives(
    comparison_input: DecisionTwinComparisonInput,
) -> DecisionTwinComparison:
    """Compare two or more representations descriptively.

    The function deliberately does not score, rank, select, optimize, or decide.
    """
    alternatives = tuple(
        sorted(comparison_input.alternatives, key=lambda item: item.representation_ref)
    )
    refs = tuple(item.representation_ref for item in alternatives)
    by_ref = {item.representation_ref: _attributes(item) for item in alternatives}
    attributes = sorted({name for values in by_ref.values() for name in values})

    observations: list[ComparisonObservation] = []
    common: list[str] = []
    differences: list[str] = []
    missing: list[str] = []
    viability_differences: list[str] = []
    consequence_differences: list[str] = []
    trace_refs: set[str] = set()

    for alternative in alternatives:
        trace_refs.update(alternative.trace_refs)

    for attribute in attributes:
        values: list[tuple[str, Any]] = []
        present = 0
        attribute_traces: set[str] = set()
        for alternative in alternatives:
            data = by_ref[alternative.representation_ref]
            if attribute in data:
                values.append((alternative.representation_ref, data[attribute]))
                present += 1
            else:
                values.append((alternative.representation_ref, None))
            attribute_traces.update(alternative.trace_refs)

        comparable = present == len(alternatives)
        observed = tuple(value for _, value in values if value is not None)
        different = comparable and any(value != observed[0] for value in observed[1:])

        if not comparable:
            for ref, value in values:
                if value is None:
                    missing.append(f"{ref}:{attribute}")
        elif different:
            differences.append(attribute)
            if attribute == "viability":
                viability_differences.append(attribute)
            if attribute == "consequences":
                consequence_differences.append(attribute)
        else:
            common.append(attribute)

        observations.append(
            ComparisonObservation(
                attribute=attribute,
                values=tuple(values),
                comparable=comparable,
                difference=different,
                trace_refs=tuple(sorted(attribute_traces)),
            )
        )

    return DecisionTwinComparison(
        alternatives=refs,
        observations=tuple(observations),
        common_values=tuple(common),
        differences=tuple(differences),
        missing_attributes=tuple(sorted(missing)),
        viability_differences=tuple(viability_differences),
        consequence_differences=tuple(consequence_differences),
        trace_refs=tuple(sorted(trace_refs)),
    )


__all__ = ["compare_alternatives"]
