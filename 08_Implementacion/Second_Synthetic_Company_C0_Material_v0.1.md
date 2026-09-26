# EIOS — Material C0 de la empresa ficticia 002 v0.1

**Resultado de prueba:** el requisito de calidad de proyección queda
`UNDETERMINED` en el expediente de suficiencia C0 del caso 002. R-DAT-003
detecta el requisito no resuelto y CRC conserva
`INFORMACIÓN INSUFICIENTE`. Es un resultado de apoyo sintético, sin
autoridad decisional.

## DISEÑAR → AUDITAR

El bundle 002 suministra compra, decisión, escenario y snapshot. Se crea un
requirement set propio de `COMPANY-MOCK-002`, ligado por fingerprint a esa
compra; un binding clasifica `REQ-PROJECTION-QUALITY` como indeterminado.
El productor existente genera la observación de suficiencia y se evalúa la
regla autorizada R-DAT-003, con su Assessment y Trace reproducible.

La exploración QTG `APTO/ALTA` realizada sobre el bundle no es una evidencia
de requisito admitida automáticamente por C0. Falta una fuente formal que
establezca ese vínculo, por lo que no se marca el requisito `SATISFIED`.
El resultado base suministrado es `INFORMACIÓN INSUFICIENTE`; PRICE, TCO y
Supplier Risk/Value no lo generan ni lo autorizan.

## DEPURAR → AUDITAR 2

El invocador observado existente acepta el binding C0 de la empresa 002,
captura Assessment, Trace y CRC de la misma llamada y rechaza una compra
con otro proveedor mediante su fingerprint. La prueba comprueba la
procedencia sintética, una única invocación y que la regla produce `TRUE`
ante el requisito indeterminado. No se han alterado reglas ni prioridad CRC.

## CERRAR → MATERIALIZAR → CI

Se añade `tests/test_second_synthetic_company_c0.py`. Es una captura C0
aislada en prueba; todavía no existe terminal E2E 002 ni sidecar C0 cerrado
contra él. Para escenarios hijos deberán producirse bindings y trazas
distintos sobre cada compra hija. La ruta mantiene
`SYNTHETIC · SYNTHETIC_TEST_ONLY · FORBIDDEN · NO_OPERATIONAL_EFFECT · decision_authority=false`.

Verificación local focalizada: catorce pruebas satisfactorias (C0, proveedor,
PRICE, TCO y bundle 002, más observación C0 del caso 001). Integración sujeta
a CI de PR.
