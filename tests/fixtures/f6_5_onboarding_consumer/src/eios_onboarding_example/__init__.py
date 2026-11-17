"""F6.5–F6.7 independent synthetic external onboarding (no real trust)."""
from .onboarding import (
    OnboardingError, ProviderRegistration, OnboardingSnapshot,
    PinnedOnboarding, ProviderEndpoint, OnboardingReceipt,
    fingerprint_provider_snapshot, review_with_onboarded_providers,
)
from .pilot import (
    REQUIREMENTS, RehearsalChecklistItem, RehearsalManifest,
    PilotReadinessError, PilotRehearsalResult, assess_read_only_rehearsal,
)
from .safe_stop import (
    SafeStopError, SafeStopResult, revalidate_before_rehearsal_reuse,
)

__all__ = (
    "OnboardingError", "ProviderRegistration", "OnboardingSnapshot",
    "PinnedOnboarding", "ProviderEndpoint", "OnboardingReceipt",
    "fingerprint_provider_snapshot", "review_with_onboarded_providers",
    "REQUIREMENTS", "RehearsalChecklistItem", "RehearsalManifest",
    "PilotReadinessError", "PilotRehearsalResult", "assess_read_only_rehearsal",
    "SafeStopError", "SafeStopResult", "revalidate_before_rehearsal_reuse",
)
