"""Rules-layer bridges for authorized EIOS profitability rules."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from eios.core.models import Assessment, DecisionContext, Evidence, PurchaseOperation, Rule
from eios.core.validation import validate_evidence
from eios.parameters import ResolvedConfiguration
from eios.profitability import (
    ProvenancedProfitabilityExecution,
    ProfitabilityResult,
    validate_provenanced_profitability_execution,
)


R_MGE_001 = "R-MGE-001"
R_MGE_002 = "R-MGE-002"
R_MGE_003 = "R-MGE-003"

P_MGE_001 = "P-MGE-001"
P_MGE_002 = "P-MGE-002"
P_MGE_003 = "P-MGE-003"

PROFITABILITY_EVIDENCE_SOURCE_TYPE = "ProfitabilityResultEvidence"
PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE = "ParameterConfigurationEvidence"

PERCENT_UNIT = "%"
PERCENTAGE_POINTS_UNIT = "puntos porcentuales"


@dataclass(frozen=True)
class MGEParameterBundle:
    """Resolved MGE thresholds plus their evidence."""

    minimum_resolution: ResolvedConfiguration | None
    minimum_evidence: Evidence | None
    target_resolution: ResolvedConfiguration | None
    target_evidence: Evidence | None
    tolerance_resolution: ResolvedConfiguration | None
    tolerance_evidence: Evidence | None


@dataclass(frozen=True)
class _ResolvedMGEPolicy:
    minimum: Decimal
    target: Decimal
    tolerance: Decimal
    evidence_ids: tuple[str, ...]


def profitability_result_ref(result: ProfitabilityResult) -> str:
    """Deterministic technical reference for binding Evidence to one result."""
    payload = json.dumps(
        result.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"profitability:{hashlib.sha256(payload).hexdigest()}"


def _validate_identity(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    expected_rule_id: str,
    execution: ProvenancedProfitabilityExecution,
) -> None:
    profitability_input = execution.profitability_input
    result = execution.profitability_result

    if purchase.decision_id != context.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
    if rule.rule_id != expected_rule_id:
        raise ValueError(f"El bridge solo evalúa {expected_rule_id}")
    if rule.version != context.rules_version:
        raise ValueError("Rule.version incompatible con DecisionContext.rules_version")
    if not rule.requires_evidence:
        raise ValueError(f"{expected_rule_id} requiere evidencia")
    if profitability_input.context != context:
        raise ValueError("ProfitabilityInput pertenece a otro DecisionContext")
    if profitability_input.purchase_operation != purchase:
        raise ValueError("ProfitabilityInput pertenece a otra PurchaseOperation")
    if result.decision_id != context.decision_id:
        raise ValueError("ProfitabilityResult pertenece a otra decisión")
    if result.scenario_id != context.scenario_id:
        raise ValueError("ProfitabilityResult pertenece a otro escenario")
    if result.data_snapshot_id != context.data_snapshot_id:
        raise ValueError("ProfitabilityResult usa otro data_snapshot_id")
    if result.parameters_version != context.parameters_version:
        raise ValueError("ProfitabilityResult usa otra parameters_version")
    if result.company_scope != profitability_input.company_scope:
        raise ValueError("ProfitabilityResult usa otro company_scope")
    if result.article_id != purchase.article_id:
        raise ValueError("ProfitabilityResult pertenece a otro artículo")
    if result.evaluation_date != profitability_input.evaluation_date:
        raise ValueError("ProfitabilityResult usa otra evaluation_date")


def _validate_profitability_evidence(
    execution: ProvenancedProfitabilityExecution,
    evidence: Evidence,
) -> None:
    profitability_input = execution.profitability_input
    result = execution.profitability_result

    if evidence.source_type != PROFITABILITY_EVIDENCE_SOURCE_TYPE:
        raise ValueError("profitability_evidence.source_type incompatible")
    if evidence.captured_at != profitability_input.evaluation_date:
        raise ValueError(
            "profitability_evidence debe corresponder a ProfitabilityInput.evaluation_date"
        )
    if (
        evidence.state == "DEMONSTRATED"
        and evidence.demonstration_ref != profitability_result_ref(result)
    ):
        raise ValueError(
            "profitability_evidence no está vinculada al ProfitabilityResult evaluado"
        )


def _validate_resolved_parameter(
    *,
    execution: ProvenancedProfitabilityExecution,
    context: DecisionContext,
    resolved: ResolvedConfiguration,
    evidence: Evidence,
    expected_parameter_id: str,
    expected_unit: str,
) -> Decimal | None:
    profitability_input = execution.profitability_input

    if resolved.parameter_id != expected_parameter_id:
        raise ValueError(f"La política MGE requiere {expected_parameter_id}")
    if resolved.parameters_version != context.parameters_version:
        raise ValueError(
            f"{expected_parameter_id} está vinculada a otra parameters_version"
        )
    if resolved.company_id != profitability_input.company_scope:
        raise ValueError(f"{expected_parameter_id} pertenece a otro company_scope")
    if resolved.effective_at.date() != profitability_input.evaluation_date:
        raise ValueError(
            f"{expected_parameter_id} debe resolverse para la evaluation_date MGE"
        )

    configuration = resolved.configuration
    try:
        active = configuration.valid_from <= resolved.effective_at and (
            configuration.valid_to is None
            or resolved.effective_at < configuration.valid_to
        )
    except TypeError as exc:
        raise ValueError(
            f"{expected_parameter_id} usa semántica temporal incompatible"
        ) from exc
    if not active:
        raise ValueError(f"{expected_parameter_id} no está vigente en effective_at")

    if evidence.source_type != PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE:
        raise ValueError("parameter_evidence.source_type incompatible")
    if evidence.captured_at != profitability_input.evaluation_date:
        raise ValueError(
            "parameter_evidence debe corresponder a ProfitabilityInput.evaluation_date"
        )
    if (
        evidence.state == "DEMONSTRATED"
        and evidence.demonstration_ref != resolved.configuration_ref
    ):
        raise ValueError(
            f"parameter_evidence no está vinculada a {expected_parameter_id}"
        )

    if validate_evidence(evidence).status != "VALID":
        return None
    if resolved.unit != expected_unit:
        return None

    try:
        value = Decimal(resolved.value)
    except (InvalidOperation, ValueError, TypeError):
        return None
    if not value.is_finite():
        return None
    return value


def _evidence_ids(
    profitability_evidence: Evidence,
    bundle: MGEParameterBundle,
) -> tuple[str, ...]:
    ordered = [profitability_evidence.evidence_id]
    for item in (
        bundle.minimum_evidence,
        bundle.target_evidence,
        bundle.tolerance_evidence,
    ):
        if item is not None:
            ordered.append(item.evidence_id)
    return tuple(dict.fromkeys(ordered))


def _resolve_policy(
    *,
    execution: ProvenancedProfitabilityExecution,
    context: DecisionContext,
    profitability_evidence: Evidence,
    bundle: MGEParameterBundle,
) -> tuple[_ResolvedMGEPolicy | None, str | None]:
    evidence_ids = _evidence_ids(profitability_evidence, bundle)

    specs = (
        (
            P_MGE_001,
            PERCENT_UNIT,
            bundle.minimum_resolution,
            bundle.minimum_evidence,
        ),
        (
            P_MGE_002,
            PERCENT_UNIT,
            bundle.target_resolution,
            bundle.target_evidence,
        ),
        (
            P_MGE_003,
            PERCENTAGE_POINTS_UNIT,
            bundle.tolerance_resolution,
            bundle.tolerance_evidence,
        ),
    )

    values: dict[str, Decimal] = {}
    missing: list[str] = []
    invalid: list[str] = []

    for parameter_id, unit, resolved, evidence in specs:
        if resolved is None or evidence is None:
            missing.append(parameter_id)
            continue

        value = _validate_resolved_parameter(
            execution=execution,
            context=context,
            resolved=resolved,
            evidence=evidence,
            expected_parameter_id=parameter_id,
            expected_unit=unit,
        )
        if value is None:
            invalid.append(parameter_id)
            continue
        values[parameter_id] = value

    if missing:
        return None, "MGE_PARAMETER_MISSING:" + ",".join(missing)
    if invalid:
        return None, "MGE_PARAMETER_NOT_USABLE:" + ",".join(invalid)

    minimum = values[P_MGE_001]
    target = values[P_MGE_002]
    tolerance = values[P_MGE_003]

    if minimum > target:
        return None, "MGE_PARAMETER_SET_CONFLICT:MINIMUM_GT_TARGET"
    if tolerance < 0:
        return None, "MGE_PARAMETER_SET_CONFLICT:NEGATIVE_TOLERANCE"

    return (
        _ResolvedMGEPolicy(
            minimum=minimum,
            target=target,
            tolerance=tolerance,
            evidence_ids=evidence_ids,
        ),
        None,
    )


def _not_evaluable(
    rule_id: str,
    evidence_ids: tuple[str, ...],
    reason: str,
) -> Assessment:
    return Assessment(
        rule_id=rule_id,
        status="NOT_EVALUABLE",
        outcome=None,
        evidence_ids=list(evidence_ids),
        reason=reason,
    )


def _prepare(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    expected_rule_id: str,
    execution: ProvenancedProfitabilityExecution,
    profitability_evidence: Evidence,
    bundle: MGEParameterBundle,
) -> tuple[Decimal | None, _ResolvedMGEPolicy | None, Assessment | None]:
    validate_provenanced_profitability_execution(execution)
    _validate_identity(purchase, context, rule, expected_rule_id, execution)
    _validate_profitability_evidence(execution, profitability_evidence)

    evidence_ids = _evidence_ids(profitability_evidence, bundle)
    if validate_evidence(profitability_evidence).status != "VALID":
        return (
            None,
            None,
            _not_evaluable(
                expected_rule_id,
                evidence_ids,
                f"{expected_rule_id} no evaluable: Profitability Core no está demostrado.",
            ),
        )

    result = execution.profitability_result
    if result.calculation_state != "DETERMINED" or result.margin_percentage is None:
        return (
            None,
            None,
            _not_evaluable(
                expected_rule_id,
                evidence_ids,
                (
                    f"{expected_rule_id} no evaluable: profitability "
                    f"{result.calculation_state}."
                ),
            ),
        )

    policy, policy_issue = _resolve_policy(
        execution=execution,
        context=context,
        profitability_evidence=profitability_evidence,
        bundle=bundle,
    )
    if policy is None:
        assert policy_issue is not None
        return (
            None,
            None,
            _not_evaluable(
                expected_rule_id,
                evidence_ids,
                f"{expected_rule_id} no evaluable: {policy_issue}.",
            ),
        )

    return result.margin_percentage, policy, None


def evaluate_r_mge_001(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    execution: ProvenancedProfitabilityExecution,
    profitability_evidence: Evidence,
    bundle: MGEParameterBundle,
) -> Assessment:
    """Evaluate margin percentage below the resolved minimum."""
    margin, policy, blocked = _prepare(
        purchase=purchase,
        context=context,
        rule=rule,
        expected_rule_id=R_MGE_001,
        execution=execution,
        profitability_evidence=profitability_evidence,
        bundle=bundle,
    )
    if blocked is not None:
        return blocked
    assert margin is not None and policy is not None

    triggered = margin < policy.minimum
    return Assessment(
        rule_id=R_MGE_001,
        status="EVALUABLE",
        outcome="TRUE" if triggered else "FALSE",
        evidence_ids=list(policy.evidence_ids),
        reason=(
            "R-MGE-001 demostrada: margen inferior a P-MGE-001."
            if triggered
            else "R-MGE-001 no demostrada: margen cumple P-MGE-001."
        ),
    )


def evaluate_r_mge_002(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    execution: ProvenancedProfitabilityExecution,
    profitability_evidence: Evidence,
    bundle: MGEParameterBundle,
) -> Assessment:
    """Evaluate the authorized non-overlapping target-tolerance band."""
    margin, policy, blocked = _prepare(
        purchase=purchase,
        context=context,
        rule=rule,
        expected_rule_id=R_MGE_002,
        execution=execution,
        profitability_evidence=profitability_evidence,
        bundle=bundle,
    )
    if blocked is not None:
        return blocked
    assert margin is not None and policy is not None

    lower_by_tolerance = policy.target - policy.tolerance
    triggered = (
        margin >= policy.minimum
        and margin >= lower_by_tolerance
        and margin < policy.target
    )
    return Assessment(
        rule_id=R_MGE_002,
        status="EVALUABLE",
        outcome="TRUE" if triggered else "FALSE",
        evidence_ids=list(policy.evidence_ids),
        reason=(
            "R-MGE-002 demostrada: margen dentro de la banda autorizada de tolerancia."
            if triggered
            else "R-MGE-002 no demostrada: margen fuera de la banda autorizada de tolerancia."
        ),
    )


def evaluate_r_mge_003(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    execution: ProvenancedProfitabilityExecution,
    profitability_evidence: Evidence,
    bundle: MGEParameterBundle,
) -> Assessment:
    """Evaluate margin percentage at or above the resolved target."""
    margin, policy, blocked = _prepare(
        purchase=purchase,
        context=context,
        rule=rule,
        expected_rule_id=R_MGE_003,
        execution=execution,
        profitability_evidence=profitability_evidence,
        bundle=bundle,
    )
    if blocked is not None:
        return blocked
    assert margin is not None and policy is not None

    triggered = margin >= policy.target
    return Assessment(
        rule_id=R_MGE_003,
        status="EVALUABLE",
        outcome="TRUE" if triggered else "FALSE",
        evidence_ids=list(policy.evidence_ids),
        reason=(
            "R-MGE-003 demostrada: margen cumple o supera P-MGE-002."
            if triggered
            else "R-MGE-003 no demostrada: margen inferior a P-MGE-002."
        ),
    )


__all__ = [
    "MGEParameterBundle",
    "PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE",
    "PERCENTAGE_POINTS_UNIT",
    "PERCENT_UNIT",
    "PROFITABILITY_EVIDENCE_SOURCE_TYPE",
    "P_MGE_001",
    "P_MGE_002",
    "P_MGE_003",
    "R_MGE_001",
    "R_MGE_002",
    "R_MGE_003",
    "evaluate_r_mge_001",
    "evaluate_r_mge_002",
    "evaluate_r_mge_003",
    "profitability_result_ref",
]
