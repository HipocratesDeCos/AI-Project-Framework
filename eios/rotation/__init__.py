"""Rotation Track A factual carrier and provenance validation."""
from .models import SalesActivityState, SalesActivityWindowEvidence
from .producer import produce_sales_activity_window_evidence
from .source_models import (
    CoverageState,
    ROT002_MVP_EXCEPTION_TYPES,
    RotationExceptionDetermination,
    RotationExceptionEvidence,
    RotationExceptionState,
    RotationExceptionType,
    SalesActivitySourceEvidence,
)
from .track_b import (
    P_ROT_002,
    P_ROT_003,
    R_ROT_001,
    RotationMetricProvenanceError,
    build_rotation_metric_evidence,
    evaluate_r_rot_001,
)
from .track_b_models import (
    ROTATION_METRIC_UNIT,
    RotationMetricEvidence,
    RotationMetricSourceEvidence,
)
from .provenance import (
    P_ROT_001,
    P_ROT_001_UNIT,
    SalesActivityWindowProvenanceError,
    validate_sales_activity_window_evidence,
)

__all__ = [
    "P_ROT_001",
    "P_ROT_001_UNIT",
    "P_ROT_002",
    "P_ROT_003",
    "R_ROT_001",
    "ROTATION_METRIC_UNIT",
    "CoverageState",
    "ROT002_MVP_EXCEPTION_TYPES",
    "RotationExceptionDetermination",
    "RotationExceptionEvidence",
    "RotationExceptionState",
    "RotationExceptionType",
    "RotationMetricEvidence",
    "RotationMetricProvenanceError",
    "RotationMetricSourceEvidence",
    "SalesActivitySourceEvidence",
    "SalesActivityState",
    "SalesActivityWindowEvidence",
    "SalesActivityWindowProvenanceError",
    "build_rotation_metric_evidence",
    "evaluate_r_rot_001",
    "produce_sales_activity_window_evidence",
    "validate_sales_activity_window_evidence",
]
