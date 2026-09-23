"""Provenance revalidation for Rotation Track A SalesActivityWindowEvidence.

The public boundary consumes the existing DecisionInputPackage and never accepts
an externally supplied ResolvedConfiguration(P-ROT-001). This module validates
only the authorized window/configuration/evidence binding. It does not claim
that upstream sales records are authentic or complete beyond the factual refs
already carried by SalesActivityWindowEvidence.
"""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal, InvalidOperation

from eios.core.decision_input_package import DecisionInputPackage
from eios.parameters import ResolvedConfiguration

from .models import SalesActivityWindowEvidence


P_ROT_001 = "P-ROT-001"
P_ROT_001_UNIT = "días"


class SalesActivityWindowProvenanceError(ValueError):
    """Technical failure of the authorized Rotation Track A boundary."""


def _error(message: str) -> SalesActivityWindowProvenanceError:
    return SalesActivityWindowProvenanceError(message)


def _select_and_validate_p_rot_001(
    package: DecisionInputPackage,
) -> tuple[ResolvedConfiguration, int, tuple[str, ...]]:
    if not isinstance(package, DecisionInputPackage):
        raise TypeError("package debe ser DecisionInputPackage")

    if P_ROT_001 not in package.requested_parameter_ids:
        raise _error("P-ROT-001 no fue solicitada en DecisionInputPackage")
    if P_ROT_001 in package.missing_parameter_ids:
        raise _error("P-ROT-001 figura como configuración ausente")

    resolutions = tuple(
        item for item in package.configurations if item.parameter_id == P_ROT_001
    )
    if len(resolutions) != 1:
        raise _error("DecisionInputPackage debe contener exactamente una P-ROT-001")

    resolution = resolutions[0]
    context = package.context

    if resolution.company_id != package.company_id:
        raise _error("P-ROT-001 pertenece a otro company_id")
    if resolution.parameters_version != context.parameters_version:
        raise _error("P-ROT-001 está vinculada a otra parameters_version")
    if resolution.effective_at != package.effective_at:
        raise _error("P-ROT-001 está vinculada a otro effective_at")

    configuration = resolution.configuration
    try:
        active = configuration.valid_from <= resolution.effective_at and (
            configuration.valid_to is None
            or resolution.effective_at < configuration.valid_to
        )
    except TypeError as exc:
        raise _error("P-ROT-001 y effective_at usan semántica temporal incompatible") from exc
    if not active:
        raise _error("P-ROT-001 no está vigente en effective_at")

    if resolution.unit != P_ROT_001_UNIT:
        raise _error("P-ROT-001 debe usar la unidad canónica 'días'")

    try:
        value = Decimal(resolution.value)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise _error("P-ROT-001 debe contener un número entero de días") from exc
    if not value.is_finite() or value <= 0 or value != value.to_integral_value():
        raise _error("P-ROT-001 debe ser un entero finito y positivo")

    matching_evidence_ids = tuple(
        evidence.evidence_id
        for evidence in package.evidence
        if evidence.source_ref == resolution.configuration_ref
        and evidence.state == "DEMONSTRATED"
        and evidence.demonstration_ref is not None
    )
    if not matching_evidence_ids:
        raise _error("P-ROT-001 no dispone de Evidence DEMONSTRATED vinculada")

    return resolution, int(value), matching_evidence_ids


def validate_sales_activity_window_evidence(
    package: DecisionInputPackage,
    carrier: SalesActivityWindowEvidence,
) -> None:
    """Revalidate the authorized period and DIP binding for a factual carrier.

    This boundary intentionally does not derive activity_state from sales
    records because no physical upstream sales-record input contract is
    authorized in this slice.
    """
    if not isinstance(package, DecisionInputPackage):
        raise TypeError("package debe ser DecisionInputPackage")
    if not isinstance(carrier, SalesActivityWindowEvidence):
        raise TypeError("carrier debe ser SalesActivityWindowEvidence")

    purchase = package.purchase
    context = package.context
    if purchase.decision_id != context.decision_id:
        raise _error("PurchaseOperation y DecisionContext no comparten decision_id")
    if purchase.scenario_id != context.scenario_id:
        raise _error("PurchaseOperation y DecisionContext no comparten scenario_id")

    resolution, period_days, configuration_evidence_ids = (
        _select_and_validate_p_rot_001(package)
    )

    expected_end = purchase.operation_date
    expected_start = expected_end - timedelta(days=period_days - 1)

    if carrier.article_id != purchase.article_id:
        raise _error("SalesActivityWindowEvidence pertenece a otro article_id")
    if carrier.evaluation_date != purchase.operation_date:
        raise _error("evaluation_date debe coincidir con PurchaseOperation.operation_date")
    if carrier.window_end != expected_end:
        raise _error("window_end no coincide con la ventana autorizada")
    if carrier.window_start != expected_start:
        raise _error("window_start no coincide con la ventana autorizada")
    if carrier.window_authority_ref != resolution.configuration_ref:
        raise _error("window_authority_ref no coincide con P-ROT-001")

    if not set(configuration_evidence_ids).intersection(carrier.evidence_refs):
        raise _error(
            "SalesActivityWindowEvidence debe conservar evidence_id de la P-ROT-001 demostrada"
        )


__all__ = [
    "P_ROT_001",
    "P_ROT_001_UNIT",
    "SalesActivityWindowProvenanceError",
    "validate_sales_activity_window_evidence",
]
