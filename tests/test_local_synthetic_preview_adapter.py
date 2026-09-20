import socket
import threading
import time
from dataclasses import FrozenInstanceError
from hashlib import sha256
from pathlib import Path

import pytest

from eios.frontend.visual import (
    build_designated_synthetic_preview_artifact,
    build_designated_synthetic_preview_delivery,
    build_local_synthetic_preview_adapter,
    build_local_synthetic_preview_admission,
    build_vertical_mvp_synthetic_preview_case,
    serve_local_synthetic_preview,
)
from eios.frontend.visual.local_synthetic_preview_adapter import (
    HOST,
    PROFILE,
    ROUTE,
    LocalSyntheticPreviewAdapter,
    LocalSyntheticPreviewRuntime,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "vertical_mvp_synthetic_preview_case_01.json"
)


def _delivery():
    case = build_vertical_mvp_synthetic_preview_case(FIXTURE_PATH.read_bytes())
    admission = build_local_synthetic_preview_admission(case)
    artifact = build_designated_synthetic_preview_artifact(admission)
    return build_designated_synthetic_preview_delivery(artifact)


def _adapter():
    return build_local_synthetic_preview_adapter(_delivery())


def _start_runtime():
    runtime = serve_local_synthetic_preview(_adapter())
    thread = threading.Thread(target=runtime.serve_forever, daemon=True)
    thread.start()
    deadline = time.time() + 2
    while not runtime._serving and time.time() < deadline:
        time.sleep(0.01)
    return runtime, thread


def _raw_request(runtime, request: bytes) -> bytes:
    with socket.create_connection((HOST, runtime.port), timeout=2) as client:
        client.sendall(request)
        client.shutdown(socket.SHUT_WR)
        chunks = []
        while True:
            chunk = client.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
    return b"".join(chunks)


def _split(response: bytes):
    head, _, body = response.partition(b"\r\n\r\n")
    lines = head.split(b"\r\n")
    status = int(lines[0].split()[1])
    headers = []
    for line in lines[1:]:
        name, value = line.split(b":", 1)
        headers.append((name.decode("ascii"), value.strip().decode("utf-8")))
    return status, tuple(headers), body


def test_adapter_is_pure_closed_and_revalidates_delivery():
    delivery = _delivery()
    adapter = build_local_synthetic_preview_adapter(delivery)

    assert type(adapter) is LocalSyntheticPreviewAdapter
    assert adapter.profile == PROFILE
    assert adapter.host == HOST
    assert adapter.route == ROUTE
    assert adapter.delivery.body == delivery.body
    assert adapter.delivery.headers == delivery.headers
    assert adapter.delivery.content_sha256 == delivery.content_sha256

    with pytest.raises(TypeError, match="build_local_synthetic_preview_adapter"):
        LocalSyntheticPreviewAdapter()
    with pytest.raises(FrozenInstanceError):
        adapter._delivery = None


@pytest.mark.parametrize("value", [None, {}, b"x", object()])
def test_adapter_rejects_non_exact_delivery(value):
    with pytest.raises(TypeError, match="DesignatedSyntheticPreviewDelivery exacto"):
        build_local_synthetic_preview_adapter(value)


def test_adapter_rejects_tampered_delivery_before_socket():
    delivery = _delivery()
    object.__setattr__(delivery, "_body", delivery.body + b"x")

    with pytest.raises(ValueError, match="body"):
        build_local_synthetic_preview_adapter(delivery)


def test_delivery_retains_artifact_for_lineage_revalidation():
    delivery = _delivery()

    assert delivery.artifact.content == delivery.body
    rebuilt = build_designated_synthetic_preview_delivery(delivery.artifact)
    assert rebuilt.as_response_parts() == delivery.as_response_parts()


def test_runtime_binds_literal_ipv4_loopback_and_ephemeral_port():
    runtime = serve_local_synthetic_preview(_adapter())
    try:
        assert type(runtime) is LocalSyntheticPreviewRuntime
        assert runtime.host == "127.0.0.1"
        assert runtime.port > 0
        assert runtime._server.server_address[0] == "127.0.0.1"
        assert runtime.url == f"http://127.0.0.1:{runtime.port}{ROUTE}"
        assert runtime.closed is False
    finally:
        runtime.close()


def test_runtime_close_is_idempotent_before_serving():
    runtime = serve_local_synthetic_preview(_adapter())

    runtime.close()
    runtime.close()

    assert runtime.closed is True
    with pytest.raises(RuntimeError, match="cerrado"):
        runtime.handle_request()
    with pytest.raises(RuntimeError, match="cerrado"):
        runtime.serve_forever()


def test_get_returns_exact_u15c_status_headers_and_body():
    delivery = _delivery()
    runtime, thread = _start_runtime()
    try:
        response = _raw_request(
            runtime,
            (
                f"GET {ROUTE} HTTP/1.1\r\n"
                f"Host: 127.0.0.1:{runtime.port}\r\n"
                "Connection: close\r\n\r\n"
            ).encode("ascii"),
        )
        status, headers, body = _split(response)

        assert status == delivery.status_code
        assert headers == delivery.headers
        assert body == delivery.body
        assert sha256(body).hexdigest() == delivery.content_sha256
    finally:
        runtime.close()
        thread.join(timeout=2)


def test_head_returns_exact_representation_headers_and_empty_body():
    delivery = _delivery()
    runtime, thread = _start_runtime()
    try:
        response = _raw_request(
            runtime,
            (
                f"HEAD {ROUTE} HTTP/1.1\r\n"
                f"Host: 127.0.0.1:{runtime.port}\r\n"
                "Connection: close\r\n\r\n"
            ).encode("ascii"),
        )
        status, headers, body = _split(response)

        assert status == delivery.status_code
        assert headers == delivery.headers
        assert dict(headers)["Content-Length"] == str(len(delivery.body))
        assert body == b""
    finally:
        runtime.close()
        thread.join(timeout=2)


@pytest.mark.parametrize(
    "target",
    [
        "/",
        f"{ROUTE}?x=1",
        f"{ROUTE}/",
        "/eios/%6cocal-synthetic-preview",
        "http://127.0.0.1/eios/local-synthetic-preview",
        "/eios/../eios/local-synthetic-preview",
    ],
)
def test_non_exact_request_targets_are_404(target):
    runtime, thread = _start_runtime()
    try:
        response = _raw_request(
            runtime,
            (
                f"GET {target} HTTP/1.1\r\n"
                f"Host: 127.0.0.1:{runtime.port}\r\n"
                "Connection: close\r\n\r\n"
            ).encode("ascii"),
        )
        status, headers, body = _split(response)
        assert status == 404
        assert dict(headers)["Content-Length"] == "0"
        assert body == b""
    finally:
        runtime.close()
        thread.join(timeout=2)


@pytest.mark.parametrize(
    "host_template",
    [
        "localhost:{port}",
        "127.0.0.1",
        "example.test:{port}",
        "127.0.0.1:1",
    ],
)
def test_non_exact_host_is_rejected(host_template):
    runtime, thread = _start_runtime()
    try:
        host = host_template.format(port=runtime.port)
        response = _raw_request(
            runtime,
            (
                f"GET {ROUTE} HTTP/1.1\r\n"
                f"Host: {host}\r\n"
                "Connection: close\r\n\r\n"
            ).encode("ascii"),
        )
        status, _, body = _split(response)
        assert status == 400
        assert body == b""
    finally:
        runtime.close()
        thread.join(timeout=2)


def test_duplicate_host_is_rejected():
    runtime, thread = _start_runtime()
    try:
        response = _raw_request(
            runtime,
            (
                f"GET {ROUTE} HTTP/1.1\r\n"
                f"Host: 127.0.0.1:{runtime.port}\r\n"
                f"Host: 127.0.0.1:{runtime.port}\r\n"
                "Connection: close\r\n\r\n"
            ).encode("ascii"),
        )
        assert _split(response)[0] == 400
    finally:
        runtime.close()
        thread.join(timeout=2)


@pytest.mark.parametrize(
    "extra",
    [
        "Content-Length: 1\r\n",
        "Transfer-Encoding: chunked\r\n",
        "Content-Length: 0\r\nContent-Length: 0\r\n",
    ],
)
def test_request_body_surfaces_are_rejected(extra):
    runtime, thread = _start_runtime()
    try:
        response = _raw_request(
            runtime,
            (
                f"GET {ROUTE} HTTP/1.1\r\n"
                f"Host: 127.0.0.1:{runtime.port}\r\n"
                f"{extra}"
                "Connection: close\r\n\r\n"
                "x"
            ).encode("ascii"),
        )
        assert _split(response)[0] == 400
    finally:
        runtime.close()
        thread.join(timeout=2)


@pytest.mark.parametrize(
    "method",
    ["POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE", "CONNECT"],
)
def test_unsupported_methods_are_405_without_body(method):
    runtime, thread = _start_runtime()
    try:
        response = _raw_request(
            runtime,
            (
                f"{method} {ROUTE} HTTP/1.1\r\n"
                f"Host: 127.0.0.1:{runtime.port}\r\n"
                "Connection: close\r\n\r\n"
            ).encode("ascii"),
        )
        status, headers, body = _split(response)
        assert status == 405
        assert dict(headers)["Allow"] == "GET, HEAD"
        assert body == b""
    finally:
        runtime.close()
        thread.join(timeout=2)


def test_success_response_adds_no_server_date_cookie_cors_or_etag_headers():
    runtime, thread = _start_runtime()
    try:
        response = _raw_request(
            runtime,
            (
                f"GET {ROUTE} HTTP/1.1\r\n"
                f"Host: 127.0.0.1:{runtime.port}\r\n"
                "Connection: close\r\n\r\n"
            ).encode("ascii"),
        )
        _, headers, _ = _split(response)
        names = {name.lower() for name, _ in headers}

        assert "server" not in names
        assert "date" not in names
        assert "set-cookie" not in names
        assert "access-control-allow-origin" not in names
        assert "etag" not in names
        assert "last-modified" not in names
    finally:
        runtime.close()
        thread.join(timeout=2)


def test_close_stops_accepting_connections():
    runtime, thread = _start_runtime()
    port = runtime.port
    runtime.close()
    thread.join(timeout=2)

    with pytest.raises(OSError):
        socket.create_connection((HOST, port), timeout=0.25)


def test_runtime_factory_rejects_non_adapter_without_binding():
    with pytest.raises(TypeError, match="LocalSyntheticPreviewAdapter exacto"):
        serve_local_synthetic_preview(_delivery())


def test_no_operational_surface_is_exposed():
    adapter = _adapter()
    names = {name for name in dir(adapter) if not name.startswith("_")}
    forbidden = {
        "authenticate",
        "authorization",
        "cookie",
        "execute",
        "load",
        "open_browser",
        "path",
        "save",
        "session",
        "token",
        "upload",
    }
    assert forbidden.isdisjoint(names)
