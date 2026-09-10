import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_MAP = ROOT / "03_Arquitectura" / "Framework_Map.md"
SECTION_DIRECTORIES = {
    "00": "00_Gobierno",
    "01": "01_Modelo",
    "02": "02_Parametros",
    "03": "03_Arquitectura",
    "04": "04_Reglas",
    "05": "05_Motor",
    "06": "06_SQL",
    "07": "07_Pruebas",
    "08": "08_Implementacion",
}
ACTIVE_NAVIGATION_DOCUMENTS = (
    ROOT / "00_Gobierno" / "Manual_Maestro_Proyecto_EIOS.md",
    ROOT / "00_Gobierno" / "Project_Context.md",
    ROOT / "00_Gobierno" / "Project_Governance.md",
    ROOT / "00_Gobierno" / "Matriz_Autoridad_Documental.md",
    FRAMEWORK_MAP,
)
OBSOLETE_REFERENCES = (
    "`00_Gobierno/EIOS_Assurance_Framework.md`",
    "`EIOS_Assurance_Framework.md`",
    "`03_LEEME_Como_se_organiza_EIOS.md`",
)
RETIRED_DOCUMENT_PATHS = (
    ROOT / "00_Gobierno" / "EIOS_Assurance_Framework.md",
    ROOT / "03_Arquitectura" / "03_LEEME_Como_se_organiza_EIOS.md",
)


def _section(text: str, number: str) -> str:
    match = re.search(
        rf"^## {number} —.*?(?=^## \d{{2}} —|^---\s*$\n\s*# 3\.)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match is not None, f"No se encontró la sección {number} en Framework Map"
    return match.group(0)


@pytest.mark.parametrize("document", ACTIVE_NAVIGATION_DOCUMENTS)
def test_active_navigation_does_not_reference_retired_documents(document: Path):
    text = document.read_text(encoding="utf-8")
    for reference in OBSOLETE_REFERENCES:
        assert reference not in text, f"Referencia retirada {reference} en {document.relative_to(ROOT)}"


@pytest.mark.parametrize("path", RETIRED_DOCUMENT_PATHS)
def test_retired_document_paths_remain_absent(path: Path):
    assert not path.exists(), f"Documento retirado reaparecido sin ciclo de autoridad: {path.relative_to(ROOT)}"


@pytest.mark.parametrize("number,directory", SECTION_DIRECTORIES.items())
def test_framework_map_current_documents_exist(number: str, directory: str):
    text = FRAMEWORK_MAP.read_text(encoding="utf-8")
    listed = re.findall(
        r"^(?:-|\d+\.) `([^`]+\.(?:md|sql))`$",
        _section(text, number),
        flags=re.MULTILINE,
    )
    assert listed, f"La sección {number} no contiene inventario verificable"
    missing = [name for name in listed if not (ROOT / directory / name).is_file()]
    assert missing == [], f"Documentos declarados como actuales pero ausentes: {missing}"
