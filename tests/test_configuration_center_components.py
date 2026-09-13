from __future__ import annotations

from datetime import datetime, timezone

import pytest

from eios.frontend.visual.configuration_center import (
    ChangeProposal,
    ConfigurationDetailViewModel,
    ConfigurationHistoryItemViewModel,
)
from eios.frontend.visual.configuration_center_components import (
    ConfigurationChangeForm,
    build_configuration_center_screen,
)
from eios.parameters.center import Configuration


NOW = datetime(2026, 9, 13, 20, 0, tzinfo=timezone.utc)
LATER = datetime(2026, 10, 13, 20, 0, tzinfo=timezone.utc)


def _configuration() -> Configuration:
    return Configuration(
        configuration_id=7,
        parameter_id="P-001",
        company_id="COMP-1",
        value="10",
        value_type="integer",
        unit="days",
        valid_from=NOW,
        valid_to=None,
        created_at=NOW,
        updated_at=NOW,
    )


def _detail() -> ConfigurationDetailViewModel:
    return ConfigurationDetailViewModel(
        company_id="COMP-1",
        parameter_id="P-001",
        actor="actor-1",
        value_type="integer",
        unit="days",
        restricted=False,
        configuration=_configuration(),
    )


def _history() -> tuple[ConfigurationHistoryItemViewModel, ...]:
    return (
        ConfigurationHistoryItemViewModel(
            configuration_id=1,
            parameter_id="P-001",
            company_id="COMP-1",
            previous_value="8",
            new_value="9",
            changed_by="actor-a",
            changed_at=NOW,
            change_reason="first",
        ),
        ConfigurationHistoryItemViewModel(
            configuration_id=2,
            parameter_id="P-001",
            company_id="COMP-1",
            previous_value="9",
            new_value="10",
            changed_by="actor-b",
            changed_at=LATER,
            change_reason="second",
        ),
    )


def _form() -> ConfigurationChangeForm:
    return ConfigurationChangeForm(
        value="not-normalized-by-presentation",
        valid_from=NOW,
        valid_to=LATER,
        reason="  preserve presentation input  ",
    )


def _proposal() -> ChangeProposal:
    return ChangeProposal(
        value="12",
        valid_from=NOW,
        valid_to=LATER,
        reason="approved proposal",
    )


def test_screen_preserves_detail_identity_and_status_literally() -> None:
    detail = _detail()

    screen = build_configuration_center_screen(
        detail=detail,
        history=(),
        form=None,
        proposal=None,
        state="VIEWING",
        error_code="CUSTOM_VISIBLE_CODE",
    )

    assert screen.detail is not None
    assert screen.detail.detail is detail
    assert screen.status.state == "VIEWING"
    assert screen.status.error_code == "CUSTOM_VISIBLE_CODE"
    assert screen.confirmation is None


def test_history_preserves_order_and_empty_is_distinct_from_unavailable() -> None:
    history = _history()

    populated = build_configuration_center_screen(
        detail=_detail(),
        history=history,
        form=None,
        proposal=None,
        state="VIEWING",
        error_code=None,
    )
    empty = build_configuration_center_screen(
        detail=_detail(),
        history=(),
        form=None,
        proposal=None,
        state="VIEWING",
        error_code=None,
    )
    unavailable = build_configuration_center_screen(
        detail=None,
        history=None,
        form=None,
        proposal=None,
        state="ERROR",
        error_code="INVALID_COMPANY_SCOPE",
    )

    assert populated.history is not None
    assert populated.history.items is history
    assert [item.configuration_id for item in populated.history.items] == [1, 2]
    assert empty.history is not None
    assert empty.history.items == ()
    assert unavailable.history is None


def test_form_is_presentation_carrier_without_transformation() -> None:
    form = _form()

    screen = build_configuration_center_screen(
        detail=_detail(),
        history=(),
        form=form,
        proposal=None,
        state="EDITING",
        error_code=None,
    )

    assert screen.form is form
    assert screen.form.value == "not-normalized-by-presentation"
    assert screen.form.reason == "  preserve presentation input  "
    assert screen.confirmation is None


def test_confirmation_reuses_exact_detail_and_proposal() -> None:
    detail = _detail()
    proposal = _proposal()

    screen = build_configuration_center_screen(
        detail=detail,
        history=(),
        form=_form(),
        proposal=proposal,
        state="AWAITING_CONFIRMATION",
        error_code=None,
    )

    assert screen.confirmation is not None
    assert screen.confirmation.detail is detail
    assert screen.confirmation.proposal is proposal
    assert screen.confirmation.detail.company_id == "COMP-1"
    assert screen.confirmation.detail.parameter_id == "P-001"
    assert screen.confirmation.detail.actor == "actor-1"


def test_awaiting_confirmation_without_proposal_fails_closed() -> None:
    with pytest.raises(ValueError, match="proposal is required"):
        build_configuration_center_screen(
            detail=_detail(),
            history=(),
            form=_form(),
            proposal=None,
            state="AWAITING_CONFIRMATION",
            error_code=None,
        )


def test_awaiting_confirmation_without_detail_fails_closed() -> None:
    with pytest.raises(ValueError, match="detail is required"):
        build_configuration_center_screen(
            detail=None,
            history=(),
            form=_form(),
            proposal=_proposal(),
            state="AWAITING_CONFIRMATION",
            error_code=None,
        )


def test_proposal_in_non_confirmation_state_does_not_create_confirmation_panel() -> None:
    proposal = _proposal()

    screen = build_configuration_center_screen(
        detail=_detail(),
        history=(),
        form=_form(),
        proposal=proposal,
        state="EDITING",
        error_code=None,
    )

    assert screen.confirmation is None


def test_applied_state_is_only_represented_not_derived() -> None:
    screen = build_configuration_center_screen(
        detail=_detail(),
        history=(),
        form=None,
        proposal=None,
        state="APPLIED",
        error_code=None,
    )

    assert screen.status.state == "APPLIED"
    assert screen.confirmation is None
