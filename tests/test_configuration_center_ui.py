from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from eios.frontend.visual.configuration_center import (
    AuthorizedConfigurationUIContext,
    ConfigurationCenterUIController,
)
from eios.parameters.center import (
    ChangeRequest,
    Configuration,
    HistoryEntry,
    ParameterConfigurationError,
    ParameterDefinition,
)


NOW = datetime(2026, 9, 13, 20, 0, tzinfo=timezone.utc)
LATER = datetime(2026, 10, 13, 20, 0, tzinfo=timezone.utc)


def _configuration(*, value: str = "10") -> Configuration:
    return Configuration(
        configuration_id=7,
        parameter_id="P-001",
        company_id="COMP-1",
        value=value,
        value_type="integer",
        unit="days",
        valid_from=NOW,
        valid_to=None,
        created_at=NOW,
        updated_at=NOW,
    )


class RecordingCenter:
    def __init__(self) -> None:
        self.definition = ParameterDefinition(
            parameter_id="P-001",
            value_type="integer",
            unit="days",
            restricted=False,
        )
        self.current = _configuration()
        self.history = (
            HistoryEntry(
                configuration_id=7,
                parameter_id="P-001",
                company_id="COMP-1",
                previous_value="8",
                new_value="10",
                changed_by="actor-1",
                changed_at=NOW,
                change_reason="approved change",
            ),
        )
        self.validate_calls: list[ChangeRequest] = []
        self.apply_calls: list[ChangeRequest] = []
        self.fail_on_validate_call: dict[int, ParameterConfigurationError] = {}
        self.apply_error: ParameterConfigurationError | None = None

    def get_parameter(self, parameter_id: str) -> ParameterDefinition:
        assert parameter_id == "P-001"
        return self.definition

    def get_current_configuration(
        self, company_id: str, parameter_id: str
    ) -> Configuration | None:
        assert (company_id, parameter_id) == ("COMP-1", "P-001")
        return self.current

    def get_parameter_history(
        self, company_id: str, parameter_id: str
    ) -> tuple[HistoryEntry, ...]:
        assert (company_id, parameter_id) == ("COMP-1", "P-001")
        return self.history

    def validate_change(self, request: ChangeRequest) -> None:
        self.validate_calls.append(request)
        call_no = len(self.validate_calls)
        if call_no in self.fail_on_validate_call:
            raise self.fail_on_validate_call[call_no]

    def apply_change(self, request: ChangeRequest) -> Configuration:
        self.apply_calls.append(request)
        if self.apply_error is not None:
            raise self.apply_error
        return replace(self.current, value=request.value, updated_at=NOW)


def _controller(center: RecordingCenter | None = None) -> tuple[ConfigurationCenterUIController, RecordingCenter]:
    recorded = center or RecordingCenter()
    context = AuthorizedConfigurationUIContext(
        company_id="COMP-1", parameter_id="P-001", actor="actor-1"
    )
    return ConfigurationCenterUIController(recorded, context), recorded


@pytest.mark.parametrize("field", ["company_id", "parameter_id", "actor"])
def test_context_rejects_blank_identity_fields(field: str) -> None:
    values = {"company_id": "COMP-1", "parameter_id": "P-001", "actor": "actor-1"}
    values[field] = "   "
    with pytest.raises(ValueError):
        AuthorizedConfigurationUIContext(**values)


def test_detail_preserves_authoritative_identity_type_unit_and_configuration() -> None:
    controller, center = _controller()

    detail = controller.load_detail()

    assert detail.company_id == "COMP-1"
    assert detail.parameter_id == "P-001"
    assert detail.actor == "actor-1"
    assert detail.value_type == "integer"
    assert detail.unit == "days"
    assert detail.restricted is False
    assert detail.configuration is center.current


def test_history_is_read_only_projection_of_backend_history() -> None:
    controller, _ = _controller()

    history = controller.load_history()

    assert len(history) == 1
    item = history[0]
    assert item.company_id == "COMP-1"
    assert item.parameter_id == "P-001"
    assert item.previous_value == "8"
    assert item.new_value == "10"
    assert item.changed_by == "actor-1"
    assert item.change_reason == "approved change"


def test_failed_initial_validation_never_creates_pending_confirmation() -> None:
    center = RecordingCenter()
    center.fail_on_validate_call[1] = ParameterConfigurationError(
        "INVALID_VALUE", "invalid"
    )
    controller, _ = _controller(center)

    result = controller.prepare_change(
        value="bad", valid_from=NOW, valid_to=LATER, reason="test"
    )

    assert result.state == "VALIDATION_FAILED"
    assert result.error_code == "INVALID_VALUE"
    assert controller.has_pending_confirmation is False
    assert center.apply_calls == []


def test_apply_without_pending_confirmation_fails_closed() -> None:
    controller, center = _controller()

    result = controller.confirm_and_apply()

    assert result.state == "ERROR"
    assert result.error_code == "NO_PENDING_CHANGE"
    assert center.validate_calls == []
    assert center.apply_calls == []


def test_confirm_revalidates_and_binds_request_to_immutable_context() -> None:
    controller, center = _controller()

    prepared = controller.prepare_change(
        value="12", valid_from=NOW, valid_to=LATER, reason="business-approved"
    )
    applied = controller.confirm_and_apply()

    assert prepared.state == "AWAITING_CONFIRMATION"
    assert applied.state == "APPLIED"
    assert len(center.validate_calls) == 2
    assert len(center.apply_calls) == 1
    for request in (*center.validate_calls, *center.apply_calls):
        assert request.company_id == "COMP-1"
        assert request.parameter_id == "P-001"
        assert request.actor == "actor-1"
        assert request.value == "12"
        assert request.reason == "business-approved"
    assert applied.configuration is not None
    assert applied.configuration.value == "12"
    assert controller.has_pending_confirmation is False


def test_revoked_authorization_between_validation_and_confirmation_blocks_write() -> None:
    center = RecordingCenter()
    center.fail_on_validate_call[2] = ParameterConfigurationError(
        "UNAUTHORIZED_CHANGE", "revoked"
    )
    controller, _ = _controller(center)

    assert controller.prepare_change(
        value="12", valid_from=NOW, valid_to=LATER, reason="test"
    ).state == "AWAITING_CONFIRMATION"

    result = controller.confirm_and_apply()

    assert result.state == "FORBIDDEN"
    assert result.error_code == "UNAUTHORIZED_CHANGE"
    assert center.apply_calls == []
    assert controller.has_pending_confirmation is False


def test_conflict_appearing_before_confirmation_blocks_write() -> None:
    center = RecordingCenter()
    center.fail_on_validate_call[2] = ParameterConfigurationError(
        "CONFLICTING_ACTIVE_CONFIGURATION", "conflict"
    )
    controller, _ = _controller(center)

    controller.prepare_change(
        value="12", valid_from=NOW, valid_to=LATER, reason="test"
    )
    result = controller.confirm_and_apply()

    assert result.state == "CONFLICT"
    assert result.error_code == "CONFLICTING_ACTIVE_CONFIGURATION"
    assert center.apply_calls == []


def test_apply_error_never_becomes_applied() -> None:
    center = RecordingCenter()
    center.apply_error = ParameterConfigurationError(
        "CONFLICTING_ACTIVE_CONFIGURATION", "atomic conflict"
    )
    controller, _ = _controller(center)

    controller.prepare_change(
        value="12", valid_from=NOW, valid_to=LATER, reason="test"
    )
    result = controller.confirm_and_apply()

    assert result.state == "CONFLICT"
    assert result.error_code == "CONFLICTING_ACTIVE_CONFIGURATION"
    assert result.configuration is None
    assert controller.has_pending_confirmation is False


def test_cancel_consumes_pending_proposal_and_prevents_apply() -> None:
    controller, center = _controller()
    controller.prepare_change(
        value="12", valid_from=NOW, valid_to=LATER, reason="test"
    )

    cancelled = controller.cancel_pending_change()
    result = controller.confirm_and_apply()

    assert cancelled.state == "VIEWING"
    assert result.error_code == "NO_PENDING_CHANGE"
    assert center.apply_calls == []
