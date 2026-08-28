"""Canonical fingerprints for C0 reproducibility."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Any

from .models import InputContract


def _canonical_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _canonical_value(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item) for item in value]
    return value


def canonical_input_payload(input_contract: InputContract) -> dict[str, Any]:
    """Return the complete canonical representation of the C0 input."""
    return _canonical_value(input_contract.model_dump(mode="python"))


def input_fingerprint(input_contract: InputContract) -> str:
    """Return a stable SHA-256 fingerprint of the complete input contract."""
    canonical = json.dumps(
        canonical_input_payload(input_contract),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


__all__ = ["canonical_input_payload", "input_fingerprint"]
