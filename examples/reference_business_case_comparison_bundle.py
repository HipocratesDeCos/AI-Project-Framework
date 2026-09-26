"""Create and replay a self-contained, synthetic two-company review bundle."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile

from .reference_business_case_demo import create_reference_demo, verify_reference_demo
from .reference_business_case_002 import (
    create_reference_business_case_002, verify_reference_business_case_002,
)
from .reference_business_case_comparison import render_comparison


def verify_comparison_bundle(directory: Path) -> None:
    directory = Path(directory)
    if directory.is_symlink() or not directory.is_dir() or {p.name for p in directory.iterdir()} != {
        "case-001", "case-002", "comparison.html"
    }:
        raise ValueError("Comparison bundle requires exactly both cases and comparison.html")
    if any(path.is_symlink() for path in directory.rglob("*")):
        raise ValueError("Comparison bundle must not contain symlinks")
    verify_reference_demo(directory / "case-001")
    verify_reference_business_case_002(directory / "case-002")
    if (directory / "comparison.html").read_text(encoding="utf-8") != render_comparison(
        directory / "case-001", directory / "case-002"
    ):
        raise ValueError("Comparison HTML differs from verified case replay")


def create_comparison_bundle(directory: Path) -> tuple[Path, Path, Path]:
    directory = Path(directory)
    if directory.exists():
        raise FileExistsError(f"Output already exists: {directory}")
    if not directory.parent.is_dir():
        raise ValueError(f"Output parent directory does not exist: {directory.parent}")
    stage = Path(tempfile.mkdtemp(prefix=".reference-comparison-", dir=directory.parent))
    try:
        create_reference_demo(
            stage / "case-001", with_price=True, with_tco=True,
            with_supplier_risk=True, with_c0=True, with_decision_twin=True,
            with_scenario_coordination=True, with_negotiation_intelligence=True,
            with_negotiation_ladder=True, with_buyer_preview=True,
        )
        create_reference_business_case_002(stage / "case-002", with_review=True)
        (stage / "comparison.html").write_text(
            render_comparison(stage / "case-001", stage / "case-002"), encoding="utf-8"
        )
        verify_comparison_bundle(stage)
        stage.rename(directory)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return directory / "case-001", directory / "case-002", directory / "comparison.html"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output-dir", type=Path)
    action.add_argument("--verify-dir", type=Path)
    args = parser.parse_args()
    if args.verify_dir is not None:
        verify_comparison_bundle(args.verify_dir)
        print("Paquete comparativo verificado; sin ruta operacional ni autoridad decisional.")
    else:
        paths = create_comparison_bundle(args.output_dir)
        print("Dos casos sintéticos y comparación de solo lectura creados:")
        for path in paths:
            print(path)


if __name__ == "__main__":
    main()
