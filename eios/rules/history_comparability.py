"""Provenance-safe executable bridge for R-HIS-003."""
from __future__ import annotations

from eios.core.models import Assessment, DecisionContext, Evidence, PurchaseOperation, Rule
from eios.pricing.historical_comparability import (
    HistoricalComparabilityDimensionDetermination,
    build_historical_commercial_comparability_observation,
)
from eios.pricing.models import PriceReference

R_HIS_003 = "R-HIS-003"


def _validate_identity(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
) -> None:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    if rule.rule_id != R_HIS_003:
        raise ValueError("El bridge solo evalúa R-HIS-003")
    if rule.version != context.rules_version:
        raise ValueError("Rule.version incompatible con DecisionContext.rules_version")
    if not rule.requires_evidence:
        raise ValueError("R-HIS-003 requiere evidencia")


def evaluate_r_his_003(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    reference: PriceReference,
    dimension_determinations: tuple[
        HistoricalComparabilityDimensionDetermination, ...
    ],
    dimension_evidences: tuple[Evidence, ...],
) -> Assessment:
    """Evaluate R-HIS-003 by rebuilding the authorized comparability carrier."""

    _validate_identity(purchase=purchase, context=context, rule=rule)

    if reference.operation_date > purchase.operation_date:
        return Assessment(
            rule_id=R_HIS_003,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=[item.evidence_id for item in dimension_evidences],
            reason="R-HIS-003 no evaluable: referencia histórica futura.",
        )

    observation = build_historical_commercial_comparability_observation(
        purchase=purchase,
        context=context,
        reference=reference,
        dimension_determinations=dimension_determinations,
        dimension_evidences=dimension_evidences,
    )
    evidence_ids = list(observation.evidence_ids)

    if observation.state == "NOT_DETERMINABLE":
        return Assessment(
            rule_id=R_HIS_003,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason=(
                "R-HIS-003 no evaluable: comparabilidad comercial "
                "no determinable en todas las dimensiones necesarias."
            ),
        )

    triggered = observation.state == "NON_COMPARABLE"
    return Assessment(
        rule_id=R_HIS_003,
        status="EVALUABLE",
        outcome="TRUE" if triggered else "FALSE",
        evidence_ids=evidence_ids,
        reason=(
            "R-HIS-003 demostrada: existe una diferencia comercial material autorizada."
            if triggered
            else "R-HIS-003 no demostrada: las siete dimensiones son comparables o no aplicables."
        ),
    )


__all__ = ["R_HIS_003", "evaluate_r_his_003"]
