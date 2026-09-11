"""EIOS Stock & Demand Intelligence v0.1."""
from .engine import (
    build_current_stock_reference,
    build_identity,
    build_projected_stock_reference,
    build_projection_horizon,
    calculate_confirmed_demand_absorption,
    calculate_coverage,
    calculate_excess,
    calculate_historical_demand,
    calculate_stock_availability,
    calculate_stock_projection,
    use_authorized_forecast,
)
from .models import *  # noqa: F401,F403

__all__ = [
    "build_current_stock_reference",
    "build_identity",
    "build_projected_stock_reference",
    "build_projection_horizon",
    "calculate_confirmed_demand_absorption",
    "calculate_coverage",
    "calculate_excess",
    "calculate_historical_demand",
    "calculate_stock_availability",
    "calculate_stock_projection",
    "use_authorized_forecast",
]
