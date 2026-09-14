from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from eios.frontend.visual.configuration_center import (
    ConfigurationDetailViewModel,
    ConfigurationHistoryItemViewModel,
    ConfigurationUIResult,
)
from eios.frontend.visual.configuration_center_components import ConfigurationChangeForm
from eios.frontend.visual.configuration_center_workflow import (
    ConfigurationCenterSelectedWorkflow,
    ConfigurationWorkflowError,
)
from eios.parameters.center import Configuration


NOW = datetime(2026, 9, 13, 20, 0, tzinfo=timezone.utc)
LATER = datetime(2026, 10, 13, 20, 0, tzinfo=timezone.utc)


def _configuration(*, value: str = "10", company_id: str = "COMP-1", parameter_id: str = "P-001") -> Configuration:
    return Configuration(
        configuration_id=7,
        parameter_id=parameter_id,
        company_id=company_id,
        value=value,
        value_type="integer",
        unit="days",
        valid_from=NOW,
        valid_to=None,
        created_at=NOW,
        updated_at=NOW,
    )


def _detail(*, configuration: Configuration | None = None) -> ConfigurationDetailViewModel:
    return ConfigurationDetailViewModel(
        company_id="COMP-1",
        parameter_id="P-001",
        actor="actor-1",
        value_type="integer",
        unit="days",
        restricted=False,
        configuration=configuration or _configuration(),
    )


def _history(value: str = "10") -> tuple[ConfigurationHistoryItemViewModel, ...]:
    return (
        ConfigurationHistoryItemViewModel(
            configuration_id=7,
            parameter_id="P-001",
            company_id="COMP-1",
            previous_value="9",
            new_value=value,
            changed_by="actor-1",
            changed_at=NOW,
            change_reason="approved",
        ),
    )


def _form(value: str = "12") -> ConfigurationChangeForm:
    return ConfigurationChangeForm(
        value=value,
        valid_from=NOW,
        valid_to=LATER,
        reason="business-approved",
    )


class ScriptedController:
    def __init__(self) -> None:
        self.state = "READY"
        self.error_code: str | None = None
        self.has_pending_confirmation = False
        self.detail: ConfigurationDetailViewModel | None = _detail()
        self.history: tuple[ConfigurationHistoryItemViewModel, ...] | None = _history()
        self.prepare_result = ConfigurationUIResult(state="AWAITING_CONFIRMATION")
        self.prepare_sets_pending = True
        self.confirm_result = ConfigurationUIResult(
            state="APPLIED", configuration=_configuration(value="12")
        )
        self.confirm_consumes_pending = True
        self.cancel_consumes_pending = True
        self.load_detail_calls = 0
        self.load_history_calls = 0
        self.prepare_calls: list[dict[str, object]] = []
        self.confirm_calls = 0
        self.cancel_calls = 0

    def load_detail(self) -> ConfigurationDetailViewModel | None:
        self.load_detail_calls += 1
        if self.detail is None:
            self.state = "ERROR"
            self.error_code = "PARAMETER_NOT_FOUND"
            return None
        self.state = "VIEWING"
        self.error_code = None
        return self.detail

    def load_history(self) -> tuple[ConfigurationHistoryItemViewModel, ...] | None:
        self.load_history_calls += 1
        if self.history is None:
            self.state = "ERROR"
            self.error_code = "INVALID_COMPANY_SCOPE"
            return None
        self.state = "VIEWING"
        self.error_code = None
        return self.history

    def prepare_change(self, **kwargs: object) -> ConfigurationUIResult:
        self.prepare_calls.append(kwargs)
        self.has_pending_confirmation = self.prepare_sets_pending
        self.state = self.prepare_result.state
        self.error_code = self.prepare_result.error_code
        return self.prepare_result

    def confirm_and_apply(self) -> ConfigurationUIResult:
        self.confirm_calls += 1
        if self.confirm_consumes_pending:
            self.has_pending_confirmation = False
        self.state = self.confirm_result.state
        self.error_code = self.confirm_result.error_code
        return self.confirm_result

    def cancel_pending_change(self) -> ConfigurationUIResult:
        self.cancel_calls += 1
        if self.cancel_consumes_pending:
            self.has_pending_confirmation = False
        self.state = "VIEWING"
        self.error_code = None
        return ConfigurationUIResult(state="VIEWING")


def _loaded_workflow(controller: ScriptedController | None = None) -> tuple[ConfigurationCenterSelectedWorkflow, ScriptedController]:
    scripted = controller or ScriptedController()
    workflow = ConfigurationCenterSelectedWorkflow(scripted)  # type: ignore[arg-type]
    workflow.refresh()
    return workflow, scripted


def test_refresh_loads_detail_and_history_and_marks_data_ready() -> None:
    controller = ScriptedController()
    workflow = ConfigurationCenterSelectedWorkflow(controller)  # type: ignore[arg-type]

    snapshot = workflow.refresh()

    assert snapshot.data_ready is True
    assert snapshot.history_stale is False
    assert snapshot.screen.detail is not None
    assert snapshot.screen.history is not None
    assert snapshot.screen.status.state == "VIEWING"
    assert controller.load_detail_calls == 1
    assert controller.load_history_calls == 1


def test_detail_failure_invalidates_snapshot_and_skips_history() -> None:
    workflow, controller = _loaded_workflow()
    controller.detail = None

    snapshot = workflow.refresh()

    assert snapshot.data_ready is False
    assert snapshot.screen.detail is None
    assert snapshot.screen.history is None
    assert snapshot.screen.status.state == "ERROR"
    assert snapshot.screen.status.error_code == "PARAMETER_NOT_FOUND"
    assert controller.load_history_calls == 1  # only the initial successful load


def test_history_failure_keeps_new_detail_but_invalidates_old_history() -> None:
    workflow, controller = _loaded_workflow()
    new_detail = _detail(configuration=_configuration(value="11"))
    controller.detail = new_detail
    controller.history = None

    snapshot = workflow.refresh()

    assert snapshot.data_ready is False
    assert snapshot.screen.detail is not None
    assert snapshot.screen.detail.detail is new_detail
    assert snapshot.screen.history is None
    assert snapshot.screen.status.error_code == "INVALID_COMPANY_SCOPE"


def test_empty_history_is_valid_loaded_data() -> None:
    controller = ScriptedController()
    controller.history = ()
    workflow = ConfigurationCenterSelectedWorkflow(controller)  # type: ignore[arg-type]

    snapshot = workflow.refresh()

    assert snapshot.data_ready is True
    assert snapshot.screen.history is not None
    assert snapshot.screen.history.items == ()


def test_edit_is_local_only_and_refresh_requires_explicit_cancel() -> None:
    workflow, controller = _loaded_workflow()
    form = _form()

    edited = workflow.edit(form)

    assert edited.screen.form is form
    assert edited.screen.status.state == "EDITING"
    assert controller.prepare_calls == []
    with pytest.raises(ConfigurationWorkflowError, match="draft"):
        workflow.refresh()

    cancelled = workflow.cancel()
    assert cancelled.screen.form is None
    assert cancelled.screen.status.state == "VIEWING"


def test_edit_and_prepare_are_blocked_if_controller_has_pending() -> None:
    workflow, controller = _loaded_workflow()
    controller.has_pending_confirmation = True

    with pytest.raises(ConfigurationWorkflowError, match="edit"):
        workflow.edit(_form())
    with pytest.raises(ConfigurationWorkflowError, match="prepare"):
        workflow.prepare(_form())


def test_prepare_retains_exact_proposal_only_with_coherent_pending() -> None:
    workflow, controller = _loaded_workflow()
    form = _form("14")

    snapshot = workflow.prepare(form)

    assert snapshot.screen.status.state == "AWAITING_CONFIRMATION"
    assert snapshot.screen.confirmation is not None
    assert snapshot.screen.confirmation.proposal.value == "14"
    assert snapshot.screen.confirmation.proposal.reason == form.reason
    assert workflow.has_local_proposal is True
    assert controller.has_pending_confirmation is True
    assert controller.prepare_calls == [
        {
            "value": form.value,
            "valid_from": form.valid_from,
            "valid_to": form.valid_to,
            "reason": form.reason,
        }
    ]


def test_prepare_awaiting_without_controller_pending_fails_closed() -> None:
    workflow, controller = _loaded_workflow()
    controller.prepare_sets_pending = False

    with pytest.raises(ConfigurationWorkflowError, match="without pending"):
        workflow.prepare(_form())

    assert workflow.has_local_proposal is False


def test_prepare_failure_with_hidden_pending_fails_closed() -> None:
    workflow, controller = _loaded_workflow()
    controller.prepare_result = ConfigurationUIResult(
        state="VALIDATION_FAILED", error_code="INVALID_VALUE"
    )
    controller.prepare_sets_pending = True

    with pytest.raises(ConfigurationWorkflowError, match="hidden pending"):
        workflow.prepare(_form())


def test_prepare_functional_failure_keeps_draft_without_confirmation() -> None:
    workflow, controller = _loaded_workflow()
    controller.prepare_result = ConfigurationUIResult(
        state="VALIDATION_FAILED", error_code="INVALID_VALUE"
    )
    controller.prepare_sets_pending = False
    form = _form("bad")

    snapshot = workflow.prepare(form)

    assert snapshot.screen.form is form
    assert snapshot.screen.confirmation is None
    assert snapshot.screen.status.state == "VALIDATION_FAILED"
    assert snapshot.screen.status.error_code == "INVALID_VALUE"
    assert workflow.has_local_proposal is False


def test_refresh_during_pending_fails_without_mutating_pending_or_snapshot() -> None:
    workflow, controller = _loaded_workflow()
    before = workflow.prepare(_form())

    with pytest.raises(ConfigurationWorkflowError, match="pending"):
        workflow.refresh()

    after = workflow.snapshot()
    assert controller.has_pending_confirmation is True
    assert after.screen.confirmation == before.screen.confirmation
    assert after.screen.status.state == "AWAITING_CONFIRMATION"


def test_cancel_consumes_controller_pending_and_local_draft() -> None:
    workflow, controller = _loaded_workflow()
    workflow.prepare(_form())

    snapshot = workflow.cancel()

    assert controller.cancel_calls == 1
    assert controller.has_pending_confirmation is False
    assert workflow.has_local_proposal is False
    assert snapshot.screen.form is None
    assert snapshot.screen.confirmation is None
    assert snapshot.screen.status.state == "VIEWING"


def test_cancel_fails_if_controller_does_not_consume_pending() -> None:
    workflow, controller = _loaded_workflow()
    workflow.prepare(_form())
    controller.cancel_consumes_pending = False

    with pytest.raises(ConfigurationWorkflowError, match="did not consume"):
        workflow.cancel()


def test_confirm_applied_updates_only_detail_and_marks_history_stale() -> None:
    workflow, controller = _loaded_workflow()
    initial = workflow.snapshot()
    assert initial.screen.history is not None
    original_history = initial.screen.history.items
    applied = _configuration(value="15")
    controller.confirm_result = ConfigurationUIResult(
        state="APPLIED", configuration=applied
    )
    workflow.prepare(_form("15"))

    snapshot = workflow.confirm()

    assert controller.confirm_calls == 1
    assert controller.has_pending_confirmation is False
    assert snapshot.screen.detail is not None
    assert snapshot.screen.detail.detail.configuration is applied
    assert snapshot.screen.history is not None
    assert snapshot.screen.history.items is original_history
    assert snapshot.history_stale is True
    assert snapshot.screen.status.state == "APPLIED"
    assert snapshot.screen.form is None
    assert snapshot.screen.confirmation is None


def test_applied_without_configuration_fails_closed() -> None:
    workflow, controller = _loaded_workflow()
    controller.confirm_result = ConfigurationUIResult(state="APPLIED")
    workflow.prepare(_form())

    with pytest.raises(ConfigurationWorkflowError, match="without configuration"):
        workflow.confirm()


def test_applied_configuration_for_other_context_is_rejected() -> None:
    workflow, controller = _loaded_workflow()
    controller.confirm_result = ConfigurationUIResult(
        state="APPLIED",
        configuration=_configuration(value="12", company_id="OTHER"),
    )
    workflow.prepare(_form())

    with pytest.raises(ConfigurationWorkflowError, match="does not match"):
        workflow.confirm()


def test_confirm_fails_if_controller_keeps_pending() -> None:
    workflow, controller = _loaded_workflow()
    controller.confirm_consumes_pending = False
    workflow.prepare(_form())

    with pytest.raises(ConfigurationWorkflowError, match="did not consume"):
        workflow.confirm()


def test_confirm_functional_failure_preserves_data_and_draft_but_consumes_proposal() -> None:
    workflow, controller = _loaded_workflow()
    before = workflow.snapshot()
    form = _form("13")
    controller.confirm_result = ConfigurationUIResult(
        state="CONFLICT", error_code="CONFLICTING_ACTIVE_CONFIGURATION"
    )
    workflow.prepare(form)

    snapshot = workflow.confirm()

    assert snapshot.screen.detail == before.screen.detail
    assert snapshot.screen.history == before.screen.history
    assert snapshot.screen.form is form
    assert snapshot.screen.confirmation is None
    assert snapshot.screen.status.state == "CONFLICT"
    assert workflow.has_local_proposal is False
    assert controller.has_pending_confirmation is False


def test_refresh_after_applied_reloads_history_and_clears_stale() -> None:
    workflow, controller = _loaded_workflow()
    applied = _configuration(value="16")
    controller.confirm_result = ConfigurationUIResult(
        state="APPLIED", configuration=applied
    )
    workflow.prepare(_form("16"))
    applied_snapshot = workflow.confirm()
    assert applied_snapshot.history_stale is True

    controller.detail = _detail(configuration=applied)
    controller.history = _history("16")
    refreshed = workflow.refresh()

    assert refreshed.history_stale is False
    assert refreshed.data_ready is True
    assert refreshed.screen.status.state == "VIEWING"
    assert refreshed.screen.detail is not None
    assert refreshed.screen.detail.detail.configuration is applied
    assert refreshed.screen.history is not None
    assert refreshed.screen.history.items[0].new_value == "16"


def test_edit_and_prepare_require_successful_refresh() -> None:
    controller = ScriptedController()
    workflow = ConfigurationCenterSelectedWorkflow(controller)  # type: ignore[arg-type]

    with pytest.raises(ConfigurationWorkflowError, match="loaded successfully"):
        workflow.edit(_form())
    with pytest.raises(ConfigurationWorkflowError, match="loaded successfully"):
        workflow.prepare(_form())
