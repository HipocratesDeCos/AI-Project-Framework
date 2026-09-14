"""Decision Twin public provenance integration quarantine.

The former public wrapper depended on the Scenario Stage 2 provenance-safe
completion boundary. That boundary is quarantined because it accepted a
caller-constructed ``ViabilityResult`` and therefore could prove contextual
consistency but not Viability Frontier producer provenance.

Decision Twin comparison mechanics remain available in their closed core
domain. EIOS must not expose a public Decision Twin integration that inherits
the quarantined Stage 2 provenance claim. Reopening this boundary requires a
provenance-safe Stage 2/VF producer path that can be audited end to end.
"""
from __future__ import annotations

# Intentional quarantine: no public provenance-safe Decision Twin integration
# symbols are exported while Scenario Stage 2 / VF producer provenance remains
# objectively blocked.
__all__: list[str] = []
