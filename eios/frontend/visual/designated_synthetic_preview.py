"""Pure designated synthetic preview artifact and delivery for U1.5C."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from hmac import compare_digest

from .synthetic_preview_admission import (
    CLASSIFICATION,
    NOTICE,
    PROFILE,
    SCOPE,
    LocalSyntheticPreviewAdmission,
    build_local_synthetic_preview_admission,
)


ARTIFACT_SCHEMA_VERSION = "EIOS-DESIGNATED-SYNTHETIC-PREVIEW-ARTIFACT-01/v0.1"
DELIVERY_SCHEMA_VERSION = "EIOS-DESIGNATED-SYNTHETIC-PREVIEW-DELIVERY-01/v0.1"
MEDIA_TYPE = "text/html; charset=utf-8"
FILENAME = "eios-synthetic-preview.html"
STATUS_OK = 200
CONTENT_SECURITY_POLICY = (
    "default-src 'none'; "
    "style-src 'unsafe-inline'; "
    "img-src 'none'; "
    "script-src 'none'; "
    "connect-src 'none'; "
    "object-src 'none'; "
    "base-uri 'none'; "
    "form-action 'none'; "
    "frame-ancestors 'none'"
)

_SYNTHETIC_STYLE = (
    ".eios-synthetic-designation{position:sticky;top:0;z-index:2147483647;"
    "padding:12px 16px;border-bottom:3px solid #111;background:#fff4cc;"
    "color:#111;font-family:Inter,system-ui,sans-serif;font-weight:800;"
    "letter-spacing:.02em;text-align:center}"
    ".eios-synthetic-designation small{display:block;margin-top:4px;font-weight:700}"
)
_STYLE_END = "\n</style>"
_BODY_OPEN = "<body>\n"
_FORBIDDEN_SOURCE_TOKENS = (
    "<script",
    "<iframe",
    "<object",
    "<embed",
    "<form",
    "<img",
    "<link",
    "<base",
    "<meta http-equiv",
    "javascript:",
    "data:",
    "src=",
    "srcset=",
    "action=",
    "formaction=",
)

Header = tuple[str, str]
Headers = tuple[Header, ...]
ResponseParts = tuple[int, Headers, bytes]


def _revalidate_admission(
    admission: LocalSyntheticPreviewAdmission,
) -> LocalSyntheticPreviewAdmission:
    if type(admission) is not LocalSyntheticPreviewAdmission:
        raise TypeError("admission debe ser una LocalSyntheticPreviewAdmission exacta")

    rebuilt = build_local_synthetic_preview_admission(admission.case)
    if admission.schema_version != rebuilt.schema_version:
        raise ValueError("admission schema_version no coincide con U1.5A")
    if admission.profile != PROFILE or admission.profile != rebuilt.profile:
        raise ValueError("admission profile no coincide con U1.5A")
    if admission.case_id != rebuilt.case_id:
        raise ValueError("admission case_id no coincide con el caso revalidado")
    if not compare_digest(admission.case_fingerprint, rebuilt.case_fingerprint):
        raise ValueError("admission case_fingerprint no coincide con el caso revalidado")
    if admission.notice != NOTICE or admission.notice != rebuilt.notice:
        raise ValueError("admission notice no coincide con el contrato sintético")
    if admission.operational_effect is not False:
        raise ValueError("admission operational_effect debe ser false")
    if admission.decision_authority is not False:
        raise ValueError("admission decision_authority debe ser false")
    if admission.execution_claim is not False:
        raise ValueError("admission execution_claim debe ser false")

    source = rebuilt.artifact.content
    source_digest = sha256(source).hexdigest()
    if not compare_digest(source_digest, rebuilt.artifact.content_sha256):
        raise ValueError("artefacto U1.3 revalidado tiene digest inconsistente")
    if rebuilt.delivery.body != source:
        raise ValueError("delivery U1.4 revalidado no conserva bytes U1.3")
    if not compare_digest(rebuilt.delivery.content_sha256, source_digest):
        raise ValueError("delivery U1.4 revalidado no conserva digest U1.3")

    if admission.artifact.content != source:
        raise ValueError("admission artifact no coincide con U1.3 revalidado")
    if admission.delivery.body != source:
        raise ValueError("admission delivery no coincide con U1.4 revalidado")
    if not compare_digest(admission.artifact_content_sha256, source_digest):
        raise ValueError("admission artifact_content_sha256 no coincide con U1.3")
    if not compare_digest(admission.delivery_content_sha256, source_digest):
        raise ValueError("admission delivery_content_sha256 no coincide con U1.4")
    if admission.content_size_bytes != len(source):
        raise ValueError("admission content_size_bytes no coincide con U1.3")
    return rebuilt


def _compose_designated_html(source: bytes) -> bytes:
    try:
        html = source.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("U1.3 no contiene UTF-8 estricto") from exc

    if not html.startswith("<!doctype html>\n<html lang=\"es\">\n<head>\n"):
        raise ValueError("U1.3 no conserva la apertura HTML contractual")
    if not html.endswith("\n</body>\n</html>"):
        raise ValueError("U1.3 no conserva el cierre HTML contractual")
    if html.count(_STYLE_END) != 1 or html.count(_BODY_OPEN) != 1:
        raise ValueError("U1.3 no conserva los anclajes estructurales contractuales")

    lowered = html.lower()
    for token in _FORBIDDEN_SOURCE_TOKENS:
        if token in lowered:
            raise ValueError(f"U1.3 contiene superficie activa no permitida: {token}")

    designation = (
        '<div class="eios-synthetic-designation" role="note" '
        'aria-label="Designación sintética de prueba">'
        f"{NOTICE}"
        "<small>SYNTHETIC · TEST_ONLY · NO OPERATIONAL EFFECT</small>"
        "</div>\n"
    )
    html = html.replace(_STYLE_END, _SYNTHETIC_STYLE + _STYLE_END, 1)
    html = html.replace(_BODY_OPEN, _BODY_OPEN + designation, 1)
    result = html.encode("utf-8")

    if result == source:
        raise ValueError("U1.5C debe ser un artefacto distinto de U1.3")
    if result.count(NOTICE.encode("utf-8")) != 1:
        raise ValueError("U1.5C no contiene exactamente un NOTICE contractual")
    for marker in (b"SYNTHETIC", b"TEST_ONLY", b"NO OPERATIONAL EFFECT"):
        if marker not in result:
            raise ValueError("U1.5C no contiene todos los marcadores sintéticos")
    return result


@dataclass(frozen=True, init=False)
class DesignatedSyntheticPreviewArtifact:
    """Immutable U1.5C HTML artifact with designation in its own bytes."""

    _source_admission: LocalSyntheticPreviewAdmission
    _case_id: str
    _case_fingerprint: str
    _source_artifact_content_sha256: str
    _content: bytes
    _content_sha256: str

    def __init__(self) -> None:
        raise TypeError("Use build_designated_synthetic_preview_artifact")

    @property
    def schema_version(self) -> str:
        return ARTIFACT_SCHEMA_VERSION

    @property
    def profile(self) -> str:
        return PROFILE

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
    def case_id(self) -> str:
        return self._case_id

    @property
    def case_fingerprint(self) -> str:
        return self._case_fingerprint

    @property
    def source_artifact_content_sha256(self) -> str:
        return self._source_artifact_content_sha256

    @property
    def content(self) -> bytes:
        return self._content

    @property
    def content_sha256(self) -> str:
        return self._content_sha256

    @property
    def size_bytes(self) -> int:
        return len(self._content)

    @property
    def media_type(self) -> str:
        return MEDIA_TYPE

    @property
    def filename(self) -> str:
        return FILENAME

    def to_metadata(self) -> dict[str, str | bool | int]:
        return {
            "schema_version": ARTIFACT_SCHEMA_VERSION,
            "profile": PROFILE,
            "classification": CLASSIFICATION,
            "scope": SCOPE,
            "operational_effect": False,
            "decision_authority": False,
            "execution_claim": False,
            "notice": NOTICE,
            "case_id": self._case_id,
            "case_fingerprint": self._case_fingerprint,
            "source_artifact_content_sha256": self._source_artifact_content_sha256,
            "content_sha256": self._content_sha256,
            "size_bytes": self.size_bytes,
            "media_type": MEDIA_TYPE,
            "filename": FILENAME,
        }


def build_designated_synthetic_preview_artifact(
    admission: LocalSyntheticPreviewAdmission,
) -> DesignatedSyntheticPreviewArtifact:
    """Revalidate U1.5A and derive one separately identified U1.5C artifact."""
    rebuilt = _revalidate_admission(admission)
    source = rebuilt.artifact.content
    source_digest = sha256(source).hexdigest()
    content = _compose_designated_html(source)
    digest = sha256(content).hexdigest()
    if compare_digest(digest, source_digest):
        raise ValueError("U1.5C digest no puede identificarse con U1.3")

    artifact = object.__new__(DesignatedSyntheticPreviewArtifact)
    object.__setattr__(artifact, "_source_admission", rebuilt)
    object.__setattr__(artifact, "_case_id", rebuilt.case_id)
    object.__setattr__(artifact, "_case_fingerprint", rebuilt.case_fingerprint)
    object.__setattr__(artifact, "_source_artifact_content_sha256", source_digest)
    object.__setattr__(artifact, "_content", content)
    object.__setattr__(artifact, "_content_sha256", digest)
    return artifact


def _revalidate_artifact(
    artifact: DesignatedSyntheticPreviewArtifact,
) -> None:
    if type(artifact) is not DesignatedSyntheticPreviewArtifact:
        raise TypeError("artifact debe ser un DesignatedSyntheticPreviewArtifact exacto")
    rebuilt = _revalidate_admission(artifact._source_admission)
    source = rebuilt.artifact.content
    source_digest = sha256(source).hexdigest()
    if artifact.case_id != rebuilt.case_id:
        raise ValueError("artifact case_id no coincide con U1.5A revalidada")
    if not compare_digest(artifact.case_fingerprint, rebuilt.case_fingerprint):
        raise ValueError("artifact case_fingerprint no coincide con U1.5A revalidada")
    if not compare_digest(artifact.source_artifact_content_sha256, source_digest):
        raise ValueError("artifact source_artifact_content_sha256 no coincide con U1.3")
    expected_content = _compose_designated_html(source)
    if artifact.content != expected_content:
        raise ValueError("artifact content no coincide con la composición U1.5C revalidada")
    if artifact.schema_version != ARTIFACT_SCHEMA_VERSION:
        raise ValueError("artifact schema_version no coincide con U1.5C")
    if artifact.profile != PROFILE or artifact.classification != CLASSIFICATION:
        raise ValueError("artifact clasificación sintética no coincide con U1.5C")
    if artifact.scope != SCOPE:
        raise ValueError("artifact scope no coincide con U1.5C")
    if artifact.operational_effect is not False:
        raise ValueError("artifact operational_effect debe ser false")
    if artifact.decision_authority is not False:
        raise ValueError("artifact decision_authority debe ser false")
    if artifact.execution_claim is not False:
        raise ValueError("artifact execution_claim debe ser false")
    if artifact.notice != NOTICE:
        raise ValueError("artifact notice no coincide con U1.5C")
    if artifact.media_type != MEDIA_TYPE or artifact.filename != FILENAME:
        raise ValueError("artifact transporte no coincide con U1.5C")
    if artifact.size_bytes != len(artifact.content):
        raise ValueError("artifact size_bytes no coincide con su contenido")
    digest = sha256(artifact.content).hexdigest()
    if not compare_digest(artifact.content_sha256, digest):
        raise ValueError("artifact content_sha256 no coincide con su contenido")
    if compare_digest(artifact.source_artifact_content_sha256, digest):
        raise ValueError("artifact U1.5C no puede compartir identidad con U1.3")
    if artifact.content.count(NOTICE.encode("utf-8")) != 1:
        raise ValueError("artifact no conserva exactamente un NOTICE contractual")
    for marker in (b"SYNTHETIC", b"TEST_ONLY", b"NO OPERATIONAL EFFECT"):
        if marker not in artifact.content:
            raise ValueError("artifact no conserva los marcadores sintéticos")


@dataclass(frozen=True, init=False)
class DesignatedSyntheticPreviewDelivery:
    """Immutable response descriptor for U1.5C; performs no HTTP I/O."""

    _headers: Headers
    _body: bytes
    _content_sha256: str

    def __init__(self) -> None:
        raise TypeError("Use build_designated_synthetic_preview_delivery")

    @property
    def schema_version(self) -> str:
        return DELIVERY_SCHEMA_VERSION

    @property
    def status_code(self) -> int:
        return STATUS_OK

    @property
    def headers(self) -> Headers:
        return self._headers

    @property
    def body(self) -> bytes:
        return self._body

    @property
    def content_sha256(self) -> str:
        return self._content_sha256

    @property
    def size_bytes(self) -> int:
        return len(self._body)

    def as_response_parts(self) -> ResponseParts:
        return (STATUS_OK, self._headers, self._body)


def build_designated_synthetic_preview_delivery(
    artifact: DesignatedSyntheticPreviewArtifact,
) -> DesignatedSyntheticPreviewDelivery:
    """Revalidate U1.5C and describe deterministic response parts without I/O."""
    _revalidate_artifact(artifact)
    headers: Headers = (
        ("Content-Type", MEDIA_TYPE),
        ("Content-Length", str(len(artifact.content))),
        ("Content-Disposition", f'inline; filename="{FILENAME}"'),
        ("Cache-Control", "no-store"),
        ("X-Content-Type-Options", "nosniff"),
        ("Referrer-Policy", "no-referrer"),
        ("Content-Security-Policy", CONTENT_SECURITY_POLICY),
    )
    delivery = object.__new__(DesignatedSyntheticPreviewDelivery)
    object.__setattr__(delivery, "_headers", headers)
    object.__setattr__(delivery, "_body", artifact.content)
    object.__setattr__(delivery, "_content_sha256", artifact.content_sha256)
    return delivery


__all__ = [
    "ARTIFACT_SCHEMA_VERSION",
    "CONTENT_SECURITY_POLICY",
    "DELIVERY_SCHEMA_VERSION",
    "DesignatedSyntheticPreviewArtifact",
    "DesignatedSyntheticPreviewDelivery",
    "FILENAME",
    "MEDIA_TYPE",
    "STATUS_OK",
    "build_designated_synthetic_preview_artifact",
    "build_designated_synthetic_preview_delivery",
]
