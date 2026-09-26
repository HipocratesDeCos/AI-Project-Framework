# EIOS — Runner ejecutable del caso ficticio 002 v0.1

**Qué produce:** un paquete técnico de nueve JSON: un terminal de la
simulación y ocho observaciones de las capacidades ejecutadas en esa misma
llamada. Su estado es `PARTIALLY_COMPLETED` porque la fiabilidad del
proveedor no se ha determinado. C0 conserva `INFORMACIÓN INSUFICIENTE`.

## DISEÑAR → AUDITAR

`examples.reference_business_case_002` usa la fuente sintética compartida
002, la fachada `run_reference_operational_simulation` y los ocho
constructores observados existentes. QTG se produce y consume solo en
`SYNTHETIC_TEST` / `TEST_ONLY`. Los sidecars se cierran contra el terminal
de esa invocación y se validan con sus validadores existentes.

## DEPURAR → AUDITAR 2

La ejecución local produjo nueve JSON y su verificación repitió exactamente
el paquete. Dos ejecuciones independientes coincidieron en terminal y
sidecars. La prueba modifica `crc_result` en `reference-c0.json` y verifica
que la revisión lo rechaza. El inventario de archivos también debe ser
exacto. Las pruebas focalizadas del runner y las fuentes 002 dieron
19 resultados satisfactorios.

## CERRAR → MATERIALIZAR → CI

Desde la raíz del repositorio, en PowerShell:

```powershell
git pull --ff-only origin main
python -m examples.reference_business_case_002 --output-dir reference-demo-002
python -m examples.reference_business_case_002 --verify-dir reference-demo-002
```

El directorio de salida debe ser nuevo. El paquete contiene
`reference-result.json` y `reference-price.json`, `reference-tco.json`,
`reference-supplier-risk.json`, `reference-c0.json`,
`reference-decision-twin.json`, `reference-scenario-coordination.json`,
`reference-negotiation-intelligence.json` y
`reference-negotiation-ladder.json`. La verificación compara la repetición
exacta de cada archivo. Esta unidad no crea HTML ni presenta un dictamen
para un comprador real.

`QTG=APTO/ALTA` expresa calidad del input sintético, mientras que
`C0=INFORMACIÓN INSUFICIENTE` refleja un requisito todavía no vinculado.
`PARTIALLY_COMPLETED` describe el estado técnico agregado; ninguna de
esas etiquetas aprueba una compra. Se mantienen
`SYNTHETIC · SYNTHETIC_TEST_ONLY · FORBIDDEN · NO_OPERATIONAL_EFFECT · decision_authority=false`.
Integración sujeta a CI de PR.
