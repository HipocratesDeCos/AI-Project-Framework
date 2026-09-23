"""Canonical provenance taxonomy for EIOS validation and operational cases.

This module classifies already-constructed source artifacts. It does not change
their material nature, authenticate external material, execute QTG, or grant
decision authority. In particular, a reference operational simulation remains
synthetic material and must use SYNTHETIC_TEST semantics downstream.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Literal

from .operational_intake import OperationalExpedientIntakeManifest
from .projection_mock_dataset import ProjectionMockDataset
from .projection_synthetic_adapter import ProjectionOnlySyntheticMaterialBundle


CaseKind = Literal[
    "SYNTHETIC_TEST",
    "REFERENCE_OPERATIONAL_SIMULATION",
    "PRESENTED_OPERATIONAL",
]
OperationalPath = Literal["FORBIDDEN", "REQUIRES_ADMISSION"]
EffectScope = Literal["NO_OPERATIONAL_EFFECT", "NOT_GRANTED_BY_CLASSIFICATION"]
ValidationScope = Literal[
    "TECHNICAL_TEST",
    "PRODUCT_REFERENCE_E2E",
    "ENTERPRISE_PRESENTED_CASE",
]

SCHEMA_VERSION = "EIOS-CASE-PROVENANCE-01/v0.1"


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _identifier(value: str, field: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"{field} must be an explicit nonempty identifier")
    if len(value) > 128:
        raise ValueError(f"{field} exceeds maximum length")
    return value


@dataclass(frozen=True, init=False)
class CaseProvenance:
    """Immutable classification bound to one exact source artifact."""

    _material: bytes

    def __init__(self) -> None:
        raise TypeError("Use a dedicated case provenance classifier")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()

    @property
    def case_kind(self) -> CaseKind:
        return self.to_payload()["case_kind"]


def _build(
    *,
    case_kind: CaseKind,
    source_type: str,
    source_fingerprint: str,
    material_nature: str,
    qtg_mode_policy: str,
    operational_path: OperationalPath,
    effect_scope: EffectScope,
    validation_scope: ValidationScope,
    requires_operational_preflight: bool,
    reference_case_id: str | None,
    limitations: tuple[str, ...],
) -> CaseProvenance:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "case_kind": case_kind,
        "source_type": source_type,
        "source_fingerprint": _identifier(source_fingerprint, "source_fingerprint"),
        "material_nature": material_nature,
        "qtg_mode_policy": qtg_mode_policy,
        "operational_path": operational_path,
        "effect_scope": effect_scope,
        "validation_scope": validation_scope,
        "requires_operational_preflight": requires_operational_preflight,
        "reference_case_id": reference_case_id,
        "decision_authority": False,
        "limitations": list(limitations),
    }
    result = object.__new__(CaseProvenance)
    object.__setattr__(result, "_material", _canonical(payload))
    return result


def classify_synthetic_test_case(dataset: ProjectionMockDataset) -> CaseProvenance:
    """Classify a structural mock dataset as a technical synthetic test."""
    if not isinstance(dataset, ProjectionMockDataset):
        raise TypeError("Expected validated ProjectionMockDataset")
    return _build(
        case_kind="SYNTHETIC_TEST",
        source_type="ProjectionMockDataset",
        source_fingerprint=dataset.fingerprint,
        material_nature="SYNTHETIC",
        qtg_mode_policy="SYNTHETIC_TEST_ONLY",
        operational_path="FORBIDDEN",
        effect_scope="NO_OPERATIONAL_EFFECT",
        validation_scope="TECHNICAL_TEST",
        requires_operational_preflight=False,
        reference_case_id=None,
        limitations=(
            "El caso existe para prueba técnica y no representa una empresa real.",
            "La clasificación no modifica la naturaleza SYNTHETIC del material.",
            "No puede producir efecto operacional ni autoridad decisional.",
        ),
    )


def classify_reference_operational_simulation(
    *,
    bundle: ProjectionOnlySyntheticMaterialBundle,
    reference_case_id: str,
) -> CaseProvenance:
    """Classify a complete synthetic bundle for product-level reference E2E."""
    if not isinstance(bundle, ProjectionOnlySyntheticMaterialBundle):
        raise TypeError("Expected ProjectionOnlySyntheticMaterialBundle")
    reference_case_id = _identifier(reference_case_id, "reference_case_id")
    payload = bundle.to_payload()
    if payload.get("case_kind") != "SYNTHETIC" \
            or payload.get("effect_scope") != "NO_OPERATIONAL_EFFECT":
        raise ValueError("Reference simulation requires synthetic no-effect material")
    if not bundle.envelope.to_payload()["recomputed_membership"].get(
        "contains_synthetic_material"
    ):
        raise ValueError("Reference simulation must preserve synthetic material nature")

    return _build(
        case_kind="REFERENCE_OPERATIONAL_SIMULATION",
        source_type="ProjectionOnlySyntheticMaterialBundle",
        source_fingerprint=bundle.fingerprint,
        material_nature="SYNTHETIC",
        qtg_mode_policy="SYNTHETIC_TEST_ONLY",
        operational_path="FORBIDDEN",
        effect_scope="NO_OPERATIONAL_EFFECT",
        validation_scope="PRODUCT_REFERENCE_E2E",
        requires_operational_preflight=False,
        reference_case_id=reference_case_id,
        limitations=(
            "La simulación reproduce un caso empresarial de referencia, no una operación real.",
            "QTG conserva SYNTHETIC_TEST y el material conserva naturaleza SYNTHETIC.",
            "REFERENCE_OPERATIONAL_SIMULATION no puede promocionarse a PRESENTED_OPERATIONAL.",
            "No puede producir efecto operacional ni autoridad decisional.",
        ),
    )


def classify_presented_operational_case(
    manifest: OperationalExpedientIntakeManifest,
) -> CaseProvenance:
    """Classify an intake manifest without granting admission or operational effect."""
    if not isinstance(manifest, OperationalExpedientIntakeManifest):
        raise TypeError("Expected OperationalExpedientIntakeManifest")
    if manifest.case_kind != "PRESENTED_OPERATIONAL":
        raise ValueError("Operational intake must preserve PRESENTED_OPERATIONAL")
    return _build(
        case_kind="PRESENTED_OPERATIONAL",
        source_type="OperationalExpedientIntakeManifest",
        source_fingerprint=manifest.manifest_fingerprint,
        material_nature="PRESENTED_OPERATIONAL",
        qtg_mode_policy="OPERATIONAL_AFTER_ADMISSION",
        operational_path="REQUIRES_ADMISSION",
        effect_scope="NOT_GRANTED_BY_CLASSIFICATION",
        validation_scope="ENTERPRISE_PRESENTED_CASE",
        requires_operational_preflight=True,
        reference_case_id=None,
        limitations=(
            "PRESENTED_OPERATIONAL describe procedencia presentada y no autentica el contenido.",
            "La clasificación no equivale a STRUCTURALLY_ADMISSIBLE ni a APTO.",
            "El modo OPERATIONAL solo puede alcanzarse tras la frontera de admisión aplicable.",
            "La clasificación no concede autoridad decisional.",
        ),
    )


__all__ = [
    "CaseKind",
    "CaseProvenance",
    "EffectScope",
    "OperationalPath",
    "SCHEMA_VERSION",
    "ValidationScope",
    "classify_presented_operational_case",
    "classify_reference_operational_simulation",
    "classify_synthetic_test_case",
]
