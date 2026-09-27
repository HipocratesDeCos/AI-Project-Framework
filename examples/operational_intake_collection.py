"""Prepare a reference-only collection sheet for a future operational case."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from eios.core.operational_intake import (
    CANONICAL_INTAKE_ITEMS,
    OperationalExpedientIntakeManifest,
    build_operational_expedient_intake_manifest,
)


def empty_collection_sheet() -> dict[str, list[str]]:
    """Expose canonical item identifiers without fabricating documentary refs."""
    return {item_id: [] for item_id, _ in CANONICAL_INTAKE_ITEMS}


def write_empty_collection_sheet(path: Path) -> None:
    """Create a new sheet; never overwrite existing user material."""
    with Path(path).open("x", encoding="utf-8") as target:
        json.dump(empty_collection_sheet(), target, ensure_ascii=False, indent=2)
        target.write("\n")


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON intake key: {key}")
        result[key] = value
    return result


def inspect_collection_sheet(path: Path) -> OperationalExpedientIntakeManifest:
    """Check references only, using the existing non-authoritative manifest."""
    supplied = json.loads(
        Path(path).read_text(encoding="utf-8"), object_pairs_hook=_unique_json_object,
    )
    if type(supplied) is not dict or any(type(refs) is not list for refs in supplied.values()):
        raise ValueError("Expected a JSON object mapping intake keys to reference arrays")
    return build_operational_expedient_intake_manifest(
        supplied_references={item_id: tuple(refs) for item_id, refs in supplied.items()},
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path, help="Create a blank reference sheet")
    action.add_argument("--check", type=Path, help="Inspect an existing reference sheet")
    args = parser.parse_args()
    if args.output is not None:
        write_empty_collection_sheet(args.output)
        print(f"Plantilla vacía creada: {args.output}")
        return
    manifest = inspect_collection_sheet(args.check)
    reading = {
        "REQUIRED_SET_INCOMPLETE": "Faltan referencias obligatorias",
        "REQUIRED_SET_COMPLETE": "Referencias obligatorias registradas",
    }[manifest.readiness]
    print(f"Inventario de referencias: {reading} ({manifest.readiness})")
    if manifest.missing_required_items:
        print("Faltan bloques obligatorios: " + ", ".join(manifest.missing_required_items))
    if manifest.pending_conditional_items:
        print("Condicionales sin referencia: " + ", ".join(manifest.pending_conditional_items))
    print("Una referencia no acredita contenido, admisión, revisión ni autoridad de compra.")


if __name__ == "__main__":
    main()
