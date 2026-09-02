"""U1 application boundary.

This module adapts UI input to the existing O1 contract. It deliberately does
not invoke analytical capabilities or create decision authority.
"""

from __future__ import annotations

from typing import Any, Mapping

from eios.core.models import DecisionContext, PurchaseOperation


FORBIDDEN_FIELDS = frozenset({"decision_version", "decision_fingerprint"})


class FrontendBoundaryError(ValueError):
    """Raised when UI input violates the U1 boundary."""


def build_purchase_operation(payload: Mapping[str, Any]) -> PurchaseOperation:
    """Build a canonical PurchaseOperation from authorized UI fields only."""
    forbidden = FORBIDDEN_FIELDS.intersection(payload.keys())
    if forbidden:
        raise FrontendBoundaryError(
            f"campos no autorizados: {', '.join(sorted(forbidden))}"
        )
    try:
        return PurchaseOperation.model_validate(dict(payload))
    except Exception as exc:
        raise FrontendBoundaryError("entrada de operación no válida") from exc


def build_decision_context(payload: Mapping[str, Any]) -> DecisionContext:
    """Build the canonical DecisionContext without introducing versioning."""
    forbidden = FORBIDDEN_FIELDS.intersection(payload.keys())
    if forbidden:
        raise FrontendBoundaryError(
            f"campos no autorizados: {', '.join(sorted(forbidden))}"
        )
    try:
        return DecisionContext.model_validate(dict(payload))
    except Exception as exc:
        raise FrontendBoundaryError("contexto de decisión no válido") from exc


def present_support_package(package: Any) -> Mapping[str, Any]:
    """Expose an existing O1 package without recalculating or mutating it."""
    if not hasattr(package, "model_dump"):
        raise FrontendBoundaryError("paquete O1 no válido")
    return package.model_dump(mode="json")
