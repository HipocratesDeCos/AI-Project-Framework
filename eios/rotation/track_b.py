"""Provenance-safe ROT001 Track B metric production and rule evaluation."""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal, InvalidOperation

from eios.core.decision_input_package import DecisionInputPackage
from eios.core.models import Assessment, Evidence
from eios.core.validation import validate_evidence
from eios.parameters import ResolvedConfiguration

from .track_b_models import (
    ROTATION_METRIC_UNIT,
    RotationMetricEvidence,
    RotationMetricSourceEvidence,
)


P_ROT_002 = "P-ROT-002"
P_ROT_003 = "P-ROT-003"
P_ROT_002_UNIT = "días"
P_ROT_003_UNIT = ROTATION_METRIC_UNIT
R_ROT_001 = "R-ROT-001"


class RotationMetricProvenanceError(ValueError):
    pass


def _select(package: DecisionInputPackage, parameter_id: str) -> ResolvedConfiguration:
    if parameter_id not in package.requested_parameter_ids:
        raise RotationMetricProvenanceError(f"{parameter_id} no fue solicitado")
    if parameter_id in package.missing_parameter_ids:
        raise RotationMetricProvenanceError(f"{parameter_id} figura como ausente")
    matches = tuple(x for x in package.configurations if x.parameter_id == parameter_id)
    if len(matches) != 1:
        raise RotationMetricProvenanceError(f"{parameter_id} debe resolverse exactamente una vez")
    item = matches[0]
    if item.company_id != package.company_id:
        raise RotationMetricProvenanceError(f"{parameter_id} company_id incompatible")
    if item.parameters_version != package.context.parameters_version:
        raise RotationMetricProvenanceError(f"{parameter_id} parameters_version incompatible")
    if item.effective_at != package.effective_at:
        raise RotationMetricProvenanceError(f"{parameter_id} effective_at incompatible")
    cfg = item.configuration
    if not (cfg.valid_from <= item.effective_at and (cfg.valid_to is None or item.effective_at < cfg.valid_to)):
        raise RotationMetricProvenanceError(f"{parameter_id} no vigente")
    evidenced = any(
        ev.source_ref == item.configuration_ref
        and ev.state == "DEMONSTRATED"
        and ev.demonstration_ref is not None
        for ev in package.evidence
    )
    if not evidenced:
        raise RotationMetricProvenanceError(f"{parameter_id} sin Evidence DEMONSTRATED")
    return item


def _period_days(resolution: ResolvedConfiguration) -> int:
    if resolution.unit != P_ROT_002_UNIT:
        raise RotationMetricProvenanceError("P-ROT-002 debe usar días")
    try:
        value = Decimal(resolution.value)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise RotationMetricProvenanceError("P-ROT-002 inválido") from exc
    if not value.is_finite() or value < 1 or value != value.to_integral_value():
        raise RotationMetricProvenanceError("P-ROT-002 debe ser entero positivo")
    return int(value)


def _threshold(resolution: ResolvedConfiguration) -> Decimal:
    if resolution.unit != P_ROT_003_UNIT:
        raise RotationMetricProvenanceError("P-ROT-003 debe usar eventos/día")
    try:
        value = Decimal(resolution.value)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise RotationMetricProvenanceError("P-ROT-003 inválido") from exc
    if not value.is_finite() or value <= 0:
        raise RotationMetricProvenanceError("P-ROT-003 debe ser decimal finito positivo")
    return value


def _demonstrated_by_id(package: DecisionInputPackage) -> dict[str, Evidence]:
    return {
        ev.evidence_id: ev
        for ev in package.evidence
        if ev.state == "DEMONSTRATED" and validate_evidence(ev).status == "VALID"
    }


def _demonstrates_ref(package: DecisionInputPackage, ref: str) -> tuple[str, ...]:
    return tuple(
        ev.evidence_id
        for ev in package.evidence
        if ev.state == "DEMONSTRATED"
        and ev.demonstration_ref == ref
        and validate_evidence(ev).status == "VALID"
    )


def build_rotation_metric_evidence(
    package: DecisionInputPackage,
    source: RotationMetricSourceEvidence,
) -> tuple[RotationMetricEvidence, Decimal]:
    """Rebuild metric and threshold from the current DIP; detached metrics are impossible."""

    p2 = _select(package, P_ROT_002)
    p3 = _select(package, P_ROT_003)
    period_days = _period_days(p2)
    threshold = _threshold(p3)

    purchase = package.purchase
    expected_end = purchase.operation_date
    expected_start = expected_end - timedelta(days=period_days - 1)

    if source.article_id != purchase.article_id:
        raise RotationMetricProvenanceError("article_id incompatible")
    if source.window_start != expected_start or source.window_end != expected_end:
        raise RotationMetricProvenanceError("ventana Track B incompatible")
    if source.coverage_state != "COMPLETE":
        raise RotationMetricProvenanceError("Track B requiere coverage_state COMPLETE")

    semantic_ids = _demonstrates_ref(package, source.source_semantics_ref)
    completeness_ids = _demonstrates_ref(package, source.completeness_ref)
    if not semantic_ids or not completeness_ids:
        raise RotationMetricProvenanceError("semántica o completitud no demostrada")

    by_id = _demonstrated_by_id(package)
    if any(ref not in by_id for ref in source.valid_sale_evidence_refs):
        raise RotationMetricProvenanceError("evento de venta no demostrado")

    count = len(source.valid_sale_evidence_refs)
    metric = Decimal(count) / Decimal(period_days)

    config_ids = tuple(
        ev.evidence_id
        for ev in package.evidence
        if ev.state == "DEMONSTRATED"
        and ev.source_ref in {p2.configuration_ref, p3.configuration_ref}
    )
    evidence_refs = tuple(dict.fromkeys((*config_ids, *semantic_ids, *completeness_ids, *source.valid_sale_evidence_refs)))

    return RotationMetricEvidence(
        article_id=source.article_id,
        evaluation_date=purchase.operation_date,
        window_start=source.window_start,
        window_end=source.window_end,
        window_authority_ref=p2.configuration_ref,
        threshold_authority_ref=p3.configuration_ref,
        source_ref=source.source_ref,
        source_semantics_ref=source.source_semantics_ref,
        completeness_ref=source.completeness_ref,
        valid_sale_event_count=count,
        rotation_metric=metric,
        metric_unit=ROTATION_METRIC_UNIT,
        evidence_refs=evidence_refs,
        trace_refs=source.trace_refs,
    ), threshold


def evaluate_r_rot_001(
    package: DecisionInputPackage,
    source: RotationMetricSourceEvidence,
) -> Assessment:
    """Evaluate R-ROT-001 from same-execution DIP and upstream qualified events."""

    try:
        metric, threshold = build_rotation_metric_evidence(package, source)
    except RotationMetricProvenanceError as exc:
        return Assessment(
            rule_id=R_ROT_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=[],
            reason=f"R-ROT-001 no evaluable: {exc}",
        )

    outcome = "TRUE" if metric.rotation_metric < threshold else "FALSE"
    reason = (
        "R-ROT-001 demostrada: frecuencia de ventas inferior al umbral autorizado."
        if outcome == "TRUE"
        else "R-ROT-001 no demostrada: frecuencia de ventas igual o superior al umbral autorizado."
    )
    return Assessment(
        rule_id=R_ROT_001,
        status="EVALUABLE",
        outcome=outcome,
        evidence_ids=list(metric.evidence_refs),
        reason=reason,
    )


__all__ = [
    "P_ROT_002",
    "P_ROT_003",
    "R_ROT_001",
    "RotationMetricProvenanceError",
    "build_rotation_metric_evidence",
    "evaluate_r_rot_001",
]
