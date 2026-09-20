"""Minimal loopback-only HTTP adapter for U1.5B synthetic preview."""

from __future__ import annotations

from dataclasses import dataclass
from hmac import compare_digest
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Final

from .designated_synthetic_preview import (
    DesignatedSyntheticPreviewDelivery,
    build_designated_synthetic_preview_delivery,
)


PROFILE: Final = "LOCAL_SYNTHETIC_PREVIEW"
HOST: Final = "127.0.0.1"
ROUTE: Final = "/eios/local-synthetic-preview"
_ALLOWED_METHODS = frozenset({"GET", "HEAD"})
_UNSUPPORTED_METHODS = (
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
    "TRACE",
    "CONNECT",
)


def _revalidate_delivery(
    delivery: DesignatedSyntheticPreviewDelivery,
) -> DesignatedSyntheticPreviewDelivery:
    if type(delivery) is not DesignatedSyntheticPreviewDelivery:
        raise TypeError("delivery debe ser un DesignatedSyntheticPreviewDelivery exacto")

    rebuilt = build_designated_synthetic_preview_delivery(delivery.artifact)
    if delivery.schema_version != rebuilt.schema_version:
        raise ValueError("delivery schema_version no coincide con U1.5C")
    if delivery.status_code != rebuilt.status_code:
        raise ValueError("delivery status_code no coincide con U1.5C")
    if delivery.headers != rebuilt.headers:
        raise ValueError("delivery headers no coinciden con U1.5C")
    if delivery.body != rebuilt.body:
        raise ValueError("delivery body no coincide con U1.5C")
    if delivery.size_bytes != rebuilt.size_bytes:
        raise ValueError("delivery size_bytes no coincide con U1.5C")
    if not compare_digest(delivery.content_sha256, rebuilt.content_sha256):
        raise ValueError("delivery content_sha256 no coincide con U1.5C")
    return rebuilt


@dataclass(frozen=True, init=False)
class LocalSyntheticPreviewAdapter:
    """Pure immutable adapter configuration; no socket is opened here."""

    _delivery: DesignatedSyntheticPreviewDelivery

    def __init__(self) -> None:
        raise TypeError("Use build_local_synthetic_preview_adapter")

    @property
    def profile(self) -> str:
        return PROFILE

    @property
    def host(self) -> str:
        return HOST

    @property
    def route(self) -> str:
        return ROUTE

    @property
    def delivery(self) -> DesignatedSyntheticPreviewDelivery:
        return self._delivery


def build_local_synthetic_preview_adapter(
    delivery: DesignatedSyntheticPreviewDelivery,
) -> LocalSyntheticPreviewAdapter:
    """Build a pure adapter only from one exact revalidated U1.5C delivery."""
    rebuilt = _revalidate_delivery(delivery)
    adapter = object.__new__(LocalSyntheticPreviewAdapter)
    object.__setattr__(adapter, "_delivery", rebuilt)
    return adapter


class _LoopbackHTTPServer(HTTPServer):
    allow_reuse_address = False


class _PreviewHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: object) -> None:
        return

    def _empty_response(self, status: int, *, allow: bool = False) -> None:
        self.send_response_only(status)
        self.send_header("Content-Length", "0")
        self.send_header("Cache-Control", "no-store")
        if allow:
            self.send_header("Allow", "GET, HEAD")
        self.end_headers()
        self.close_connection = True

    def _request_is_valid(self) -> bool:
        hosts = self.headers.get_all("Host", failobj=[])
        expected_host = f"{HOST}:{self.server.server_port}"
        if hosts != [expected_host]:
            self._empty_response(400)
            return False

        if self.headers.get("Transfer-Encoding") is not None:
            self._empty_response(400)
            return False

        content_lengths = self.headers.get_all("Content-Length", failobj=[])
        if len(content_lengths) > 1:
            self._empty_response(400)
            return False
        if content_lengths:
            raw = content_lengths[0].strip()
            if raw != "0":
                self._empty_response(400)
                return False

        if self.path != ROUTE:
            self._empty_response(404)
            return False

        return True

    def _serve_authorized(self, *, include_body: bool) -> None:
        if not self._request_is_valid():
            return

        delivery = self.server.adapter.delivery
        try:
            rebuilt = _revalidate_delivery(delivery)
        except (TypeError, ValueError):
            self._empty_response(500)
            return

        self.send_response_only(rebuilt.status_code)
        for name, value in rebuilt.headers:
            self.send_header(name, value)
        self.end_headers()
        if include_body:
            self.wfile.write(rebuilt.body)
        self.wfile.flush()
        self.close_connection = True

    def do_GET(self) -> None:
        self._serve_authorized(include_body=True)

    def do_HEAD(self) -> None:
        self._serve_authorized(include_body=False)


for _method in _UNSUPPORTED_METHODS:
    setattr(
        _PreviewHandler,
        f"do_{_method}",
        lambda self, _method=_method: self._empty_response(405, allow=True),
    )


@dataclass(init=False)
class LocalSyntheticPreviewRuntime:
    """Explicit foreground runtime owning one loopback HTTP server."""

    _server: _LoopbackHTTPServer
    _closed: bool

    def __init__(self) -> None:
        raise TypeError("Use serve_local_synthetic_preview")

    @property
    def host(self) -> str:
        return HOST

    @property
    def port(self) -> int:
        return int(self._server.server_port)

    @property
    def url(self) -> str:
        return f"http://{HOST}:{self.port}{ROUTE}"

    @property
    def closed(self) -> bool:
        return self._closed

    def handle_request(self) -> None:
        if self._closed:
            raise RuntimeError("runtime cerrado")
        self._server.handle_request()

    def serve_forever(self) -> None:
        if self._closed:
            raise RuntimeError("runtime cerrado")
        self._server.serve_forever(poll_interval=0.05)

    def close(self) -> None:
        if self._closed:
            return
        self._server.shutdown()
        self._server.server_close()
        self._closed = True


def serve_local_synthetic_preview(
    adapter: LocalSyntheticPreviewAdapter,
) -> LocalSyntheticPreviewRuntime:
    """Open one explicit ephemeral IPv4 loopback listener for the adapter."""
    if type(adapter) is not LocalSyntheticPreviewAdapter:
        raise TypeError("adapter debe ser un LocalSyntheticPreviewAdapter exacto")
    rebuilt = build_local_synthetic_preview_adapter(adapter.delivery)
    server = _LoopbackHTTPServer((HOST, 0), _PreviewHandler, bind_and_activate=True)
    server.adapter = rebuilt
    runtime = object.__new__(LocalSyntheticPreviewRuntime)
    runtime._server = server
    runtime._closed = False
    return runtime


__all__ = [
    "HOST",
    "LocalSyntheticPreviewAdapter",
    "LocalSyntheticPreviewRuntime",
    "PROFILE",
    "ROUTE",
    "build_local_synthetic_preview_adapter",
    "serve_local_synthetic_preview",
]
