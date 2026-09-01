"""Contract tests for EIOS Price Intelligence C1."""
from decimal import Decimal
import pytest
from eios.pricing.models import PriceCounts, PriceIntelligenceAssessmentContext, PriceIntelligenceResult
from eios.pricing.sufficiency import SufficiencyObservation


def test_counts_are_monotonic():
    counts = PriceCounts(n_raw=5, n_unique=4, n_comparable=3, n_representative=2, n_selected=2)
    assert counts.n_selected == 2


def test_counts_cannot_increase_downstream():
    with pytest.raises(ValueError):
        PriceCounts(n_raw=2, n_unique=3, n_comparable=2, n_representative=2, n_selected=1)


def test_zero_selected_requires_not_justifiable_and_null_value():
    result = PriceIntelligenceResult(
        decision_id="D1", scenario_id="S1", data_snapshot_id="SNAP-1",
        methodology_version="8.5", pr_value=None, currency=None,
        sufficiency_status="NOT_JUSTIFIABLE", pr_status="PR_NOT_JUSTIFIABLE",
        reference_set=(), counts=PriceCounts(n_raw=0,n_unique=0,n_comparable=0,n_representative=0,n_selected=0),
        aggregation_method="MEDIAN_UNWEIGHTED"
    )
    assert result.pr_value is None


def test_single_selected_cannot_be_pr_available():
    with pytest.raises(ValueError):
        PriceIntelligenceResult(
            decision_id="D1", scenario_id="S1", data_snapshot_id="SNAP-1",
            methodology_version="8.5", pr_value=Decimal("10.00"), currency="EUR",
            sufficiency_status="LIMITED", pr_status="PR_AVAILABLE",
            reference_set=("R1",), counts=PriceCounts(n_raw=1,n_unique=1,n_comparable=1,n_representative=1,n_selected=1),
            aggregation_method="MEDIAN_UNWEIGHTED"
        )


def test_snapshot_is_required_in_result():
    result = PriceIntelligenceResult(
        decision_id="D1", scenario_id="S1", data_snapshot_id="SNAP-1",
        methodology_version="8.5", pr_value=Decimal("10.00"), currency="EUR",
        sufficiency_status="LIMITED", pr_status="PR_LIMITED",
        reference_set=("R1",), counts=PriceCounts(n_raw=1,n_unique=1,n_comparable=1,n_representative=1,n_selected=1),
        aggregation_method="MEDIAN_UNWEIGHTED"
    )
    assert result.data_snapshot_id == "SNAP-1"


def test_assessment_context_has_independent_default_containers():
    sufficiency = SufficiencyObservation()
    a = PriceIntelligenceAssessmentContext(sufficiency=sufficiency)
    b = PriceIntelligenceAssessmentContext(sufficiency=sufficiency)
    assert a.temporal is not b.temporal
    assert a.representativeness is not b.representativeness
