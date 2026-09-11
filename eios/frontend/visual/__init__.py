"""U1.1 presentation layer plus isolated Vertical MVP presentation adapters."""

from .vertical_mvp_view_model import build_vertical_mvp_view_model
from .view_model import build_view_model

__all__ = ["build_vertical_mvp_view_model", "build_view_model"]
