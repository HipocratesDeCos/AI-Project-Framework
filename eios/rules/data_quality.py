"""Rules-layer bridge for DAT001 data freshness authority."""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal, InvalidOperation

from eios.core.models import Assessment, DecisionContext, Evidence, PurchaseOperation, Rule
from eios.core.validation import validate_evidence
from eios.data_freshness import (
    DATA_SNAPSHOT_FRESHNESS_EVIDENCE_SOURCE_TYPE,
    DataSnapshotFreshnessObservation,
    data_snapshot_freshness_ref,
    data_snapshot_purchase_ref,
)
from eios.parameters import ResolvedConfiguration


R_DAT_001 = "R-DAT-001"
R_DAT_002 = "R-DAT-002"
P_DAT_001 = "P-DAT-001"
PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE = "ParameterConfigurationEvidence"


def _validate_identity(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    observation: DataSnapshotFreshnessObservation,
) -> None:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    if rule.rule_id != R_DAT_001:
        raise ValueError("El bridge solo evalúa R-DAT-001")
    if rule.version != context.rules_version:
        raise ValueError("Rule.version incompatible con DecisionContext.rules_version")
    if not rule.requires_evidence:
        raise ValueError("R-DAT-001 requiere evidencia")
    if observation.decision_id != context.decision_id:
        raise ValueError("DataSnapshotFreshnessObservation pertenece a otra decisión")
    if observation.scenario_id != context.scenario_id:
        raise ValueError("DataSnapshotFreshnessObservation pertenece a otro escenario")
    if observation.data_snapshot_id != context.data_snapshot_id:
        raise ValueError("DataSnapshotFreshnessObservation pertenece a otro data_snapshot_id")
    if observation.evaluation_date != purchase.operation_date:
        raise ValueError("DataSnapshotFreshnessObservation usa otra evaluation_date")
    if observation.purchase_operation_ref != data_snapshot_purchase_ref(purchase):
        raise ValueError("DataSnapshotFreshnessObservation no está vinculada a la PurchaseOperation exacta")


def _validate_observation_evidence(
    observation: DataSnapshotFreshnessObservation,
    evidence: Evidence,
) -> None:
    if evidence.source_type != DATA_SNAPSHOT_FRESHNESS_EVIDENCE_SOURCE_TYPE:
        raise ValueError("freshness_evidence.source_type incompatible")
    if evidence.captured_at != observation.evaluation_date:
        raise ValueError("freshness_evidence debe corresponder a evaluation_date")
    if (
        evidence.state == "DEMONSTRATED"
        and evidence.demonstration_ref != data_snapshot_freshness_ref(observation)
    ):
        raise ValueError("freshness_evidence no está vinculada a DataSnapshotFreshnessObservation")


def _validated_weeks(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    company_scope: str,
    resolved: ResolvedConfiguration,
    evidence: Evidence,
) -> int | None:
    if resolved.parameter_id != P_DAT_001:
        raise ValueError("R-DAT-001 requiere P-DAT-001")
    if resolved.parameters_version != context.parameters_version:
        raise ValueError("P-DAT-001 está vinculada a otra parameters_version")
    if resolved.company_id != company_scope:
        raise ValueError("P-DAT-001 pertenece a otro company_scope")
    if resolved.effective_at.date() != purchase.operation_date:
        raise ValueError("P-DAT-001 debe resolverse para evaluation_date")

    configuration = resolved.configuration
    try:
        active = configuration.valid_from <= resolved.effective_at and (
            configuration.valid_to is None
            or resolved.effective_at < configuration.valid_to
        )
    except TypeError as exc:
        raise ValueError("P-DAT-001 usa semántica temporal incompatible") from exc
    if not active:
        raise ValueError("P-DAT-001 no está vigente en effective_at")

    if evidence.source_type != PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE:
        raise ValueError("parameter_evidence.source_type incompatible")
    if evidence.captured_at != purchase.operation_date:
        raise ValueError("parameter_evidence debe corresponder a evaluation_date")
    if (
        evidence.state == "DEMONSTRATED"
        and evidence.demonstration_ref != resolved.configuration_ref
    ):
        raise ValueError("parameter_evidence no está vinculada a P-DAT-001")
    if resolved.unit != "semanas":
        return None

    try:
        value = Decimal(resolved.value)
    except (InvalidOperation, ValueError, TypeError):
        return None
    if not value.is_finite() or value <= 0 or value != value.to_integral_value():
        return None
    return int(value)


def evaluate_r_dat_001(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    observation: DataSnapshotFreshnessObservation,
    freshness_evidence: Evidence,
    maximum_age_resolution: ResolvedConfiguration | None,
    parameter_evidence: Evidence | None,
) -> Assessment:
    """Evaluate whether the selected snapshot is inside P-DAT-001."""
    _validate_identity(purchase, context, rule, observation)
    _validate_observation_evidence(observation, freshness_evidence)
    evidence_ids = [freshness_evidence.evidence_id]

    if validate_evidence(freshness_evidence).status != "VALID":
        return Assessment(
            rule_id=R_DAT_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-DAT-001 no evaluable: frescura del snapshot no demostrada.",
        )
    if observation.state != "AVAILABLE":
        return Assessment(
            rule_id=R_DAT_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason=f"R-DAT-001 no evaluable: estado de frescura {observation.state}.",
        )
    updated = observation.source_updated_date
    if updated is None:
        return Assessment(
            rule_id=R_DAT_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-DAT-001 no evaluable: source_updated_date ausente.",
        )
    if updated > observation.evaluation_date:
        return Assessment(
            rule_id=R_DAT_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-DAT-001 no evaluable: source_updated_date futura.",
        )

    if maximum_age_resolution is None or parameter_evidence is None:
        return Assessment(
            rule_id=R_DAT_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-DAT-001 no evaluable: P-DAT-001 no resuelta/evidenciada.",
        )

    evidence_ids.append(parameter_evidence.evidence_id)
    weeks = _validated_weeks(
        purchase=purchase,
        context=context,
        company_scope=observation.company_scope,
        resolved=maximum_age_resolution,
        evidence=parameter_evidence,
    )
    if validate_evidence(parameter_evidence).status != "VALID" or weeks is None:
        return Assessment(
            rule_id=R_DAT_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-DAT-001 no evaluable: P-DAT-001 no utilizable.",
        )

    cutoff = observation.evaluation_date - timedelta(days=weeks * 7)
    fresh = updated >= cutoff
    return Assessment(
        rule_id=R_DAT_001,
        status="EVALUABLE",
        outcome="TRUE" if fresh else "FALSE",
        evidence_ids=evidence_ids,
        reason=(
            "R-DAT-001 demostrada: snapshot dentro del horizonte P-DAT-001."
            if fresh
            else "R-DAT-001 no demostrada: snapshot anterior al horizonte P-DAT-001."
        ),
    )


def _validate_dat002_identity(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    observation: DataSnapshotFreshnessObservation,
) -> None:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    if rule.rule_id != R_DAT_002:
        raise ValueError("El bridge solo evalúa R-DAT-002")
    if rule.version != context.rules_version:
        raise ValueError("Rule.version incompatible con DecisionContext.rules_version")
    if not rule.requires_evidence:
        raise ValueError("R-DAT-002 requiere evidencia")
    if observation.decision_id != context.decision_id:
        raise ValueError("DataSnapshotFreshnessObservation pertenece a otra decisión")
    if observation.scenario_id != context.scenario_id:
        raise ValueError("DataSnapshotFreshnessObservation pertenece a otro escenario")
    if observation.data_snapshot_id != context.data_snapshot_id:
        raise ValueError("DataSnapshotFreshnessObservation pertenece a otro data_snapshot_id")
    if observation.evaluation_date != purchase.operation_date:
        raise ValueError("DataSnapshotFreshnessObservation usa otra evaluation_date")
    if observation.purchase_operation_ref != data_snapshot_purchase_ref(purchase):
        raise ValueError("DataSnapshotFreshnessObservation no está vinculada a la PurchaseOperation exacta")


def evaluate_r_dat_002(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    observation: DataSnapshotFreshnessObservation,
    freshness_evidence: Evidence,
    maximum_age_resolution: ResolvedConfiguration | None,
    parameter_evidence: Evidence | None,
) -> Assessment:
    """Evaluate whether the selected snapshot exceeds P-DAT-001 maximum age."""
    _validate_dat002_identity(purchase, context, rule, observation)
    _validate_observation_evidence(observation, freshness_evidence)
    evidence_ids = [freshness_evidence.evidence_id]

    if validate_evidence(freshness_evidence).status != "VALID":
        return Assessment(
            rule_id=R_DAT_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-DAT-002 no evaluable: frescura del snapshot no demostrada.",
        )
    if observation.state != "AVAILABLE":
        return Assessment(
            rule_id=R_DAT_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason=f"R-DAT-002 no evaluable: estado de frescura {observation.state}.",
        )

    updated = observation.source_updated_date
    if updated is None:
        return Assessment(
            rule_id=R_DAT_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-DAT-002 no evaluable: source_updated_date ausente.",
        )
    if updated > observation.evaluation_date:
        return Assessment(
            rule_id=R_DAT_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-DAT-002 no evaluable: source_updated_date futura.",
        )
    if maximum_age_resolution is None or parameter_evidence is None:
        return Assessment(
            rule_id=R_DAT_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-DAT-002 no evaluable: P-DAT-001 no resuelta/evidenciada.",
        )

    evidence_ids.append(parameter_evidence.evidence_id)
    weeks = _validated_weeks(
        purchase=purchase,
        context=context,
        company_scope=observation.company_scope,
        resolved=maximum_age_resolution,
        evidence=parameter_evidence,
    )
    if validate_evidence(parameter_evidence).status != "VALID" or weeks is None:
        return Assessment(
            rule_id=R_DAT_002,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-DAT-002 no evaluable: P-DAT-001 no utilizable.",
        )

    cutoff = observation.evaluation_date - timedelta(days=weeks * 7)
    stale = updated < cutoff
    return Assessment(
        rule_id=R_DAT_002,
        status="EVALUABLE",
        outcome="TRUE" if stale else "FALSE",
        evidence_ids=evidence_ids,
        reason=(
            "R-DAT-002 demostrada: snapshot supera el horizonte P-DAT-001."
            if stale
            else "R-DAT-002 no demostrada: snapshot no supera el horizonte P-DAT-001."
        ),
    )


__all__ = [
    "P_DAT_001",
    "R_DAT_001",
    "R_DAT_002",
    "evaluate_r_dat_001",
    "evaluate_r_dat_002",
]
