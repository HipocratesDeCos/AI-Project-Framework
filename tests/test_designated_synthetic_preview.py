import ast
from dataclasses import FrozenInstanceError
from hashlib import sha256
import inspect
from pathlib import Path

import pytest

import eios.frontend.visual.designated_synthetic_preview as designated_module
from eios.frontend.visual import (
    DesignatedSyntheticPreviewArtifact,
    DesignatedSyntheticPreviewDelivery,
    build_designated_synthetic_preview_artifact,
    build_designated_synthetic_preview_delivery,
    build_local_synthetic_preview_admission,
    build_vertical_mvp_synthetic_preview_case,
)
from eios.frontend.visual.designated_synthetic_preview import (
    ARTIFACT_SCHEMA_VERSION,
    CONTENT_SECURITY_POLICY,
    DELIVERY_SCHEMA_VERSION,
    FILENAME,
    MEDIA_TYPE,
    NOTICE,
    PROFILE,
    STATUS_OK,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "vertical_mvp_synthetic_preview_case_01.json"
)


def _case():
    return build_vertical_mvp_synthetic_preview_case(FIXTURE_PATH.read_bytes())


def _admission():
    return build_local_synthetic_preview_admission(_case())


def _artifact():
    return build_designated_synthetic_preview_artifact(_admission())


def test_happy_path_builds_separate_deterministic_designated_artifact():
    admission = _admission()
    first = build_designated_synthetic_preview_artifact(admission)
    second = build_designated_synthetic_preview_artifact(_admission())

    assert first.schema_version == ARTIFACT_SCHEMA_VERSION
    assert first.profile == PROFILE
    assert first.case_id == admission.case_id
    assert first.case_fingerprint == admission.case_fingerprint
    assert first.source_artifact_content_sha256 == admission.artifact.content_sha256
    assert first.content != admission.artifact.content
    assert first.content_sha256 != first.source_artifact_content_sha256
    assert first.content_sha256 == sha256(first.content).hexdigest()
    assert first.size_bytes == len(first.content)
    assert first.media_type == MEDIA_TYPE
    assert first.filename == FILENAME
    assert first.content == second.content
    assert first.to_metadata() == second.to_metadata()


def test_designation_is_in_same_document_and_structurally_sticky():
    content = _artifact().content.decode("utf-8")

    assert content.startswith("<!doctype html>")
    assert content.endswith("</html>")
    assert NOTICE in content
    assert "SYNTHETIC · TEST_ONLY · NO OPERATIONAL EFFECT" in content
    assert 'class="eios-synthetic-designation"' in content
    assert 'role="note"' in content
    assert "position:sticky" in content
    assert "top:0" in content
    assert content.index(NOTICE) < content.index('<main class="shell">')
    assert content.count(NOTICE) == 1


def test_source_vertical_content_is_preserved_inside_designated_document():
    admission = _admission()
    artifact = build_designated_synthetic_preview_artifact(admission)
    source = admission.artifact.content.decode("utf-8")
    target = artifact.content.decode("utf-8")

    for invariant in (
        "EIOS · Vertical MVP · Solo lectura",
        "Composición visual de solo lectura",
        '<section id="execution">',
        '<section id="capabilities">',
        '<section id="rules">',
        '<section id="scenarios">',
    ):
        assert invariant in source
        assert invariant in target


def test_artifact_metadata_is_exact_and_non_operational():
    artifact = _artifact()
    metadata = artifact.to_metadata()

    assert metadata == {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "profile": PROFILE,
        "classification": "SYNTHETIC_PRESENTATION_FIXTURE",
        "scope": "TEST_ONLY",
        "operational_effect": False,
        "decision_authority": False,
        "execution_claim": False,
        "notice": NOTICE,
        "case_id": artifact.case_id,
        "case_fingerprint": artifact.case_fingerprint,
        "source_artifact_content_sha256": artifact.source_artifact_content_sha256,
        "content_sha256": artifact.content_sha256,
        "size_bytes": artifact.size_bytes,
        "media_type": MEDIA_TYPE,
        "filename": FILENAME,
    }
    assert "provenance" not in metadata
    assert "signature" not in metadata


def test_delivery_has_own_type_and_exact_response_contract():
    artifact = _artifact()
    delivery = build_designated_synthetic_preview_delivery(artifact)

    assert type(delivery) is DesignatedSyntheticPreviewDelivery
    assert delivery.schema_version == DELIVERY_SCHEMA_VERSION
    assert delivery.status_code == STATUS_OK
    assert delivery.body is artifact.content
    assert delivery.body == artifact.content
    assert delivery.content_sha256 == artifact.content_sha256
    assert delivery.size_bytes == artifact.size_bytes
    assert delivery.as_response_parts() == (STATUS_OK, delivery.headers, artifact.content)
    assert delivery.headers == (
        ("Content-Type", MEDIA_TYPE),
        ("Content-Length", str(len(artifact.content))),
        ("Content-Disposition", f'inline; filename="{FILENAME}"'),
        ("Cache-Control", "no-store"),
        ("X-Content-Type-Options", "nosniff"),
        ("Referrer-Policy", "no-referrer"),
        ("Content-Security-Policy", CONTENT_SECURITY_POLICY),
    )


def test_csp_remains_deny_by_default_without_embedding_or_network_relaxation():
    assert CONTENT_SECURITY_POLICY == (
        "default-src 'none'; style-src 'unsafe-inline'; img-src 'none'; "
        "script-src 'none'; connect-src 'none'; object-src 'none'; "
        "base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
    )


def test_direct_construction_is_closed_and_carriers_are_frozen():
    with pytest.raises(TypeError, match="build_designated_synthetic_preview_artifact"):
        DesignatedSyntheticPreviewArtifact()
    with pytest.raises(TypeError, match="build_designated_synthetic_preview_delivery"):
        DesignatedSyntheticPreviewDelivery()

    artifact = _artifact()
    delivery = build_designated_synthetic_preview_delivery(artifact)
    with pytest.raises(FrozenInstanceError):
        artifact._content = b"changed"
    with pytest.raises(FrozenInstanceError):
        delivery._body = b"changed"


@pytest.mark.parametrize("value", [None, {}, b"html", object(), _case()])
def test_artifact_factory_rejects_non_exact_admission_inputs(value):
    with pytest.raises(TypeError, match="LocalSyntheticPreviewAdmission exacta"):
        build_designated_synthetic_preview_artifact(value)


@pytest.mark.parametrize("value", [None, {}, b"html", object(), _admission()])
def test_delivery_factory_rejects_non_exact_artifact_inputs(value):
    with pytest.raises(TypeError, match="DesignatedSyntheticPreviewArtifact exacto"):
        build_designated_synthetic_preview_delivery(value)


def test_artifact_factory_revalidates_tampered_admission_case_reference():
    admission = _admission()
    object.__setattr__(admission, "_case_fingerprint", "0" * 64)

    with pytest.raises(ValueError, match="case_fingerprint"):
        build_designated_synthetic_preview_artifact(admission)


def test_artifact_factory_revalidates_tampered_u13_content():
    admission = _admission()
    object.__setattr__(admission.artifact, "_content", admission.artifact.content + b"x")

    with pytest.raises(ValueError, match="artifact no coincide"):
        build_designated_synthetic_preview_artifact(admission)


def test_artifact_factory_revalidates_tampered_u14_body():
    admission = _admission()
    object.__setattr__(admission.delivery, "_body", admission.delivery.body + b"x")

    with pytest.raises(ValueError, match="delivery no coincide"):
        build_designated_synthetic_preview_artifact(admission)


def test_artifact_factory_revalidates_tampered_admission_digest_metadata():
    admission = _admission()
    object.__setattr__(admission, "_artifact_content_sha256", "0" * 64)

    with pytest.raises(ValueError, match="artifact_content_sha256"):
        build_designated_synthetic_preview_artifact(admission)


def test_designated_artifact_never_reuses_source_identity():
    artifact = _artifact()

    assert artifact.content_sha256 != artifact.source_artifact_content_sha256
    assert artifact.content_sha256 == sha256(artifact.content).hexdigest()


def test_delivery_revalidates_tampered_artifact_content():
    artifact = _artifact()
    object.__setattr__(artifact, "_content", artifact.content + b"x")

    with pytest.raises(ValueError, match="composición U1.5C"):
        build_designated_synthetic_preview_delivery(artifact)


def test_delivery_revalidates_tampered_artifact_digest():
    artifact = _artifact()
    object.__setattr__(artifact, "_content_sha256", "0" * 64)

    with pytest.raises(ValueError, match="content_sha256"):
        build_designated_synthetic_preview_delivery(artifact)


def test_delivery_rejects_missing_notice_after_deliberate_internal_tamper():
    artifact = _artifact()
    changed = artifact.content.replace(NOTICE.encode("utf-8"), b"NOT-A-NOTICE")
    object.__setattr__(artifact, "_content", changed)
    object.__setattr__(artifact, "_content_sha256", sha256(changed).hexdigest())

    with pytest.raises(ValueError, match="composición U1.5C"):
        build_designated_synthetic_preview_delivery(artifact)


def test_delivery_revalidates_artifact_lineage_metadata():
    artifact = _artifact()
    object.__setattr__(artifact, "_case_id", "SYNTHETIC-PREVIEW-TAMPERED")
    with pytest.raises(ValueError, match="case_id"):
        build_designated_synthetic_preview_delivery(artifact)

    artifact = _artifact()
    object.__setattr__(artifact, "_source_artifact_content_sha256", "0" * 64)
    with pytest.raises(ValueError, match="source_artifact_content_sha256"):
        build_designated_synthetic_preview_delivery(artifact)


def test_delivery_revalidates_retained_source_admission():
    artifact = _artifact()
    object.__setattr__(artifact._source_admission, "_case_fingerprint", "0" * 64)

    with pytest.raises(ValueError, match="case_fingerprint"):
        build_designated_synthetic_preview_delivery(artifact)


@pytest.mark.parametrize(
    "token",
    [
        b"<script></script>",
        b"<iframe></iframe>",
        b"<object></object>",
        b"<embed>",
        b"<form></form>",
        b"<img>",
        b"<link>",
        b"javascript:",
        b'src="x"',
        b'action="x"',
    ],
)
def test_internal_composer_rejects_active_surface_tokens(token):
    source = _admission().artifact.content
    changed = source.replace(
        b'<main class="shell">', token + b'<main class="shell">', 1
    )

    with pytest.raises(ValueError, match="superficie activa"):
        designated_module._compose_designated_html(changed)


@pytest.mark.parametrize(
    "mutator",
    [
        lambda source: source.replace(b"<!doctype html>", b"<!DOCTYPE changed>", 1),
        lambda source: source.replace(b"<body>\n", b"<body>", 1),
        lambda source: source.replace(b"\n</style>", b"\n</STYLE>", 1),
        lambda source: source + b"x",
    ],
)
def test_internal_composer_rejects_structural_drift(mutator):
    source = _admission().artifact.content

    with pytest.raises(ValueError, match="contractual"):
        designated_module._compose_designated_html(mutator(source))


def test_module_is_pure_and_does_not_import_io_web_or_operational_engines():
    source = inspect.getsource(designated_module)
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
    assert "render_vertical_mvp_readonly" not in source


def test_public_surface_exposes_no_io_routing_auth_or_decision_actions():
    artifact = _artifact()
    delivery = build_designated_synthetic_preview_delivery(artifact)
    forbidden = {
        "authenticate",
        "authorization",
        "cookie",
        "execute",
        "open",
        "path",
        "route",
        "save",
        "send",
        "server",
        "session",
        "socket",
        "token",
        "url",
    }
    for carrier in (artifact, delivery):
        public_names = {name for name in dir(carrier) if not name.startswith("_")}
        assert forbidden.isdisjoint(public_names)


def test_u15c_does_not_mutate_u15a_objects():
    admission = _admission()
    source_before = admission.artifact.content
    delivery_before = admission.delivery.as_response_parts()
    metadata_before = admission.to_metadata()

    artifact = build_designated_synthetic_preview_artifact(admission)
    build_designated_synthetic_preview_delivery(artifact)

    assert admission.artifact.content == source_before
    assert admission.delivery.as_response_parts() == delivery_before
    assert admission.to_metadata() == metadata_before


def test_gate_evidence_is_physical_not_metadata_only():
    artifact = _artifact()
    body = artifact.content

    assert NOTICE.encode("utf-8") in body
    assert b"position:sticky" in body
    assert b"SYNTHETIC" in body
    assert b"TEST_ONLY" in body
    assert b"NO OPERATIONAL EFFECT" in body


def test_delivery_retains_exact_artifact_for_downstream_lineage_revalidation():
    artifact = _artifact()
    delivery = build_designated_synthetic_preview_delivery(artifact)

    assert delivery.artifact is artifact
    assert delivery.artifact.content == delivery.body
    assert delivery.artifact.content_sha256 == delivery.content_sha256
