"""Provenance-safe UI slice for the EIOS Configuration Center.

This module is deliberately narrow.  It presents and coordinates an already
selected company/parameter/actor context and delegates all configuration
semantics to ``ParameterConfigurationCenter``.  It does not authenticate the
actor, enumerate companies or parameters, access persistence directly, or
make business decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from eios.parameters.center import (
    ChangeRequest,
    Configuration,
    ParameterConfigurationCenter,
    ParameterConfigurationError,
)


@dataclass(frozen=True)
class AuthorizedConfigurationUIContext:
    """Immutable carrier supplied by a trusted upstream integration boundary.

    The type is not an authenticator or credential.  Its provenance must be
    established outside this UI slice; the configuration center still performs
    the authoritative modification check.
    """

    company_id: str
    parameter_id: str
    actor: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("company_id", self.company_id),
            ("parameter_id", self.parameter_id),
            ("actor", self.actor),
        ):
            if not value or not value.strip():
                raise ValueError(f"{field_name} must not be blank")


@dataclass(frozen=True)
class ConfigurationDetailViewModel:
    company_id: str
    parameter_id: str
    actor: str
    value_type: str | None
    unit: str | None
    restricted: bool
    configuration: Configuration | None


@dataclass(frozen=True)
class ConfigurationHistoryItemViewModel:
    configuration_id: int
    parameter_id: str
    company_id: str
    previous_value: str | None
    new_value: str
    changed_by: str
    changed_at: datetime
    change_reason: str


@dataclass(frozen=True)
class ChangeProposal:
    value: str
    valid_from: datetime
    valid_to: datetime | None
    reason: str


@dataclass(frozen=True)
class ConfigurationUIResult:
    state: str
    error_code: str | None = None
    configuration: Configuration | None = None


class ConfigurationCenterUIController:
    """Coordinates one authorized configuration selection.

    Company, parameter and actor are bound to the immutable context.  Change
    proposals cannot replace them.  Functional validation and writes always go
    through ``ParameterConfigurationCenter``.
    """

    def __init__(
        self,
        center: ParameterConfigurationCenter,
        context: AuthorizedConfigurationUIContext,
    ) -> None:
        self._center = center
        self._context = context
        self._pending: ChangeProposal | None = None

    @property
    def context(self) -> AuthorizedConfigurationUIContext:
        return self._context

    @property
    def has_pending_confirmation(self) -> bool:
        return self._pending is not None

    def load_detail(self) -> ConfigurationDetailViewModel:
        definition = self._center.get_parameter(self._context.parameter_id)
        current = self._center.get_current_configuration(
            self._context.company_id, self._context.parameter_id
        )
        return ConfigurationDetailViewModel(
            company_id=self._context.company_id,
            parameter_id=definition.parameter_id,
            actor=self._context.actor,
            value_type=definition.value_type,
            unit=definition.unit,
            restricted=definition.restricted,
            configuration=current,
        )

    def load_history(self) -> tuple[ConfigurationHistoryItemViewModel, ...]:
        history = self._center.get_parameter_history(
            self._context.company_id, self._context.parameter_id
        )
        return tuple(
            ConfigurationHistoryItemViewModel(
                configuration_id=item.configuration_id,
                parameter_id=item.parameter_id,
                company_id=item.company_id,
                previous_value=item.previous_value,
                new_value=item.new_value,
                changed_by=item.changed_by,
                changed_at=item.changed_at,
                change_reason=item.change_reason,
            )
            for item in history
        )

    def prepare_change(
        self,
        *,
        value: str,
        valid_from: datetime,
        valid_to: datetime | None,
        reason: str,
    ) -> ConfigurationUIResult:
        proposal = ChangeProposal(
            value=value,
            valid_from=valid_from,
            valid_to=valid_to,
            reason=reason,
        )
        request = self._request_from(proposal)
        try:
            self._center.validate_change(request)
        except ParameterConfigurationError as exc:
            self._pending = None
            return ConfigurationUIResult(
                state=_state_for_error(exc.code), error_code=exc.code
            )
        self._pending = proposal
        return ConfigurationUIResult(state="AWAITING_CONFIRMATION")

    def cancel_pending_change(self) -> ConfigurationUIResult:
        self._pending = None
        return ConfigurationUIResult(state="VIEWING")

    def confirm_and_apply(self) -> ConfigurationUIResult:
        proposal = self._pending
        if proposal is None:
            return ConfigurationUIResult(state="ERROR", error_code="NO_PENDING_CHANGE")

        # Consume the pending proposal before any write attempt.  A failure must
        # require a new validation and a new explicit confirmation.
        self._pending = None
        request = self._request_from(proposal)
        try:
            # UI anti-stale revalidation.  apply_change() intentionally validates
            # again and the repository closes the validate/write race atomically.
            self._center.validate_change(request)
            configuration = self._center.apply_change(request)
        except ParameterConfigurationError as exc:
            return ConfigurationUIResult(
                state=_state_for_error(exc.code), error_code=exc.code
            )
        return ConfigurationUIResult(
            state="APPLIED", configuration=configuration
        )

    def _request_from(self, proposal: ChangeProposal) -> ChangeRequest:
        return ChangeRequest(
            company_id=self._context.company_id,
            parameter_id=self._context.parameter_id,
            value=proposal.value,
            valid_from=proposal.valid_from,
            valid_to=proposal.valid_to,
            actor=self._context.actor,
            reason=proposal.reason,
        )


def _state_for_error(code: str) -> str:
    if code in {"UNAUTHORIZED_CHANGE", "RESTRICTED_PARAMETER"}:
        return "FORBIDDEN"
    if code == "CONFLICTING_ACTIVE_CONFIGURATION":
        return "CONFLICT"
    if code in {
        "INVALID_VALUE",
        "INVALID_TYPE",
        "INVALID_VALIDITY",
        "INVALID_COMPANY_SCOPE",
        "PARAMETER_NOT_FOUND",
    }:
        return "VALIDATION_FAILED"
    return "ERROR"


__all__ = [
    "AuthorizedConfigurationUIContext",
    "ChangeProposal",
    "ConfigurationCenterUIController",
    "ConfigurationDetailViewModel",
    "ConfigurationHistoryItemViewModel",
    "ConfigurationUIResult",
]
