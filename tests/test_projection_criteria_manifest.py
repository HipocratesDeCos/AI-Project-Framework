from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from hashlib import sha256
import json

import pytest

from eios.core.finance_quality_preparation import (
    PresentedQualityCriteria, build_finance_quality_preparation,
)
from eios.core.projection_criteria_manifest import (
    AuthorizedProjectionCriterion, ProjectionCriteriaManifest, REQUIRED_FUNCTIONS,
    build_projection_criteria_manifest, validate_preparation_criteria_against_manifest,
)
from test_documentary_payment_chain_boundaries import material  # noqa: F401
from test_finance_decision_input_package import capture  # noqa: F401
from test_finance_quality_preparation import prepared_args  # noqa: F401


def criterion_material():
    return {function: (f"criterion-{index}".encode())
            for index, function in enumerate(REQUIRED_FUNCTIONS, start=1)}


def manifest_for(material=None, **changes):
    material = material or criterion_material()
    criteria = tuple(AuthorizedProjectionCriterion(function=function,
        reference=f"projection-only-{index}", version="1.0",
        content_sha256=sha256(material[function]).hexdigest())
        for index, function in enumerate(REQUIRED_FUNCTIONS, start=1))
    args = dict(manifest_ref="projection-only-authorized-criteria",
        manifest_version="1.0", authority_ref="approved-owner-decision",
        authorized_at=datetime(2026, 9, 19, tzinfo=timezone.utc), criteria=criteria)
    args.update(changes)
    return build_projection_criteria_manifest(**args)


def preparation_for(prepared_args, material=None):
    material = material or criterion_material()
    prepared_args["criteria"] = tuple(PresentedQualityCriteria(
        reference=f"projection-only-{index}", version="1.0", content=material[function])
        for index, function in enumerate(REQUIRED_FUNCTIONS, start=1))
    return build_finance_quality_preparation(**prepared_args)


def test_manifest_preserves_closed_profile_and_authority():
    result = manifest_for()
    payload = result.to_payload()
    assert payload["profile"] == "PROJECTION_ONLY"
    assert payload["required_functions"] == list(REQUIRED_FUNCTIONS)
    assert {item["function"] for item in payload["criteria"]} == set(REQUIRED_FUNCTIONS)
    assert payload["assurance_scope"] == "EXACT_AUTHORIZED_CRITERION_IDENTITIES_ONLY"
    assert not {"content", "content_base64", "quality_checks", "quality_result"} & payload.keys()


def test_exact_preparation_match_is_accepted(prepared_args):
    preparation = preparation_for(prepared_args)
    validate_preparation_criteria_against_manifest(preparation, manifest_for())


@pytest.mark.parametrize("change", ["content", "reference", "version", "extra", "missing"])
def test_preparation_difference_is_rejected(prepared_args, change):
    material = criterion_material()
    preparation = preparation_for(prepared_args, material)
    if change == "content":
        material[REQUIRED_FUNCTIONS[0]] = b"different"
        manifest = manifest_for(material)
    else:
        payload = preparation.to_payload()
        if change == "reference": payload["presented_criteria"][0]["reference"] = "other"
        if change == "version": payload["presented_criteria"][0]["version"] = "2.0"
        if change == "extra": payload["presented_criteria"].append(dict(
            reference="extra", version="1", sha256="0" * 64, content_base64="eA=="))
        if change == "missing": payload["presented_criteria"].pop()
        forged = object.__new__(type(preparation))
        object.__setattr__(forged, "_material", json.dumps(payload).encode())
        preparation = forged
        manifest = manifest_for(material)
    with pytest.raises(ValueError, match="exactly match"):
        validate_preparation_criteria_against_manifest(preparation, manifest)


@pytest.mark.parametrize("change", ["missing", "duplicate_function", "duplicate_key"])
def test_manifest_requires_exact_unique_functions(change):
    base = manifest_for().to_payload()["criteria"]
    criteria = tuple(AuthorizedProjectionCriterion(**item) for item in base)
    if change == "missing": criteria = criteria[:-1]
    elif change == "duplicate_function":
        criteria = criteria[:-1] + (criteria[0].model_copy(update={
            "reference": "another-reference"}),)
    else:
        criteria = criteria[:-1] + (criteria[-1].model_copy(update={
            "reference": criteria[0].reference, "version": criteria[0].version}),)
    with pytest.raises(ValueError):
        manifest_for(criteria=criteria)


@pytest.mark.parametrize("field,value", [
    ("manifest_ref", " "), ("manifest_version", ""), ("authority_ref", "\t"),
    ("authorized_at", datetime(2026, 9, 19)), ("criteria", []),
])
def test_invalid_authority_material_is_rejected(field, value):
    with pytest.raises((TypeError, ValueError)):
        manifest_for(**{field: value})


def test_hash_format_and_immutable_record():
    with pytest.raises(ValueError):
        AuthorizedProjectionCriterion(function=REQUIRED_FUNCTIONS[0], reference="x",
            version="1", content_sha256="not-a-sha256")
    result = manifest_for()
    exported = result.to_payload(); exported["criteria"].clear()
    assert result.to_payload()["criteria"]
    with pytest.raises(FrozenInstanceError): result._material = b"forged"
    with pytest.raises(TypeError): ProjectionCriteriaManifest()


def test_validation_rejects_unconstructed_inputs(prepared_args):
    with pytest.raises(TypeError):
        validate_preparation_criteria_against_manifest(object(), manifest_for())
    with pytest.raises(TypeError):
        validate_preparation_criteria_against_manifest(preparation_for(prepared_args), object())
