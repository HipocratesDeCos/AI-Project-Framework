import ast
import copy
from dataclasses import FrozenInstanceError
from hashlib import sha256
import inspect

import pytest

import eios.frontend.visual.vertical_mvp_artifact as artifact_module
from eios.frontend.visual.vertical_mvp_artifact import (
    FILENAME,
    MEDIA_TYPE,
    VerticalMVPReadOnlyArtifact,
    build_vertical_mvp_readonly_artifact,
)
from eios.frontend.visual.vertical_mvp_renderer import render_vertical_mvp_readonly
from test_vertical_mvp_readonly_renderer import _view


def test_artifact_preserves_exact_u1_2_utf8_bytes_and_hash():
    view = _view()
    expected = render_vertical_mvp_readonly(view).encode("utf-8")

    artifact = build_vertical_mvp_readonly_artifact(view)

    assert artifact.content == expected
    assert artifact.size_bytes == len(expected)
    assert artifact.content_sha256 == sha256(expected).hexdigest()
    assert artifact.media_type == MEDIA_TYPE
    assert artifact.filename == FILENAME


def test_artifact_metadata_is_transport_only_and_exact():
    artifact = build_vertical_mvp_readonly_artifact(_view())

    assert artifact.to_metadata() == {
        "media_type": "text/html; charset=utf-8",
        "filename": "eios-vertical-mvp-readonly.html",
        "size_bytes": len(artifact.content),
        "content_sha256": artifact.content_sha256,
    }
    assert set(artifact.to_metadata()) == {
        "media_type",
        "filename",
        "size_bytes",
        "content_sha256",
    }


def test_artifact_is_factory_built_immutable_and_deterministic():
    view = _view()

    first = build_vertical_mvp_readonly_artifact(view)
    second = build_vertical_mvp_readonly_artifact(view)

    assert first.content == second.content
    assert first.content_sha256 == second.content_sha256
    assert first.to_metadata() == second.to_metadata()

    with pytest.raises(TypeError):
        VerticalMVPReadOnlyArtifact()
    with pytest.raises(FrozenInstanceError):
        first._content = b"changed"


def test_material_view_change_changes_content_hash_without_mutating_source():
    view = _view()
    original = copy.deepcopy(view)

    first = build_vertical_mvp_readonly_artifact(view)
    changed = copy.deepcopy(view)
    changed["execution_status"] = "FAILED"
    second = build_vertical_mvp_readonly_artifact(changed)

    assert first.content_sha256 != second.content_sha256
    assert first.content != second.content
    assert view == original


def test_artifact_propagates_renderer_fail_closed_validation():
    view = _view()
    del view["execution_status"]

    with pytest.raises(ValueError, match="claves contractuales"):
        build_vertical_mvp_readonly_artifact(view)


def test_artifact_does_not_unescape_or_transform_dynamic_html_content():
    view = _view()
    view["assessments"][0]["reason"] = '<script>alert("x")</script>'

    artifact = build_vertical_mvp_readonly_artifact(view)
    text = artifact.content.decode("utf-8")

    assert '<script>alert("x")</script>' not in text
    assert "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;" in text


def test_content_sha256_is_not_exposed_as_decision_or_input_identity():
    metadata = build_vertical_mvp_readonly_artifact(_view()).to_metadata()

    forbidden = {
        "decision_fingerprint",
        "input_fingerprint",
        "trace_id",
        "decision_version",
        "provenance_fingerprint",
        "signature",
    }
    assert forbidden.isdisjoint(metadata)


def test_artifact_module_has_no_filesystem_network_or_engine_imports():
    source = inspect.getsource(artifact_module)
    tree = ast.parse(source)
    imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")

    forbidden_roots = {
        "os",
        "pathlib",
        "tempfile",
        "shutil",
        "socket",
        "urllib",
        "requests",
        "http",
        "fastapi",
        "flask",
        "django",
    }
    assert all(name.split(".")[0] not in forbidden_roots for name in imports)
    assert all(
        not name.startswith(
            (
                "eios.core",
                "eios.rules",
                "eios.finance",
                "eios.quality",
            )
        )
        for name in imports
    )
