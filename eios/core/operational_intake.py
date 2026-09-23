"""Non-authoritative intake manifest for the first operational expediente.

The intake layer answers only whether the collection package contains references
for the canonical documentary blocks required by the closed admission contract.
It does not authenticate, parse, approve, or promote any supplied material.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Literal


RequirementKind = Literal["REQUIRED", "CONDITIONAL"]
IntakeReadiness = Literal["REQUIRED_SET_COMPLETE", "REQUIRED_SET_INCOMPLETE"]


CANONICAL_INTAKE_ITEMS: tuple[tuple[str, RequirementKind], ...] = (
    ("purchase_operation", "REQUIRED"),
    ("decision_context", "REQUIRED"),
    ("finance_snapshot", "REQUIRED"),
    ("finance_cash_flows", "REQUIRED"),
    ("parameter_p_fin_001", "REQUIRED"),
    ("parameter_p_fin_002", "CONDITIONAL"),
    ("operation_support_document", "REQUIRED"),
    ("order_document", "REQUIRED"),
    ("order_version", "REQUIRED"),
    ("confirmation_document", "REQUIRED"),
    ("required_installment_calendar", "REQUIRED"),
    ("projection_criteria_content", "REQUIRED"),
    ("treasury_support_documents", "REQUIRED"),
    ("treasury_declaration", "REQUIRED"),
    ("treasury_contextual_assessment", "REQUIRED"),
    ("treasury_additional_material", "CONDITIONAL"),
    ("treasury_mandate_documents", "REQUIRED"),
    ("treasury_personal_review", "REQUIRED"),
    ("flow_inventory_perimeters", "REQUIRED"),
    ("flow_inventory_documents", "REQUIRED"),
    ("flow_inventory_candidates", "REQUIRED"),
    ("captured_flow_assessments", "REQUIRED"),
    ("flow_inventory_mandate_documents", "REQUIRED"),
    ("flow_inventory_personal_review", "REQUIRED"),
)


@dataclass(frozen=True)
class OperationalIntakeItem:
    item_id: str
    requirement: RequirementKind
    supplied_refs: tuple[str, ...]

    @property
    def present(self) -> bool:
        return bool(self.supplied_refs)


@dataclass(frozen=True)
class OperationalExpedientIntakeManifest:
    profile: str
    case_kind: str
    items: tuple[OperationalIntakeItem, ...]
    readiness: IntakeReadiness
    missing_required_items: tuple[str, ...]
    pending_conditional_items: tuple[str, ...]
    limitations: tuple[str, ...]
    manifest_fingerprint: str


def _validate_refs(item_id: str, refs: tuple[str, ...]) -> tuple[str, ...]:
    if type(refs) is not tuple:
        raise TypeError(f"{item_id} references must be a tuple")
    if len(refs) != len(set(refs)):
        raise ValueError(f"{item_id} contains duplicate references")
    for ref in refs:
        if not isinstance(ref, str) or not ref or ref != ref.strip():
            raise ValueError(f"{item_id} contains an invalid reference")
    return refs


def build_operational_expedient_intake_manifest(
    *,
    supplied_references: dict[str, tuple[str, ...]],
) -> OperationalExpedientIntakeManifest:
    """Build a deterministic collection manifest without interpreting documents.

    Unknown keys fail closed so the manifest cannot silently grow a parallel
    intake vocabulary. Conditional items are reported separately and never
    treated as required without the relevant downstream contract deciding so.
    """
    if type(supplied_references) is not dict:
        raise TypeError("supplied_references must be a dict")

    known = {item_id for item_id, _ in CANONICAL_INTAKE_ITEMS}
    unknown = set(supplied_references) - known
    if unknown:
        raise ValueError(
            "Unknown intake item(s): " + ", ".join(sorted(unknown))
        )

    items: list[OperationalIntakeItem] = []
    missing_required: list[str] = []
    pending_conditional: list[str] = []

    for item_id, requirement in CANONICAL_INTAKE_ITEMS:
        refs = _validate_refs(item_id, supplied_references.get(item_id, ()))
        item = OperationalIntakeItem(
            item_id=item_id,
            requirement=requirement,
            supplied_refs=refs,
        )
        items.append(item)
        if not item.present:
            if requirement == "REQUIRED":
                missing_required.append(item_id)
            else:
                pending_conditional.append(item_id)

    readiness: IntakeReadiness = (
        "REQUIRED_SET_COMPLETE"
        if not missing_required
        else "REQUIRED_SET_INCOMPLETE"
    )

    limitations = (
        "La presencia de una referencia no demuestra autenticidad, suficiencia ni autoridad.",
        "REQUIRED_SET_COMPLETE no equivale a STRUCTURALLY_ADMISSIBLE ni a APTO.",
        "Los elementos CONDITIONAL no se promocionan a obligatorios en esta capa.",
        "El intake no construye objetos de dominio ni ejecuta QTG.",
    )

    payload = {
        "schema_version": "EIOS-OPERATIONAL-INTAKE-01/v0.1",
        "profile": "PROJECTION_ONLY",
        "case_kind": "PRESENTED_OPERATIONAL",
        "items": [
            {
                "item_id": item.item_id,
                "requirement": item.requirement,
                "supplied_refs": list(item.supplied_refs),
            }
            for item in items
        ],
        "readiness": readiness,
        "missing_required_items": missing_required,
        "pending_conditional_items": pending_conditional,
        "limitations": list(limitations),
    }
    fingerprint = sha256(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()

    return OperationalExpedientIntakeManifest(
        profile="PROJECTION_ONLY",
        case_kind="PRESENTED_OPERATIONAL",
        items=tuple(items),
        readiness=readiness,
        missing_required_items=tuple(missing_required),
        pending_conditional_items=tuple(pending_conditional),
        limitations=limitations,
        manifest_fingerprint=fingerprint,
    )


def empty_operational_expedient_intake_manifest() -> OperationalExpedientIntakeManifest:
    """Return the canonical empty template; it is intentionally incomplete."""
    return build_operational_expedient_intake_manifest(supplied_references={})


__all__ = [
    "CANONICAL_INTAKE_ITEMS",
    "IntakeReadiness",
    "OperationalExpedientIntakeManifest",
    "OperationalIntakeItem",
    "RequirementKind",
    "build_operational_expedient_intake_manifest",
    "empty_operational_expedient_intake_manifest",
]
