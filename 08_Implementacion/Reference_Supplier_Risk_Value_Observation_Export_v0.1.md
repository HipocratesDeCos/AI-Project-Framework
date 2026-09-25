# EIOS — Exportación de Supplier Risk/Value sintético v0.1

## DISEÑAR

Presentar la captura de la evaluación externa sintética del caso de
referencia, con un sidecar por variante y una sección legible en la revisión
HTML. El usuario puede combinar `--with-supplier-risk` con `--with-price` y
`--with-tco` sin ejecutar dos veces una variante.

## AUDITAR

La captura de la PR #354 vincula compra completa, resultado y estado O1 a un
terminal sintético. El fixture no aporta candidatos, observaciones, hechos
históricos, métricas, señales ni comparaciones estructurales. Declara
externamente `RELIABILITY=FAVORABLE` y ninguna dimensión Value.

## DEPURAR

El HTML valida la pareja de sidecars antes de representar los datos y escapa
sus valores. Muestra el inventario factual, la dimensión Risk y la ausencia
de comparación Value. Explica que la evaluación declarada no demuestra
desempeño factual ni recomienda seleccionar al proveedor. No produce de
nuevo el resultado para dibujar la vista.

## AUDITAR 2

Las pruebas verifican la modalidad aislada y la combinación de las tres
observaciones, huellas terminales, repetición de fixtures, parejas completas
y rechazo de resultados alterados. Los modos previos de tres, cinco y siete
archivos conservan su formato y comportamiento.

## CERRAR

Esta vista es validación de producto con material `SYNTHETIC`, política
`SYNTHETIC_TEST_ONLY`, ruta `FORBIDDEN`, efecto `NO_OPERATIONAL_EFFECT` y
`decision_authority=false`. `FAVORABLE` permanece una declaración externa
ficticia, no una inferencia sobre proveedores reales.

## MATERIALIZAR

Tras actualizar la copia local de `main`, crear un directorio nuevo:

```powershell
python -m examples.reference_business_case_demo --output-dir reference-demo-supplier --with-supplier-risk
Invoke-Item .\reference-demo-supplier\reference-review.html
python -m examples.reference_business_case_demo --verify-dir reference-demo-supplier
```

Para reunir PRICE, TCO y Supplier Risk/Value en la misma ejecución por
variante, usar `--with-price --with-tco --with-supplier-risk` con otro
directorio nuevo. Los sidecars son `reference-negative-supplier-risk.json` y
`reference-supplier-risk.json`. La vista individual acepta las opciones
`--negative-supplier-risk` y `--qtg-eligible-supplier-risk` como pareja.

## CI

La integración requiere la suite completa y CI satisfactoria en PR.
