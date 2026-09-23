"""Authorized producer from upstream ROT002 source evidence to Track A carrier."""
from __future__ import annotations

from eios.core.decision_input_package import DecisionInputPackage
from eios.core.models import Evidence
from eios.core.validation import validate_evidence

from .models import SalesActivityWindowEvidence
from .provenance import _select_and_validate_p_rot_001
from .source_models import SalesActivitySourceEvidence


def _evidence_by_id(package: DecisionInputPackage) -> dict[str, Evidence]:
    ids = tuple(item.evidence_id for item in package.evidence)
    if len(ids) != len(set(ids)):
        raise ValueError("DecisionInputPackage contiene evidence_id duplicados")
    return {item.evidence_id: item for item in package.evidence}


def _demonstrates_ref(package: DecisionInputPackage, ref: str) -> tuple[str, ...]:
    return tuple(
        item.evidence_id
        for item in package.evidence
        if item.state == "DEMONSTRATED"
        and item.demonstration_ref == ref
        and validate_evidence(item).status == "VALID"
    )


def _valid_sale_evidence_ids(
    package: DecisionInputPackage,
    source: SalesActivitySourceEvidence,
) -> tuple[str, ...]:
    by_id = _evidence_by_id(package)
    valid: list[str] = []
    for evidence_id in source.valid_sale_evidence_refs:
        evidence = by_id.get(evidence_id)
        if evidence is None:
            continue
        if evidence.state != "DEMONSTRATED":
            continue
        if validate_evidence(evidence).status != "VALID":
            continue
        valid.append(evidence_id)
    return tuple(valid)


def produce_sales_activity_window_evidence(
    package: DecisionInputPackage,
    source: SalesActivitySourceEvidence,
) -> SalesActivityWindowEvidence:
    """Produce the authorized Track A carrier without classifying raw sales documents."""

    if not isinstance(package, DecisionInputPackage):
        raise TypeError("package debe ser DecisionInputPackage")
    if not isinstance(source, SalesActivitySourceEvidence):
        raise TypeError("source debe ser SalesActivitySourceEvidence")

    resolution, period_days, configuration_evidence_ids = _select_and_validate_p_rot_001(package)
    purchase = package.purchase
    expected_end = purchase.operation_date
    from datetime import timedelta
    expected_start = expected_end - timedelta(days=period_days - 1)

    if source.article_id != purchase.article_id:
        raise ValueError("SalesActivitySourceEvidence pertenece a otro article_id")
    if source.window_start != expected_start or source.window_end != expected_end:
        raise ValueError("SalesActivitySourceEvidence no corresponde a la ventana autorizada")

    semantic_ids = _demonstrates_ref(package, source.source_semantics_ref)
    completeness_ids = _demonstrates_ref(package, source.completeness_ref)
    sale_ids = _valid_sale_evidence_ids(package, source)

    # A declared valid-sale ref that is not demonstrated cannot be promoted to presence.
    all_declared_sales_demonstrated = set(source.valid_sale_evidence_refs) == set(sale_ids)

    if source.valid_sale_evidence_refs and semantic_ids and all_declared_sales_demonstrated:
        activity_state = "SALES_ACTIVITY_PRESENT"
    elif source.coverage_state == "CONFLICTING":
        activity_state = "CONFLICTING_DATA"
    elif (
        source.coverage_state == "COMPLETE"
        and not source.valid_sale_evidence_refs
        and semantic_ids
        and completeness_ids
    ):
        activity_state = "ZERO_VALID_SALES_DEMONSTRATED"
    elif source.coverage_state in {"PARTIAL", "NOT_DEMONSTRATED"}:
        activity_state = "NOT_EVIDENCED"
    else:
        activity_state = "NOT_DETERMINABLE"

    evidence_refs = tuple(
        dict.fromkeys(
            (
                *configuration_evidence_ids,
                *semantic_ids,
                *completeness_ids,
                *sale_ids,
            )
        )
    )
    return SalesActivityWindowEvidence(
        article_id=source.article_id,
        evaluation_date=purchase.operation_date,
        window_start=source.window_start,
        window_end=source.window_end,
        window_authority_ref=resolution.configuration_ref,
        source_ref=source.source_ref,
        source_semantics_ref=source.source_semantics_ref,
        completeness_ref=source.completeness_ref,
        activity_state=activity_state,
        evidence_refs=evidence_refs,
        trace_refs=source.trace_refs,
    )


__all__ = ["produce_sales_activity_window_evidence"]
