"""Pure controlled-delivery descriptor for the U1.3 read-only artifact."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .vertical_mvp_artifact import (
    FILENAME,
    MEDIA_TYPE,
    VerticalMVPReadOnlyArtifact,
)


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

Header = tuple[str, str]
Headers = tuple[Header, ...]
ResponseParts = tuple[int, Headers, bytes]


@dataclass(frozen=True, init=False)
class VerticalMVPReadOnlyDelivery:
    """Immutable response parts; this object does not perform HTTP I/O."""

    _headers: Headers
    _body: bytes
    _content_sha256: str

    def __init__(self) -> None:
        raise TypeError("Use build_vertical_mvp_readonly_delivery")

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

    def as_response_parts(self) -> ResponseParts:
        return (STATUS_OK, self._headers, self._body)


def build_vertical_mvp_readonly_delivery(
    artifact: VerticalMVPReadOnlyArtifact,
) -> VerticalMVPReadOnlyDelivery:
    """Verify U1.3 transport invariants and describe a locked HTTP response."""
    if type(artifact) is not VerticalMVPReadOnlyArtifact:
        raise TypeError("artifact must be an exact VerticalMVPReadOnlyArtifact")
    if artifact.media_type != MEDIA_TYPE:
        raise ValueError("artifact media_type does not match the U1.3 contract")
    if artifact.filename != FILENAME:
        raise ValueError("artifact filename does not match the U1.3 contract")
    if artifact.size_bytes != len(artifact.content):
        raise ValueError("artifact size_bytes does not match its content")

    digest = sha256(artifact.content).hexdigest()
    if artifact.content_sha256 != digest:
        raise ValueError("artifact content_sha256 does not match its content")

    headers: Headers = (
        ("Content-Type", MEDIA_TYPE),
        ("Content-Length", str(len(artifact.content))),
        ("Content-Disposition", f'inline; filename="{FILENAME}"'),
        ("Cache-Control", "no-store"),
        ("X-Content-Type-Options", "nosniff"),
        ("Content-Security-Policy", CONTENT_SECURITY_POLICY),
    )

    delivery = object.__new__(VerticalMVPReadOnlyDelivery)
    object.__setattr__(delivery, "_headers", headers)
    object.__setattr__(delivery, "_body", artifact.content)
    object.__setattr__(delivery, "_content_sha256", digest)
    return delivery


__all__ = [
    "CONTENT_SECURITY_POLICY",
    "STATUS_OK",
    "VerticalMVPReadOnlyDelivery",
    "build_vertical_mvp_readonly_delivery",
]
