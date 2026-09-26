# EIOS — Exportación JSON de Negotiation Ladder v0.1

**Base:** `main @ 5860eda4a31817715e47c904430ac4d865f6ebd5`  
**Método:** DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI

## DISEÑAR

Exportar la estructura Ladder capturada en ambas variantes del caso sintético
como pareja de archivos JSON, sin añadir todavía una sección Ladder al HTML.

## AUDITAR

La captura integrada en la PR #366 valida fuentes C0-bound, estructura y
capacidad terminal. No prueba que el invocador NI separado produjera ese
mismo objeto, ni concede autoridad negociadora real.

## DEPURAR

`--with-negotiation-ladder` añade los sidecars
`reference-negative-negotiation-ladder.json` y
`reference-negotiation-ladder.json` al directorio nuevo de la demo. Cada
variante se ejecuta una vez. La exportación puede combinarse con las otras
observaciones sin modificar el terminal.

## AUDITAR 2

`--verify-dir` exige ambos sidecars, valida cada uno contra su terminal y
repite ambos fixtures para cotejar los JSON completos. El HTML existente se
verifica por separado y no presenta contenido Ladder. Las pruebas cubren el
modo aislado y combinado, pareja incompleta, cruce de variantes, alteración de
un paso y huellas terminales estables.

## CERRAR

La ruta sigue `FORBIDDEN`, el efecto `NO_OPERATIONAL_EFFECT`, el material
`SYNTHETIC`, la política QTG `SYNTHETIC_TEST_ONLY` y la autoridad decisional
`false`.

## MATERIALIZAR

Después de actualizar `main`, desde la raíz del repositorio y con un
directorio nuevo:

```powershell
python -m examples.reference_business_case_demo --output-dir reference-demo-ladder --with-negotiation-ladder
python -m examples.reference_business_case_demo --verify-dir reference-demo-ladder
```

## CI

Suite completa y CI de la PR necesarias antes de integrar.
