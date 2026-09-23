import pytest

from eios.core.operational_intake import (
    CANONICAL_INTAKE_ITEMS,
    build_operational_expedient_intake_manifest,
    empty_operational_expedient_intake_manifest,
)


def _required_refs():
    return {
        item_id: (f"ref:{item_id}",)
        for item_id, requirement in CANONICAL_INTAKE_ITEMS
        if requirement == "REQUIRED"
    }


def test_empty_manifest_is_intentionally_incomplete():
    manifest = empty_operational_expedient_intake_manifest()
    assert manifest.readiness == "REQUIRED_SET_INCOMPLETE"
    assert manifest.missing_required_items
    assert "parameter_p_fin_002" in manifest.pending_conditional_items
    assert "treasury_additional_material" in manifest.pending_conditional_items


def test_required_set_complete_does_not_require_conditional_items():
    manifest = build_operational_expedient_intake_manifest(
        supplied_references=_required_refs()
    )
    assert manifest.readiness == "REQUIRED_SET_COMPLETE"
    assert manifest.missing_required_items == ()
    assert set(manifest.pending_conditional_items) == {
        "parameter_p_fin_002",
        "treasury_additional_material",
    }
    assert any("no equivale a STRUCTURALLY_ADMISSIBLE" in x for x in manifest.limitations)


def test_conditional_items_can_be_supplied_without_changing_required_semantics():
    refs = _required_refs()
    refs["parameter_p_fin_002"] = ("ref:p-fin-002",)
    refs["treasury_additional_material"] = ("ref:treasury-additional",)

    manifest = build_operational_expedient_intake_manifest(
        supplied_references=refs
    )
    assert manifest.readiness == "REQUIRED_SET_COMPLETE"
    assert manifest.pending_conditional_items == ()


def test_unknown_item_fails_closed():
    with pytest.raises(ValueError, match="Unknown intake item"):
        build_operational_expedient_intake_manifest(
            supplied_references={"invented_item": ("ref:x",)}
        )


def test_duplicate_references_fail_closed():
    refs = _required_refs()
    refs["purchase_operation"] = ("ref:purchase", "ref:purchase")
    with pytest.raises(ValueError, match="duplicate references"):
        build_operational_expedient_intake_manifest(
            supplied_references=refs
        )


@pytest.mark.parametrize("bad_ref", ["", " ref:x", "ref:x "])
def test_invalid_reference_format_fails_closed(bad_ref):
    refs = _required_refs()
    refs["purchase_operation"] = (bad_ref,)
    with pytest.raises(ValueError, match="invalid reference"):
        build_operational_expedient_intake_manifest(
            supplied_references=refs
        )


def test_manifest_is_deterministic_for_same_reference_set():
    refs = _required_refs()
    first = build_operational_expedient_intake_manifest(
        supplied_references=refs
    )
    second = build_operational_expedient_intake_manifest(
        supplied_references=dict(reversed(list(refs.items())))
    )
    assert first.manifest_fingerprint == second.manifest_fingerprint
    assert first.items == second.items


def test_manifest_contains_no_business_decision_fields():
    manifest = build_operational_expedient_intake_manifest(
        supplied_references=_required_refs()
    )
    forbidden = {
        "apto",
        "approved",
        "quality_result",
        "decision_result",
        "authority",
        "recommendation",
        "execution",
    }
    assert all(
        not any(token in item.item_id for token in forbidden)
        for item in manifest.items
    )
