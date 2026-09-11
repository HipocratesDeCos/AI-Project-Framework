"""Deterministic Supplier Evidence Core processing.

The engine preserves supplier facts and performs only explicitly requested
structural comparisons. It never scores, ranks, recommends or executes R-PROV.
"""
from __future__ import annotations

from decimal import Decimal

from .models import (
    CandidateResolution,
    StructuralComparisonRequest,
    StructuralComparisonResult,
    SupplierCandidateEvidence,
    SupplierDataIssueRef,
    SupplierEvidenceInput,
    SupplierEvidenceResult,
    SupplierItemRef,
    SupplierObservation,
    SupplierResultIdentity,
)


def _dedupe_strings(values: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _dedupe_issues(values: list[SupplierDataIssueRef]) -> tuple[SupplierDataIssueRef, ...]:
    """Deduplicate only exactly equal issues, preserving first appearance."""
    seen: set[tuple[object, ...]] = set()
    result: list[SupplierDataIssueRef] = []
    for item in values:
        key = (
            item.issue_id,
            item.issue_type,
            item.issue_record_ref,
            item.evidence_refs,
            item.trace_refs,
        )
        if key not in seen:
            seen.add(key)
            result.append(item)
    return tuple(result)


def _dedupe_item_refs(values: list[SupplierItemRef]) -> tuple[SupplierItemRef, ...]:
    seen: set[tuple[str, str]] = set()
    result: list[SupplierItemRef] = []
    for item in values:
        key = (item.item_type, item.item_id)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return tuple(result)


def _candidate_resolution(candidate: SupplierCandidateEvidence) -> CandidateResolution:
    if candidate.state == "CURRENT_OPERATION_DEMONSTRATED":
        state = "EVIDENCED_CANDIDATE"
        limitations: list[str] = []
    elif candidate.state == "CONFLICTING_DATA":
        state = "CONFLICTING_DATA"
        limitations = ["CANDIDATE_CONFLICTING_DATA"]
    elif candidate.state == "REFERENCE_ONLY":
        state = "NOT_EVIDENCED"
        limitations = ["CANDIDATE_REFERENCE_ONLY"]
    else:
        state = "NOT_EVIDENCED"
        limitations = ["CANDIDATE_GAP"]

    evidence_refs: list[str] = []
    if candidate.evidence_id:
        evidence_refs.append(candidate.evidence_id)
    trace_refs = list(candidate.trace_refs)
    for issue in candidate.issue_refs:
        evidence_refs.extend(issue.evidence_refs)
        trace_refs.extend(issue.trace_refs)

    return CandidateResolution(
        candidate_id=candidate.candidate_id,
        supplier_id=candidate.supplier_id,
        state=state,
        evidence_refs=_dedupe_strings(evidence_refs),
        issue_refs=candidate.issue_refs,
        trace_refs=_dedupe_strings(trace_refs),
        limitations=tuple(limitations),
    )


def _is_currently_valid(observation: SupplierObservation, evaluation_date) -> bool:
    if observation.valid_from and observation.valid_from > evaluation_date:
        return False
    if observation.valid_to and observation.valid_to < evaluation_date:
        return False
    return True


def _comparison(
    request: StructuralComparisonRequest,
    current: SupplierObservation,
    candidate: SupplierObservation,
    candidate_resolution: CandidateResolution,
    evaluation_date,
) -> StructuralComparisonResult:
    issues: list[SupplierDataIssueRef] = []
    limitations: list[str] = []
    difference: Decimal | None = None

    def build(
        state: str,
        *,
        difference_decimal: Decimal | None = None,
        issue_refs: tuple[SupplierDataIssueRef, ...] = (),
        limitations_out: tuple[str, ...] = (),
        preserve_authority: bool = True,
    ) -> StructuralComparisonResult:
        return StructuralComparisonResult(
            comparison_id=request.comparison_id,
            current_observation_id=current.observation_id,
            candidate_observation_id=candidate.observation_id,
            current_dimension=current.dimension,
            candidate_dimension=candidate.dimension,
            state=state,
            difference_decimal=difference_decimal,
            comparison_authority_ref=(
                request.comparison_authority_ref if preserve_authority else None
            ),
            issue_refs=issue_refs,
            limitations=limitations_out,
        )

    # Contract precedence step 1: current candidacy.
    if candidate_resolution.state != "EVIDENCED_CANDIDATE":
        limitations.append("CANDIDATE_NOT_EVIDENCED_CURRENTLY")
        issues.extend(candidate_resolution.issue_refs)
        return build(
            "UNKNOWN",
            issue_refs=_dedupe_issues(issues),
            limitations_out=tuple(limitations),
        )

    # Step 2: observation evidence states.
    if current.state == "NOT_EVIDENCED" or candidate.state == "NOT_EVIDENCED":
        limitations.append("OBSERVATION_NOT_EVIDENCED")
        return build("UNKNOWN", limitations_out=tuple(limitations))

    if current.state == "CONFLICTING_DATA" or candidate.state == "CONFLICTING_DATA":
        limitations.append("OBSERVATION_CONFLICTING_DATA")
        issues.extend(current.issue_refs)
        issues.extend(candidate.issue_refs)
        return build(
            "NOT_STRUCTURALLY_COMPARABLE",
            issue_refs=_dedupe_issues(issues),
            limitations_out=tuple(limitations),
        )

    # Step 3: current validity.
    if not _is_currently_valid(current, evaluation_date) or not _is_currently_valid(candidate, evaluation_date):
        limitations.append("OBSERVATION_OUTSIDE_VALIDITY")
        return build("NOT_STRUCTURALLY_COMPARABLE", limitations_out=tuple(limitations))

    # Step 4: basic structural compatibility. No unit conversion is performed.
    mismatches: list[str] = []
    if current.dimension != candidate.dimension:
        mismatches.append("DIMENSION_INCOMPATIBLE")
    if current.value_kind != candidate.value_kind:
        mismatches.append("VALUE_KIND_INCOMPATIBLE")
    if current.semantic_ref != candidate.semantic_ref:
        mismatches.append("SEMANTIC_REF_INCOMPATIBLE")
    if current.object_id != candidate.object_id:
        mismatches.append("OBJECT_INCOMPATIBLE")
    if current.value_kind in {"DECIMAL", "INTEGER"} and current.unit != candidate.unit:
        mismatches.append("UNIT_INCOMPATIBLE")

    if mismatches:
        return build("NOT_STRUCTURALLY_COMPARABLE", limitations_out=tuple(mismatches))

    # Step 5: PRICE comparability stays under PRICE authority.
    if current.dimension == "PRICE_REFERENCE" and request.comparison_authority_ref is None:
        limitations.append("PRICE_COMPARABILITY_AUTHORITY_REQUIRED")
        return build(
            "UNKNOWN",
            limitations_out=tuple(limitations),
            preserve_authority=False,
        )

    # Steps 6-7: structurally comparable; optional descriptive Decimal delta.
    if current.value_kind == "DECIMAL":
        assert current.value_decimal is not None
        assert candidate.value_decimal is not None
        difference = candidate.value_decimal - current.value_decimal

    return build(
        "STRUCTURALLY_COMPARABLE",
        difference_decimal=difference,
        limitations_out=(),
    )


def evaluate_supplier_evidence(payload: SupplierEvidenceInput) -> SupplierEvidenceResult:
    """Evaluate factual supplier evidence without supplier valuation or decision."""
    resolutions = tuple(_candidate_resolution(candidate) for candidate in payload.candidates)
    resolution_by_id = {item.candidate_id: item for item in resolutions}
    observation_by_id = {item.observation_id: item for item in payload.observations}

    comparisons: list[StructuralComparisonResult] = []
    for request in payload.comparison_requests:
        current = observation_by_id[request.current_observation_id]
        candidate = observation_by_id[request.candidate_observation_id]
        assert candidate.candidate_id is not None
        comparisons.append(
            _comparison(
                request,
                current,
                candidate,
                resolution_by_id[candidate.candidate_id],
                payload.evaluation_date,
            )
        )

    unresolved: list[SupplierItemRef] = []
    conflicting: list[SupplierItemRef] = []
    limitations: list[str] = []

    for item in resolutions:
        limitations.extend(item.limitations)
        if item.state == "NOT_EVIDENCED":
            unresolved.append(SupplierItemRef(item_type="CANDIDATE", item_id=item.candidate_id))
        elif item.state == "CONFLICTING_DATA":
            conflicting.append(SupplierItemRef(item_type="CANDIDATE", item_id=item.candidate_id))

    for item in payload.observations:
        if item.state == "NOT_EVIDENCED":
            unresolved.append(SupplierItemRef(item_type="OBSERVATION", item_id=item.observation_id))
        elif item.state == "CONFLICTING_DATA":
            conflicting.append(SupplierItemRef(item_type="OBSERVATION", item_id=item.observation_id))

    for item in payload.external_metrics:
        if item.data_state == "NOT_EVIDENCED":
            unresolved.append(SupplierItemRef(item_type="METRIC", item_id=item.metric_id))
        elif item.data_state == "CONFLICTING_DATA":
            conflicting.append(SupplierItemRef(item_type="METRIC", item_id=item.metric_id))

    for result in comparisons:
        limitations.extend(result.limitations)
        if result.state == "UNKNOWN":
            unresolved.append(SupplierItemRef(item_type="COMPARISON", item_id=result.comparison_id))
        if result.issue_refs:
            conflicting.append(SupplierItemRef(item_type="COMPARISON", item_id=result.comparison_id))

    context = payload.context
    operation = payload.purchase_operation
    identity = SupplierResultIdentity(
        decision_id=context.decision_id,
        scenario_id=context.scenario_id,
        rules_version=context.rules_version,
        parameters_version=context.parameters_version,
        data_snapshot_id=context.data_snapshot_id,
        company_scope=payload.company_scope,
        article_id=operation.article_id,
        evaluation_date=payload.evaluation_date,
        methodology_version=payload.methodology_version,
    )

    return SupplierEvidenceResult(
        identity=identity,
        current_supplier_id=operation.supplier_id,
        candidates=payload.candidates,
        candidate_resolutions=resolutions,
        observations=payload.observations,
        historical_facts=payload.historical_facts,
        external_metrics=payload.external_metrics,
        signals=payload.signals,
        structural_comparisons=tuple(comparisons),
        unresolved_items=_dedupe_item_refs(unresolved),
        conflicting_items=_dedupe_item_refs(conflicting),
        limitations=_dedupe_strings(limitations),
    )


__all__ = ["evaluate_supplier_evidence"]
