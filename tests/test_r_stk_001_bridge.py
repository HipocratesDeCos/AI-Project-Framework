from types import SimpleNamespace

import pytest

import eios.rules.delivery as delivery


def _patch_validation(monkeypatch):
    monkeypatch.setattr(delivery, "_validate_identity", lambda *args, **kwargs: None)
    monkeypatch.setattr(delivery, "_validate_conclusive_state", lambda *args, **kwargs: None)
    monkeypatch.setattr(delivery, "_validate_evidence_binding", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        delivery,
        "validate_evidence",
        lambda evidence: SimpleNamespace(status="VALID"),
    )


def _evidence(evidence_id: str):
    return SimpleNamespace(evidence_id=evidence_id)


@pytest.mark.parametrize(
    ("state", "outcome"),
    (
        ("LATE_DELIVERY_DEMONSTRATED", "TRUE"),
        ("NOT_LATE_DEMONSTRATED", "FALSE"),
        ("NOT_LATE_WITHIN_EVIDENCED_HORIZON", "FALSE"),
    ),
)
def test_r_stk_001_maps_closed_temporal_fact(monkeypatch, state, outcome):
    _patch_validation(monkeypatch)
    analysis = SimpleNamespace(state=state, limitation_codes=())

    result = delivery.evaluate_r_stk_001(
        object(),
        object(),
        object(),
        object(),
        analysis,
        _evidence("EV-BASE"),
        _evidence("EV-DELIVERY"),
    )

    assert result.rule_id == "R-STK-001"
    assert result.status == "EVALUABLE"
    assert result.outcome == outcome
    assert result.evidence_ids == ["EV-BASE", "EV-DELIVERY"]


@pytest.mark.parametrize("state", ("NOT_EVIDENCED", "CONFLICTING_DATA", "NOT_DETERMINABLE"))
def test_r_stk_001_preserves_uncertainty(monkeypatch, state):
    _patch_validation(monkeypatch)
    analysis = SimpleNamespace(state=state, limitation_codes=())

    result = delivery.evaluate_r_stk_001(
        object(),
        object(),
        object(),
        object(),
        analysis,
        _evidence("EV-BASE"),
        _evidence("EV-DELIVERY"),
    )

    assert result.rule_id == "R-STK-001"
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None
