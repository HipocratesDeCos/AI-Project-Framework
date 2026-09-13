"""Selected-context workflow for the EIOS Configuration Center UI.

Slice 3 composes the closed Slice 1 controller with the closed Slice 2
presentation builder. It does not create authentication, company/parameter
selection, configuration semantics, persistence, or decision authority.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .configuration_center import (
    ChangeProposal,
    ConfigurationCenterUIController,
    ConfigurationDetailViewModel,
    ConfigurationHistoryItemViewModel,
)
from .configuration_center_components import (
    ConfigurationCenterScreen,
    ConfigurationChangeForm,
    build_configuration_center_screen,
)


class ConfigurationWorkflowError(RuntimeError):
    """Raised when Slice 3 internal state/preconditions are inconsistent."""


@dataclass(frozen=True)
class ConfigurationWorkflowSnapshot:
    screen: ConfigurationCenterScreen
    data_ready: bool
    history_stale: bool


class ConfigurationCenterSelectedWorkflow:
    """Orchestrate one already-selected Configuration Center context."""

    def __init__(self, controller: ConfigurationCenterUIController) -> None:
        self._controller = controller
        self._detail: ConfigurationDetailViewModel | None = None
        self._history: tuple[ConfigurationHistoryItemViewModel, ...] | None = None
        self._form: ConfigurationChangeForm | None = None
        self._proposal: ChangeProposal | None = None
        self._data_ready = False
        self._history_stale = False
        self._state = "READY"
        self._error_code: str | None = None

    @property
    def data_ready(self) -> bool:
        return self._data_ready

    @property
    def history_stale(self) -> bool:
        return self._history_stale

    @property
    def has_local_proposal(self) -> bool:
        return self._proposal is not None

    def snapshot(self) -> ConfigurationWorkflowSnapshot:
        return ConfigurationWorkflowSnapshot(
            screen=build_configuration_center_screen(
                detail=self._detail,
                history=self._history,
                form=self._form,
                proposal=self._proposal,
                state=self._state,
                error_code=self._error_code,
            ),
            data_ready=self._data_ready,
            history_stale=self._history_stale,
        )

    def refresh(self) -> ConfigurationWorkflowSnapshot:
        if self._controller.has_pending_confirmation:
            raise ConfigurationWorkflowError(
                "cannot refresh while confirmation is pending"
            )
        if self._form is not None:
            raise ConfigurationWorkflowError("cannot refresh while a draft is active")

        # A refresh replaces the previously demonstrated read snapshot. Never
        # leave old values visible as though they belonged to the new read.
        self._detail = None
        self._history = None
        self._data_ready = False
        self._history_stale = False
        self._proposal = None

        detail = self._controller.load_detail()
        if detail is None:
            self._state = self._controller.state
            self._error_code = self._controller.error_code
            return self.snapshot()

        self._detail = detail
        history = self._controller.load_history()
        if history is None:
            self._history = None
            self._state = self._controller.state
            self._error_code = self._controller.error_code
            return self.snapshot()

        self._history = history
        self._data_ready = True
        self._history_stale = False
        self._state = "VIEWING"
        self._error_code = None
        return self.snapshot()

    def edit(self, form: ConfigurationChangeForm) -> ConfigurationWorkflowSnapshot:
        self._require_ready()
        self._require_no_pending("cannot edit while confirmation is pending")
        self._form = form
        self._proposal = None
        self._state = "EDITING"
        self._error_code = None
        return self.snapshot()

    def prepare(self, form: ConfigurationChangeForm) -> ConfigurationWorkflowSnapshot:
        self._require_ready()
        self._require_no_pending("cannot prepare while confirmation is pending")

        proposal = ChangeProposal(
            value=form.value,
            valid_from=form.valid_from,
            valid_to=form.valid_to,
            reason=form.reason,
        )
        self._form = form
        self._proposal = None

        result = self._controller.prepare_change(
            value=form.value,
            valid_from=form.valid_from,
            valid_to=form.valid_to,
            reason=form.reason,
        )

        pending = self._controller.has_pending_confirmation
        if result.state == "AWAITING_CONFIRMATION":
            if not pending:
                raise ConfigurationWorkflowError(
                    "controller reported awaiting confirmation without pending change"
                )
            self._proposal = proposal
        elif pending:
            raise ConfigurationWorkflowError(
                "controller retained a hidden pending change"
            )

        self._state = result.state
        self._error_code = result.error_code
        return self.snapshot()

    def confirm(self) -> ConfigurationWorkflowSnapshot:
        if self._proposal is None or not self._controller.has_pending_confirmation:
            raise ConfigurationWorkflowError(
                "cannot confirm without coherent local and controller pending state"
            )

        previous_detail = self._detail
        previous_history = self._history
        result = self._controller.confirm_and_apply()
        self._proposal = None

        if self._controller.has_pending_confirmation:
            raise ConfigurationWorkflowError(
                "controller did not consume pending change after confirmation"
            )

        if result.state == "APPLIED":
            if result.configuration is None:
                raise ConfigurationWorkflowError(
                    "controller reported APPLIED without configuration"
                )
            if previous_detail is None:
                raise ConfigurationWorkflowError(
                    "APPLIED cannot update an absent detail snapshot"
                )
            if (
                result.configuration.company_id != previous_detail.company_id
                or result.configuration.parameter_id != previous_detail.parameter_id
            ):
                raise ConfigurationWorkflowError(
                    "APPLIED configuration does not match selected context"
                )
            self._detail = replace(
                previous_detail, configuration=result.configuration
            )
            self._history = previous_history
            self._form = None
            self._history_stale = True
            self._state = "APPLIED"
            self._error_code = None
            return self.snapshot()

        # A functional failure consumes confirmation but must not change the
        # previously read configuration/history. Keep the draft available so it
        # can be corrected and explicitly prepared again.
        self._detail = previous_detail
        self._history = previous_history
        self._state = result.state
        self._error_code = result.error_code
        return self.snapshot()

    def cancel(self) -> ConfigurationWorkflowSnapshot:
        if self._controller.has_pending_confirmation:
            self._controller.cancel_pending_change()
        if self._controller.has_pending_confirmation:
            raise ConfigurationWorkflowError(
                "controller did not consume pending change after cancellation"
            )

        self._proposal = None
        self._form = None
        self._error_code = None
        self._state = "VIEWING" if self._data_ready else "READY"
        return self.snapshot()

    def _require_ready(self) -> None:
        if not self._data_ready:
            raise ConfigurationWorkflowError(
                "configuration data must be loaded successfully first"
            )

    def _require_no_pending(self, message: str) -> None:
        if self._controller.has_pending_confirmation:
            raise ConfigurationWorkflowError(message)


__all__ = [
    "ConfigurationCenterSelectedWorkflow",
    "ConfigurationWorkflowError",
    "ConfigurationWorkflowSnapshot",
]
