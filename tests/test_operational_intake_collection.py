"""Collection sheet CLI logic stays separate from admission and QTG."""
import json
import sys

import pytest

from eios.core.operational_intake import CANONICAL_INTAKE_ITEMS
from examples.operational_intake_collection import (
    empty_collection_sheet, inspect_collection_sheet, main, write_empty_collection_sheet,
)


def test_blank_sheet_matches_canonical_items_and_remains_incomplete(tmp_path):
    path = tmp_path / "references.json"
    write_empty_collection_sheet(path)
    assert list(json.loads(path.read_text(encoding="utf-8"))) == [
        name for name, _ in CANONICAL_INTAKE_ITEMS
    ]
    assert inspect_collection_sheet(path).readiness == "REQUIRED_SET_INCOMPLETE"
    with pytest.raises(FileExistsError):
        write_empty_collection_sheet(path)


def test_collection_check_uses_manifest_without_promoting_references(tmp_path):
    sheet = empty_collection_sheet()
    for item_id, requirement in CANONICAL_INTAKE_ITEMS:
        if requirement == "REQUIRED":
            sheet[item_id] = [f"document:{item_id}"]
    path = tmp_path / "references.json"
    path.write_text(json.dumps(sheet), encoding="utf-8")
    manifest = inspect_collection_sheet(path)
    assert manifest.readiness == "REQUIRED_SET_COMPLETE"
    assert len(manifest.pending_conditional_items) == 2
    assert any("no equivale a STRUCTURALLY_ADMISSIBLE" in x for x in manifest.limitations)


@pytest.mark.parametrize("bad", [{"unknown": []}, {"purchase_operation": "document:1"}, []])
def test_collection_rejects_unknown_keys_or_non_array_values(tmp_path, bad):
    path = tmp_path / "references.json"
    path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError):
        inspect_collection_sheet(path)


def test_collection_rejects_duplicate_json_key_without_losing_first_reference(tmp_path):
    path = tmp_path / "references.json"
    path.write_text(
        '{"order_document": ["document:order"], "order_document": []}',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Duplicate JSON intake key: order_document"):
        inspect_collection_sheet(path)


def test_check_command_explains_readiness_without_implying_admission(tmp_path, monkeypatch, capsys):
    path = tmp_path / "references.json"
    sheet = empty_collection_sheet()
    for readiness, expected in (
        ("REQUIRED_SET_INCOMPLETE", "Faltan referencias obligatorias"),
        ("REQUIRED_SET_COMPLETE", "Referencias obligatorias registradas"),
    ):
        if readiness == "REQUIRED_SET_COMPLETE":
            for item_id, requirement in CANONICAL_INTAKE_ITEMS:
                if requirement == "REQUIRED":
                    sheet[item_id] = [f"document:{item_id}"]
        path.write_text(json.dumps(sheet), encoding="utf-8")
        monkeypatch.setattr(sys, "argv", ["operational_intake_collection", "--check", str(path)])
        main()
        output = capsys.readouterr().out
        assert f"{expected} ({readiness})" in output
        assert "Una referencia no acredita contenido, admisión, revisión ni autoridad de compra." in output
