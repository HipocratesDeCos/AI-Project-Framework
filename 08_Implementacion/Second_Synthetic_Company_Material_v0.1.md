# EIOS — Material de una segunda empresa ficticia v0.1

**Resumen:** un segundo expediente sintético pasa el mismo cargador y adaptador
que el caso 001. Esto demuestra reutilización de la frontera de material;
todavía no demuestra un segundo runner con ocho capacidades.

## Conceptos

| Término | En esta prueba |
|---|---|
| **Fixture 002** | Trece JSON de una empresa ficticia nueva y un manifiesto con hashes. |
| **Bundle** | Material canónico que construye el adaptador existente a partir de esos JSON. |
| **Procedencia** | Etiqueta vinculada al bundle: sintético, sin efectos ni autoridad decisional. |

## DISEÑAR → AUDITAR

Se parte de la estructura semántica completa del fixture QTG elegible 001.
Se declara otra identidad (`COMPANY-MOCK-002`), otra compra (`15 × 21.00 EUR`),
otra cuota y flujo (`315 EUR`), identificadores vinculados propios y
`dataset_id=EIOS-REFERENCE-BUSINESS-002-SEMANTIC`. El importe y la moneda de
la compra, calendario y flujo son coherentes. Los criterios metodológicos
`CRITERION-MOCK-001` a `006` se conservan como referencias comunes: cambiar
indiscriminadamente `001` generaba una colisión con el criterio `002`,
rechazada físicamente por el adaptador durante la auditoría.

Los trece archivos se serializan en UTF-8 y el manifiesto liga sus bytes por
SHA-256. No se añaden defaults, atajos de validación ni contratos nuevos.

## DEPURAR → AUDITAR 2

La carga y el adaptador existentes producen un bundle distinto con la compra
de la empresa 002. `classify_reference_operational_simulation` liga
`REF-BUSINESS-002` a ese bundle y conserva:

`SYNTHETIC · SYNTHETIC_TEST_ONLY · FORBIDDEN · NO_OPERATIONAL_EFFECT · decision_authority=false`.

Una prueba adversa cambia `finance_input.company_id` a la empresa 001 y
actualiza deliberadamente el hash del manifiesto. El cargador admite los
bytes íntegros, pero el adaptador rechaza la mezcla con
`Financial snapshot company/context mismatch`. Así se distingue la
integridad física de la coherencia entre empresas.

## CERRAR

Queda probado el tramo **dataset → bundle → procedencia sintética** para
una segunda empresa. No se ejecutó QTG, la fachada de referencia, PRICE,
TCO, Supplier Risk/Value, C0/CRC, Decision Twin, Scenario Coordination,
Negotiation Intelligence ni Ladder. Tampoco existe todavía paquete HTML para
el caso 002. Ningún resultado del 001 se traslada como dictamen del 002.

La próxima unidad inventariará el material propio requerido por cada
invocador antes de intentar un segundo E2E. No se modifica el runner fijo del
001 para aceptar una carpeta arbitraria.

## MATERIALIZAR → CI

Archivos: `tests/fixtures/reference_business_case_002_semantic/` y
`tests/test_second_synthetic_company_bundle.py`. Ejecutar las pruebas
focalizadas y la suite completa; integrar solo con CI satisfactoria.
