"""Provenance-safe executable core for R-PAG-001."""
from __future__ import annotations

from dataclasses import dataclass

from eios.core.models import Assessment, DecisionContext, Evidence, PurchaseOperation, Rule
from eios.parameters import ResolvedConfiguration
from eios.payment_term_control import resolve_payment_term_control
from eios.payment_term_tolerance import resolve_payment_term_tolerance
from eios.payment_terms import PaymentTermObservationAdapter, PaymentTermSemanticAuthority
from eios.supplier.models import SupplierEvidenceResult


R_PAG_001 = "R-PAG-001"

PAG001_OFFERED_TERM_ADAPTER_AUTHORITY_REF = (
    "01_Modelo/PAG001_Offered_Payment_Term_Authority_v0.1.md"
)
PAG001_OFFERED_TERM_ADAPTER_METHODOLOGY_REF = (
    "08_Implementacion/PAG001_Offered_Payment_Term_Adapter_Technical_Contract_v0.1.md"
)


@dataclass(frozen=True)
class PAG001ParameterBundle:
    target_resolution: ResolvedConfiguration | None
    target_evidence: Evidence | None
    tolerance_resolution: ResolvedConfiguration | None
    tolerance_evidence: Evidence | None
    control_resolution: ResolvedConfiguration | None
    control_evidence: Evidence | None


def _validate_identity(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    supplier_result: SupplierEvidenceResult,
) -> None:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    if rule.rule_id != R_PAG_001:
        raise ValueError("El bridge solo evalúa R-PAG-001")
    if rule.version != context.rules_version:
        raise ValueError("Rule.version incompatible con DecisionContext.rules_version")
    if not rule.requires_evidence:
        raise ValueError("R-PAG-001 requiere evidencia")

    identity = supplier_result.identity
    if identity.decision_id != context.decision_id:
        raise ValueError("SupplierEvidenceResult pertenece a otra decisión")
    if identity.scenario_id != context.scenario_id:
        raise ValueError("SupplierEvidenceResult pertenece a otro escenario")
    if identity.rules_version != context.rules_version:
        raise ValueError("SupplierEvidenceResult usa otra rules_version")
    if identity.parameters_version != context.parameters_version:
        raise ValueError("SupplierEvidenceResult usa otra parameters_version")
    if identity.data_snapshot_id != context.data_snapshot_id:
        raise ValueError("SupplierEvidenceResult usa otro data_snapshot_id")
    if identity.article_id != purchase.article_id:
        raise ValueError("SupplierEvidenceResult pertenece a otro artículo")
    if identity.evaluation_date != purchase.operation_date:
        raise ValueError("SupplierEvidenceResult usa otra evaluation_date")
    if supplier_result.current_supplier_id != purchase.supplier_id:
        raise ValueError("SupplierEvidenceResult pertenece a otro proveedor actual")


def _unique_evidence_ids(*values: str | None) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def evaluate_r_pag_001(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    supplier_result: SupplierEvidenceResult,
    semantic_authority: PaymentTermSemanticAuthority,
    parameters: PAG001ParameterBundle,
) -> Assessment:
    """Evaluate offered payment term below the authorized effective threshold.

    All derived PAG001 inputs are rebuilt from their authorized upstream
    sources in this invocation. P-PAG-005 is deliberately not an input to the
    core comparator.
    """

    _validate_identity(
        purchase=purchase,
        context=context,
        rule=rule,
        supplier_result=supplier_result,
    )

    identity = supplier_result.identity

    control = resolve_payment_term_control(
        context=context,
        company_scope=identity.company_scope,
        evaluation_date=identity.evaluation_date,
        control_resolution=parameters.control_resolution,
        control_evidence=parameters.control_evidence,
    )
    control_evidence_id = (
        parameters.control_evidence.evidence_id
        if parameters.control_evidence is not None
        else None
    )

    if control.state == "DISABLED":
        return Assessment(
            rule_id=R_PAG_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=_unique_evidence_ids(control_evidence_id),
            reason=(
                "R-PAG-001 no evaluable: el criterio de plazo está "
                "deshabilitado por P-PAG-004."
            ),
        )

    if control.state != "ENABLED":
        return Assessment(
            rule_id=R_PAG_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=_unique_evidence_ids(control_evidence_id),
            reason=(
                "R-PAG-001 no evaluable: P-PAG-004 no es utilizable "
                f"({control.reason_code})."
            ),
        )

    parameter_evidences = tuple(
        item
        for item in (
            parameters.control_evidence,
            parameters.target_evidence,
            parameters.tolerance_evidence,
        )
        if item is not None
    )
    parameter_evidence_ids = tuple(item.evidence_id for item in parameter_evidences)
    if len(parameter_evidence_ids) != len(set(parameter_evidence_ids)):
        return Assessment(
            rule_id=R_PAG_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=list(dict.fromkeys(parameter_evidence_ids)),
            reason=(
                "R-PAG-001 no evaluable: evidencia de configuración reutilizada "
                "entre parámetros PAG distintos."
            ),
        )

    resolved_parameters = (
        parameters.control_resolution,
        parameters.target_resolution,
        parameters.tolerance_resolution,
    )
    if all(item is not None for item in resolved_parameters):
        effective_times = {item.effective_at for item in resolved_parameters if item is not None}
        if len(effective_times) != 1:
            return Assessment(
                rule_id=R_PAG_001,
                status="NOT_EVALUABLE",
                outcome=None,
                evidence_ids=list(dict.fromkeys(parameter_evidence_ids)),
                reason=(
                    "R-PAG-001 no evaluable: P-PAG-002/003/004 no pertenecen "
                    "al mismo contexto efectivo de configuración."
                ),
            )

    offered = PaymentTermObservationAdapter(
        authority_ref=PAG001_OFFERED_TERM_ADAPTER_AUTHORITY_REF,
        methodology_ref=PAG001_OFFERED_TERM_ADAPTER_METHODOLOGY_REF,
    ).adapt(supplier_result, semantic_authority)

    offered_evidence_id = offered.evidence_id
    if offered.state != "AVAILABLE" or offered.offered_payment_term_days is None:
        return Assessment(
            rule_id=R_PAG_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=_unique_evidence_ids(
                control_evidence_id,
                offered_evidence_id,
            ),
            reason=(
                "R-PAG-001 no evaluable: plazo ofrecido no disponible "
                f"({offered.state})."
            ),
        )

    threshold = resolve_payment_term_tolerance(
        context=context,
        company_scope=identity.company_scope,
        evaluation_date=identity.evaluation_date,
        target_resolution=parameters.target_resolution,
        target_evidence=parameters.target_evidence,
        tolerance_resolution=parameters.tolerance_resolution,
        tolerance_evidence=parameters.tolerance_evidence,
    )

    target_evidence_id = (
        parameters.target_evidence.evidence_id
        if parameters.target_evidence is not None
        else None
    )
    tolerance_evidence_id = (
        parameters.tolerance_evidence.evidence_id
        if parameters.tolerance_evidence is not None
        else None
    )
    evidence_ids = _unique_evidence_ids(
        control_evidence_id,
        offered_evidence_id,
        target_evidence_id,
        tolerance_evidence_id,
    )

    if threshold.state != "AVAILABLE" or threshold.effective_threshold_days is None:
        return Assessment(
            rule_id=R_PAG_001,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason=(
                "R-PAG-001 no evaluable: umbral de plazo no disponible "
                f"({threshold.reason_code})."
            ),
        )

    offered_days = offered.offered_payment_term_days
    threshold_days = threshold.effective_threshold_days
    triggered = offered_days < threshold_days

    return Assessment(
        rule_id=R_PAG_001,
        status="EVALUABLE",
        outcome="TRUE" if triggered else "FALSE",
        evidence_ids=evidence_ids,
        reason=(
            "R-PAG-001 demostrada: plazo ofrecido inferior al umbral efectivo."
            if triggered
            else "R-PAG-001 no demostrada: plazo ofrecido igual o superior al umbral efectivo."
        ),
    )


__all__ = [
    "PAG001ParameterBundle",
    "R_PAG_001",
    "evaluate_r_pag_001",
]
