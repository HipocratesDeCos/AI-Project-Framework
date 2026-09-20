# EIOS — PROJECTION_ONLY Mock Dataset Validator Contract v0.1

**Estado:** CERRADO — MATERIALIZADO

**Baseline de diseño:** `main @ 66afe664b741d5da147f90d80d48adcb833cbd08`

## 1. DISEÑAR

Se materializa `EIOS-PROJECTION-ONLY-MOCK-DATASET-01` mediante un manifiesto JSON, trece componentes sintéticos y un cargador estructural. La salida es material inmutable ligado por hash; no es un objeto de dominio ni una entrada operacional.

El manifiesto fija `SYNTHETIC`, `PROJECTION_ONLY` y `NO_OPERATIONAL_EFFECT`, inventario lógico exacto, rutas relativas y SHA-256 de cada archivo.

## 2. AUDITAR

Riesgos controlados: promoción operacional, traversal, rutas absolutas o Windows, aliases de componentes, archivos omitidos o añadidos, enlaces simbólicos, sustitución de bytes, campos de manifiesto no autorizados y resultados QTG inyectados.

## 3. DEPURAR

Se excluyen el mapeo hacia modelos EIOS, la validación semántica empresarial, la ejecución financiera, el productor QTG y cualquier inferencia de autoridad. `OP-2026-001` solo identifica la fixture sintética.

## 4. AUDITAR 2

La API solo acepta un `Path` de directorio no simbólico. Rechaza por defecto cualquier diferencia respecto del conjunto cerrado de archivos y campos. Conserva los bytes exactos y expone copias o vistas inmutables. El fingerprint depende del manifiesto admitido y de metadatos recomputados de los trece componentes.

## 5. CERRAR

La frontera se cierra como **admisión estructural de Mock Data**. Una unidad posterior deberá diseñar explícitamente el adaptador semántico antes de construir contratos canónicos.

## 6. MATERIALIZAR

- `eios/core/projection_mock_dataset.py`: validador fail-closed.
- `tests/fixtures/projection_only_mock_dataset_01/`: paquete sintético reproducible.
- `tests/test_projection_mock_dataset.py`: invariantes positivos y negativos.

QTG continúa sin habilitarse y no se declara resultado esperado alguno.

## 7. CI

La suite focal y la suite completa deben superar el mismo commit exacto antes del merge. La modificación local ajena de `Viability_Frontier_Scenario_Analytics_Integration_Contract_v0.1.md` queda excluida.
