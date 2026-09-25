# EIOS — Exportación Negotiation Intelligence de referencia v0.1

## DISEÑAR

Exportar las capturas NI de ambas variantes como sidecars JSON y presentarlas
en la revisión HTML de solo lectura.

## AUDITAR

La captura integrada en la PR #364 contiene fuentes C0-bound, resultado NI,
capacidad y terminal de una misma invocación. El fixture declara autoridad
negociadora y contenido ficticios; no hay mandato empresarial real ni prueba
de causalidad del texto desde C0, Twin o Viability.

## DEPURAR

La vista muestra objetivo, solicitud inicial, espera, número de justificaciones
y referencias C0. Explica el origen sintético de `AUTHORIZED` y los límites de
la traza. Valida cada sidecar antes de leerlo y escapa los valores dinámicos.

## AUDITAR 2

`--with-negotiation-intelligence` funciona solo o junto a las cinco
observaciones anteriores y Scenario Coordination. La demo ejecuta cada
variante una vez, produce la pareja de sidecars y HTML en un directorio nuevo.
`--verify-dir` detecta ambos sidecars, valida terminales, huellas, resultado
reproducido y HTML, y compara los JSON íntegros con los fixtures repetidos.
La CLI de la vista individual requiere también ambos archivos.

## CERRAR

Se mantienen `material_nature=SYNTHETIC`,
`qtg_mode_policy=SYNTHETIC_TEST_ONLY`, `operational_path=FORBIDDEN`,
`effect_scope=NO_OPERATIONAL_EFFECT` y `decision_authority=false`.
La captura no autoriza negociación ni contacto con un proveedor.

## MATERIALIZAR

Tras actualizar `main`, usar un directorio nuevo:

```powershell
python -m examples.reference_business_case_demo --output-dir reference-demo-ni --with-negotiation-intelligence
Invoke-Item .\reference-demo-ni\reference-review.html
python -m examples.reference_business_case_demo --verify-dir reference-demo-ni
```

Los sidecars son `reference-negative-negotiation-intelligence.json` y
`reference-negotiation-intelligence.json`. La vista individual acepta la
pareja `--negative-negotiation-intelligence` y
`--qtg-eligible-negotiation-intelligence`.

## CI

La suite y CI de la PR deben pasar antes de integrar.
