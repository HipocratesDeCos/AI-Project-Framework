"""F6.5–F6.8 independent synthetic external onboarding (no real trust)."""
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
from .recovery import (
    RecoveryError, RecoveryResult, recover_after_safe_stop,
)

__all__ = (
    "OnboardingError", "ProviderRegistration", "OnboardingSnapshot",
    "PinnedOnboarding", "ProviderEndpoint", "OnboardingReceipt",
    "fingerprint_provider_snapshot", "review_with_onboarded_providers",
    "REQUIREMENTS", "RehearsalChecklistItem", "RehearsalManifest",
    "PilotReadinessError", "PilotRehearsalResult", "assess_read_only_rehearsal",
    "SafeStopError", "SafeStopResult", "revalidate_before_rehearsal_reuse",
    "RecoveryError", "RecoveryResult", "recover_after_safe_stop",
)
