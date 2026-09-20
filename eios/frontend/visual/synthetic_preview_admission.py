"""Pure admission boundary for registered U1.5A synthetic visual fixtures."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from hmac import compare_digest
import json
import math
import re
from types import MappingProxyType
from typing import Any

from .vertical_mvp_artifact import (
    VerticalMVPReadOnlyArtifact,
    build_vertical_mvp_readonly_artifact,
)
from .vertical_mvp_delivery import (
    VerticalMVPReadOnlyDelivery,
    build_vertical_mvp_readonly_delivery,
)


SCHEMA_VERSION = "EIOS-VERTICAL-MVP-SYNTHETIC-PREVIEW-CASE-01/v0.1"
ADMISSION_SCHEMA_VERSION = "EIOS-LOCAL-SYNTHETIC-PREVIEW-ADMISSION-01/v0.1"
PROFILE = "LOCAL_SYNTHETIC_PREVIEW"
CLASSIFICATION = "SYNTHETIC_PRESENTATION_FIXTURE"
SCOPE = "TEST_ONLY"
NOTICE = "VISTA SINTÉTICA DE PRUEBA — NO ES UNA EJECUCIÓN OPERACIONAL DE EIOS"
MAX_FIXTURE_BYTES = 262_144
MAX_JSON_DEPTH = 32

_CASE_ID_PATTERN = re.compile(r"SYNTHETIC-PREVIEW-[A-Z0-9][A-Z0-9-]{0,63}")
_AUTHORIZED_SYNTHETIC_PREVIEW_CASES = MappingProxyType(
    {
        "SYNTHETIC-PREVIEW-001": (
            "fbe81e2e898bbc209a853c9b88beca01"
            "e1e88153e1f69b5b76ba3ff348926f60"
        )
    }
)

_CASE_KEYS = frozenset(
    {
        "schema_version",
        "case_id",
        "classification",
        "scope",
        "operational_effect",
        "decision_authority",
        "execution_claim",
        "notice",
        "view_model",
    }
)
_VIEW_MODEL_KEYS = frozenset(
    {
        "execution_status",
        "policy_version",
        "failure_reason",
        "unresolved_items",
        "capabilities",
        "rules_available",
        "rule_coverage",
        "crc_support_result",
        "assessments",
        "rule_trace_references",
        "scenario_support_available",
        "scenario_execution_context",
        "scenario_records",
        "scenario_comparison",
    }
)
_CAPABILITY_KEYS = frozenset(
    {
        "capability",
        "status",
        "result_available",
        "trace_references",
        "unresolved_items",
    }
)
_RULE_COVERAGE_KEYS = frozenset({"executed_rule_ids", "omitted_rule_ids"})
_CRC_RESULT_KEYS = frozenset(
    {"consolidated_result", "dominant_reason", "relevant_factors", "conflicts"}
)
_ASSESSMENT_KEYS = frozenset(
    {"rule_id", "status", "outcome", "reason", "evidence_ids"}
)
_SCENARIO_CONTEXT_KEYS = frozenset(
    {
        "execution_id",
        "decision_id",
        "rules_version",
        "parameters_version",
        "data_snapshot_id",
    }
)
_SCENARIO_RECORD_KEYS = frozenset(
    {
        "scenario_id",
        "status",
        "values",
        "trace_references",
        "unresolved_items",
        "failure_reason",
    }
)
_SCENARIO_COMPARISON_KEYS = frozenset(
    {
        "scenario_ids",
        "observations",
        "differences",
        "missing",
        "statuses",
        "unresolved_items",
        "traceability",
    }
)


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("fixture JSON contiene una clave duplicada")
        result[key] = value
    return result


def _reject_non_json_constant(value: str) -> None:
    raise ValueError(f"fixture JSON contiene una constante no finita: {value}")


def _validate_json_value(value: Any, *, depth: int = 1) -> None:
    if depth > MAX_JSON_DEPTH:
        raise ValueError(f"fixture JSON supera la profundidad máxima {MAX_JSON_DEPTH}")
    if value is None or type(value) in {bool, int}:
        return
    if type(value) is str:
        try:
            value.encode("utf-8", errors="strict")
        except UnicodeEncodeError as exc:
            raise ValueError("fixture JSON contiene Unicode no escalar") from exc
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("fixture JSON contiene un número no finito")
        return
    if type(value) is list:
        for item in value:
            _validate_json_value(item, depth=depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError("fixture JSON contiene una clave no textual")
            try:
                key.encode("utf-8", errors="strict")
            except UnicodeEncodeError as exc:
                raise ValueError("fixture JSON contiene Unicode no escalar") from exc
            _validate_json_value(item, depth=depth + 1)
        return
    raise ValueError("fixture contiene un tipo ajeno al dominio JSON")


def _exact_object(value: Any, required: frozenset[str], name: str) -> dict[str, Any]:
    if type(value) is not dict:
        raise ValueError(f"{name} debe ser un objeto JSON")
    actual = frozenset(value)
    if actual != required:
        missing = ", ".join(sorted(required - actual)) or "ninguna"
        extra = ", ".join(sorted(actual - required)) or "ninguna"
        raise ValueError(f"{name} tiene claves no exactas; faltan: {missing}; sobran: {extra}")
    return value


def _string(value: Any, name: str, *, non_empty: bool = False) -> str:
    if type(value) is not str:
        raise ValueError(f"{name} debe ser string")
    if non_empty and not value:
        raise ValueError(f"{name} no puede estar vacío")
    return value


def _nullable_string(value: Any, name: str) -> None:
    if value is not None:
        _string(value, name)


def _boolean(value: Any, name: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{name} debe ser boolean")
    return value


def _array(value: Any, name: str) -> list[Any]:
    if type(value) is not list:
        raise ValueError(f"{name} debe ser un array JSON")
    return value


def _string_array(value: Any, name: str) -> list[str]:
    items = _array(value, name)
    for index, item in enumerate(items):
        _string(item, f"{name}[{index}]")
    return items


def _validate_capabilities(value: Any) -> None:
    for index, raw in enumerate(_array(value, "view_model.capabilities")):
        name = f"view_model.capabilities[{index}]"
        item = _exact_object(raw, _CAPABILITY_KEYS, name)
        _string(item["capability"], f"{name}.capability")
        _string(item["status"], f"{name}.status")
        _boolean(item["result_available"], f"{name}.result_available")
        _string_array(item["trace_references"], f"{name}.trace_references")
        _string_array(item["unresolved_items"], f"{name}.unresolved_items")


def _validate_rules(view: dict[str, Any]) -> None:
    available = _boolean(view["rules_available"], "view_model.rules_available")
    names = (
        "rule_coverage",
        "crc_support_result",
        "assessments",
        "rule_trace_references",
    )
    if not available:
        if any(view[name] is not None for name in names):
            raise ValueError("rules_available=false exige bloques Rules/CRC null")
        return

    coverage = _exact_object(
        view["rule_coverage"], _RULE_COVERAGE_KEYS, "view_model.rule_coverage"
    )
    _string_array(
        coverage["executed_rule_ids"], "view_model.rule_coverage.executed_rule_ids"
    )
    _string_array(
        coverage["omitted_rule_ids"], "view_model.rule_coverage.omitted_rule_ids"
    )

    crc = _exact_object(
        view["crc_support_result"], _CRC_RESULT_KEYS, "view_model.crc_support_result"
    )
    _string(crc["consolidated_result"], "view_model.crc_support_result.consolidated_result")
    _string(crc["dominant_reason"], "view_model.crc_support_result.dominant_reason")
    _string_array(
        crc["relevant_factors"], "view_model.crc_support_result.relevant_factors"
    )
    _string_array(crc["conflicts"], "view_model.crc_support_result.conflicts")

    assessments = _array(view["assessments"], "view_model.assessments")
    for index, raw in enumerate(assessments):
        name = f"view_model.assessments[{index}]"
        item = _exact_object(raw, _ASSESSMENT_KEYS, name)
        _string(item["rule_id"], f"{name}.rule_id")
        _string(item["status"], f"{name}.status")
        _nullable_string(item["outcome"], f"{name}.outcome")
        _string(item["reason"], f"{name}.reason")
        _string_array(item["evidence_ids"], f"{name}.evidence_ids")
    _string_array(view["rule_trace_references"], "view_model.rule_trace_references")


def _validate_scenarios(view: dict[str, Any]) -> None:
    available = _boolean(
        view["scenario_support_available"],
        "view_model.scenario_support_available",
    )
    names = (
        "scenario_execution_context",
        "scenario_records",
        "scenario_comparison",
    )
    if not available:
        if any(view[name] is not None for name in names):
            raise ValueError("scenario_support_available=false exige bloques de escenario null")
        return

    context = _exact_object(
        view["scenario_execution_context"],
        _SCENARIO_CONTEXT_KEYS,
        "view_model.scenario_execution_context",
    )
    for key in _SCENARIO_CONTEXT_KEYS:
        _string(context[key], f"view_model.scenario_execution_context.{key}")

    records = _array(view["scenario_records"], "view_model.scenario_records")
    for index, raw in enumerate(records):
        name = f"view_model.scenario_records[{index}]"
        item = _exact_object(raw, _SCENARIO_RECORD_KEYS, name)
        _string(item["scenario_id"], f"{name}.scenario_id")
        _string(item["status"], f"{name}.status")
        if type(item["values"]) is not dict:
            raise ValueError(f"{name}.values debe ser un objeto JSON")
        _string_array(item["trace_references"], f"{name}.trace_references")
        _string_array(item["unresolved_items"], f"{name}.unresolved_items")
        _nullable_string(item["failure_reason"], f"{name}.failure_reason")

    comparison = view["scenario_comparison"]
    if comparison is None:
        return
    comparison = _exact_object(
        comparison,
        _SCENARIO_COMPARISON_KEYS,
        "view_model.scenario_comparison",
    )
    _string_array(
        comparison["scenario_ids"], "view_model.scenario_comparison.scenario_ids"
    )
    _array(comparison["observations"], "view_model.scenario_comparison.observations")
    _array(comparison["differences"], "view_model.scenario_comparison.differences")
    _array(comparison["missing"], "view_model.scenario_comparison.missing")
    _string_array(comparison["statuses"], "view_model.scenario_comparison.statuses")
    _string_array(
        comparison["unresolved_items"],
        "view_model.scenario_comparison.unresolved_items",
    )
    _string_array(
        comparison["traceability"], "view_model.scenario_comparison.traceability"
    )


def _validate_view_model(value: Any) -> dict[str, Any]:
    view = _exact_object(value, _VIEW_MODEL_KEYS, "view_model")
    _string(view["execution_status"], "view_model.execution_status", non_empty=True)
    _string(view["policy_version"], "view_model.policy_version", non_empty=True)
    _nullable_string(view["failure_reason"], "view_model.failure_reason")
    _string_array(view["unresolved_items"], "view_model.unresolved_items")
    _validate_capabilities(view["capabilities"])
    _validate_rules(view)
    _validate_scenarios(view)
    return view


def _parse_and_validate(fixture_content: bytes) -> tuple[dict[str, Any], bytes, str]:
    if type(fixture_content) is not bytes:
        raise TypeError("fixture_content debe ser bytes exactos")
    if not fixture_content:
        raise ValueError("fixture_content no puede estar vacío")
    if len(fixture_content) > MAX_FIXTURE_BYTES:
        raise ValueError("fixture_content supera MAX_FIXTURE_BYTES")
    try:
        text = fixture_content.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("fixture_content no es UTF-8 estricto") from exc
    if text.startswith("\ufeff"):
        raise ValueError("fixture_content no puede contener BOM")
    try:
        parsed = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_non_json_constant,
        )
    except RecursionError as exc:
        raise ValueError("fixture JSON supera la profundidad admisible") from exc
    except json.JSONDecodeError as exc:
        raise ValueError("fixture_content no contiene un documento JSON único") from exc

    _validate_json_value(parsed)
    case = _exact_object(parsed, _CASE_KEYS, "fixture")
    if _string(case["schema_version"], "fixture.schema_version") != SCHEMA_VERSION:
        raise ValueError("fixture.schema_version no coincide con el contrato")
    case_id = _string(case["case_id"], "fixture.case_id")
    if _CASE_ID_PATTERN.fullmatch(case_id) is None:
        raise ValueError("fixture.case_id no cumple el patrón sintético")
    if _string(case["classification"], "fixture.classification") != CLASSIFICATION:
        raise ValueError("fixture.classification no coincide con el contrato")
    if _string(case["scope"], "fixture.scope") != SCOPE:
        raise ValueError("fixture.scope no coincide con el contrato")
    for name in ("operational_effect", "decision_authority", "execution_claim"):
        if _boolean(case[name], f"fixture.{name}") is not False:
            raise ValueError(f"fixture.{name} debe ser false")
    if _string(case["notice"], "fixture.notice") != NOTICE:
        raise ValueError("fixture.notice no coincide con el contrato")
    _validate_view_model(case["view_model"])

    canonical_content = json.dumps(
        case,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    fingerprint = sha256(canonical_content).hexdigest()
    expected = _AUTHORIZED_SYNTHETIC_PREVIEW_CASES.get(case_id)
    if expected is None:
        raise ValueError("fixture.case_id no está registrado")
    if not compare_digest(fingerprint, expected):
        raise ValueError("fixture no coincide con el digest registrado")
    return case, canonical_content, fingerprint


def _decoded_case(case: VerticalMVPSyntheticPreviewCase) -> dict[str, Any]:
    return json.loads(case._canonical_content.decode("utf-8"))


@dataclass(frozen=True, init=False)
class VerticalMVPSyntheticPreviewCase:
    """Immutable registered presentation fixture; never an EIOS execution."""

    _canonical_content: bytes
    _case_fingerprint: str

    def __init__(self) -> None:
        raise TypeError("Use build_vertical_mvp_synthetic_preview_case")

    @property
    def schema_version(self) -> str:
        return SCHEMA_VERSION

    @property
    def case_id(self) -> str:
        return _decoded_case(self)["case_id"]

    @property
    def classification(self) -> str:
        return CLASSIFICATION

    @property
    def scope(self) -> str:
        return SCOPE

    @property
    def operational_effect(self) -> bool:
        return False

    @property
    def decision_authority(self) -> bool:
        return False

    @property
    def execution_claim(self) -> bool:
        return False

    @property
    def notice(self) -> str:
        return NOTICE

    @property
    def canonical_content(self) -> bytes:
        return self._canonical_content

    @property
    def case_fingerprint(self) -> str:
        return self._case_fingerprint

    @property
    def view_model(self) -> dict[str, Any]:
        return _decoded_case(self)["view_model"]

    def to_metadata(self) -> dict[str, str | bool]:
        return {
            "schema_version": SCHEMA_VERSION,
            "case_id": self.case_id,
            "classification": CLASSIFICATION,
            "scope": SCOPE,
            "operational_effect": False,
            "decision_authority": False,
            "execution_claim": False,
            "notice": NOTICE,
            "case_fingerprint": self._case_fingerprint,
        }


def build_vertical_mvp_synthetic_preview_case(
    fixture_content: bytes,
) -> VerticalMVPSyntheticPreviewCase:
    """Build a closed carrier only from exact registered in-memory fixture bytes."""
    _, canonical_content, fingerprint = _parse_and_validate(fixture_content)
    case = object.__new__(VerticalMVPSyntheticPreviewCase)
    object.__setattr__(case, "_canonical_content", canonical_content)
    object.__setattr__(case, "_case_fingerprint", fingerprint)
    return case


@dataclass(frozen=True, init=False)
class LocalSyntheticPreviewAdmission:
    """Atomic U1.3/U1.4 binding for one exact registered synthetic case."""

    _case: VerticalMVPSyntheticPreviewCase
    _artifact: VerticalMVPReadOnlyArtifact
    _delivery: VerticalMVPReadOnlyDelivery
    _case_id: str
    _case_fingerprint: str
    _artifact_content_sha256: str
    _delivery_content_sha256: str
    _content_size_bytes: int

    def __init__(self) -> None:
        raise TypeError("Use build_local_synthetic_preview_admission")

    @property
    def schema_version(self) -> str:
        return ADMISSION_SCHEMA_VERSION

    @property
    def profile(self) -> str:
        return PROFILE

    @property
    def case(self) -> VerticalMVPSyntheticPreviewCase:
        return self._case

    @property
    def artifact(self) -> VerticalMVPReadOnlyArtifact:
        return self._artifact

    @property
    def delivery(self) -> VerticalMVPReadOnlyDelivery:
        return self._delivery

    @property
    def case_id(self) -> str:
        return self._case_id

    @property
    def case_fingerprint(self) -> str:
        return self._case_fingerprint

    @property
    def artifact_content_sha256(self) -> str:
        return self._artifact_content_sha256

    @property
    def delivery_content_sha256(self) -> str:
        return self._delivery_content_sha256

    @property
    def content_size_bytes(self) -> int:
        return self._content_size_bytes

    @property
    def operational_effect(self) -> bool:
        return False

    @property
    def decision_authority(self) -> bool:
        return False

    @property
    def execution_claim(self) -> bool:
        return False

    @property
    def notice(self) -> str:
        return NOTICE

    def to_metadata(self) -> dict[str, str | bool | int]:
        return {
            "schema_version": ADMISSION_SCHEMA_VERSION,
            "profile": PROFILE,
            "case_id": self._case_id,
            "case_fingerprint": self._case_fingerprint,
            "artifact_content_sha256": self._artifact_content_sha256,
            "delivery_content_sha256": self._delivery_content_sha256,
            "content_size_bytes": self._content_size_bytes,
            "operational_effect": False,
            "decision_authority": False,
            "execution_claim": False,
            "notice": NOTICE,
        }


def build_local_synthetic_preview_admission(
    case: VerticalMVPSyntheticPreviewCase,
) -> LocalSyntheticPreviewAdmission:
    """Revalidate one case and atomically build its exact U1.3/U1.4 binding."""
    if type(case) is not VerticalMVPSyntheticPreviewCase:
        raise TypeError("case debe ser un VerticalMVPSyntheticPreviewCase exacto")

    material, canonical_content, fingerprint = _parse_and_validate(
        case._canonical_content
    )
    if canonical_content != case._canonical_content:
        raise ValueError("case no conserva bytes canónicos exactos")
    if not compare_digest(fingerprint, case._case_fingerprint):
        raise ValueError("case_fingerprint no coincide con el contenido registrado")

    artifact = build_vertical_mvp_readonly_artifact(material["view_model"])
    delivery = build_vertical_mvp_readonly_delivery(artifact)
    body_digest = sha256(delivery.body).hexdigest()
    if not (
        compare_digest(body_digest, artifact.content_sha256)
        and compare_digest(body_digest, delivery.content_sha256)
    ):
        raise ValueError("binding U1.3/U1.4 no conserva un digest único")
    if delivery.body != artifact.content:
        raise ValueError("binding U1.3/U1.4 no conserva los bytes exactos")

    admission = object.__new__(LocalSyntheticPreviewAdmission)
    object.__setattr__(admission, "_case", case)
    object.__setattr__(admission, "_artifact", artifact)
    object.__setattr__(admission, "_delivery", delivery)
    object.__setattr__(admission, "_case_id", material["case_id"])
    object.__setattr__(admission, "_case_fingerprint", fingerprint)
    object.__setattr__(
        admission, "_artifact_content_sha256", artifact.content_sha256
    )
    object.__setattr__(
        admission, "_delivery_content_sha256", delivery.content_sha256
    )
    object.__setattr__(admission, "_content_size_bytes", len(delivery.body))
    return admission


__all__ = [
    "ADMISSION_SCHEMA_VERSION",
    "CLASSIFICATION",
    "LocalSyntheticPreviewAdmission",
    "MAX_FIXTURE_BYTES",
    "NOTICE",
    "PROFILE",
    "SCHEMA_VERSION",
    "SCOPE",
    "VerticalMVPSyntheticPreviewCase",
    "build_local_synthetic_preview_admission",
    "build_vertical_mvp_synthetic_preview_case",
]
