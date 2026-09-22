"""Provenance-safe executable core for R-PAG-002."""
from __future__ import annotations

from dataclasses import dataclass

from eios.core.documentary_payment_capture import DocumentaryPaymentCapture
from eios.core.models import Assessment, DecisionContext, Evidence, PurchaseOperation, Rule
from eios.finance.provenance import (
    ProvenancedFinanceBasicExecution,
    validate_provenanced_finance_basic_execution,
)
from eios.parameters import ResolvedConfiguration
from eios.payment_term_control import resolve_payment_term_control
from eios.payment_term_counterfactual import (
    build_pag002_counterfactual_finance_execution,
    build_pag002_counterfactual_payment_schedule,
)
from eios.payment_term_minimum import resolve_minimum_payment_term
from eios.payment_terms import PaymentTermObservationAdapter, PaymentTermSemanticAuthority
from eios.supplier.models import SupplierEvidenceResult

from .payment import (
    PAG001_OFFERED_TERM_ADAPTER_AUTHORITY_REF,
    PAG001_OFFERED_TERM_ADAPTER_METHODOLOGY_REF,
)
from .payment_financial import (
    classify_pag002_counterfactual_financial_state,
    classify_pag002_financial_state,
)

R_PAG_002 = "R-PAG-002"


@dataclass(frozen=True)
class PAG002ParameterBundle:
    minimum_resolution: ResolvedConfiguration | None
    minimum_evidence: Evidence | None
    control_resolution: ResolvedConfiguration | None
    control_evidence: Evidence | None
    treasury_minimum_resolution: ResolvedConfiguration | None
    treasury_minimum_evidence: Evidence | None


@dataclass(frozen=True)
class PAG002FinanceInputs:
    baseline_execution: ProvenancedFinanceBasicExecution
    baseline_evidence: Evidence
    documentary_capture: DocumentaryPaymentCapture


def _evidence_ids(*items: Evidence | None) -> list[str]:
    return list(dict.fromkeys(item.evidence_id for item in items if item is not None))


def _validate_identity(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    supplier_result: SupplierEvidenceResult,
    finance: PAG002FinanceInputs,
) -> None:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    if rule.rule_id != R_PAG_002:
        raise ValueError("El bridge solo evalúa R-PAG-002")
    if rule.version != context.rules_version:
        raise ValueError("Rule.version incompatible con DecisionContext.rules_version")
    if not rule.requires_evidence:
        raise ValueError("R-PAG-002 requiere evidencia")

    identity = supplier_result.identity
    checks = (
        (identity.decision_id, context.decision_id, "decision_id"),
        (identity.scenario_id, context.scenario_id, "scenario_id"),
        (identity.rules_version, context.rules_version, "rules_version"),
        (identity.parameters_version, context.parameters_version, "parameters_version"),
        (identity.data_snapshot_id, context.data_snapshot_id, "data_snapshot_id"),
        (identity.article_id, purchase.article_id, "article_id"),
        (identity.evaluation_date, purchase.operation_date, "evaluation_date"),
        (supplier_result.current_supplier_id, purchase.supplier_id, "supplier_id"),
    )
    for actual, expected, label in checks:
        if actual != expected:
            raise ValueError(f"SupplierEvidenceResult incompatible en {label}")

    validate_provenanced_finance_basic_execution(finance.baseline_execution)
    baseline_input = finance.baseline_execution.finance_input
    if baseline_input.context != context:
        raise ValueError("Finance Basic baseline pertenece a otro DecisionContext")
    if baseline_input.snapshot.company_scope != identity.company_scope:
        raise ValueError("Finance Basic baseline pertenece a otro company_scope")
    if baseline_input.snapshot.as_of_date != purchase.operation_date:
        raise ValueError("Finance Basic baseline usa otra evaluation_date")

    capture_payload = finance.documentary_capture.to_payload()
    captured_base = capture_payload["finance_package"]["decision_input_package"]
    captured_purchase = PurchaseOperation.model_validate(captured_base["purchase"])
    captured_context = DecisionContext.model_validate(captured_base["context"])
    if captured_purchase != purchase:
        raise ValueError("DocumentaryPaymentCapture pertenece a otra PurchaseOperation")
    if captured_context != context:
        raise ValueError("DocumentaryPaymentCapture pertenece a otro DecisionContext")


def _not_evaluable(evidence_ids: list[str], reason: str) -> Assessment:
    return Assessment(
        rule_id=R_PAG_002,
        status="NOT_EVALUABLE",
        outcome=None,
        evidence_ids=evidence_ids,
        reason=reason,
    )


def evaluate_r_pag_002(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    supplier_result: SupplierEvidenceResult,
    semantic_authority: PaymentTermSemanticAuthority,
    parameters: PAG002ParameterBundle,
    finance: PAG002FinanceInputs,
) -> Assessment:
    """Evaluate R-PAG-002 from authorized provenance sources."""

    _validate_identity(
        purchase=purchase,
        context=context,
        rule=rule,
        supplier_result=supplier_result,
        finance=finance,
    )

    identity = supplier_result.identity
    control = resolve_payment_term_control(
        context=context,
        company_scope=identity.company_scope,
        evaluation_date=identity.evaluation_date,
        control_resolution=parameters.control_resolution,
        control_evidence=parameters.control_evidence,
    )
    base_evidence_ids = _evidence_ids(
        parameters.control_evidence,
        parameters.minimum_evidence,
        finance.baseline_evidence,
        parameters.treasury_minimum_evidence,
    )

    if control.state == "DISABLED":
        return _not_evaluable(
            base_evidence_ids,
            "R-PAG-002 no evaluable: el criterio de plazo está deshabilitado por P-PAG-004.",
        )
    if control.state != "ENABLED":
        return _not_evaluable(
            base_evidence_ids,
            f"R-PAG-002 no evaluable: P-PAG-004 no es utilizable ({control.reason_code}).",
        )

    if (
        parameters.control_resolution is not None
        and parameters.minimum_resolution is not None
        and parameters.control_resolution.effective_at
        != parameters.minimum_resolution.effective_at
    ):
        return _not_evaluable(
            base_evidence_ids,
            "R-PAG-002 no evaluable: P-PAG-001 y P-PAG-004 no comparten effective_at.",
        )

    config_evidences = tuple(
        item
        for item in (
            parameters.minimum_evidence,
            parameters.control_evidence,
            parameters.treasury_minimum_evidence,
        )
        if item is not None
    )
    ids = tuple(item.evidence_id for item in config_evidences)
    if len(ids) != len(set(ids)):
        return _not_evaluable(
            list(dict.fromkeys(ids)),
            "R-PAG-002 no evaluable: evidence_id reutilizado entre parámetros.",
        )

    offered = PaymentTermObservationAdapter(
        authority_ref=PAG001_OFFERED_TERM_ADAPTER_AUTHORITY_REF,
        methodology_ref=PAG001_OFFERED_TERM_ADAPTER_METHODOLOGY_REF,
    ).adapt(supplier_result, semantic_authority)
    minimum = resolve_minimum_payment_term(
        context=context,
        company_scope=identity.company_scope,
        evaluation_date=identity.evaluation_date,
        minimum_resolution=parameters.minimum_resolution,
        minimum_evidence=parameters.minimum_evidence,
    )

    if (
        offered.state != "AVAILABLE"
        or offered.offered_payment_term_days is None
        or minimum.state != "AVAILABLE"
        or minimum.minimum_payment_term_days is None
    ):
        return _not_evaluable(
            base_evidence_ids,
            "R-PAG-002 no evaluable: plazo ofrecido o P-PAG-001 no disponibles.",
        )

    offered_days = offered.offered_payment_term_days
    minimum_days = minimum.minimum_payment_term_days

    if offered_days >= minimum_days:
        return Assessment(
            rule_id=R_PAG_002,
            status="EVALUABLE",
            outcome="FALSE",
            evidence_ids=list(
                dict.fromkeys(
                    base_evidence_ids
                    + ([offered.evidence_id] if offered.evidence_id else [])
                )
            ),
            reason=(
                "R-PAG-002 no demostrada: el plazo ofrecido ya alcanza o supera P-PAG-001."
            ),
        )

    baseline_state = classify_pag002_financial_state(
        context=context,
        finance_execution=finance.baseline_execution,
        finance_evidence=finance.baseline_evidence,
        treasury_minimum_resolution=parameters.treasury_minimum_resolution,
        treasury_minimum_evidence=parameters.treasury_minimum_evidence,
    )

    if baseline_state.state == "PAG002_FINANCIAL_STATE_NOT_DETERMINABLE":
        return _not_evaluable(
            base_evidence_ids,
            "R-PAG-002 no evaluable: estado financiero baseline no determinable.",
        )

    if baseline_state.state == "PAG002_FINANCIALLY_VIABLE":
        return Assessment(
            rule_id=R_PAG_002,
            status="EVALUABLE",
            outcome="FALSE",
            evidence_ids=list(
                dict.fromkeys(
                    base_evidence_ids
                    + ([offered.evidence_id] if offered.evidence_id else [])
                )
            ),
            reason=(
                "R-PAG-002 no demostrada: la operación ya cumple el criterio financiero con el plazo ofrecido."
            ),
        )

    schedule = build_pag002_counterfactual_payment_schedule(
        capture=finance.documentary_capture,
        baseline_execution=finance.baseline_execution,
        supplier_result=supplier_result,
        semantic_authority=semantic_authority,
        minimum_resolution=parameters.minimum_resolution,
        minimum_evidence=parameters.minimum_evidence,
    )
    if schedule.state != "AVAILABLE":
        return _not_evaluable(
            base_evidence_ids,
            f"R-PAG-002 no evaluable: escenario minimum-term no materializable ({schedule.reason_code}).",
        )

    counterfactual_execution = build_pag002_counterfactual_finance_execution(
        baseline_execution=finance.baseline_execution,
        schedule=schedule,
    )
    counterfactual_state = classify_pag002_counterfactual_financial_state(
        execution=counterfactual_execution,
        treasury_minimum_resolution=parameters.treasury_minimum_resolution,
        treasury_minimum_evidence=parameters.treasury_minimum_evidence,
    )

    if counterfactual_state.state == "PAG002_FINANCIAL_STATE_NOT_DETERMINABLE":
        return _not_evaluable(
            base_evidence_ids,
            "R-PAG-002 no evaluable: estado financiero minimum-term no determinable.",
        )

    evidence_ids = list(
        dict.fromkeys(
            base_evidence_ids
            + ([offered.evidence_id] if offered.evidence_id else [])
        )
    )

    if counterfactual_state.state == "PAG002_FINANCIALLY_VIABLE":
        return Assessment(
            rule_id=R_PAG_002,
            status="EVALUABLE",
            outcome="TRUE",
            evidence_ids=evidence_ids,
            reason=(
                "R-PAG-002 demostrada: baseline no viable financieramente y minimum-term viable bajo cambio único autorizado."
            ),
        )

    return Assessment(
        rule_id=R_PAG_002,
        status="EVALUABLE",
        outcome="FALSE",
        evidence_ids=evidence_ids,
        reason=(
            "R-PAG-002 no demostrada: el escenario minimum-term continúa sin cumplir el criterio financiero."
        ),
    )


__all__ = [
    "PAG002FinanceInputs",
    "PAG002ParameterBundle",
    "R_PAG_002",
    "evaluate_r_pag_002",
]
