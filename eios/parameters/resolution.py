"""Context binding for parameter configurations used by decision rules.

The Centre of Parameterisation owns configuration history and validity, while
DecisionContext owns the parameter-version identity used for reproducibility.
This module binds both without creating a second versioning system.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from eios.core.models import DecisionContext

from .center import Configuration, ParameterConfigurationError


@dataclass(frozen=True)
class ResolvedConfiguration:
    """One effective configuration bound to a DecisionContext version."""

    configuration: Configuration
    parameters_version: str
    effective_at: datetime

    @property
    def parameter_id(self) -> str:
        return self.configuration.parameter_id

    @property
    def company_id(self) -> str:
        return self.configuration.company_id

    @property
    def value(self) -> str:
        return self.configuration.value

    @property
    def unit(self) -> str | None:
        return self.configuration.unit

    @property
    def configuration_ref(self) -> str:
        """Stable technical reference for evidence binding, not business authority."""
        return (
            f"parameter_configuration:{self.configuration.configuration_id}"
            f"@{self.effective_at.isoformat()}"
        )


def resolve_configuration_for_context(
    configuration: Configuration | None,
    context: DecisionContext,
    effective_at: datetime,
) -> ResolvedConfiguration | None:
    """Bind an already-retrieved effective configuration to DecisionContext.

    ``configuration`` is expected to come from the Centre's
    ``get_configuration_at`` operation.  This function rechecks validity and
    records the DecisionContext parameter version; it does not invent or own a
    separate configuration version.
    """
    if configuration is None:
        return None

    try:
        active = configuration.valid_from <= effective_at and (
            configuration.valid_to is None or effective_at < configuration.valid_to
        )
    except TypeError as exc:
        raise ParameterConfigurationError(
            "INVALID_VALIDITY",
            "La configuración y effective_at deben usar semántica temporal compatible",
        ) from exc

    if not active:
        raise ParameterConfigurationError(
            "INVALID_VALIDITY",
            "La configuración no está vigente en effective_at",
        )

    return ResolvedConfiguration(
        configuration=configuration,
        parameters_version=context.parameters_version,
        effective_at=effective_at,
    )


__all__ = ["ResolvedConfiguration", "resolve_configuration_for_context"]
