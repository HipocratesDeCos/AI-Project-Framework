"""CRC-MVP deterministic consolidation."""

from .engine import consolidate_crc
from .models import CRCConflict, CRCInput, CRCResult, CRCRuleMetadata

__all__ = ["CRCConflict", "CRCInput", "CRCResult", "CRCRuleMetadata", "consolidate_crc"]
