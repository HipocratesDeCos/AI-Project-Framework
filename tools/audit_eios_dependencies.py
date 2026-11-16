"""F4.1 read-only architecture inventory for EIOS.

Run: python tools/audit_eios_dependencies.py [--json]
Only Python static imports are inspected. This is not a dynamic dependency,
distribution-isolation or multi-project compatibility certification.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import json
from pathlib import Path
import tomllib


SCHEMA = "EIOS-F4-1-STATIC-DEPENDENCIES-01"


def module_name(path: Path, root: Path) -> str:
    parts = list(path.relative_to(root).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def family(module: str) -> str:
    if module.startswith("eios.company_") or module == "eios.company_app":
        return "company_application"
    if module == "eios.frontend" or module.startswith("eios.frontend."):
        return "frontend"
    if module == "eios.mvp" or module == "eios.vertical_orchestration":
        return "vertical_entry"
    if module == "eios.core" or module.startswith("eios.core."):
        return "named_core"
    if module == "eios.parameters" or module.startswith("eios.parameters."):
        return "parameters"
    if module.startswith("eios."):
        return "specialized_or_support"
    return "external"


def _resolve_import_from(node: ast.ImportFrom, current_module: str, is_package: bool = False) -> str:
    if not node.level:
        return node.module or ""
    # A source eios.core.foo has package eios.core; '.' stays there,
    # '..' goes to eios. A package initializer is passed as its own module.
    package = current_module.split(".") if is_package else current_module.split(".")[:-1]
    if node.level > len(package):
        return ""
    base = package[: len(package) - node.level + 1]
    if node.module:
        base.extend(node.module.split("."))
    return ".".join(base)


def static_imports(source: str, current_module: str, known: set[str], is_package: bool = False) -> set[str]:
    """Return resolved import *modules*, not guessed symbols or invocations."""
    parsed = ast.parse(source, filename=current_module + ".py")
    imported: set[str] = set()
    for node in ast.walk(parsed):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("eios."):
                    imported.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            parent = _resolve_import_from(node, current_module, is_package=is_package)
            if not parent.startswith("eios"):
                continue
            for alias in node.names:
                candidate = parent + "." + alias.name
                imported.add(candidate if candidate in known else parent)
    return imported


def audit(root: Path) -> dict:
    root = Path(root)
    files = sorted((root / "eios").rglob("*.py"))
    if not files:
        raise ValueError("No eios/*.py source files found")
    known = {module_name(path, root) for path in files}
    groups = Counter()
    edges: set[tuple[str, str]] = set()
    parse_failures: list[dict] = []
    for path in files:
        source = module_name(path, root)
        groups[family(source)] += 1
        try:
            content = path.read_text(encoding="utf-8")
            imports = static_imports(content, source, known, is_package=path.name == "__init__.py")
        except (OSError, UnicodeDecodeError, SyntaxError) as exc:
            parse_failures.append({"file": str(path.relative_to(root)), "error": str(exc)})
            continue
        edges.update((source, dest) for dest in imports if dest in known and dest != source)

    edge_items = sorted(edges)
    direct_app_coupling = [
        {"source": a, "target": b} for a, b in edge_items
        if family(a) in ("named_core", "parameters")
        and family(b) in ("company_application", "frontend", "vertical_entry")
    ]
    core_specialized_coupling = [
        {"source": a, "target": b} for a, b in edge_items
        if family(a) == "named_core" and family(b) == "specialized_or_support"
    ]
    core_to_parameters = [
        {"source": a, "target": b} for a, b in edge_items
        if family(a) == "named_core" and family(b) == "parameters"
    ]
    # Syntactic domain naming inside the physical core is a follow-up review
    # signal only. No amount of static scanning proves runtime portability.
    core_purchase_contracts = sorted(
        str(p.relative_to(root)) for p in files
        if p.relative_to(root).as_posix().startswith("eios/core/")
        and "PurchaseOperation" in p.read_text(encoding="utf-8")
    )

    packaging = {"name": None, "find_include": [], "dependencies": []}
    config = root / "pyproject.toml"
    if config.is_file():
        data = tomllib.loads(config.read_text(encoding="utf-8"))
        project = data.get("project", {})
        packages = data.get("tool", {}).get("setuptools", {}).get("packages", {}).get("find", {})
        packaging = {
            "name": project.get("name"),
            "find_include": packages.get("include", []),
            "dependencies": project.get("dependencies", []),
        }

    return {
        "schema": SCHEMA,
        "analysis": "STATIC_IMPORTS_ONLY_NOT_RUNTIME_OR_PORTABILITY_CERTIFICATION",
        "python_source_count": len(files),
        "module_family_counts": dict(sorted(groups.items())),
        "internal_import_edge_count": len(edges),
        "parse_failures": parse_failures,
        "direct_core_or_parameters_to_application": direct_app_coupling,
        "core_to_specialized_or_support": core_specialized_coupling,
        "core_to_parameters": core_to_parameters,
        "core_files_containing_purchase_contract_name": core_purchase_contracts,
        "packaging": packaging,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true", help="Print deterministic JSON report")
    args = parser.parse_args()
    result = audit(args.root)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print(f"F4.1 static audit: {result['python_source_count']} files, "
              f"{result['internal_import_edge_count']} internal import edges")
        print("Module families:", json.dumps(result["module_family_counts"], sort_keys=True))
        for group in (
            "direct_core_or_parameters_to_application",
            "core_to_specialized_or_support",
            "core_to_parameters",
            "parse_failures",
        ):
            print(group + ":", len(result[group]))
            for item in result[group]:
                print(" ", json.dumps(item, sort_keys=True))
        print("Package:", json.dumps(result["packaging"], sort_keys=True))


if __name__ == "__main__":
    main()
