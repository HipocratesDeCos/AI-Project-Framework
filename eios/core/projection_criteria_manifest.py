"""Bind the exact authorized criteria for PROJECTION_ONLY; never execute them."""
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .documentary_payment_review import _reference
from .finance_quality_preparation import FinanceQualityPreparation


CriterionFunction = Literal[
    "HORIZON_FLOW_INVENTORY_COMPLETENESS",
    "PARTICIPATING_FLOW_ATTRIBUTE_SUPPORT",
    "DETERMINATE_PROJECTION_RELIABILITY",
    "OUT_OF_HORIZON_CONFLICT_PRESERVATION",
    "INITIAL_TREASURY_SUFFICIENCY",
    "ECONOMIC_FLOW_UNIQUENESS",
]

REQUIRED_FUNCTIONS = (
    "HORIZON_FLOW_INVENTORY_COMPLETENESS",
    "PARTICIPATING_FLOW_ATTRIBUTE_SUPPORT",
    "DETERMINATE_PROJECTION_RELIABILITY",
    "OUT_OF_HORIZON_CONFLICT_PRESERVATION",
    "INITIAL_TREASURY_SUFFICIENCY",
    "ECONOMIC_FLOW_UNIQUENESS",
)


class AuthorizedProjectionCriterion(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    function: CriterionFunction
    reference: str = Field(min_length=1)
    version: str = Field(min_length=1)
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


@dataclass(frozen=True, init=False)
class ProjectionCriteriaManifest:
    _material: bytes

    def __init__(self):
        raise TypeError("Use build_projection_criteria_manifest")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()


def build_projection_criteria_manifest(*, manifest_ref: str, manifest_version: str,
    authority_ref: str, authorized_at: datetime,
    criteria: tuple[AuthorizedProjectionCriterion, ...]) -> ProjectionCriteriaManifest:
    """Preserve a closed authorization declaration, not executable policy."""
    for value in (manifest_ref, manifest_version, authority_ref):
        _reference(value)
    if not isinstance(authorized_at, datetime) or authorized_at.utcoffset() is None:
        raise ValueError("Aware authorization time required")
    if type(criteria) is not tuple:
        raise TypeError("Explicit criterion tuple required")
    entries, functions, keys = [], set(), set()
    for criterion in criteria:
        if not isinstance(criterion, AuthorizedProjectionCriterion):
            raise TypeError("Expected AuthorizedProjectionCriterion")
        criterion = AuthorizedProjectionCriterion.model_validate(
            criterion.model_dump(mode="python"))
        _reference(criterion.reference); _reference(criterion.version)
        key = (criterion.reference, criterion.version)
        if criterion.function in functions:
            raise ValueError("Duplicate criterion function")
        if key in keys:
            raise ValueError("Duplicate criterion reference/version")
        functions.add(criterion.function); keys.add(key)
        entries.append(criterion.model_dump(mode="json"))
    if functions != set(REQUIRED_FUNCTIONS):
        raise ValueError("Manifest must cover the exact PROJECTION_ONLY criterion functions")
    payload = dict(schema_version="QTG-PROJECTION-CRITERIA-MANIFEST-01/v0.2",
        profile="PROJECTION_ONLY", consumer="future_projection_only_quality_producer",
        manifest_ref=manifest_ref, manifest_version=manifest_version,
        authority_ref=authority_ref, authorized_at=authorized_at.isoformat(),
        criteria=entries, required_functions=list(REQUIRED_FUNCTIONS),
        assurance_scope="EXACT_AUTHORIZED_CRITERION_IDENTITIES_ONLY")
    result = object.__new__(ProjectionCriteriaManifest)
    object.__setattr__(result, "_material", json.dumps(payload, ensure_ascii=False,
        sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"))
    return result


def validate_preparation_criteria_against_manifest(
    preparation: FinanceQualityPreparation, manifest: ProjectionCriteriaManifest) -> None:
    """Require exact reference/version/hash equality; do not read criterion text."""
    if not isinstance(preparation, FinanceQualityPreparation):
        raise TypeError("Expected constructed FinanceQualityPreparation")
    if not isinstance(manifest, ProjectionCriteriaManifest):
        raise TypeError("Expected constructed ProjectionCriteriaManifest")
    presented = preparation.to_payload()["presented_criteria"]
    presented_map = {(item["reference"], item["version"]): item["sha256"]
                     for item in presented}
    authorized = manifest.to_payload()["criteria"]
    authorized_map = {(item["reference"], item["version"]): item["content_sha256"]
                      for item in authorized}
    if presented_map != authorized_map:
        raise ValueError("Presented criteria do not exactly match authorized manifest")


__all__ = ["AuthorizedProjectionCriterion", "CriterionFunction",
    "ProjectionCriteriaManifest", "REQUIRED_FUNCTIONS",
    "build_projection_criteria_manifest",
    "validate_preparation_criteria_against_manifest"]
