"""Rules-layer bridges for authorized Stock Intelligence results."""
from __future__ import annotations

from eios.core.models import Assessment, DecisionContext, Evidence, PurchaseOperation, Rule
from eios.core.validation import validate_evidence
from eios.stock.models import ExcessResult


R_STK_003 = "R-STK-003"
STOCK_EXCESS_EVIDENCE_SOURCE_TYPE = "StockExcessEvaluationEvidence"


def _validate_identity(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    excess: ExcessResult,
) -> None:
    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    if rule.rule_id != R_STK_003:
        raise ValueError("El bridge solo evalúa R-STK-003")
    if rule.version != context.rules_version:
        raise ValueError("Rule.version incompatible con DecisionContext.rules_version")
    if not rule.requires_evidence:
        raise ValueError("R-STK-003 requiere evidencia")

    identity = excess.identity
    if identity.decision_id != context.decision_id:
        raise ValueError("ExcessResult pertenece a otra decisión")
    if identity.scenario_id != context.scenario_id:
        raise ValueError("ExcessResult pertenece a otro escenario")
    if identity.rules_version != context.rules_version:
        raise ValueError("ExcessResult usa otra rules_version")
    if identity.parameters_version != context.parameters_version:
        raise ValueError("ExcessResult usa otra parameters_version")
    if identity.data_snapshot_id != context.data_snapshot_id:
        raise ValueError("ExcessResult usa otro data_snapshot_id")
    if identity.article_id != purchase.article_id:
        raise ValueError("ExcessResult pertenece a otro artículo")
    if excess.stock_reference.reference_kind != "PROJECTED":
        raise ValueError("R-STK-003 requiere referencia de stock PROJECTED posterior a la compra")


def _validate_evidence_binding(excess: ExcessResult, evidence: Evidence) -> None:
    if evidence.source_type != STOCK_EXCESS_EVIDENCE_SOURCE_TYPE:
        raise ValueError("stock_evidence.source_type incompatible")
    if evidence.state != "DEMONSTRATED":
        return

    allowed_refs = {
        *excess.trace_refs,
        *excess.stock_reference.trace_refs,
    }
    if excess.stock_reference.source_ref:
        allowed_refs.add(excess.stock_reference.source_ref)
    if evidence.demonstration_ref not in allowed_refs:
        raise ValueError("stock_evidence.demonstration_ref no pertenece a la provenance M07")


def evaluate_r_stk_003(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    excess: ExcessResult,
    stock_evidence: Evidence,
) -> Assessment:
    """Map the closed M07 excess result into the Assessment of R-STK-003.

    R-STK-003 is TRUE only for the M07 ``EXCESS`` state. ``NO_EXCESS`` and
    ``WITHIN_TOLERANCE`` are FALSE. M09/M10 uncertainty never becomes FALSE.
    """

    _validate_identity(purchase, context, rule, excess)
    _validate_evidence_binding(excess, stock_evidence)
    evidence_ids = [stock_evidence.evidence_id]

    if excess.state == "NOT_EVIDENCED":
        return Assessment(
            rule_id=R_STK_003,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-STK-003 no evaluable: exceso de stock no evidenciado.",
        )
    if excess.state == "CONFLICTING_DATA":
        return Assessment(
            rule_id=R_STK_003,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-STK-003 no evaluable: datos M07 contradictorios.",
        )
    if excess.state == "UNKNOWN":
        return Assessment(
            rule_id=R_STK_003,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-STK-003 no evaluable: estado de exceso desconocido.",
        )

    if validate_evidence(stock_evidence).status != "VALID":
        return Assessment(
            rule_id=R_STK_003,
            status="NOT_EVALUABLE",
            outcome=None,
            evidence_ids=evidence_ids,
            reason="R-STK-003 no evaluable: la evidencia M07 no está demostrada.",
        )

    if excess.state == "EXCESS":
        return Assessment(
            rule_id=R_STK_003,
            status="EVALUABLE",
            outcome="TRUE",
            evidence_ids=evidence_ids,
            reason="R-STK-003 demostrada: stock proyectado por encima del máximo y tolerancia autorizados.",
        )

    if excess.state in {"NO_EXCESS", "WITHIN_TOLERANCE"}:
        reason = (
            "R-STK-003 no demostrada: no existe exceso de stock."
            if excess.state == "NO_EXCESS"
            else "R-STK-003 no demostrada: stock sobre máximo pero dentro de la tolerancia autorizada."
        )
        return Assessment(
            rule_id=R_STK_003,
            status="EVALUABLE",
            outcome="FALSE",
            evidence_ids=evidence_ids,
            reason=reason,
        )

    raise ValueError(f"Estado M07 no soportado para R-STK-003: {excess.state}")


__all__ = [
    "R_STK_003",
    "STOCK_EXCESS_EVIDENCE_SOURCE_TYPE",
    "evaluate_r_stk_003",
]
