"""F6.5 independent synthetic provider onboarding (no real trust)."""
from .onboarding import (
    OnboardingError, ProviderRegistration, OnboardingSnapshot,
    PinnedOnboarding, ProviderEndpoint, OnboardingReceipt,
    fingerprint_provider_snapshot, review_with_onboarded_providers,
)
from .pilot import (
    REQUIREMENTS, RehearsalChecklistItem, RehearsalManifest,
    PilotReadinessError, PilotRehearsalResult, assess_read_only_rehearsal,
)

__all__ = (
    "OnboardingError", "ProviderRegistration", "OnboardingSnapshot",
    "PinnedOnboarding", "ProviderEndpoint", "OnboardingReceipt",
    "fingerprint_provider_snapshot", "review_with_onboarded_providers",
    "REQUIREMENTS", "RehearsalChecklistItem", "RehearsalManifest",
    "PilotReadinessError", "PilotRehearsalResult", "assess_read_only_rehearsal",
)
