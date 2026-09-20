"""U1.1 presentation layer plus isolated Vertical MVP presentation adapters."""

from .designated_synthetic_preview import (
    DesignatedSyntheticPreviewArtifact,
    DesignatedSyntheticPreviewDelivery,
    build_designated_synthetic_preview_artifact,
    build_designated_synthetic_preview_delivery,
)
from .vertical_mvp_artifact import (
    VerticalMVPReadOnlyArtifact,
    build_vertical_mvp_readonly_artifact,
)
from .vertical_mvp_delivery import (
    VerticalMVPReadOnlyDelivery,
    build_vertical_mvp_readonly_delivery,
)
from .synthetic_preview_admission import (
    LocalSyntheticPreviewAdmission,
    VerticalMVPSyntheticPreviewCase,
    build_local_synthetic_preview_admission,
    build_vertical_mvp_synthetic_preview_case,
)
from .vertical_mvp_renderer import render_vertical_mvp_readonly
from .vertical_mvp_view_model import build_vertical_mvp_view_model
from .view_model import build_view_model

__all__ = [
    "DesignatedSyntheticPreviewArtifact",
    "DesignatedSyntheticPreviewDelivery",
    "LocalSyntheticPreviewAdmission",
    "VerticalMVPReadOnlyArtifact",
    "VerticalMVPReadOnlyDelivery",
    "VerticalMVPSyntheticPreviewCase",
    "build_designated_synthetic_preview_artifact",
    "build_designated_synthetic_preview_delivery",
    "build_local_synthetic_preview_admission",
    "build_vertical_mvp_readonly_artifact",
    "build_vertical_mvp_readonly_delivery",
    "build_vertical_mvp_synthetic_preview_case",
    "build_vertical_mvp_view_model",
    "build_view_model",
    "render_vertical_mvp_readonly",
]
