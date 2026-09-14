from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

from eios.frontend.application_boundary import (
    FrontendBoundaryError,
    present_configuration_center_snapshot,
)
from eios.frontend.visual.configuration_center import (
    ChangeProposal,
    ConfigurationDetailViewModel,
    ConfigurationHistoryItemViewModel,
)
from eios.frontend.visual.configuration_center_components import (
    ConfigurationChangeForm,
    build_configuration_center_screen,
)
from eios.frontend.visual.configuration_center_workflow import (
    ConfigurationWorkflowSnapshot,
)
from eios.parameters.center import Configuration


TZ = timezone(timedelta(hours=2))
NOW = datetime(2026, 9, 14, 8, 30, 15, 123456, tzinfo=TZ)
LATER = datetime(2026, 10, 14, 8, 30, 15, 123456, tzinfo=TZ)


def _configuration(value: str = "10") -> Configuration:
    return Configuration(
        configuration_id=7,
        parameter_id="P-001",
        company_id="COMP-1",
        value=value,
        value_type="integer",
        unit="days",
        valid_from=NOW,
        valid_to=LATER,
        created_at=NOW,
        updated_at=LATER,
    )


def _detail(value: str = "10") -> ConfigurationDetailViewModel:
    return ConfigurationDetailViewModel(
        company_id="COMP-1",
        parameter_id="P-001",
        actor="actor-1",
        value_type="integer",
        unit="days",
        restricted=False,
        configuration=_configuration(value),
    )


def _history() -> tuple[ConfigurationHistoryItemViewModel, ...]:
    return (
        ConfigurationHistoryItemViewModel(
            configuration_id=1,
            parameter_id="P-001",
            company_id="COMP-1",
            previous_value=None,
            new_value="8",
            changed_by="actor-a",
            changed_at=NOW,
            change_reason="initial",
        ),
        ConfigurationHistoryItemViewModel(
            configuration_id=2,
            parameter_id="P-001",
            company_id="COMP-1",
            previous_value="8",
            new_value="10",
            changed_by="actor-b",
            changed_at=LATER,
            change_reason="second",
        ),
    )


def test_rejects_non_snapshot_input() -> None:
    with pytest.raises(FrontendBoundaryError, match="snapshot de Configuration Center"):
        present_configuration_center_snapshot({})  # type: ignore[arg-type]


def test_ready_snapshot_preserves_absence_as_null() -> None:
    screen = build_configuration_center_screen(
        detail=None,
        history=None,
        form=None,
        proposal=None,
        state="READY",
        error_code=None,
    )
    snapshot = ConfigurationWorkflowSnapshot(
        screen=screen,
        data_ready=False,
        history_stale=False,
    )

    payload = present_configuration_center_snapshot(snapshot)

    assert payload == {
        "data_ready": False,
        "history_stale": False,
        "status": {"state": "READY", "error_code": None},
        "detail": None,
        "history": None,
        "form": None,
        "confirmation": None,
    }
    json.dumps(payload)


def test_empty_history_is_empty_list_not_null() -> None:
    screen = build_configuration_center_screen(
        detail=_detail(),
        history=(),
        form=None,
        proposal=None,
        state="VIEWING",
        error_code=None,
    )
    snapshot = ConfigurationWorkflowSnapshot(
        screen=screen,
        data_ready=True,
        history_stale=False,
    )

    payload = present_configuration_center_snapshot(snapshot)

    assert payload["history"] == []
    assert payload["detail"] is not None


def test_detail_configuration_and_datetimes_are_projected_exactly() -> None:
    screen = build_configuration_center_screen(
        detail=_detail(),
        history=(),
        form=None,
        proposal=None,
        state="VIEWING",
        error_code=None,
    )
    snapshot = ConfigurationWorkflowSnapshot(screen, True, False)

    payload = present_configuration_center_snapshot(snapshot)
    detail = payload["detail"]
    assert isinstance(detail, dict)
    assert detail == {
        "company_id": "COMP-1",
        "parameter_id": "P-001",
        "actor": "actor-1",
        "value_type": "integer",
        "unit": "days",
        "restricted": False,
        "configuration": {
            "configuration_id": 7,
            "parameter_id": "P-001",
            "company_id": "COMP-1",
            "value": "10",
            "value_type": "integer",
            "unit": "days",
            "valid_from": NOW.isoformat(),
            "valid_to": LATER.isoformat(),
            "created_at": NOW.isoformat(),
            "updated_at": LATER.isoformat(),
        },
    }
    assert detail["configuration"]["valid_from"] == "2026-09-14T08:30:15.123456+02:00"
    json.dumps(payload)


def test_history_preserves_order_fields_and_none_previous_value() -> None:
    history = _history()
    screen = build_configuration_center_screen(
        detail=_detail(),
        history=history,
        form=None,
        proposal=None,
        state="VIEWING",
        error_code=None,
    )
    snapshot = ConfigurationWorkflowSnapshot(screen, True, False)

    payload = present_configuration_center_snapshot(snapshot)
    items = payload["history"]

    assert isinstance(items, list)
    assert [item["configuration_id"] for item in items] == [1, 2]
    assert items[0] == {
        "configuration_id": 1,
        "parameter_id": "P-001",
        "company_id": "COMP-1",
        "previous_value": None,
        "new_value": "8",
        "changed_by": "actor-a",
        "changed_at": NOW.isoformat(),
        "change_reason": "initial",
    }
    assert items[1]["changed_at"] == LATER.isoformat()


def test_form_is_projected_without_text_normalization() -> None:
    form = ConfigurationChangeForm(
        value="  raw-value  ",
        valid_from=NOW,
        valid_to=None,
        reason="  preserve reason  ",
    )
    screen = build_configuration_center_screen(
        detail=_detail(),
        history=(),
        form=form,
        proposal=None,
        state="EDITING",
        error_code=None,
    )
    snapshot = ConfigurationWorkflowSnapshot(screen, True, False)

    payload = present_configuration_center_snapshot(snapshot)

    assert payload["form"] == {
        "value": "  raw-value  ",
        "valid_from": NOW.isoformat(),
        "valid_to": None,
        "reason": "  preserve reason  ",
    }
    assert payload["confirmation"] is None


def test_confirmation_projects_its_own_detail_and_proposal_literally() -> None:
    detail = _detail()
    proposal = ChangeProposal(
        value="12",
        valid_from=NOW,
        valid_to=LATER,
        reason="approved candidate",
    )
    form = ConfigurationChangeForm(
        value="12",
        valid_from=NOW,
        valid_to=LATER,
        reason="approved candidate",
    )
    screen = build_configuration_center_screen(
        detail=detail,
        history=(),
        form=form,
        proposal=proposal,
        state="AWAITING_CONFIRMATION",
        error_code=None,
    )
    snapshot = ConfigurationWorkflowSnapshot(screen, True, False)

    payload = present_configuration_center_snapshot(snapshot)
    confirmation = payload["confirmation"]

    assert isinstance(confirmation, dict)
    assert confirmation["detail"]["company_id"] == "COMP-1"
    assert confirmation["detail"]["parameter_id"] == "P-001"
    assert confirmation["proposal"] == {
        "value": "12",
        "valid_from": NOW.isoformat(),
        "valid_to": LATER.isoformat(),
        "reason": "approved candidate",
    }
    json.dumps(payload)


def test_status_error_and_history_stale_are_preserved_literally() -> None:
    screen = build_configuration_center_screen(
        detail=_detail("12"),
        history=_history(),
        form=None,
        proposal=None,
        state="APPLIED",
        error_code="CUSTOM_CODE",
    )
    snapshot = ConfigurationWorkflowSnapshot(
        screen=screen,
        data_ready=True,
        history_stale=True,
    )

    payload = present_configuration_center_snapshot(snapshot)

    assert payload["data_ready"] is True
    assert payload["history_stale"] is True
    assert payload["status"] == {
        "state": "APPLIED",
        "error_code": "CUSTOM_CODE",
    }


def test_complete_payload_is_json_serializable() -> None:
    proposal = ChangeProposal("12", NOW, LATER, "reason")
    form = ConfigurationChangeForm("12", NOW, LATER, "reason")
    screen = build_configuration_center_screen(
        detail=_detail(),
        history=_history(),
        form=form,
        proposal=proposal,
        state="AWAITING_CONFIRMATION",
        error_code=None,
    )
    snapshot = ConfigurationWorkflowSnapshot(screen, True, False)

    encoded = json.dumps(present_configuration_center_snapshot(snapshot))

    assert '"AWAITING_CONFIRMATION"' in encoded
    assert NOW.isoformat() in encoded
