"""EIOS parameter-configuration components and read-only public lookup."""

from .resolution import ResolvedConfiguration, resolve_configuration_for_context
from .company_resolution_api import (
    CompanyParameterLookup,
    ParameterLookupEntry,
    ParameterLookupError,
    configuration_evidence_source_ref,
    read_company_parameters_for_context,
)

__all__ = [
    "ResolvedConfiguration", "resolve_configuration_for_context",
    "CompanyParameterLookup", "ParameterLookupEntry", "ParameterLookupError",
    "configuration_evidence_source_ref", "read_company_parameters_for_context",
]

from .version_binding import (
    ParameterVersionBindingError,
    ParameterVersionManifest,
    ParameterVersionSource,
    VersionBoundParameterSelection,
    fingerprint_parameter_selection,
    fingerprint_historical_parameter_configurations,
    read_version_bound_parameter_selection,
)

__all__ += [
    "ParameterVersionBindingError", "ParameterVersionManifest",
    "ParameterVersionSource", "VersionBoundParameterSelection",
    "fingerprint_parameter_selection", "read_version_bound_parameter_selection",
]

# The local SQLite adapter is deliberately imported from its module, not here.
# Eager imports create a cycle with company_finance_parameters and app startup.
__all__ += ["fingerprint_historical_parameter_configurations"]
