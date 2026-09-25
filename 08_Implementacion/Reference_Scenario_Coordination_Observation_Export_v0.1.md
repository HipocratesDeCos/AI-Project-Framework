# EIOS — Exportación Scenario Coordination de referencia v0.1

## DISEÑAR

Exportar el paquete O2 capturado en la misma invocación del caso de referencia
para sus variantes negativa y QTG elegible, y mostrar una vista de solo lectura.

## AUDITAR

La captura cerrada en la PR #362 liga fuentes Stage 2, soporte O2, capacidad
`SCENARIO_COORDINATION` y huella terminal. El productor reconstruye el soporte
desde fuentes con provenance validada. Las dos variantes tienen dos escenarios
`COMPLETED` y viabilidad `VIABLE`.

## DEPURAR

La vista valida la pareja de sidecars antes de representarla y escapa los
valores dinámicos. Enseña identidad, estado, viabilidad y trazas por escenario.
Aclara que `O2Comparison.differences.viability_result` compara objetos
completos que incluyen distintos `scenario_id`; no constituye una diferencia
en el estado de viabilidad ni una preferencia empresarial.

## AUDITAR 2

La demo genera dos JSON y HTML en un directorio nuevo. Permite
`--with-scenario-coordination` aislado o junto a PRICE, TCO, Supplier Risk,
C0 y Decision Twin. Cada variante se ejecuta una vez. `--verify-dir` exige
ambos sidecars, valida huellas y HTML, y repite los dos fixtures para comparar
los JSON completos. La vista individual también exige ambas variantes.

## CERRAR

Se conserva `selected_scenario=null`, `material_nature=SYNTHETIC`,
`qtg_mode_policy=SYNTHETIC_TEST_ONLY`, `operational_path=FORBIDDEN`,
`effect_scope=NO_OPERATIONAL_EFFECT` y `decision_authority=false`.
`COMPLETED` es un estado técnico; no supone admisión QTG ni autorización.

## MATERIALIZAR

Después de actualizar `main`, crear un directorio nuevo:

```powershell
python -m examples.reference_business_case_demo --output-dir reference-demo-scenarios --with-scenario-coordination
Invoke-Item .\reference-demo-scenarios\reference-review.html
python -m examples.reference_business_case_demo --verify-dir reference-demo-scenarios
```

Los sidecars son `reference-negative-scenario-coordination.json` y
`reference-scenario-coordination.json`. La vista individual acepta la pareja
`--negative-scenario-coordination` y `--qtg-eligible-scenario-coordination`.

## CI

La suite completa y CI de la PR deben pasar antes de integrar.
