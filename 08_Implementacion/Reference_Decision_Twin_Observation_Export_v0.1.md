# EIOS — Exportación Decision Twin de referencia v0.1

## DISEÑAR

Exportar las comparaciones Decision Twin capturadas en la invocación O1 de
ambas variantes y presentarlas en la revisión HTML local como resultados
estructurales descriptivos.

## AUDITAR

La captura de la PR #360 vincula compra raíz, preparación, entradas Stage 2,
comparación, estado O1 y terminal. El fixture representa dos escenarios hijos
con `viability=VIABLE`, sin diferencias en los atributos aportados, sin
condiciones, consecuencias o referencias de riesgo y sin selección.

## DEPURAR

La vista valida ambos sidecars antes de representar sus valores y los escapa.
Nombra las referencias como representaciones transitorias, enseña viabilidad,
diferencias y faltantes y explica que ausencia de diferencias no acredita
equivalencia comercial universal. No ejecuta Stage 2 durante el renderizado.

## AUDITAR 2

La demo permite `--with-decision-twin` aislado o combinado con PRICE, TCO,
Supplier Risk/Value y C0. Cada variante se ejecuta una vez. La verificación
detecta la pareja de sidecars, coteja huellas y HTML, y repite el fixture para
comparar los JSON completos. Pruebas cubren 5 y 13 archivos, pareja ausente,
alteración del resultado y terminales sin cambio.

## CERRAR

La comparación no puntúa, prefiere ni selecciona. Conserva
`material_nature=SYNTHETIC`, `qtg_mode_policy=SYNTHETIC_TEST_ONLY`,
`operational_path=FORBIDDEN`, `effect_scope=NO_OPERATIONAL_EFFECT` y
`decision_authority=false`.

## MATERIALIZAR

Después de actualizar `main`, crear un directorio nuevo:

```powershell
python -m examples.reference_business_case_demo --output-dir reference-demo-twin --with-decision-twin
Invoke-Item .\reference-demo-twin\reference-review.html
python -m examples.reference_business_case_demo --verify-dir reference-demo-twin
```

Los sidecars son `reference-negative-decision-twin.json` y
`reference-decision-twin.json`. La vista individual acepta la pareja
`--negative-decision-twin` y `--qtg-eligible-decision-twin`.

## CI

La suite completa y la CI de la PR deben pasar antes de integrar.
