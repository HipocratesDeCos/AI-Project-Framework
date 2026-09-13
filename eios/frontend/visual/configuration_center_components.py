"""Pure presentation components for Configuration Center UI Slice 2.

The module composes values already produced by authorized layers. It does not
call services, engines, repositories, catalogues, authorization providers, or
persistence.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .configuration_center import (
    ChangeProposal,
    ConfigurationDetailViewModel,
    ConfigurationHistoryItemViewModel,
)


@dataclass(frozen=True)
class ConfigurationDetailPanel:
    detail: ConfigurationDetailViewModel


@dataclass(frozen=True)
class ConfigurationHistoryPanel:
    items: tuple[ConfigurationHistoryItemViewModel, ...]


@dataclass(frozen=True)
class ConfigurationChangeForm:
    value: str
    valid_from: datetime
    valid_to: datetime | None
    reason: str


@dataclass(frozen=True)
class ConfigurationConfirmationPanel:
    detail: ConfigurationDetailViewModel
    proposal: ChangeProposal


@dataclass(frozen=True)
class ConfigurationStatusPanel:
    state: str
    error_code: str | None


@dataclass(frozen=True)
class ConfigurationCenterScreen:
    detail: ConfigurationDetailPanel | None
    history: ConfigurationHistoryPanel | None
    form: ConfigurationChangeForm | None
    confirmation: ConfigurationConfirmationPanel | None
    status: ConfigurationStatusPanel


def build_configuration_center_screen(
    *,
    detail: ConfigurationDetailViewModel | None,
    history: tuple[ConfigurationHistoryItemViewModel, ...] | None,
    form: ConfigurationChangeForm | None,
    proposal: ChangeProposal | None,
    state: str,
    error_code: str | None,
) -> ConfigurationCenterScreen:
    """Compose a Configuration Center screen without deriving domain facts.

    ``None`` history is preserved as unavailable; an empty tuple is preserved
    as a successful query with no entries. A confirmation panel is constructed
    only for the explicit ``AWAITING_CONFIRMATION`` state.
    """

    confirmation: ConfigurationConfirmationPanel | None = None
    if state == "AWAITING_CONFIRMATION":
        if detail is None:
            raise ValueError("detail is required while awaiting confirmation")
        if proposal is None:
            raise ValueError("proposal is required while awaiting confirmation")
        confirmation = ConfigurationConfirmationPanel(
            detail=detail,
            proposal=proposal,
        )

    return ConfigurationCenterScreen(
        detail=ConfigurationDetailPanel(detail) if detail is not None else None,
        history=(
            ConfigurationHistoryPanel(items=history) if history is not None else None
        ),
        form=form,
        confirmation=confirmation,
        status=ConfigurationStatusPanel(state=state, error_code=error_code),
    )


__all__ = [
    "ConfigurationCenterScreen",
    "ConfigurationChangeForm",
    "ConfigurationConfirmationPanel",
    "ConfigurationDetailPanel",
    "ConfigurationHistoryPanel",
    "ConfigurationStatusPanel",
    "build_configuration_center_screen",
]
