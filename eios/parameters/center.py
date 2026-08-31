"""Application boundary for the EIOS Centre of Parameterisation.

The module implements only the approved configuration contract. Persistence,
parameter identity and authorization are supplied through explicit ports.
No rule evaluation, CRC resolution or decision-making is performed here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Protocol


ValueValidation = Callable[[str], str | None]


@dataclass(frozen=True)
class ParameterDefinition:
    """Authorized parameter metadata supplied by the parameter catalogue."""

    parameter_id: str
    value_type: str | None = None
    unit: str | None = None
    validate_value: ValueValidation | None = None
    restricted: bool = False


@dataclass(frozen=True)
class Configuration:
    configuration_id: int
    parameter_id: str
    company_id: str
    value: str
    value_type: str | None
    unit: str | None
    valid_from: datetime
    valid_to: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class HistoryEntry:
    configuration_id: int
    parameter_id: str
    company_id: str
    previous_value: str | None
    new_value: str
    changed_by: str
    changed_at: datetime
    change_reason: str


@dataclass(frozen=True)
class ChangeRequest:
    company_id: str
    parameter_id: str
    value: str
    valid_from: datetime
    valid_to: datetime | None
    actor: str
    reason: str


class ParameterConfigurationError(ValueError):
    """Contract-level error carrying a stable implementation code."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class ParameterCatalogue(Protocol):
    def get_parameter(self, parameter_id: str) -> ParameterDefinition | None: ...


class ConfigurationAuthorization(Protocol):
    def can_modify(self, company_id: str, parameter_id: str, actor: str) -> bool: ...


class ConfigurationRepository(Protocol):
    """Persistence port; implementations must make writes atomic."""

    def get_current(self, company_id: str, parameter_id: str) -> Configuration | None: ...

    def get_at(
        self, company_id: str, parameter_id: str, effective_at: datetime
    ) -> Configuration | None: ...

    def get_history(self, company_id: str, parameter_id: str) -> tuple[HistoryEntry, ...]: ...

    def has_overlapping_configuration(
        self,
        company_id: str,
        parameter_id: str,
        valid_from: datetime,
        valid_to: datetime | None,
    ) -> bool: ...

    def apply_change_atomically(self, request: ChangeRequest) -> Configuration: ...


class ParameterConfigurationCenter:
    """Implements the approved Centre semantics without owning persistence."""

    def __init__(
        self,
        catalogue: ParameterCatalogue,
        authorization: ConfigurationAuthorization,
        repository: ConfigurationRepository,
    ) -> None:
        self._catalogue = catalogue
        self._authorization = authorization
        self._repository = repository

    def get_parameter(self, parameter_id: str) -> ParameterDefinition:
        definition = self._catalogue.get_parameter(parameter_id)
        if definition is None:
            raise ParameterConfigurationError(
                "PARAMETER_NOT_FOUND", f"Parámetro no encontrado: {parameter_id}"
            )
        return definition

    def get_current_configuration(
        self, company_id: str, parameter_id: str
    ) -> Configuration | None:
        self._validate_scope(company_id)
        self.get_parameter(parameter_id)
        return self._repository.get_current(company_id, parameter_id)

    def get_configuration_at(
        self, company_id: str, parameter_id: str, effective_at: datetime
    ) -> Configuration | None:
        self._validate_scope(company_id)
        self.get_parameter(parameter_id)
        return self._repository.get_at(company_id, parameter_id, effective_at)

    def get_parameter_history(
        self, company_id: str, parameter_id: str
    ) -> tuple[HistoryEntry, ...]:
        self._validate_scope(company_id)
        self.get_parameter(parameter_id)
        return self._repository.get_history(company_id, parameter_id)

    def validate_change(self, request: ChangeRequest) -> None:
        definition = self.get_parameter(request.parameter_id)
        self._validate_request_scope(request)
        if not self._authorization.can_modify(
            request.company_id, request.parameter_id, request.actor
        ):
            code = "RESTRICTED_PARAMETER" if definition.restricted else "UNAUTHORIZED_CHANGE"
            raise ParameterConfigurationError(
                code, "El actor no está autorizado para modificar el parámetro"
            )
        if definition.validate_value is not None:
            validation_error = definition.validate_value(request.value)
            if validation_error is not None:
                if validation_error not in {"INVALID_VALUE", "INVALID_TYPE"}:
                    validation_error = "INVALID_VALUE"
                raise ParameterConfigurationError(
                    validation_error,
                    "El valor no cumple la validación autorizada del parámetro",
                )
        if request.valid_to is not None and request.valid_from >= request.valid_to:
            raise ParameterConfigurationError(
                "INVALID_VALIDITY", "valid_from debe ser anterior a valid_to"
            )
        if self._repository.has_overlapping_configuration(
            request.company_id,
            request.parameter_id,
            request.valid_from,
            request.valid_to,
        ):
            raise ParameterConfigurationError(
                "CONFLICTING_ACTIVE_CONFIGURATION",
                "Existe una configuración incompatible en el intervalo solicitado",
            )

    def apply_change(self, request: ChangeRequest) -> Configuration:
        self.validate_change(request)
        # The repository operation must repeat the conflict check under the
        # write transaction to close the validate/write race window.
        return self._repository.apply_change_atomically(request)

    @staticmethod
    def _validate_scope(company_id: str) -> None:
        if not company_id or not company_id.strip():
            raise ParameterConfigurationError(
                "INVALID_COMPANY_SCOPE", "company_id no puede estar vacío"
            )

    def _validate_request_scope(self, request: ChangeRequest) -> None:
        self._validate_scope(request.company_id)
        if not request.actor or not request.actor.strip():
            raise ParameterConfigurationError(
                "UNAUTHORIZED_CHANGE", "actor no puede estar vacío"
            )
        if not request.reason or not request.reason.strip():
            raise ParameterConfigurationError(
                "INVALID_VALUE", "change_reason no puede estar vacío"
            )


__all__ = [
    "ChangeRequest",
    "Configuration",
    "ConfigurationAuthorization",
    "ConfigurationRepository",
    "HistoryEntry",
    "ParameterCatalogue",
    "ParameterConfigurationCenter",
    "ParameterConfigurationError",
    "ParameterDefinition",
]
