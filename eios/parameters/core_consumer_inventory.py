"""Source-audited catalogue of existing *core* parameter consumers.

This metadata is NOT parameter configuration, activation, rule authority, or
evidence that an enterprise application routes values to these consumers.
No numeric business values or operational defaults are defined here.

All listed modules/functions/parameter constants are checked by the
tests/test_core_parameter_consumer_inventory.py structural regression.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Relationship = Literal[
    "DIRECT_RULE",
    "DERIVED_ENGINE",
    "COMPOSITE_RULE",
    "SHARED_RULE_POLICY",
    "DERIVED_THRESHOLD",
    "CONTROL_GATE",
]


@dataclass(frozen=True, slots=True)
class CoreParameterConsumer:
    parameter_id: str
    domain: Literal["FIN", "PRE", "HIS", "STK", "MGE", "PAG"]
    module: str
    callable_name: str
    constant_name: str
    relationship: Relationship
    downstream_rules: tuple[str, ...]
    # A presence record is never proof of activation or evaluability.
    status: Literal["CORE_CONSUMER_SOURCE_IDENTIFIED"] = (
        "CORE_CONSUMER_SOURCE_IDENTIFIED"
    )
    company_activation: Literal["NOT_ATTESTED"] = "NOT_ATTESTED"


CORE_PARAMETER_CONSUMERS: tuple[CoreParameterConsumer, ...] = (
    CoreParameterConsumer(
        "P-FIN-001", "FIN", "eios.finance.provenance",
        "_validate_horizon_resolution", "P_FIN_001", "DERIVED_ENGINE",
        ("R-FIN-001",),
    ),
    CoreParameterConsumer(
        "P-FIN-002", "FIN", "eios.rules.finance",
        "_treasury_minimum", "P_FIN_002", "COMPOSITE_RULE",
        ("R-FIN-001", "R-FIN-003"),
    ),
    CoreParameterConsumer(
        "P-FIN-003", "FIN", "eios.rules.finance",
        "_working_capital_minimum", "P_FIN_003", "DIRECT_RULE",
        ("R-FIN-002",),
    ),
    CoreParameterConsumer(
        "P-FIN-004", "FIN", "eios.rules.finance",
        "evaluate_r_fin_003", "P_FIN_004", "DIRECT_RULE",
        ("R-FIN-003",),
    ),
    CoreParameterConsumer(
        "P-PRE-001", "PRE", "eios.rules.pricing",
        "evaluate_r_pre_001", "P_PRE_001", "DIRECT_RULE",
        ("R-PRE-001",),
    ),
    CoreParameterConsumer(
        "P-PRE-004", "PRE", "eios.rules.pricing",
        "evaluate_r_pre_001", "P_PRE_004", "DIRECT_RULE",
        ("R-PRE-001",),
    ),
    CoreParameterConsumer(
        "P-PRE-005", "PRE", "eios.rules.pricing",
        "evaluate_r_pre_002", "P_PRE_005", "DIRECT_RULE",
        ("R-PRE-002",),
    ),
    CoreParameterConsumer(
        "P-PRE-006", "HIS", "eios.rules.pricing",
        "_minimum_comparable_operations", "P_PRE_006", "DIRECT_RULE",
        ("R-HIS-002",),
    ),
    CoreParameterConsumer(
        "P-DAT-002", "HIS", "eios.rules.pricing",
        "evaluate_r_his_001", "P_DAT_002", "DIRECT_RULE",
        ("R-HIS-001",),
    ),
    CoreParameterConsumer(
        "P-STK-004", "STK", "eios.rules.stock",
        "_coverage_maximum", "P_STK_004", "DIRECT_RULE",
        ("R-STK-002",),
    ),
    CoreParameterConsumer(
        "P-MGE-001", "MGE", "eios.rules.profitability",
        "_resolve_policy", "P_MGE_001", "SHARED_RULE_POLICY",
        ("R-MGE-001", "R-MGE-002", "R-MGE-003"),
    ),
    CoreParameterConsumer(
        "P-MGE-002", "MGE", "eios.rules.profitability",
        "_resolve_policy", "P_MGE_002", "SHARED_RULE_POLICY",
        ("R-MGE-001", "R-MGE-002", "R-MGE-003"),
    ),
    CoreParameterConsumer(
        "P-MGE-003", "MGE", "eios.rules.profitability",
        "_resolve_policy", "P_MGE_003", "SHARED_RULE_POLICY",
        ("R-MGE-001", "R-MGE-002", "R-MGE-003"),
    ),
    CoreParameterConsumer(
        "P-PAG-001", "PAG", "eios.payment_term_minimum",
        "resolve_minimum_payment_term", "P_PAG_001", "DIRECT_RULE",
        ("R-PAG-002",),
    ),
    CoreParameterConsumer(
        "P-PAG-002", "PAG", "eios.payment_term_tolerance",
        "resolve_payment_term_tolerance", "P_PAG_002", "DERIVED_THRESHOLD",
        ("R-PAG-001",),
    ),
    CoreParameterConsumer(
        "P-PAG-003", "PAG", "eios.payment_term_tolerance",
        "resolve_payment_term_tolerance", "P_PAG_003", "DERIVED_THRESHOLD",
        ("R-PAG-001",),
    ),
    CoreParameterConsumer(
        "P-PAG-004", "PAG", "eios.payment_term_control",
        "resolve_payment_term_control", "P_PAG_004", "CONTROL_GATE",
        ("R-PAG-001", "R-PAG-002"),
    ),
)


def get_core_parameter_consumers(
    parameter_id: str | None = None,
) -> tuple[CoreParameterConsumer, ...]:
    """Return source-identified contracts, not actual company configurations.

    An empty result means 'not inventoried in this audited subset'; it does
    NOT prove that the parameter has no consumer elsewhere in EIOS.
    """
    if parameter_id is None:
        return CORE_PARAMETER_CONSUMERS
    if (
        not isinstance(parameter_id, str)
        or not parameter_id
        or parameter_id.strip() != parameter_id
    ):
        raise ValueError("parameter_id must be a canonical, nonempty identifier")
    return tuple(
        consumer for consumer in CORE_PARAMETER_CONSUMERS
        if consumer.parameter_id == parameter_id
    )


__all__ = [
    "CoreParameterConsumer",
    "CORE_PARAMETER_CONSUMERS",
    "get_core_parameter_consumers",
]
