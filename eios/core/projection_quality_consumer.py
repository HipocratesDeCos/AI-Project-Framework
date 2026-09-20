"""Dedicated provenance-preserving consumer for PROJECTION_ONLY QTG receipts.

This boundary validates the exact receipt against the exact material before it
exposes a specialized consumption record.  It is deliberately independent of
the generic MVP capability invoker and grants no decision authority.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Literal

from .projection_material_envelope import ProjectionMaterialEnvelope
from .projection_quality_producer import (
    ExecutionMode,
    ProjectionQualityReceipt,
    validate_projection_quality_receipt,
)

ConsumptionScope = Literal["TEST_ONLY", "OPERATIONAL"]
CONSUMER_ID = "QTG-PROJECTION-CONSUMER-01"
CONSUMER_VERSION = "0.1"


def _canonical(payload: dict) -> bytes:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8")


@dataclass(frozen=True, init=False)
class ProjectionQualityConsumption:
    """Immutable specialized record retaining the complete validated receipt."""

    _material: bytes

    def __init__(self):
        raise TypeError("Use consume_projection_quality")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()


def consume_projection_quality(*, receipt: ProjectionQualityReceipt,
    envelope: ProjectionMaterialEnvelope, execution_mode: ExecutionMode,
    consumption_scope: ConsumptionScope) -> ProjectionQualityConsumption:
    """Validate exact provenance and expose a non-decisional QTG record."""
    if consumption_scope not in ("TEST_ONLY", "OPERATIONAL"):
        raise ValueError("Unsupported projection quality consumption scope")

    validate_projection_quality_receipt(
        receipt=receipt, envelope=envelope, execution_mode=execution_mode)
    receipt_payload = receipt.to_payload()

    expected_scope = "TEST_ONLY" if execution_mode == "SYNTHETIC_TEST" else "OPERATIONAL"
    if consumption_scope != expected_scope:
        raise ValueError("Projection quality mode and consumption scope do not match")
    if consumption_scope == "OPERATIONAL" and not receipt_payload["operational_effect"]:
        raise ValueError("Operational consumption rejects a nonoperational receipt")

    payload = dict(
        schema_version="QTG-PROJECTION-CONSUMPTION-01/v0.1",
        profile="PROJECTION_ONLY",
        consumer_id=CONSUMER_ID,
        consumer_version=CONSUMER_VERSION,
        technical_status="VALIDATED",
        execution_mode=execution_mode,
        consumption_scope=consumption_scope,
        operational_effect=consumption_scope == "OPERATIONAL",
        assurance_scope=("VALIDATED_SYNTHETIC_TEST_RECEIPT_ONLY"
            if consumption_scope == "TEST_ONLY"
            else "VALIDATED_OPERATIONAL_PROJECTION_INPUT_QUALITY_ONLY"),
        envelope_fingerprint=envelope.fingerprint,
        receipt_fingerprint=receipt.fingerprint,
        functional_quality_result=receipt_payload["quality_result"],
        receipt=receipt_payload,
        decision_authority=False,
    )
    result = object.__new__(ProjectionQualityConsumption)
    object.__setattr__(result, "_material", _canonical(payload))
    return result


def validate_projection_quality_consumption(*,
    consumption: ProjectionQualityConsumption,
    receipt: ProjectionQualityReceipt,
    envelope: ProjectionMaterialEnvelope,
    execution_mode: ExecutionMode,
    consumption_scope: ConsumptionScope) -> None:
    """Recompute the complete specialized record from its exact inputs."""
    if not isinstance(consumption, ProjectionQualityConsumption):
        raise TypeError("Expected constructed ProjectionQualityConsumption")
    recomputed = consume_projection_quality(receipt=receipt, envelope=envelope,
        execution_mode=execution_mode, consumption_scope=consumption_scope)
    if consumption.to_payload() != recomputed.to_payload() \
            or consumption.fingerprint != recomputed.fingerprint:
        raise ValueError("Projection quality consumption is not reproducible")


__all__ = ["CONSUMER_ID", "CONSUMER_VERSION", "ConsumptionScope",
    "ProjectionQualityConsumption", "consume_projection_quality",
    "validate_projection_quality_consumption"]
