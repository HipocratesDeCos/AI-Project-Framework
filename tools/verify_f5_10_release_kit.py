"""F5.10 — certify a ZIP without EIOS source or runtime internet.

The CI driver is in the EIOS repository, but the certification actually runs
the *shipped standalone script* in an unpacked kit, outside the checkout.
It verifies identical results in two separate fresh venvs and adversarial
manifest/wheel/lockfile corruption before reporting success.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

if __package__:
    from .build_f5_10_release_kit import (
        BUNDLE_FILENAME, safe_extract_kit,
    )
    from .f5_10_certify_deployment import digest_file
else:
    from build_f5_10_release_kit import (
        BUNDLE_FILENAME, safe_extract_kit,
    )
    from f5_10_certify_deployment import digest_file


def _run_external(extracted: Path, *, output: Path | None = None, trusted_hash: str | None = None):
    cmd = [
        sys.executable, "-I", str(extracted / "certify_deployment.py"),
        "--kit", str(extracted),
    ]
    if output is not None:
        cmd += ["--output", str(output)]
    if trusted_hash is not None:
        cmd += ["--expected-manifest-sha256", trusted_hash]
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env["PYTHONNOUSERSITE"] = "1"
    env["PIP_NO_INDEX"] = "1"
    return subprocess.run(
        cmd, cwd=extracted.parent, env=env, capture_output=True, text=True,
        timeout=230 if output is not None else 35,
    )


def _reject_corruption(
    original: Path, temp: Path, change, expected: str,
) -> None:
    directory = temp / "bad-kit"
    if directory.exists():
        shutil.rmtree(directory)
    shutil.copytree(original, directory)
    change(directory)
    test = _run_external(directory, output=temp / "SHOULD_NOT_BE_CREATED")
    if test.returncode == 0 or expected not in test.stdout + test.stderr:
        raise ValueError(
            "Preflight unexpectedly accepted a corrupted kit: "
            + (test.stderr + test.stdout)[-1900:]
        )
    if (temp / "SHOULD_NOT_BE_CREATED").exists():
        raise ValueError("Corrupt kit created deployment before integrity verification")
    shutil.rmtree(directory)


def verify(bundle: Path) -> dict:
    if not bundle.is_file() or bundle.name != BUNDLE_FILENAME:
        raise ValueError("Expected the specifically named F5.10 release kit ZIP")
    with tempfile.TemporaryDirectory(prefix="eios-f5-10-external-validation-") as work:
        root = Path(work)
        extracted = root / "kit"
        safe_extract_kit(bundle, extracted)
        trusted_hash = digest_file(extracted / "manifest.json")
        preflight = _run_external(extracted, trusted_hash=trusted_hash)
        if preflight.returncode:
            raise RuntimeError("External preflight failed:\n" + preflight.stderr[-2200:])
        declared = json.loads(preflight.stdout)
        if (
            declared.get("manifest_sha256") != trusted_hash
            or declared.get("status") != "INTEGRITY_PREFLIGHT_PASS"
            or declared.get("wheel_count", 0) < 7
        ):
            raise ValueError("External preflight returned the wrong manifest")
        if _run_external(extracted, trusted_hash="0" * 64).returncode == 0:
            raise ValueError("Wrong independent trusted manifest anchor accepted")

        receipts = []
        for attempt in (1, 2):
            deployment = root / f"separate-installation-{attempt}"
            result = _run_external(extracted, output=deployment, trusted_hash=trusted_hash)
            if result.returncode:
                raise RuntimeError(
                    f"External offline installer run {attempt} failed:\n"
                    + result.stdout[-1200:] + "\n" + result.stderr[-4200:]
                )
            receipt_path = deployment / "technical_certification.json"
            if not receipt_path.is_file():
                raise ValueError("External certification did not create durable JSON evidence")
            content = json.loads(receipt_path.read_text(encoding="utf-8"))
            if content != json.loads(result.stdout):
                raise ValueError("Durable certificate differs from reported result")
            if (
                content.get("status") != "TECHNICAL_ONBOARDING_PASS"
                or content.get("production_authorized") is not False
                or content.get("operational_path") != "FORBIDDEN"
                or content.get("manifest_sha256") != trusted_hash
                or content.get("result", {}).get("initial_status") != "PARTIALLY_COMPLETED"
                or content.get("result", {}).get("later_status") != "COMPLETED"
                or content.get("real_user_authentication") != "NOT_TESTED"
                or content.get("real_documentary_admission") != "NOT_TESTED"
            ):
                raise ValueError("Unfounded production approval or missing technical result")
            receipts.append(content)
        if receipts[0] != receipts[1]:
            raise ValueError("Two independent installations gave different results")

        def mutate_wheel(directory: Path) -> None:
            entry = json.loads((directory / "manifest.json").read_text())["wheels"][0]
            with (directory / "wheels" / entry["filename"]).open("ab") as handle:
                handle.write(b"F5_10_SYNTHETIC_TAMPER")

        _reject_corruption(extracted, root, mutate_wheel, "WHEEL_DIGEST_MISMATCH")
        _reject_corruption(
            extracted, root,
            lambda folder: (folder / "requirements.lock").write_text("NOPE\n"),
            "SUPPORT_FILE_DIGEST_MISMATCH",
        )
        _reject_corruption(
            extracted, root,
            lambda folder: (folder / "wheels" / json.loads(
                (folder / "manifest.json").read_text()
            )["wheels"][0]["filename"]).unlink(),
            "MISSING_OR_UNTRUSTED_FILE",
        )
        _reject_corruption(
            extracted, root,
            lambda folder: (folder / "wheels" / "eios_price_procurement-0.2.0-py3-none-any.whl").write_text("UNDECLARED"),
            "UNDECLARED_OR_MISSING_WHEEL",
        )
        _reject_corruption(
            extracted, root,
            lambda folder: (folder / "manifest.json").write_text(
                (folder / "manifest.json").read_text().replace(
                    '"purpose": "SYNTHETIC_TECHNICAL_ONBOARDING_ONLY"',
                    '"purpose": "OPERATIONS_AUTHORIZED"',
                )
            ),
            "UNSUPPORTED_KIT_PURPOSE",
        )
        return {
            "verification": "F5_10_PORTABLE_EXTERNAL_DEPLOYMENT_SUCCESS",
            "kit_sha256": digest_file(bundle),
            "manifest_sha256": trusted_hash,
            "offline_installations": 2,
            "extracted_outside_repository": True,
            "python_isolated": True,
            "hash_locked_dependencies": True,
            "adversarial_preflight_cases": 5,
            "third_domain": "equipment_maintenance",
            "neutral_wheel_count": 4,
            "operational_path": "FORBIDDEN",
            "production_authorized": False,
            "certificate": receipts[0],
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit-dir", type=Path, default=Path("dist/release-kit"))
    args = parser.parse_args()
    report = verify(args.kit_dir.resolve() / BUNDLE_FILENAME)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
