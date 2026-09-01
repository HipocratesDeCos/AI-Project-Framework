"""Deterministic CRC-MVP consolidation."""
from __future__ import annotations

from collections import defaultdict

from .models import CRCConflict, CRCInput, CRCResult

_EFFECT_PRIORITY = {"R0": 0, "R1": 1, "R2": 2, "R3": 3}
_EFFECT_RESULT = {
    "R0": "NO COMPRAR",
    "R1": "COMPRAR CONDICIONADO",
    "R2": "NEGOCIAR",
}


def consolidate_crc(payload: CRCInput) -> CRCResult:
    """Consolidate authorized Assessment effects without scoring or override.

    Rule metadata is resolved externally and must match the DecisionContext
    rules version. NOT_EVALUABLE remains distinct from FALSE and only produces
    INFORMATION INSUFFICIENT when no higher-priority actionable effect exists.
    """
    metadata = {item.rule_id: item for item in payload.rule_metadata}

    if len(metadata) != len(payload.rule_metadata):
        raise ValueError("CRC requiere un único metadato normativo por rule_id")

    effects: dict[str, list[str]] = defaultdict(list)
    unresolved: list[str] = []

    for assessment in payload.assessments:
        item = metadata.get(assessment.rule_id)
        if item is None:
            raise ValueError(f"Regla no resuelta: {assessment.rule_id}")
        if item.version != payload.decision_context.rules_version:
            raise ValueError(f"Versión incompatible para regla: {assessment.rule_id}")

        if assessment.status == "NOT_EVALUABLE":
            unresolved.append(assessment.rule_id)
            continue

        if assessment.outcome == "FALSE":
            effects[item.effect].append(item.rule_id)

    active_effects = tuple(sorted(effects, key=lambda effect: _EFFECT_PRIORITY[effect]))
    conflicts: tuple[CRCConflict, ...] = ()
    if len(active_effects) > 1:
        conflicts = (
            CRCConflict(
                effects=active_effects,
                rule_ids=tuple(
                    rule_id
                    for effect in active_effects
                    for rule_id in effects[effect]
                ),
            ),
        )

    if "R0" in effects:
        dominant_effect = "R0"
    elif "R1" in effects:
        dominant_effect = "R1"
    elif "R2" in effects:
        dominant_effect = "R2"
    elif unresolved:
        dominant_effect = None
    else:
        dominant_effect = "R3"

    if dominant_effect is None:
        result = "INFORMACIÓN INSUFICIENTE"
        reason = "Existe al menos una evaluación no evaluable sin un efecto accionable de mayor precedencia."
    elif dominant_effect == "R3":
        result = "COMPRAR"
        reason = "No existe un efecto R0, R1 o R2 incumplido."
    else:
        result = _EFFECT_RESULT[dominant_effect]
        rule_id = effects[dominant_effect][0]
        reason = f"Resultado determinado por {rule_id} con efecto {dominant_effect}."

    relevant = tuple(
        f"{rule_id}: {effect}"
        for effect in active_effects
        for rule_id in effects[effect]
        if effect != dominant_effect
    )
    if unresolved:
        relevant += tuple(f"{rule_id}: NOT_EVALUABLE" for rule_id in unresolved)

    return CRCResult(
        consolidated_result=result,
        dominant_reason=reason,
        relevant_factors=relevant,
        conflicts=conflicts,
        traceability=tuple(
            [f"Assessment:{assessment.rule_id}" for assessment in payload.assessments]
            + [f"Rule:{rule_id}" for rule_id in metadata]
        ),
    )


__all__ = ["consolidate_crc"]
