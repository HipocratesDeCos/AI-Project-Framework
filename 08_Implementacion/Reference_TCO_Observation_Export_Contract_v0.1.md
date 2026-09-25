# EIOS — Exportación de observación TCO de referencia v0.1

## DISEÑAR

Exportar la captura TCO de la ejecución sintética de ambas variantes en dos
sidecars JSON y presentarla en la revisión HTML local. El terminal existente
conserva su formato y sus huellas. `--with-tco` puede combinarse con
`--with-price`; cada variante se ejecuta una vez y ambas observaciones se
capturan en las invocaciones admitidas en O1.

## AUDITAR

La unidad de captura anterior proporciona `ReferenceTCOObservation`, una
validación de sidecar separado y un invocador de un solo uso. La demo exporta
dos terminales y HTML, con dos sidecars PRICE opcionales. Su verificador
detecta sidecars y repite las variantes con los fixtures vigentes.

## DEPURAR

La ruta TCO usa exclusivamente el resultado capturado; no vuelve a calcular
TCO para construir el HTML. Se conservan los modos anteriores de tres y cinco
archivos. Los pares incompletos se rechazan antes de repetir ejecuciones. La
vista valida las observaciones antes de representar sus datos, escapa el
contenido y no atribuye trazas que el productor no proporcionó.

## AUDITAR 2

Las pruebas comprueban exportación y repetición para TCO solo y combinado,
igualdad de huellas terminales, precio y coste en secciones distintas,
rechazo de sidecar faltante o modificado y preservación de la demo anterior.

## CERRAR

El valor `205.00 EUR` corresponde a la adquisición modelada de 10 unidades
del fixture: `ACQUISITION` es el único componente aportado. La ausencia de
otros costes atribuibles en la entrada no equivale a un coste real cero. La
vista no compara el total TCO con el precio de referencia unitario PRICE ni
infiere ahorro. Permanece `SYNTHETIC_TEST_ONLY`, `FORBIDDEN`,
`NO_OPERATIONAL_EFFECT` y `decision_authority=false`.

## MATERIALIZAR

```powershell
python -m examples.reference_business_case_demo --output-dir reference-demo-tco --with-tco
Invoke-Item .\reference-demo-tco\reference-review.html
python -m examples.reference_business_case_demo --verify-dir reference-demo-tco
```

Para exportar también PRICE desde las mismas ejecuciones:

```powershell
python -m examples.reference_business_case_demo --output-dir reference-demo-analytical --with-price --with-tco
python -m examples.reference_business_case_demo --verify-dir reference-demo-analytical
```

Los sidecars TCO son `reference-negative-tco.json` y `reference-tco.json`.
La vista independiente también admite `--negative-tco` y
`--qtg-eligible-tco` como pareja, además de la pareja PRICE existente.

## CI

La suite local y CI de la PR deben pasar antes de integrar.
