# EIOS — Exportación de observación C0/CRC v0.1

## DISEÑAR

Exportar las dos observaciones C0/CRC ya capturadas en la misma invocación
O1 y presentarlas en la revisión HTML local, sin convertir el consolidado
CRC en una instrucción empresarial.

## AUDITAR

El resultado C0/CRC contiene `Assessment`, `Trace`, `c0_capability`, CRC y
paquete de soporte. El `Trace` raíz del fixture recibía `created_at` del reloj
en cada ejecución. Su ID y el terminal se reproducían, pero el sidecar
completo no pasaba `--verify-dir` con igualdad de JSON. La entrada sintética
dispone de fecha de compra estable; el caso asigna al trace sintético las
00:00 UTC de esa fecha sin modificar su ID, Assessment ni resultado O1.

## DEPURAR

La vista valida ambos sidecars antes de representar datos y escapa el
contenido. Muestra QTG de cada variante, `R-DAT-003=FALSE`, la base CRC
`COMPRAR` declarada y el consolidado. Indica expresamente que C0 no deriva
causalmente del QTG de esa ejecución y que `COMPRAR` no es una orden. La
exportación sigue siendo una única ejecución por variante incluso si se
combinan PRICE, TCO y Supplier Risk/Value.

## AUDITAR 2

Pruebas: modalidad C0 aislada y combinada, igualdad completa en replay,
huellas terminales antiguas, QTG divergente, rechazo de pareja ausente y
sidecar modificado. Las opciones de exportación anteriores conservan su
formato y archivos.

## CERRAR

Material `SYNTHETIC`, política `SYNTHETIC_TEST_ONLY`, ruta `FORBIDDEN`,
efecto `NO_OPERATIONAL_EFFECT` y `decision_authority=false` permanentes.
`R-DAT-003=FALSE` de la variante negativa no equivale a QTG apto.

## MATERIALIZAR

Tras actualizar la copia local de `main`, usar un directorio nuevo:

```powershell
python -m examples.reference_business_case_demo --output-dir reference-demo-c0 --with-c0
Invoke-Item .\reference-demo-c0\reference-review.html
python -m examples.reference_business_case_demo --verify-dir reference-demo-c0
```

Los sidecars son `reference-negative-c0.json` y `reference-c0.json`. Para
incluir todas las observaciones, añadir `--with-price --with-tco
--with-supplier-risk` al primer comando y elegir otro directorio nuevo. La
vista individual admite la pareja `--negative-c0` y `--qtg-eligible-c0`.

## CI

La suite completa y CI de la PR deben concluir satisfactoriamente.
