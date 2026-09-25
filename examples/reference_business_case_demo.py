"""Generate both synthetic reference results and their local review in one run."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import tempfile

from .reference_business_case_001 import execute_reference_business_case
from .reference_business_case_review import render_review


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
    names = ("reference-negative-result.json", "reference-result.json", "reference-review.html")
    try:
        for name, payload in zip(names[:2], (negative, eligible)):
            (stage / name).write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        (stage / names[2]).write_text(html, encoding="utf-8")
        stage.rename(output_dir)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return tuple(output_dir / name for name in names)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path,
                        help="New directory for the two JSON files and read-only HTML")
    args = parser.parse_args()
    files = create_reference_demo(args.output_dir)
    print("Simulación sintética completada; ruta operacional FORBIDDEN.")
    for path in files:
        print(path)


if __name__ == "__main__":
    main()
