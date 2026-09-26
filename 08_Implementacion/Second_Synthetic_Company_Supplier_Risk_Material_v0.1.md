# EIOS — Material de riesgo de proveedor para empresa ficticia 002 v0.1

**Resultado de prueba:** la fiabilidad del proveedor 002 es
`NOT_DETERMINABLE` (no determinable). La invocación termina
`PARTIALLY_COMPLETED` porque hay una dimensión sin resolver. No se califica
al proveedor como favorable ni adverso y no se compara su valor con otro.

## DISEÑAR → AUDITAR

El evaluador factual recibe compra, contexto y `COMPANY-MOCK-002` desde el
bundle 002, sin observaciones, historial, métricas, señales ni candidatos.
La capa externa recibe una **declaración sintética explícita** de riesgo no
determinable, con autoridad, evidencia y traza `ref-business-002` propias.
Se reutiliza el constructor observado existente.

## DEPURAR → AUDITAR 2

La prueba confirma identidad de empresa y proveedor, inventario factual
vacío, una dimensión `RELIABILITY=NOT_DETERMINABLE`, cero dimensiones de
valor, elemento pendiente y estado parcial. También prueba que una compra
con otro proveedor se rechaza antes de capturar resultado y que el invocador
válido se ejecuta una sola vez.

La evidencia demuestra la **declaración dentro de la simulación**; no
aporta hechos comerciales sobre el proveedor. El estado parcial no declara
un riesgo real. La procedencia conserva
`SYNTHETIC · SYNTHETIC_TEST_ONLY · FORBIDDEN · NO_OPERATIONAL_EFFECT · decision_authority=false`.

## CERRAR → MATERIALIZAR → CI

Se añade `tests/test_second_synthetic_company_supplier_risk.py`; no se
modifican motor, contratos, fixture ni runner 001. Es una captura de
capacidad aislada en prueba: todavía no hay terminal E2E 002 ni sidecar
cerrado contra él. El siguiente bloque debe preparar C0 con requisitos y
trazas propios del caso 002, sin inferir una decisión desde PRICE o TCO.

Verificación local focalizada: trece pruebas satisfactorias (material 002
de proveedor, PRICE, TCO y bundle, más observación del proveedor 001).
Integración sujeta a CI de PR.
