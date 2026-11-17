"""External F6.2 synthetic company adapter. Not part of the EIOS kernel."""
from .adapter import (
    AdapterError, ExternalSourceScope, PreparedExternalCase,
    SyntheticEquipmentRecord, prepare_external_case,
)

__all__ = [
    "AdapterError", "ExternalSourceScope", "PreparedExternalCase",
    "SyntheticEquipmentRecord", "prepare_external_case",
]
