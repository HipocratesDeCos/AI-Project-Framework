"""F5.10 — build a portable, offline-installable *technical* onboarding ZIP.

Reuses F4/F5.6–F5.9 audited wheels without changing EIOS production modules.
Adds exact hash-locked binary dependency wheels for the current host
platform/Python minor version and the independently built maintenance sample.
The resulting kit requires NO network or project checkout at install time.
No claim of authenticity: the ZIP/manifest is unsigned.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile

if __package__:
    from .f5_10_certify_deployment import (
        MODULES, NEUTRAL, PERMITTED_DEPENDENCIES, PURPOSE,
        SAMPLE, MAX_BYTES, _wheel_identity, validate_kit,
        digest_file,
    )
    from .verify_f5_9_third_domain import (
        NEUTRAL_WHEELS, WHEEL_SPECS, inspect_wheels,
        build_project_wheel, audit_project_wheel,
    )
else:
    from f5_10_certify_deployment import (
        MODULES, NEUTRAL, PERMITTED_DEPENDENCIES, PURPOSE,
        SAMPLE, MAX_BYTES, _wheel_identity, validate_kit,
        digest_file,
    )
    from verify_f5_9_third_domain import (
        NEUTRAL_WHEELS, WHEEL_SPECS, inspect_wheels,
        build_project_wheel, audit_project_wheel,
    )

ROOT = Path(__file__).resolve().parents[1]
SOURCE_CERTIFIER = ROOT / "tools/f5_10_certify_deployment.py"
SOURCE_README = ROOT / "tests/fixtures/f5_10_deployment_kit/README.md"
BUNDLE_FILENAME = "EIOS_F5_10_Neutral_Onboarding_Kit.zip"
MAX_MEMBER_COUNT = 30
MAX_TOTAL_UNCOMPRESSED = 110_000_000


def _neutral_wheels(wheels: dict[str, Path]) -> dict[str, Path]:
    if set(wheels) != set(NEUTRAL_WHEELS):
        raise ValueError("F5.10 requires precisely four audited neutral EIOS wheels")
    for name in NEUTRAL_WHEELS:
        if not wheels[name].is_file():
            raise ValueError(f"Missing audited neutral wheel: {name}")
    return {name: wheels[name].resolve() for name in NEUTRAL_WHEELS}


def prepare_kit(
    destination: Path,
    wheel_paths: dict[str, Path],
    *,
    dependencies: Path | None = None,
) -> dict:
    """Create a complete extracted kit at an empty destination.

    Dependencies downloaded at build time are fully inventoried with hashes.
    Supply a directory with binary wheels for a hermetic builder in tests.
    """
    audited = _neutral_wheels(wheel_paths)
    hashes = inspect_wheels(audited)
    if destination.exists():
        raise ValueError("Kit staging destination already exists")
    destination.mkdir(parents=True)
    wheels_dir = destination / "wheels"
    wheels_dir.mkdir()
    with tempfile.TemporaryDirectory(prefix="eios-f5-10-package-") as temporary:
        sample = build_project_wheel(Path(temporary) / "sample")
        sample_hashes = audit_project_wheel(sample)
        module_hashes = {**hashes, **sample_hashes}
        if set(module_hashes) != set(MODULES):
            raise ValueError("Unexpected or missing source modules in technical onboarding kit")
        sources: dict[str, tuple[Path, str]] = {
            name: (path, "neutral") for name, path in audited.items()
        }
        sources["eios-maintenance-example"] = (sample, "example")
        if dependencies is None:
            dependency_dir = Path(temporary) / "third-party-dependencies"
            dependency_dir.mkdir()
            result = subprocess.run(
                [
                    sys.executable, "-m", "pip", "download",
                    "--only-binary=:all:", "--dest", str(dependency_dir),
                    "pydantic>=2,<3",
                ],
                cwd=destination, capture_output=True, text=True, timeout=180,
            )
            if result.returncode:
                raise RuntimeError(
                    "Cannot download platform-specific binary dependencies: "
                    + result.stderr[-3000:]
                )
        else:
            dependency_dir = dependencies.resolve()
            if not dependency_dir.is_dir():
                raise ValueError("Pre-resolved binary dependency directory missing")
        for path in dependency_dir.iterdir():
            if not path.is_file() or path.suffix != ".whl":
                raise ValueError("Unexpected non-wheel third-party dependency payload")
            name, _ = _wheel_identity(path)
            if name not in PERMITTED_DEPENDENCIES or name in sources:
                raise ValueError(f"Unapproved runtime wheel: {name}")
            sources[name] = (path, "dependency")
        if "pydantic" not in sources or "pydantic-core" not in sources:
            raise ValueError("Pydantic and pydantic-core wheels must be vendored")
        entries = []
        filenames = set()
        for name, (source, role) in sorted(sources.items()):
            actual_name, version = _wheel_identity(source)
            if actual_name != name or source.name in filenames:
                raise ValueError("Wheel identity does not match its approved logical name")
            if source.stat().st_size > MAX_BYTES:
                raise ValueError("Individual distribution exceeds size budget")
            filenames.add(source.name)
            target = wheels_dir / source.name
            shutil.copy2(source, target)
            entries.append({
                "name": name,
                "version": version,
                "filename": source.name,
                "sha256": digest_file(target),
                "bytes": target.stat().st_size,
                "role": role,
            })

    for source, name in (
        (SOURCE_CERTIFIER, "certify_deployment.py"),
        (SOURCE_README, "README.md"),
    ):
        shutil.copyfile(source, destination / name)
    entries.sort(key=lambda item: item["name"])
    lock = [
        f"{item['name']}=={item['version']} --hash=sha256:{item['sha256']}"
        for item in entries
    ]
    (destination / "requirements.lock").write_text(
        "\n".join(lock) + "\n", encoding="utf-8",
    )
    support_files = {
        name: digest_file(destination / name)
        for name in ("certify_deployment.py", "requirements.lock", "README.md")
    }
    manifest = {
        "format_version": 1,
        "purpose": PURPOSE,
        "platform": sys.platform,
        "python_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
        "machine": platform.machine(),
        "wheels": entries,
        "files": support_files,
        "module_hashes": module_hashes,
    }
    (destination / "manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    validate_kit(destination)
    return manifest


def archive_kit(source: Path, output: Path) -> Path:
    validate_kit(source)
    if output.exists():
        raise ValueError("Refusing to overwrite an existing technical onboarding ZIP")
    output.parent.mkdir(parents=True, exist_ok=True)
    members = sorted(file for file in source.rglob("*") if file.is_file())
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zip_file:
        for file in members:
            rel = file.relative_to(source).as_posix()
            info = zipfile.ZipInfo(rel)
            info.date_time = (2020, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zip_file.writestr(info, file.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)
    return output


def safe_extract_kit(bundle: Path, destination: Path) -> None:
    """Reject traversal, symlinks, duplicate files and zip bombs before writing."""
    if destination.exists():
        raise ValueError("Refusing to extract onto an existing target")
    if bundle.stat().st_size > MAX_TOTAL_UNCOMPRESSED:
        raise ValueError("Technical kit ZIP exceeds expected size budget")
    with zipfile.ZipFile(bundle) as archive:
        members = archive.infolist()
        if not (8 <= len(members) <= MAX_MEMBER_COUNT):
            raise ValueError("Unexpected technical kit ZIP item count")
        names = [x.filename for x in members]
        if len(set(names)) != len(names):
            raise ValueError("Duplicate technical kit ZIP path")
        total = 0
        for entry in members:
            name = entry.filename
            path = Path(name)
            if (
                name.startswith("/") or "\\" in name
                or path.is_absolute() or not path.parts
                or any(part in ("", ".", "..") for part in path.parts)
                or entry.is_dir()
            ):
                raise ValueError("Unsafe technical kit archive path")
            if ((entry.external_attr >> 16) & 0o170000) == 0o120000:
                raise ValueError("Symlinks are forbidden in technical kit archive")
            total += entry.file_size
            if entry.file_size > MAX_BYTES or total > MAX_TOTAL_UNCOMPRESSED:
                raise ValueError("Technical kit uncompressed size budget exceeded")
        destination.mkdir(parents=True)
        for entry in members:
            target = destination / entry.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(entry) as source, target.open("wb") as dest:
                shutil.copyfileobj(source, dest)
    validate_kit(destination)


def build(output_dir: Path, wheel_paths: dict[str, Path]) -> Path:
    with tempfile.TemporaryDirectory(prefix="eios-f5-10-stage-") as temp:
        staging = Path(temp) / "extracted"
        prepare_kit(staging, wheel_paths)
        output = output_dir.resolve() / BUNDLE_FILENAME
        result = archive_kit(staging, output)
        with tempfile.TemporaryDirectory(prefix="eios-f5-10-archive-audit-") as audit:
            safe_extract_kit(result, Path(audit) / "unpacked")
        return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("dist/release-kit"))
    for directory in ("kernel", "inputs", "catalog", "governance"):
        parser.add_argument(f"--{directory}-dir", type=Path, default=Path("dist") / directory)
    opts = parser.parse_args()
    wheels: dict[str, Path] = {}
    for dist in NEUTRAL_WHEELS:
        folder, pattern, _, _ = WHEEL_SPECS[dist]
        matches = list(getattr(opts, folder + "_dir").resolve().glob(pattern))
        if len(matches) != 1:
            parser.error(f"Expected exactly one wheel for {dist}: {len(matches)} found")
        wheels[dist] = matches[0]
    print(f"F5.10 auditable technical kit: {build(opts.output, wheels)}")


if __name__ == "__main__":
    main()
