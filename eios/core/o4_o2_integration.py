"""Controlled O4 -> O2 scenario materialization.

The integration invokes the closed O4 generator and immediately delegates
scenario identity, canonicalization and versioning to the closed O2 Scenario
Engine using the same DecisionContext snapshot. It does not evaluate O3 or
create business decision authority.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, model_validator

from .models import DecisionContext
from .scenario_engine import ScenarioVersion, create_scenario
from .scenario_generation import (
    GenerationPolicy,
    GenerationResult,
    GenerationStatus,
    GenerationVariable,
    generate_scenarios,
)


class O4O2MaterializationResult(BaseModel):
    """Immutable integration output preserving O4 source and O2 materialization."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    generation: GenerationResult
    scenarios: tuple[ScenarioVersion, ...] = ()

    @model_validator(mode="after")
    def validate_materialization(self) -> "O4O2MaterializationResult":
        if self.generation.status == GenerationStatus.GENERATED:
            if len(self.scenarios) != len(self.generation.candidates):
                raise ValueError(
                    "GENERATED requiere una materialización O2 por candidato O4"
                )
        elif self.scenarios:
            raise ValueError(
                "Solo GENERATED puede contener escenarios materializados"
            )
        return self


def run_o4_o2_materialization(
    *,
    context: DecisionContext,
    variables: tuple[GenerationVariable, ...],
    policy: GenerationPolicy,
    parent_scenario_id: str | None = None,
    depth: int = 0,
) -> O4O2MaterializationResult:
    """Generate O4 candidates and materialize them through O2 in one context.

    No detached ``GenerationResult`` is accepted here because that model does
    not carry decision/version/snapshot provenance. The integration therefore
    binds generation and materialization to the same deep-copied context.
    """
    context_snapshot = context.model_copy(deep=True)
    variables_snapshot = tuple(item.model_copy(deep=True) for item in variables)
    policy_snapshot = policy.model_copy(deep=True)

    generation = generate_scenarios(
        context_snapshot,
        variables_snapshot,
        policy_snapshot,
        parent_scenario_id=parent_scenario_id,
        depth=depth,
    )
    generation_snapshot = generation.model_copy(deep=True)

    if generation_snapshot.status != GenerationStatus.GENERATED:
        return O4O2MaterializationResult(
            generation=generation_snapshot,
            scenarios=(),
        )

    scenarios = tuple(
        create_scenario(
            context_snapshot.model_copy(deep=True),
            changes=tuple(change.model_copy(deep=True) for change in candidate.changes),
            parent_scenario_id=candidate.parent_scenario_id,
            validate=True,
        )
        for candidate in generation_snapshot.candidates
    )

    return O4O2MaterializationResult(
        generation=generation_snapshot,
        scenarios=scenarios,
    )


__all__ = ["O4O2MaterializationResult", "run_o4_o2_materialization"]
