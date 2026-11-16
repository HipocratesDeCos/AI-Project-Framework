"""Structural and governance regressions for the source-audited core inventory.

These checks ensure named producers and their parameter constants still exist.
They DO NOT replace the behavioral tests of each authorized Rule/Engine.
"""
import ast
from dataclasses import FrozenInstanceError
import importlib
import inspect
import textwrap

import pytest

from eios.company_parameters import BY_ID
from eios.parameters.core_consumer_inventory import (
    CORE_PARAMETER_CONSUMERS,
    CoreParameterConsumer,
    get_core_parameter_consumers,
)


def test_inventory_is_a_deliberately_bounded_subset():
    assert len(CORE_PARAMETER_CONSUMERS) == 17
    assert len({x.parameter_id for x in CORE_PARAMETER_CONSUMERS}) == 17
    assert {x.domain for x in CORE_PARAMETER_CONSUMERS} == {
        "FIN", "PRE", "HIS", "STK", "MGE", "PAG",
    }
    assert all(x.parameter_id in BY_ID for x in CORE_PARAMETER_CONSUMERS)


@pytest.mark.parametrize(
    "entry", CORE_PARAMETER_CONSUMERS,
    ids=lambda item: item.parameter_id,
)
def test_each_inventory_entry_has_real_function_and_referenced_parameter(entry):
    module = importlib.import_module(entry.module)
    assert getattr(module, entry.constant_name) == entry.parameter_id
    producer = getattr(module, entry.callable_name)
    assert inspect.isfunction(producer)
    assert producer.__module__ == entry.module
    tree = ast.parse(textwrap.dedent(inspect.getsource(producer)))
    loaded = {
        node.id for node in ast.walk(tree)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    assert entry.constant_name in loaded, (
        entry.parameter_id + " is no longer used in " + entry.callable_name
    )
    assert entry.status == "CORE_CONSUMER_SOURCE_IDENTIFIED"
    assert entry.company_activation == "NOT_ATTESTED"
    assert entry.downstream_rules


@pytest.mark.parametrize(
    "id,relationships", [
        ("P-FIN-001", ("DERIVED_ENGINE",)),
        ("P-FIN-002", ("COMPOSITE_RULE",)),
        ("P-MGE-001", ("SHARED_RULE_POLICY",)),
        ("P-PAG-002", ("DERIVED_THRESHOLD",)),
        ("P-PAG-004", ("CONTROL_GATE",)),
    ],
)
def test_relationship_classifications_do_not_imply_direct_rule_authority(id, relationships):
    matches = get_core_parameter_consumers(id)
    assert tuple(x.relationship for x in matches) == relationships


def test_registry_does_not_equate_prepared_sales_values_to_core_evidence():
    assert get_core_parameter_consumers("P-MGE-004") == ()
    assert get_core_parameter_consumers("P-PAG-005") == ()
    assert get_core_parameter_consumers("P-STK-002") == ()
    # These intentionally unlisted IDs may have separate consumers; they
    # cannot be treated as a blanket proof of "no consumer".


def test_registry_returns_immutable_copies_and_cannot_activate_configuration():
    assert get_core_parameter_consumers() is CORE_PARAMETER_CONSUMERS
    assert all(isinstance(x, CoreParameterConsumer) for x in CORE_PARAMETER_CONSUMERS)
    original = get_core_parameter_consumers("P-PRE-001")[0]
    with pytest.raises(FrozenInstanceError):
        original.company_activation = "ACTIVE"
    assert original.company_activation == "NOT_ATTESTED"


@pytest.mark.parametrize("invalid", ["", " ", " P-FIN-001", "P-FIN-001 ", 1, [], {}])
def test_noncanonical_or_untyped_identifiers_are_rejected(invalid):
    with pytest.raises(ValueError, match="canonical"):
        get_core_parameter_consumers(invalid)


def test_unknown_parameter_does_not_produce_fake_policy_or_activation():
    assert get_core_parameter_consumers("P-UNKNOWN-999") == ()
    assert all(not hasattr(x, "value") for x in CORE_PARAMETER_CONSUMERS)


def test_inventory_does_not_import_application_or_persistence_modules():
    import eios.parameters.core_consumer_inventory as module

    source = inspect.getsource(module)
    assert "from eios.company_" not in source
    assert "import sqlite3" not in source
    assert "DEFAULT_VALUE" not in source


def test_prepared_sales_path_is_explicitly_non_authoritative():
    import eios.company_sales_negotiation as module

    source = inspect.getsource(module.analyze_offer)
    assert "EXPLICIT_PREPARED_VALUES_NOT_RULES_ACTIVATION" in source
    assert "decision_authority=False" in source
    assert "operational_path='FORBIDDEN'" in source
