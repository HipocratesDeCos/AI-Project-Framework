# EIOS — TCO de la segunda empresa ficticia v0.1

**Resultado:** el constructor observado existente calcula el coste de
adquisición de la compra 002 (`15 × 21,00 EUR = 315,00 EUR`) usando el
material sintético del segundo bundle. No hay costes atribuibles adicionales
declarados; «completo» significa completo para los componentes suministrados,
no un coste empresarial total verificado.

## DISEÑAR → AUDITAR

El fixture 002 proporciona la compra y el contexto canónicos. El adaptador
existente construye el bundle, la clasificación liga `REF-BUSINESS-002` al
bundle exacto y `TCOInput` recibe esa misma compra. El constructor observado
TCO verifica la identidad de compra y decisión al invocarse una sola vez.

## DEPURAR → AUDITAR 2

La prueba positiva compara artículo, proveedor, cantidad y precio del fixture,
el valor calculado, los componentes, la captura y la ejecución. La prueba
adversa cambia la cantidad en la invocación: el constructor rechaza la mezcla
con el input congelado y no deja captura disponible. No se copian importes ni
dictámenes del caso 001.

La procedencia conserva
`SYNTHETIC · SYNTHETIC_TEST_ONLY · FORBIDDEN · NO_OPERATIONAL_EFFECT · decision_authority=false`.

## CERRAR → MATERIALIZAR → CI

Se añade `tests/test_second_synthetic_company_tco.py`; no cambia el motor,
la fachada ni los contratos. Es una **captura de capacidad aislada en prueba**:
todavía no existe terminal de ocho capacidades para 002, ni sidecar TCO
cerrado contra tal terminal, ni paquete HTML 002. La siguiente fuente a
materializar será PRICE, con referencias de precio declaradas para 002.

Verificación local focalizada: ocho pruebas satisfactorias (bundle 002,
observación TCO 001 y material TCO 002). La CI de PR decidirá su integración.
