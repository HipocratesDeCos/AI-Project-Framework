# EIOS — Higiene de compatibilidad del runtime v0.1

**Estado:** CERRADO — MATERIALIZADO — INTEGRADO EN `main` — CI VALIDADO
**Baseline:** `1686f0fe5b9a2f9947777214bacb9c7a00d2f5b6`
**Ámbito:** pruebas C0/O2 y artefactos locales del runtime Python

## 1. DISEÑAR

Eliminar dos advertencias reproducibles de Pydantic y evitar que la ejecución local ensucie el árbol de trabajo, sin modificar contratos, modelos ejecutables, resultados, identidades, trazabilidad ni autoridad decisional.

La unidad queda limitada a pruebas y configuración de exclusión de artefactos. No reabre C0, O2 ni U1.1.

## 2. AUDITAR

La suite completa sobre Python 3.13 y Pydantic 2.13.5 produjo `265 passed` y dos advertencias:

- `PydanticSerializationUnexpectedValue` al introducir un `float` mediante `model_copy(update=...)` en un campo decimal del test C0;
- `PydanticDeprecatedSince211` al consultar `model_fields` desde una instancia O2.

La ejecución también generó directorios `__pycache__` y metadatos `*.egg-info` no cubiertos por el `.gitignore` local. La búsqueda global confirmó un único acceso obsoleto a `model_fields`; los demás usos de `model_copy(update=...)` no emitieron advertencias.

## 3. DEPURAR

- El test C0 conserva el tipo canónico mediante `Decimal("99.99")`.
- El test O2 consulta los campos mediante `type(failed).model_fields`.
- `.gitignore` excluye `__pycache__/`, `*.py[cod]`, `*.egg-info/` y `.pytest_cache/`.

Las aserciones y comportamientos comprobados permanecen invariantes.

## 4. AUDITAR 2

Resultado:

- `265 passed`;
- advertencias `PydanticDeprecationWarning` y `UserWarning` promovidas a error;
- cero fallos y cero advertencias;
- ningún archivo bajo `eios/`, contrato funcional, SQL o workflow CI modificado;
- diff limitado a dos tests, `.gitignore` y este expediente.

## 5. CERRAR

No queda defecto reproducible dentro del alcance. Cualquier warning distinto o fallo funcional constituye una incidencia nueva y no autoriza a ampliar esta unidad.

## 6. MATERIALIZAR

La materialización conserva exactamente el comportamiento anterior y corrige únicamente la fidelidad de tipos en fixtures, el uso de la API pública vigente y la higiene del árbol local.

## 7. CI

La validación local reproduce el job Python de `.github/workflows/tests.yml`.

- Materialización: `ac25749e410f37786fdc46d0d757675463172091`.
- Pull request: #38.
- CI del head materializado: run `34517960658` — SUCCESS.
- Integración en `main`: `da5352565d0547c65f5807f299e64a1b9adaf80f`.
- CI post-merge: run `34518234149` — SUCCESS.

La unidad queda validada por CI sobre el commit materializado y sobre el merge efectivo en `main`.
