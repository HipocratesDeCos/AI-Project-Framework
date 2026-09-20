import ast
from dataclasses import FrozenInstanceError
from hashlib import sha256
import inspect

import pytest

import eios.frontend.visual.vertical_mvp_artifact as artifact_module
import eios.frontend.visual.vertical_mvp_delivery as delivery_module
from eios.frontend.visual import (
    VerticalMVPReadOnlyDelivery,
    build_vertical_mvp_readonly_artifact,
    build_vertical_mvp_readonly_delivery,
)
from eios.frontend.visual.vertical_mvp_delivery import CONTENT_SECURITY_POLICY
from test_vertical_mvp_readonly_renderer import _view


def _artifact():
    return build_vertical_mvp_readonly_artifact(_view())


def test_delivery_preserves_exact_u1_3_bytes_hash_and_response_parts():
    artifact = _artifact()

    delivery = build_vertical_mvp_readonly_delivery(artifact)

    assert delivery.status_code == 200
    assert delivery.body is artifact.content
    assert delivery.body == artifact.content
    assert delivery.content_sha256 == artifact.content_sha256
    assert delivery.content_sha256 == sha256(delivery.body).hexdigest()
    assert delivery.as_response_parts() == (
        delivery.status_code,
        delivery.headers,
        delivery.body,
    )


def test_delivery_headers_are_exact_ordered_and_locked():
    artifact = _artifact()

    delivery = build_vertical_mvp_readonly_delivery(artifact)

    assert delivery.headers == (
        ("Content-Type", "text/html; charset=utf-8"),
        ("Content-Length", str(len(artifact.content))),
        (
            "Content-Disposition",
            'inline; filename="eios-vertical-mvp-readonly.html"',
        ),
        ("Cache-Control", "no-store"),
        ("X-Content-Type-Options", "nosniff"),
        ("Content-Security-Policy", CONTENT_SECURITY_POLICY),
    )
    assert isinstance(delivery.headers, tuple)
    assert all(isinstance(header, tuple) for header in delivery.headers)


def test_content_security_policy_denies_active_and_external_capabilities():
    directives = set(CONTENT_SECURITY_POLICY.split("; "))

    assert directives == {
        "default-src 'none'",
        "style-src 'unsafe-inline'",
        "img-src 'none'",
        "script-src 'none'",
        "connect-src 'none'",
        "object-src 'none'",
        "base-uri 'none'",
        "form-action 'none'",
        "frame-ancestors 'none'",
    }


def test_delivery_is_factory_built_immutable_and_deterministic():
    artifact = _artifact()

    first = build_vertical_mvp_readonly_delivery(artifact)
    second = build_vertical_mvp_readonly_delivery(artifact)

    assert first == second
    assert first.as_response_parts() == second.as_response_parts()
    with pytest.raises(TypeError):
        VerticalMVPReadOnlyDelivery()
    with pytest.raises(FrozenInstanceError):
        first._body = b"changed"


@pytest.mark.parametrize("value", [None, b"html", "<html></html>", {}, object()])
def test_delivery_rejects_non_u1_3_inputs(value):
    with pytest.raises(TypeError, match="exact VerticalMVPReadOnlyArtifact"):
        build_vertical_mvp_readonly_delivery(value)


def test_delivery_rejects_content_or_digest_tampering():
    changed_content = _artifact()
    object.__setattr__(changed_content, "_content", changed_content.content + b"x")
    with pytest.raises(ValueError, match="content_sha256"):
        build_vertical_mvp_readonly_delivery(changed_content)

    changed_digest = _artifact()
    object.__setattr__(changed_digest, "_content_sha256", "0" * 64)
    with pytest.raises(ValueError, match="content_sha256"):
        build_vertical_mvp_readonly_delivery(changed_digest)


def test_delivery_rejects_tampered_size_contract(monkeypatch):
    artifact = _artifact()
    monkeypatch.setattr(
        artifact_module.VerticalMVPReadOnlyArtifact,
        "size_bytes",
        property(lambda self: len(self.content) + 1),
    )

    with pytest.raises(ValueError, match="size_bytes"):
        build_vertical_mvp_readonly_delivery(artifact)


@pytest.mark.parametrize(
    ("attribute", "value", "message"),
    [
        ("MEDIA_TYPE", "text/plain", "media_type"),
        ("FILENAME", "altered.html", "filename"),
    ],
)
def test_delivery_rejects_tampered_canonical_metadata(
    monkeypatch, attribute, value, message
):
    artifact = _artifact()
    monkeypatch.setattr(artifact_module, attribute, value)

    with pytest.raises(ValueError, match=message):
        build_vertical_mvp_readonly_delivery(artifact)


def test_delivery_does_not_mutate_artifact():
    artifact = _artifact()
    before = (artifact.content, artifact.content_sha256, artifact.to_metadata())

    build_vertical_mvp_readonly_delivery(artifact)

    assert (artifact.content, artifact.content_sha256, artifact.to_metadata()) == before


def test_delivery_exposes_no_decision_identity_authentication_or_routing_fields():
    delivery = build_vertical_mvp_readonly_delivery(_artifact())
    public_names = {
        name for name in dir(delivery) if not name.startswith("_")
    }
    forbidden = {
        "decision_fingerprint",
        "input_fingerprint",
        "trace_id",
        "decision_version",
        "provenance_fingerprint",
        "signature",
        "token",
        "session",
        "cookie",
        "url",
        "route",
        "method",
        "recipient",
        "save",
        "send",
    }

    assert forbidden.isdisjoint(public_names)
    assert all(
        header_name not in {"Set-Cookie", "ETag", "Authorization"}
        for header_name, _ in delivery.headers
    )


def test_delivery_module_has_no_io_web_framework_or_engine_imports():
    source = inspect.getsource(delivery_module)
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
        "wsgiref",
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
                "eios.application_boundary",
            )
        )
        for name in imports
    )
