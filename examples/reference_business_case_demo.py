"""Generate both synthetic reference results and their local review in one run."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import tempfile

from .reference_business_case_001 import execute_reference_business_case
from .reference_business_case_review import render_review


_NAMES = ("reference-negative-result.json", "reference-result.json", "reference-review.html")


def create_reference_demo(output_dir: Path) -> tuple[Path, Path, Path]:
    """Reuse closed runners and publish one complete local demonstration directory."""
    output_dir = Path(output_dir)
    if output_dir.exists():
        raise FileExistsError(f"Output already exists: {output_dir}")
    if not output_dir.parent.is_dir():
        raise ValueError(f"Output parent directory does not exist: {output_dir.parent}")

    negative = execute_reference_business_case(variant="negative").to_payload()
    eligible = execute_reference_business_case(variant="qtg-eligible").to_payload()
    html = render_review(negative, eligible)

    stage = Path(tempfile.mkdtemp(prefix=".reference-demo-", dir=output_dir.parent))
    try:
        for name, payload in zip(_NAMES[:2], (negative, eligible)):
            (stage / name).write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        (stage / _NAMES[2]).write_text(html, encoding="utf-8")
        stage.rename(output_dir)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return tuple(output_dir / name for name in _NAMES)


def verify_reference_demo(directory: Path) -> tuple[str, str]:
    """Read and replay the fixed synthetic cases without changing the directory."""
    directory = Path(directory)
    if not directory.is_dir():
        raise ValueError(f"Demo directory does not exist: {directory}")
    negative = json.loads((directory / _NAMES[0]).read_text(encoding="utf-8"))
    eligible = json.loads((directory / _NAMES[1]).read_text(encoding="utf-8"))
    stored_html = (directory / _NAMES[2]).read_text(encoding="utf-8")

    expected_html = render_review(negative, eligible)
    if stored_html != expected_html:
        raise ValueError("Review HTML differs from the two terminal artifacts")
    for variant, stored in (("negative", negative), ("qtg-eligible", eligible)):
        replayed = execute_reference_business_case(variant=variant).to_payload()
        if stored != replayed:
            raise ValueError(f"{variant}: terminal differs from the current fixture replay")
    return negative["terminal_fingerprint"], eligible["terminal_fingerprint"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output-dir", type=Path,
                        help="New directory for the two JSON files and read-only HTML")
    action.add_argument("--verify-dir", type=Path,
                        help="Read and replay an existing synthetic demo directory")
    args = parser.parse_args()
    if args.verify_dir is not None:
        negative_fp, eligible_fp = verify_reference_demo(args.verify_dir)
        print("Revisión y repetición sintética coinciden; ruta operacional FORBIDDEN.")
        print(f"negative: {negative_fp}")
        print(f"qtg-eligible: {eligible_fp}")
        return
    files = create_reference_demo(args.output_dir)
    print("Simulación sintética completada; ruta operacional FORBIDDEN.")
    for path in files:
        print(path)


if __name__ == "__main__":
    main()
