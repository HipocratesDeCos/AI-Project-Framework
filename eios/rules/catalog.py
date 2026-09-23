"""Technical catalog of normative metadata for implemented EIOS rules.

This module does not define new business authority. It materializes only the
rule properties already approved for rules with executable bridges.
"""
from __future__ import annotations

from dataclasses import dataclass

from eios.core.crc_mvp import ConsolidatedResult, Effect, RuleMetadata, Severity
from eios.core.models import Rule


@dataclass(frozen=True)
class ImplementedRuleMetadata:
    rule_id: str
    effect: Effect
    severity: Severity
    requires_evidence: bool = True
    active_result: ConsolidatedResult | None = None


_IMPLEMENTED_RULES: dict[str, ImplementedRuleMetadata] = {
    "R-DAT-001": ImplementedRuleMetadata("R-DAT-001", "R3", "INFORMATIVA"),
    "R-DAT-002": ImplementedRuleMetadata("R-DAT-002", "R3", "MEDIA"),
    "R-DAT-003": ImplementedRuleMetadata("R-DAT-003", "R0", "CRÍTICA", active_result="INFORMACIÓN INSUFICIENTE"),
    "R-ENT-001": ImplementedRuleMetadata("R-ENT-001", "R2", "ALTA"),
    "R-STK-001": ImplementedRuleMetadata("R-STK-001", "R1", "ALTA"),
    "R-STK-002": ImplementedRuleMetadata("R-STK-002", "R2", "ALTA"),
    "R-STK-003": ImplementedRuleMetadata("R-STK-003", "R2", "ALTA"),
    "R-STK-004": ImplementedRuleMetadata("R-STK-004", "R1", "ALTA"),
    "R-FIN-001": ImplementedRuleMetadata("R-FIN-001", "R0", "CRÍTICA"),
    "R-FIN-002": ImplementedRuleMetadata("R-FIN-002", "R0", "CRÍTICA"),
    # FIN-AUTH-v0.1 authorizes the ordinary R1 condition only; no automatic R0 escalation.
    "R-FIN-003": ImplementedRuleMetadata("R-FIN-003", "R1", "ALTA"),
    "R-HIS-001": ImplementedRuleMetadata("R-HIS-001", "R3", "MEDIA"),
    "R-HIS-002": ImplementedRuleMetadata("R-HIS-002", "R3", "INFORMATIVA"),
    "R-HIS-003": ImplementedRuleMetadata("R-HIS-003", "R3", "MEDIA"),
    "R-PRE-001": ImplementedRuleMetadata("R-PRE-001", "R2", "ALTA"),
    "R-PRE-002": ImplementedRuleMetadata("R-PRE-002", "R1", "ALTA"),
    "R-PRE-003": ImplementedRuleMetadata("R-PRE-003", "R3", "INFORMATIVA"),
    "R-PAG-001": ImplementedRuleMetadata("R-PAG-001", "R2", "ALTA", active_result="NEGOCIAR"),
    "R-PAG-002": ImplementedRuleMetadata("R-PAG-002", "R1", "ALTA", active_result="COMPRAR CONDICIONADO"),
    "R-PROV-001": ImplementedRuleMetadata("R-PROV-001", "R2", "MEDIA", active_result="NEGOCIAR"),
    "R-PROV-002": ImplementedRuleMetadata("R-PROV-002", "R2", "ALTA", active_result="NEGOCIAR"),
    # ROT001 Track B Completion Package v0.1: negotiation only; no automatic escalation.
    "R-ROT-001": ImplementedRuleMetadata("R-ROT-001", "R2", "ALTA", active_result="NEGOCIAR"),
    # ROT002 Completion Package v0.1: R1 remains ordinary; no automatic R0 escalation.
    "R-ROT-002": ImplementedRuleMetadata("R-ROT-002", "R1", "ALTA", active_result="NO COMPRAR"),
    # MGE-RULES-AUTH v0.1 authorizes ordinary metadata only; no R0 escalation.
    "R-MGE-001": ImplementedRuleMetadata("R-MGE-001", "R1", "ALTA"),
    "R-MGE-002": ImplementedRuleMetadata("R-MGE-002", "R2", "MEDIA"),
    "R-MGE-003": ImplementedRuleMetadata("R-MGE-003", "R3", "INFORMATIVA"),
}


def implemented_rule_ids() -> tuple[str, ...]:
    """Return the deterministic set of rules backed by executable bridges."""
    return tuple(sorted(_IMPLEMENTED_RULES))


def _implemented(rule_id: str) -> ImplementedRuleMetadata:
    item = _IMPLEMENTED_RULES.get(rule_id)
    if item is None:
        raise ValueError(f"rule_id no materializada en catálogo: {rule_id}")
    return item


def _validate_version(rules_version: str) -> None:
    if not rules_version or not rules_version.strip():
        raise ValueError("rules_version no puede estar vacía")


def authorized_rule(rule_id: str, rules_version: str) -> Rule:
    """Build the canonical C0 Rule object for one implemented rule."""
    _validate_version(rules_version)
    item = _implemented(rule_id)
    return Rule(
        rule_id=item.rule_id,
        version=rules_version,
        requires_evidence=item.requires_evidence,
    )


def authorized_rule_metadata(rule_id: str, rules_version: str) -> RuleMetadata:
    """Resolve approved metadata for one implemented rule and rules version."""
    _validate_version(rules_version)
    item = _implemented(rule_id)
    return RuleMetadata(
        rule_id=item.rule_id,
        version=rules_version,
        effect=item.effect,
        severity=item.severity,
        active_result=item.active_result,
    )


__all__ = [
    "ImplementedRuleMetadata",
    "authorized_rule",
    "authorized_rule_metadata",
    "implemented_rule_ids",
]
