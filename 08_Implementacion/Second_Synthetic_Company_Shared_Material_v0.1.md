# EIOS — Fuente única del material sintético 002 v0.1

**Resultado:** las declaraciones del caso ficticio 002 residen en
`examples/reference_business_case_002_material.py`. Los tests de TCO,
PRICE, proveedor, C0, escenarios y negociación importan esa fuente; un
futuro runner podrá hacerlo sin importar módulos de test.

## DISEÑAR → AUDITAR

Se extrajeron los preparadores que ya habían pasado pruebas aisladas. El
módulo carga el fixture 002 y ensambla inputs tipados mediante los productores
existentes. Conserva precios de referencia declarados, riesgo
`NOT_DETERMINABLE`, requisito C0 `UNDETERMINED`, trazas deterministas,
dos escenarios hijos y contenido de solicitud de información.

## DEPURAR → AUDITAR 2

Las pruebas importan funciones del módulo compartido y mantienen las
comprobaciones de identidad, estado, procedencia, rechazo adverso y
reproducibilidad. Se eliminaron de ellas los preparadores duplicados. La
suite focalizada de siete archivos, incluido el bundle, dio 17 pruebas
satisfactorias. El nuevo módulo no depende de `tests/test_*.py`; sus datos
ficticios siguen viviendo en el fixture físico 002.

## CERRAR → MATERIALIZAR → CI

Esta unidad establece una fuente reutilizable, sin cambiar motores,
contratos ni la fachada. **Aún no existe runner público 002 ni paquete de
revisión.** La siguiente unidad conectará estas funciones a
`run_reference_operational_simulation`, capturará resultados de la misma
invocación y comprobará repetición exacta. El estado previsto sigue siendo
`PARTIALLY_COMPLETED`, con riesgo no determinable y C0 que conserva
`INFORMACIÓN INSUFICIENTE`.

La ruta mantiene
`SYNTHETIC · SYNTHETIC_TEST_ONLY · FORBIDDEN · NO_OPERATIONAL_EFFECT · decision_authority=false`.
Integración sujeta a CI de PR.
