"""Immutable transport artifact for the U1.2 read-only Vertical MVP HTML."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
from typing import Any

from .vertical_mvp_renderer import render_vertical_mvp_readonly


MEDIA_TYPE = "text/html; charset=utf-8"
FILENAME = "eios-vertical-mvp-readonly.html"


@dataclass(frozen=True, init=False)
class VerticalMVPReadOnlyArtifact:
    """Exact immutable bytes emitted by the authorized U1.2 renderer."""

    _content: bytes
    _content_sha256: str

    def __init__(self) -> None:
        raise TypeError("Use build_vertical_mvp_readonly_artifact")

    @property
    def media_type(self) -> str:
        return MEDIA_TYPE

    @property
    def filename(self) -> str:
        return FILENAME

    @property
    def content(self) -> bytes:
        return self._content

    @property
    def size_bytes(self) -> int:
        return len(self._content)

    @property
    def content_sha256(self) -> str:
        return self._content_sha256

    def to_metadata(self) -> dict[str, str | int]:
        return {
            "media_type": MEDIA_TYPE,
            "filename": FILENAME,
            "size_bytes": self.size_bytes,
            "content_sha256": self._content_sha256,
        }


def build_vertical_mvp_readonly_artifact(
    view_model: Mapping[str, Any],
) -> VerticalMVPReadOnlyArtifact:
    """Build exact UTF-8 transport bytes from the closed U1.2 renderer."""
    html = render_vertical_mvp_readonly(view_model)
    content = html.encode("utf-8")
    digest = sha256(content).hexdigest()

    artifact = object.__new__(VerticalMVPReadOnlyArtifact)
    object.__setattr__(artifact, "_content", content)
    object.__setattr__(artifact, "_content_sha256", digest)
    return artifact


__all__ = [
    "FILENAME",
    "MEDIA_TYPE",
    "VerticalMVPReadOnlyArtifact",
    "build_vertical_mvp_readonly_artifact",
]
