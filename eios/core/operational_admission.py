"""Structural preflight for the first PROJECTION_ONLY operational expediente.

This module validates admission structure only. It does not authenticate external
sources, execute QTG, or determine APTO/NO_APTO.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Literal

from .projection_material_envelope import ProjectionMaterialEnvelope
from .projection_quality_producer import (
    ProjectionQualityReceipt,
    produce_projection_quality,
    validate_projection_quality_receipt,
)
from .projection_quality_consumer import (
    ProjectionQualityConsumption,
    consume_projection_quality,
    validate_projection_quality_consumption,
)


AdmissionStatus = Literal[
    "STRUCTURALLY_ADMISSIBLE",
    "REJECTED_SYNTHETIC_MATERIAL",
    "REJECTED_NON_OPERATIONAL_NATURE",
]


@dataclass(frozen=True)
class OperationalAdmissionPreflight:
    status: AdmissionStatus
    profile: str
    envelope_fingerprint: str
    material_natures: tuple[tuple[str, str | None], ...]
    pending_treasury_conditions: tuple[str, ...]
    pending_flow_conditions: tuple[str, ...]
    unassessed_captured_flow_ids: tuple[str, ...]
    unmatched_candidate_refs: tuple[str, ...]
    unreviewed_required_installment_refs: tuple[str, ...]
    limitations: tuple[str, ...]
    preflight_fingerprint: str

    @property
    def structurally_admissible(self) -> bool:
        return self.status == "STRUCTURALLY_ADMISSIBLE"


def _canonical(payload: dict) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def preflight_projection_only_operational_envelope(
    envelope: ProjectionMaterialEnvelope,
) -> OperationalAdmissionPreflight:
    """Check whether exact bound material may legitimately enter OPERATIONAL QTG.

    The preflight deliberately does not require complete/favorable business
    findings. Pending/conflicting material remains visible for QTG to evaluate.
    """
    if not isinstance(envelope, ProjectionMaterialEnvelope):
        raise TypeError("Expected constructed ProjectionMaterialEnvelope")

    payload = envelope.to_payload()
    if payload.get("profile") != "PROJECTION_ONLY":
        raise ValueError("Operational admission requires PROJECTION_ONLY profile")

    membership = payload.get("recomputed_membership")
    if not isinstance(membership, dict):
        raise ValueError("Projection material envelope lacks recomputed membership")

    natures = membership.get("material_natures")
    if not isinstance(natures, dict):
        raise ValueError("Projection material envelope lacks material natures")

    ordered_natures = tuple(sorted(natures.items()))
    non_operational = tuple(
        key for key, value in ordered_natures
        if value is not None and value != "PRESENTED_OPERATIONAL"
    )

    if membership.get("contains_synthetic_material") is True:
        status: AdmissionStatus = "REJECTED_SYNTHETIC_MATERIAL"
    elif non_operational:
        status = "REJECTED_NON_OPERATIONAL_NATURE"
    else:
        status = "STRUCTURALLY_ADMISSIBLE"

    limitations = [
        "La admisión estructural no autentica documentos, personas, canales ni mandatos.",
        "PRESENTED_OPERATIONAL declara naturaleza presentada; no equivale a verdad o suficiencia.",
        "Pendientes, conflictos y material incompleto se conservan para evaluación QTG.",
        "STRUCTURALLY_ADMISSIBLE no equivale a APTO.",
    ]
    if non_operational:
        limitations.append(
            "Naturalezas no operacionales detectadas: " + ", ".join(non_operational)
        )

    core = dict(
        schema_version="QTG-OPERATIONAL-ADMISSION-PREFLIGHT-01/v0.1",
        status=status,
        profile="PROJECTION_ONLY",
        envelope_fingerprint=envelope.fingerprint,
        material_natures=list(ordered_natures),
        pending_treasury_conditions=list(
            membership.get("treasury_pending_conditions", ())
        ),
        pending_flow_conditions=list(membership.get("flow_pending_conditions", ())),
        unassessed_captured_flow_ids=list(
            membership.get("unassessed_captured_flow_ids", ())
        ),
        unmatched_candidate_refs=list(membership.get("unmatched_candidate_refs", ())),
        unreviewed_required_installment_refs=list(
            membership.get("unreviewed_required_installment_refs", ())
        ),
        limitations=limitations,
    )
    fingerprint = sha256(_canonical(core)).hexdigest()

    return OperationalAdmissionPreflight(
        status=status,
        profile="PROJECTION_ONLY",
        envelope_fingerprint=envelope.fingerprint,
        material_natures=ordered_natures,
        pending_treasury_conditions=tuple(core["pending_treasury_conditions"]),
        pending_flow_conditions=tuple(core["pending_flow_conditions"]),
        unassessed_captured_flow_ids=tuple(core["unassessed_captured_flow_ids"]),
        unmatched_candidate_refs=tuple(core["unmatched_candidate_refs"]),
        unreviewed_required_installment_refs=tuple(
            core["unreviewed_required_installment_refs"]
        ),
        limitations=tuple(limitations),
        preflight_fingerprint=fingerprint,
    )


def build_operational_qtg_from_admitted_envelope(
    envelope: ProjectionMaterialEnvelope,
) -> tuple[
    OperationalAdmissionPreflight,
    ProjectionQualityReceipt,
    ProjectionQualityConsumption,
]:
    """Run the already-authorized operational producer only after preflight passes."""
    preflight = preflight_projection_only_operational_envelope(envelope)
    if not preflight.structurally_admissible:
        raise ValueError(f"Operational envelope is not admissible: {preflight.status}")

    receipt = produce_projection_quality(
        envelope=envelope,
        execution_mode="OPERATIONAL",
    )
    validate_projection_quality_receipt(
        receipt=receipt,
        envelope=envelope,
        execution_mode="OPERATIONAL",
    )
    consumption = consume_projection_quality(
        receipt=receipt,
        envelope=envelope,
        execution_mode="OPERATIONAL",
        consumption_scope="OPERATIONAL",
    )
    validate_projection_quality_consumption(
        consumption=consumption,
        receipt=receipt,
        envelope=envelope,
        execution_mode="OPERATIONAL",
        consumption_scope="OPERATIONAL",
    )
    return preflight, receipt, consumption


__all__ = [
    "AdmissionStatus",
    "OperationalAdmissionPreflight",
    "build_operational_qtg_from_admitted_envelope",
    "preflight_projection_only_operational_envelope",
]
