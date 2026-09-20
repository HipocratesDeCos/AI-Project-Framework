import ast
import copy
from dataclasses import FrozenInstanceError
from hashlib import sha256
import inspect
import json
from pathlib import Path

import pytest

import eios.frontend.visual.synthetic_preview_admission as admission_module
from eios.frontend.visual import (
    LocalSyntheticPreviewAdmission,
    VerticalMVPSyntheticPreviewCase,
    build_local_synthetic_preview_admission,
    build_vertical_mvp_readonly_artifact,
    build_vertical_mvp_readonly_delivery,
    build_vertical_mvp_synthetic_preview_case,
)
from eios.frontend.visual.synthetic_preview_admission import (
    ADMISSION_SCHEMA_VERSION,
    CLASSIFICATION,
    MAX_FIXTURE_BYTES,
    NOTICE,
    PROFILE,
    SCHEMA_VERSION,
    SCOPE,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "vertical_mvp_synthetic_preview_case_01.json"
)
EXPECTED_CASE_FINGERPRINT = (
    "fbe81e2e898bbc209a853c9b88beca01"
    "e1e88153e1f69b5b76ba3ff348926f60"
)
CASE_KEYS = (
    "schema_version",
    "case_id",
    "classification",
    "scope",
    "operational_effect",
    "decision_authority",
    "execution_claim",
    "notice",
    "view_model",
)
VIEW_MODEL_KEYS = (
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
)


def _fixture_bytes() -> bytes:
    return FIXTURE_PATH.read_bytes()


def _fixture_mapping():
    return json.loads(_fixture_bytes().decode("utf-8"))


def _encode(value) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _case():
    return build_vertical_mvp_synthetic_preview_case(_fixture_bytes())


def test_registered_fixture_builds_exact_canonical_case():
    fixture = _fixture_mapping()

    case = _case()

    assert case.schema_version == SCHEMA_VERSION
    assert case.case_id == "SYNTHETIC-PREVIEW-001"
    assert case.classification == CLASSIFICATION
    assert case.scope == SCOPE
    assert case.operational_effect is False
    assert case.decision_authority is False
    assert case.execution_claim is False
    assert case.notice == NOTICE
    assert case.canonical_content == _encode(fixture)
    assert case.case_fingerprint == EXPECTED_CASE_FINGERPRINT
    assert case.case_fingerprint == sha256(case.canonical_content).hexdigest()
    assert case.view_model == fixture["view_model"]
    assert set(case.to_metadata()) == {
        "schema_version",
        "case_id",
        "classification",
        "scope",
        "operational_effect",
        "decision_authority",
        "execution_claim",
        "notice",
        "case_fingerprint",
    }


def test_canonical_case_is_independent_of_json_whitespace_and_key_order():
    fixture = _fixture_mapping()
    reordered = dict(reversed(tuple(fixture.items())))

    first = _case()
    second = build_vertical_mvp_synthetic_preview_case(_encode(reordered))

    assert first == second
    assert first.canonical_content == second.canonical_content
    assert first.case_fingerprint == second.case_fingerprint


def test_admission_atomically_binds_exact_case_artifact_and_delivery():
    case = _case()

    admission = build_local_synthetic_preview_admission(case)

    assert admission.schema_version == ADMISSION_SCHEMA_VERSION
    assert admission.profile == PROFILE
    assert admission.case is case
    assert admission.delivery.body is admission.artifact.content
    assert admission.delivery.body == admission.artifact.content
    assert admission.case_id == case.case_id
    assert admission.case_fingerprint == case.case_fingerprint
    assert admission.artifact_content_sha256 == admission.artifact.content_sha256
    assert admission.delivery_content_sha256 == admission.delivery.content_sha256
    assert admission.artifact_content_sha256 == admission.delivery_content_sha256
    assert admission.delivery_content_sha256 == sha256(admission.delivery.body).hexdigest()
    assert admission.content_size_bytes == len(admission.delivery.body)
    assert admission.operational_effect is False
    assert admission.decision_authority is False
    assert admission.execution_claim is False
    assert admission.notice == NOTICE
    assert admission.delivery.status_code == 200
    assert admission.delivery.headers[-1][0] == "Content-Security-Policy"


def test_admission_metadata_is_exact_and_contains_no_extra_hash():
    admission = build_local_synthetic_preview_admission(_case())

    assert admission.to_metadata() == {
        "schema_version": ADMISSION_SCHEMA_VERSION,
        "profile": PROFILE,
        "case_id": "SYNTHETIC-PREVIEW-001",
        "case_fingerprint": EXPECTED_CASE_FINGERPRINT,
        "artifact_content_sha256": admission.artifact.content_sha256,
        "delivery_content_sha256": admission.delivery.content_sha256,
        "content_size_bytes": len(admission.delivery.body),
        "operational_effect": False,
        "decision_authority": False,
        "execution_claim": False,
        "notice": NOTICE,
    }
    assert "admission_sha256" not in admission.to_metadata()


def test_carriers_are_factory_built_frozen_and_deterministic():
    with pytest.raises(TypeError, match="build_vertical_mvp_synthetic_preview_case"):
        VerticalMVPSyntheticPreviewCase()
    with pytest.raises(TypeError, match="build_local_synthetic_preview_admission"):
        LocalSyntheticPreviewAdmission()

    first_case = _case()
    second_case = _case()
    first = build_local_synthetic_preview_admission(first_case)
    second = build_local_synthetic_preview_admission(second_case)

    assert first_case == second_case
    assert first.to_metadata() == second.to_metadata()
    assert first.artifact.content == second.artifact.content
    assert first.delivery.as_response_parts() == second.delivery.as_response_parts()
    with pytest.raises(FrozenInstanceError):
        first_case._canonical_content = b"changed"
    with pytest.raises(FrozenInstanceError):
        first._content_size_bytes = 0


@pytest.mark.parametrize(
    "value",
    [None, "{}", bytearray(b"{}"), memoryview(b"{}"), {}, object()],
)
def test_case_factory_rejects_every_non_exact_bytes_input(value):
    with pytest.raises(TypeError, match="bytes exactos"):
        build_vertical_mvp_synthetic_preview_case(value)


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (b"", "vacío"),
        (b"\xef\xbb\xbf{}", "BOM"),
        (b"\xff", "UTF-8"),
        (b"{} {}", "documento JSON único"),
        (b"[", "documento JSON único"),
    ],
)
def test_case_factory_rejects_invalid_byte_documents(value, message):
    with pytest.raises(ValueError, match=message):
        build_vertical_mvp_synthetic_preview_case(value)


def test_case_factory_rejects_oversized_input_before_parsing():
    with pytest.raises(ValueError, match="MAX_FIXTURE_BYTES"):
        build_vertical_mvp_synthetic_preview_case(b" " * (MAX_FIXTURE_BYTES + 1))


@pytest.mark.parametrize(
    "needle",
    [
        b'"scope": "TEST_ONLY",',
        b'"status": "COMPLETED",',
    ],
)
def test_case_factory_rejects_duplicate_keys_at_any_level(needle):
    duplicated = _fixture_bytes().replace(needle, needle + b"\n    " + needle, 1)

    with pytest.raises(ValueError, match="clave duplicada"):
        build_vertical_mvp_synthetic_preview_case(duplicated)


@pytest.mark.parametrize("constant", [b"NaN", b"Infinity", b"-Infinity"])
def test_case_factory_rejects_non_json_numeric_constants(constant):
    changed = _fixture_bytes().replace(b'"PARTIAL"', constant, 1)

    with pytest.raises(ValueError, match="constante no finita"):
        build_vertical_mvp_synthetic_preview_case(changed)


def test_case_factory_rejects_unpaired_unicode_surrogate_before_canonicalization():
    changed = _fixture_bytes().replace(b'"PARTIAL"', b'"\\ud800"', 1)

    with pytest.raises(ValueError, match="Unicode no escalar"):
        build_vertical_mvp_synthetic_preview_case(changed)


def test_case_factory_rejects_json_deeper_than_contract():
    fixture = _fixture_mapping()
    nested = "leaf"
    for _ in range(40):
        nested = [nested]
    fixture["view_model"]["scenario_records"][0]["values"] = {"nested": nested}

    with pytest.raises(ValueError, match="profundidad"):
        build_vertical_mvp_synthetic_preview_case(_encode(fixture))


@pytest.mark.parametrize("key", CASE_KEYS)
def test_case_factory_rejects_each_missing_root_key(key):
    fixture = _fixture_mapping()
    del fixture[key]

    with pytest.raises(ValueError, match="claves no exactas"):
        build_vertical_mvp_synthetic_preview_case(_encode(fixture))


def test_case_factory_rejects_unknown_root_key():
    fixture = _fixture_mapping()
    fixture["caller_fingerprint"] = "0" * 64

    with pytest.raises(ValueError, match="claves no exactas"):
        build_vertical_mvp_synthetic_preview_case(_encode(fixture))


@pytest.mark.parametrize(
    ("key", "value", "message"),
    [
        ("schema_version", "OTHER", "schema_version"),
        ("case_id", "CASE-001", "patrón sintético"),
        ("classification", "SYNTHETIC", "classification"),
        ("scope", "OPERATIONAL", "scope"),
        ("operational_effect", True, "operational_effect"),
        ("decision_authority", 0, "boolean"),
        ("execution_claim", "false", "boolean"),
        ("notice", "synthetic", "notice"),
    ],
)
def test_case_factory_rejects_altered_root_contract(key, value, message):
    fixture = _fixture_mapping()
    fixture[key] = value

    with pytest.raises(ValueError, match=message):
        build_vertical_mvp_synthetic_preview_case(_encode(fixture))


@pytest.mark.parametrize("key", VIEW_MODEL_KEYS)
def test_case_factory_rejects_each_missing_view_model_key(key):
    fixture = _fixture_mapping()
    del fixture["view_model"][key]

    with pytest.raises(ValueError, match="claves no exactas"):
        build_vertical_mvp_synthetic_preview_case(_encode(fixture))


@pytest.mark.parametrize(
    "path",
    [
        ("capabilities", 0),
        ("rule_coverage",),
        ("crc_support_result",),
        ("assessments", 0),
        ("scenario_execution_context",),
        ("scenario_records", 0),
        ("scenario_comparison",),
    ],
)
def test_case_factory_rejects_extra_key_in_every_closed_nested_object(path):
    fixture = _fixture_mapping()
    target = fixture["view_model"]
    for part in path:
        target = target[part]
    target["unexpected"] = None

    with pytest.raises(ValueError, match="claves no exactas"):
        build_vertical_mvp_synthetic_preview_case(_encode(fixture))


@pytest.mark.parametrize(
    ("path", "value", "message"),
    [
        (("execution_status",), "", "no puede estar vacío"),
        (("unresolved_items",), "item", "array JSON"),
        (("capabilities", 0, "result_available"), 1, "boolean"),
        (("rule_coverage", "executed_rule_ids"), [1], "string"),
        (("crc_support_result", "conflicts"), {}, "array JSON"),
        (("assessments", 0, "outcome"), False, "string"),
        (("scenario_execution_context", "execution_id"), 1, "string"),
        (("scenario_records", 0, "values"), [], "objeto JSON"),
        (("scenario_comparison", "statuses"), [None], "string"),
    ],
)
def test_case_factory_rejects_nested_type_drift(path, value, message):
    fixture = _fixture_mapping()
    target = fixture["view_model"]
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = value

    with pytest.raises(ValueError, match=message):
        build_vertical_mvp_synthetic_preview_case(_encode(fixture))


def test_case_factory_rejects_inconsistent_rules_availability():
    fixture = _fixture_mapping()
    fixture["view_model"]["rules_available"] = False

    with pytest.raises(ValueError, match="Rules/CRC null"):
        build_vertical_mvp_synthetic_preview_case(_encode(fixture))


def test_case_factory_rejects_inconsistent_scenario_availability():
    fixture = _fixture_mapping()
    fixture["view_model"]["scenario_support_available"] = False

    with pytest.raises(ValueError, match="escenario null"):
        build_vertical_mvp_synthetic_preview_case(_encode(fixture))


def test_case_factory_rejects_unregistered_case_id():
    fixture = _fixture_mapping()
    fixture["case_id"] = "SYNTHETIC-PREVIEW-UNREGISTERED"

    with pytest.raises(ValueError, match="no está registrado"):
        build_vertical_mvp_synthetic_preview_case(_encode(fixture))


def test_case_factory_rejects_registered_id_with_mutated_content():
    fixture = _fixture_mapping()
    fixture["view_model"]["policy_version"] = "POLICY-SYNTHETIC-MUTATED"

    with pytest.raises(ValueError, match="digest registrado"):
        build_vertical_mvp_synthetic_preview_case(_encode(fixture))


def test_case_never_retains_or_exposes_mutable_caller_mapping():
    source = _fixture_mapping()
    case = build_vertical_mvp_synthetic_preview_case(_encode(source))
    before = case.canonical_content

    source["view_model"]["execution_status"] = "MUTATED"
    returned = case.view_model
    returned["execution_status"] = "MUTATED"

    assert case.canonical_content == before
    assert case.view_model["execution_status"] == "PARTIAL"
    assert case.case_fingerprint == EXPECTED_CASE_FINGERPRINT


def test_admission_revalidates_tampered_case_content_and_fingerprint():
    changed_content = _case()
    fixture = _fixture_mapping()
    fixture["view_model"]["policy_version"] = "POLICY-SYNTHETIC-MUTATED"
    object.__setattr__(changed_content, "_canonical_content", _encode(fixture))
    with pytest.raises(ValueError, match="digest registrado"):
        build_local_synthetic_preview_admission(changed_content)

    changed_fingerprint = _case()
    object.__setattr__(changed_fingerprint, "_case_fingerprint", "0" * 64)
    with pytest.raises(ValueError, match="case_fingerprint"):
        build_local_synthetic_preview_admission(changed_fingerprint)


@pytest.mark.parametrize("value", [None, {}, _fixture_mapping(), b"case", object()])
def test_admission_rejects_non_carrier_inputs(value):
    with pytest.raises(TypeError, match="VerticalMVPSyntheticPreviewCase exacto"):
        build_local_synthetic_preview_admission(value)


def test_admission_rejects_detached_artifact_and_delivery_objects():
    case = _case()
    artifact = build_vertical_mvp_readonly_artifact(case.view_model)
    delivery = build_vertical_mvp_readonly_delivery(artifact)

    for detached in (artifact, delivery):
        with pytest.raises(TypeError, match="VerticalMVPSyntheticPreviewCase exacto"):
            build_local_synthetic_preview_admission(detached)


def test_fixture_is_unequivocally_synthetic_and_contains_no_numeric_facts():
    fixture = _fixture_mapping()
    serialized = json.dumps(fixture, ensure_ascii=False)

    assert fixture["scope"] == "TEST_ONLY"
    assert fixture["classification"] == "SYNTHETIC_PRESENTATION_FIXTURE"
    assert fixture["execution_claim"] is False
    assert "SYNTHETIC" in serialized
    assert "NO ES UNA EJECUCIÓN OPERACIONAL" in serialized

    def numeric_values(value):
        if type(value) in {int, float}:
            yield value
        elif type(value) is list:
            for item in value:
                yield from numeric_values(item)
        elif type(value) is dict:
            for item in value.values():
                yield from numeric_values(item)

    assert list(numeric_values(fixture)) == []


def test_public_surface_has_no_io_auth_routing_or_decision_authority():
    admission = build_local_synthetic_preview_admission(_case())
    public_names = {name for name in dir(admission) if not name.startswith("_")}
    forbidden = {
        "admission_sha256",
        "authenticate",
        "authorization",
        "cookie",
        "execute",
        "open",
        "path",
        "recipient",
        "route",
        "save",
        "send",
        "server",
        "session",
        "socket",
        "token",
        "url",
    }

    assert forbidden.isdisjoint(public_names)


def test_module_is_pure_and_does_not_import_operational_engines_or_io():
    source = inspect.getsource(admission_module)
    tree = ast.parse(source)
    imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")

    forbidden_roots = {
        "asyncio",
        "django",
        "fastapi",
        "flask",
        "http",
        "os",
        "pathlib",
        "requests",
        "shutil",
        "socket",
        "sqlite3",
        "subprocess",
        "tempfile",
        "urllib",
        "wsgiref",
    }
    assert all(name.split(".")[0] not in forbidden_roots for name in imports)
    assert all(
        not name.startswith(
            (
                "eios.application_boundary",
                "eios.core",
                "eios.finance",
                "eios.quality",
                "eios.rules",
            )
        )
        for name in imports
    )
    assert "build_vertical_mvp_view_model" not in source


def test_admission_does_not_mutate_case_or_view_model():
    case = _case()
    before_bytes = case.canonical_content
    before_view = copy.deepcopy(case.view_model)

    build_local_synthetic_preview_admission(case)

    assert case.canonical_content == before_bytes
    assert case.view_model == before_view
