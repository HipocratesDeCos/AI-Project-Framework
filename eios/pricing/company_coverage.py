"""Strict, opt-in PRICE intake boundary for a specific company.

Legacy C1 inputs remain readable through run_price_intelligence. This
entrypoint requires documentary coverage of supported economic dimensions,
but does not authenticate companies, documents, QTG or HIS003 verdicts.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .engine import assess_economic_basis, run_price_intelligence
from .models import (
    PriceIntelligenceAssessmentContext,
    PriceIntelligenceInput,
    PriceIntelligenceResult,
    PriceReferenceAssessment,
)


MATERIAL_DIMENSIONS = (
    "QUANTITY", "TAX", "TRANSPORT", "DISCOUNT", "SURCHARGE", "COMMERCIAL",
)
_TARGET_FIELDS = {
    "TAX": "target_tax_basis",
    "TRANSPORT": "target_transport_basis",
    "DISCOUNT": "target_discount_basis",
    "SURCHARGE": "target_surcharge_basis",
    "COMMERCIAL": "target_commercial_basis",
}


class PriceCompanyCoverageProfile(BaseModel):
    """Declared context for mandatory economic completeness at C1 intake.

    expected_company_id must be supplied separately by a trusted caller.
    An in-payload company_id alone is not tenant authentication.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    profile_id: str = Field(min_length=1, max_length=128)
    company_id: str = Field(min_length=1, max_length=128)
    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    source_ref: str = Field(min_length=1, max_length=256)
    evidence_id: str = Field(min_length=1, max_length=64)
    rule_reference: str = Field(min_length=1, max_length=128)
    trace_reference: str = Field(min_length=1, max_length=128)


@dataclass(frozen=True)
class PriceCoverageReport:
    company_id: str
    profile_id: str
    status: Literal["COMPLETE", "INCOMPLETE"]
    issues: tuple[str, ...]
    reference_count: int

    @property
    def complete(self) -> bool:
        return self.status == "COMPLETE"


class PriceCoverageError(ValueError):
    def __init__(self, report: PriceCoverageReport):
        self.report = report
        super().__init__(
            "PRICE intake incompleto: " + ", ".join(report.issues)
        )


def assess_price_company_coverage(
    payload: PriceIntelligenceInput,
    profile: PriceCompanyCoverageProfile,
    *,
    expected_company_id: str,
) -> PriceCoverageReport:
    """Require all six supported material dimensions for every reference.

    This validates *declared* documentary coverage and mathematical C1
    normalizability, not truth of the external documentation. The caller
    supplies an authenticated company context and verified evidence status.
    """
    issues: list[str] = []
    if not expected_company_id or profile.company_id != expected_company_id:
        issues.append("COMPANY_SCOPE_MISMATCH")

    for field in (
        "decision_id", "scenario_id", "parameters_version", "data_snapshot_id",
    ):
        if getattr(profile, field) != getattr(payload.decision_context, field):
            issues.append("PROFILE_CONTEXT_MISMATCH:" + field)

    validations = payload.evidence_validations
    status_by_id = {item.evidence_id: item.status for item in validations}
    if len(status_by_id) != len(validations):
        issues.append("DUPLICATE_EVIDENCE_VALIDATION")
    if status_by_id.get(profile.evidence_id) != "VALID":
        issues.append("PROFILE_EVIDENCE_UNVALIDATED")

    basis = payload.normalization_basis
    if basis is None:
        issues.append("NORMALIZATION_BASIS_MISSING")
    else:
        for dimension, field in _TARGET_FIELDS.items():
            if getattr(basis, field) is None:
                issues.append("MATERIAL_TARGET_MISSING:" + dimension)

    if not payload.references:
        issues.append("PRICE_REFERENCES_MISSING")

    proofs = {
        (item.reference_id, item.dimension): item
        for item in payload.economic_basis_comparisons
    }
    evidence_groups: dict[tuple[str, str], list] = {}
    for item in payload.economic_basis_evidence:
        evidence_groups.setdefault((item.reference_id, item.dimension), []).append(item)

    unique_references = {}
    for reference in payload.references:
        reference_id = reference.source_transaction_id
        if reference_id in unique_references:
            if unique_references[reference_id] != reference:
                issues.append("CONFLICTING_REFERENCE_ID:" + reference_id)
            continue
        unique_references[reference_id] = reference

        for dimension in MATERIAL_DIMENSIONS:
            marker = reference_id + ":" + dimension
            proof = proofs.get((reference_id, dimension))
            evidence = evidence_groups.get((reference_id, dimension), ())
            if proof is None:
                issues.append("MATERIAL_COMPARISON_MISSING:" + marker)
                continue
            if proof.status != "EQUIVALENT":
                # Explicit "not applicable" can be represented by an
                # evidenced, identical NO_APLICA basis in this v0.1 profile.
                issues.append("MATERIAL_EQUIVALENCE_UNRESOLVED:" + marker)

            if dimension == "QUANTITY":
                if (
                    proof.source_basis != format(reference.quantity, "f")
                    or proof.target_basis != format(payload.purchase_operation.quantity, "f")
                ):
                    issues.append("MATERIAL_CONTEXT_MISMATCH:" + marker)
            elif basis is not None:
                target = getattr(basis, _TARGET_FIELDS[dimension])
                if target is not None and proof.target_basis != target:
                    issues.append("MATERIAL_CONTEXT_MISMATCH:" + marker)
                if (
                    dimension == "COMMERCIAL"
                    and reference.commercial_conditions is not None
                    and proof.source_basis != reference.commercial_conditions
                ):
                    issues.append("MATERIAL_CONTEXT_MISMATCH:" + marker)

            if len(evidence) != 1 or evidence[0].status != "RESOLVED":
                issues.append("MATERIAL_EVIDENCE_MISSING:" + marker)
            elif (
                proof.rule_reference != evidence[0].rule_reference
                or proof.trace_reference != evidence[0].trace_reference
                or not set(proof.evidence_refs).issubset(evidence[0].evidence_refs)
                or any(status_by_id.get(ref) != "VALID" for ref in proof.evidence_refs)
                or any(status_by_id.get(ref) != "VALID" for ref in evidence[0].evidence_refs)
            ):
                issues.append("MATERIAL_EVIDENCE_INVALID:" + marker)

        if status_by_id and all(
            status_by_id.get(ref) == "VALID" for ref in reference.evidence_refs
        ):
            assessment = assess_economic_basis(
                payload,
                reference,
                PriceReferenceAssessment(
                    reference_id=reference_id, comparability="COMPARABLE"
                ),
            )
            if assessment.normalization_status != "NORMALIZED":
                issues.append("PRICE_NOT_NORMALIZED:" + reference_id)
        else:
            issues.append("REFERENCE_EVIDENCE_UNVALIDATED:" + reference_id)

    unique_issues = tuple(dict.fromkeys(issues))
    return PriceCoverageReport(
        company_id=profile.company_id,
        profile_id=profile.profile_id,
        status="INCOMPLETE" if unique_issues else "COMPLETE",
        issues=unique_issues,
        reference_count=len(unique_references),
    )


def run_price_intelligence_for_company(
    payload: PriceIntelligenceInput,
    context: PriceIntelligenceAssessmentContext,
    profile: PriceCompanyCoverageProfile,
    *,
    expected_company_id: str,
) -> PriceIntelligenceResult:
    """Fail before C1 aggregation unless the declared company profile is complete."""
    report = assess_price_company_coverage(
        payload, profile, expected_company_id=expected_company_id,
    )
    if not report.complete:
        raise PriceCoverageError(report)
    result = run_price_intelligence(payload, context)
    references = tuple(dict.fromkeys((
        *result.trace_references,
        profile.profile_id,
        profile.source_ref,
        profile.evidence_id,
        profile.rule_reference,
        profile.trace_reference,
    )))
    return result.model_copy(update={"trace_references": references})


__all__ = [
    "MATERIAL_DIMENSIONS",
    "PriceCompanyCoverageProfile",
    "PriceCoverageReport",
    "PriceCoverageError",
    "assess_price_company_coverage",
    "run_price_intelligence_for_company",
]
