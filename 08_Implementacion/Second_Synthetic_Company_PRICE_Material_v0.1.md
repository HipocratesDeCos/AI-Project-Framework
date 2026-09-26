# EIOS — Material PRICE de la segunda empresa ficticia v0.1

**Resultado de prueba:** dos referencias de precio **declaradas** para el
artículo ficticio 002 (`20,00` y `22,00 EUR`) producen una mediana de
`21,00 EUR`. Ese precio de referencia no procede de transacciones reales ni
constituye recomendación de compra.

## DISEÑAR → AUDITAR

Se reutilizan el adaptador del dataset 002, la clasificación de procedencia y
el constructor PRICE observado. El ejemplo 001 contiene precios y evidencias
propios; se preparan nuevos identificadores `REF-PRICE-TX-002-A/B`, pruebas de
validación sintética y declaraciones temporales, de representatividad y de
suficiencia específicas. La compra y el contexto vienen del bundle 002.

## DEPURAR → AUDITAR 2

La prueba verifica los dos identificadores seleccionados, la mediana, la
captura del mismo resultado adaptado y la ejecución de un solo uso. Una compra
con otro proveedor se rechaza antes de que exista captura. El estado
`PR_AVAILABLE` significa que **las dos referencias suministradas cumplen las
declaraciones sintéticas de esta prueba**; no verifica un mercado ni demuestra
que los precios sean suficientes para una empresa real.

La procedencia conserva
`SYNTHETIC · SYNTHETIC_TEST_ONLY · FORBIDDEN · NO_OPERATIONAL_EFFECT · decision_authority=false`.

## CERRAR → MATERIALIZAR → CI

Se añade `tests/test_second_synthetic_company_price.py`. Esta unidad solo
materializa fuentes y captura PRICE aisladas: no hay terminal E2E, observación
PRICE cerrada contra terminal ni paquete visual 002. No se modifica el motor
PRICE ni se transporta una evaluación del caso 001. La siguiente unidad debe
examinar Supplier Risk/Value y distinguir datos faltantes de hipótesis
sintéticas declaradas.

Verificación local focalizada: doce pruebas satisfactorias, incluidas las de
bundle 002, TCO 002 y observación PRICE 001. Integración sujeta a CI de PR.
