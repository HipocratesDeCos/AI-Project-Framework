"""Generate both synthetic reference results and their local review in one run."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import tempfile

from .reference_business_case_001 import (
    execute_reference_business_case,
    execute_reference_business_case_with_price_observation,
    execute_reference_business_case_with_tco_observation,
    execute_reference_business_case_with_analytical_observations,
)
from .reference_business_case_review import render_review


_NAMES = ("reference-negative-result.json", "reference-result.json", "reference-review.html")
_PRICE_NAMES = ("reference-negative-price.json", "reference-price.json")
_TCO_NAMES = ("reference-negative-tco.json", "reference-tco.json")


def create_reference_demo(output_dir: Path, *, with_price: bool = False,
                          with_tco: bool = False) -> tuple[Path, ...]:
    """Reuse closed runners and publish one complete local demonstration directory."""
    output_dir = Path(output_dir)
    if output_dir.exists():
        raise FileExistsError(f"Output already exists: {output_dir}")
    if not output_dir.parent.is_dir():
        raise ValueError(f"Output parent directory does not exist: {output_dir.parent}")

    observations = None
    tco_observations = None
    if with_price and with_tco:
        negative_execution, negative_price, negative_tco = (
            execute_reference_business_case_with_analytical_observations(variant="negative")
        )
        eligible_execution, eligible_price, eligible_tco = (
            execute_reference_business_case_with_analytical_observations(variant="qtg-eligible")
        )
        negative, eligible = negative_execution.to_payload(), eligible_execution.to_payload()
        observations = (negative_price.to_payload(), eligible_price.to_payload())
        tco_observations = (negative_tco.to_payload(), eligible_tco.to_payload())
    elif with_price:
        negative_execution, negative_price = execute_reference_business_case_with_price_observation(
            variant="negative",
        )
        eligible_execution, eligible_price = execute_reference_business_case_with_price_observation(
            variant="qtg-eligible",
        )
        negative, eligible = negative_execution.to_payload(), eligible_execution.to_payload()
        observations = (negative_price.to_payload(), eligible_price.to_payload())
    elif with_tco:
        negative_execution, negative_tco = execute_reference_business_case_with_tco_observation(
            variant="negative",
        )
        eligible_execution, eligible_tco = execute_reference_business_case_with_tco_observation(
            variant="qtg-eligible",
        )
        negative, eligible = negative_execution.to_payload(), eligible_execution.to_payload()
        tco_observations = (negative_tco.to_payload(), eligible_tco.to_payload())
    else:
        negative = execute_reference_business_case(variant="negative").to_payload()
        eligible = execute_reference_business_case(variant="qtg-eligible").to_payload()
    html = render_review(negative, eligible, price_observations=observations,
                         tco_observations=tco_observations)

    stage = Path(tempfile.mkdtemp(prefix=".reference-demo-", dir=output_dir.parent))
    try:
        for name, payload in zip(_NAMES[:2], (negative, eligible)):
            (stage / name).write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        (stage / _NAMES[2]).write_text(html, encoding="utf-8")
        if observations is not None:
            for name, payload in zip(_PRICE_NAMES, observations):
                (stage / name).write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        if tco_observations is not None:
            for name, payload in zip(_TCO_NAMES, tco_observations):
                (stage / name).write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        stage.rename(output_dir)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return tuple(output_dir / name for name in (
        _NAMES + (_PRICE_NAMES if with_price else ()) + (_TCO_NAMES if with_tco else ())
    ))


def verify_reference_demo(directory: Path) -> tuple[str, str]:
    """Read and replay the fixed synthetic cases without changing the directory."""
    directory = Path(directory)
    if not directory.is_dir():
        raise ValueError(f"Demo directory does not exist: {directory}")
    negative = json.loads((directory / _NAMES[0]).read_text(encoding="utf-8"))
    eligible = json.loads((directory / _NAMES[1]).read_text(encoding="utf-8"))
    stored_html = (directory / _NAMES[2]).read_text(encoding="utf-8")
    present = tuple((directory / name).exists() for name in _PRICE_NAMES)
    if any(present) and not all(present):
        raise ValueError("Both PRICE observations are required together")
    observations = (tuple(json.loads((directory / name).read_text(encoding="utf-8"))
                          for name in _PRICE_NAMES) if all(present) else None)
    tco_present = tuple((directory / name).exists() for name in _TCO_NAMES)
    if any(tco_present) and not all(tco_present):
        raise ValueError("Both TCO observations are required together")
    tco_observations = (tuple(json.loads((directory / name).read_text(encoding="utf-8"))
                              for name in _TCO_NAMES) if all(tco_present) else None)

    expected_html = render_review(negative, eligible, price_observations=observations,
                                  tco_observations=tco_observations)
    if stored_html != expected_html:
        raise ValueError("Review HTML differs from the two terminal artifacts")
    for variant, stored in (("negative", negative), ("qtg-eligible", eligible)):
        if observations is not None and tco_observations is not None:
            replayed, replayed_price, replayed_tco = (
                execute_reference_business_case_with_analytical_observations(variant=variant)
            )
            saved_price = observations[0 if variant == "negative" else 1]
            saved_tco = tco_observations[0 if variant == "negative" else 1]
            if saved_price != replayed_price.to_payload():
                raise ValueError(f"{variant}: PRICE observation differs from fixture replay")
            if saved_tco != replayed_tco.to_payload():
                raise ValueError(f"{variant}: TCO observation differs from fixture replay")
            replayed = replayed.to_payload()
        elif observations is None and tco_observations is None:
            replayed = execute_reference_business_case(variant=variant).to_payload()
        elif observations is not None:
            replayed, replayed_price = execute_reference_business_case_with_price_observation(
                variant=variant,
            )
            replayed = replayed.to_payload()
            saved_price = observations[0 if variant == "negative" else 1]
            if saved_price != replayed_price.to_payload():
                raise ValueError(f"{variant}: PRICE observation differs from fixture replay")
        else:
            replayed, replayed_tco = execute_reference_business_case_with_tco_observation(
                variant=variant,
            )
            replayed = replayed.to_payload()
            saved_tco = tco_observations[0 if variant == "negative" else 1]
            if saved_tco != replayed_tco.to_payload():
                raise ValueError(f"{variant}: TCO observation differs from fixture replay")
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
    parser.add_argument("--with-price", action="store_true",
                        help="Export both same-run PRICE observations and show them in HTML")
    parser.add_argument("--with-tco", action="store_true",
                        help="Export both same-run TCO observations and show them in HTML")
    args = parser.parse_args()
    if args.verify_dir is not None:
        if args.with_price or args.with_tco:
            parser.error("--with-price/--with-tco apply only to --output-dir; verification detects sidecars")
        negative_fp, eligible_fp = verify_reference_demo(args.verify_dir)
        print("Revisión y repetición sintética coinciden; ruta operacional FORBIDDEN.")
        print(f"negative: {negative_fp}")
        print(f"qtg-eligible: {eligible_fp}")
        return
    files = create_reference_demo(args.output_dir, with_price=args.with_price,
                                  with_tco=args.with_tco)
    print("Simulación sintética completada; ruta operacional FORBIDDEN.")
    for path in files:
        print(path)


if __name__ == "__main__":
    main()
