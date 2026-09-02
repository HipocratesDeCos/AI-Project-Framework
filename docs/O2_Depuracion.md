# EIOS — O2 DEPURAR

**Resultado: DEPURAR → 🟢 COMPLETADO**

La revisión de diseño se traduce en estas restricciones de materialización:

1. **Reutilización O1:** O2 debe usar el contexto y semántica de O1; no crear un segundo envelope equivalente.
2. **Identidad por escenario:** cada escenario requiere `scenario_id` y no puede compartir accidentalmente resultados con otro escenario.
3. **Contexto material:** cada escenario conserva `decision_id`, `scenario_id`, `rules_version`, `parameters_version` y `data_snapshot_id`.
4. **Estado antes que valor:** un resultado sin ejecución, no evaluable o fallido debe conservar su estado y no interpretarse como valor empresarial negativo.
5. **Comparabilidad condicionada:** el comparador debe transportar `missing` y estados de ejecución junto con las diferencias; no puede afirmar equivalencia cuando faltan datos.
6. **Trazabilidad:** las referencias de trazas se conservan por escenario y en el paquete consolidado.
7. **Sin autoridad:** el agregado O2 no tendrá campos ni funciones de score, ranking, selección, aprobación, rechazo u optimización.
8. **Inmutabilidad:** modelos de entrada y resultados consolidados serán inmutables.
9. **Determinismo:** el identificador de ejecución O2 debe derivarse del contexto y de una representación estable de escenarios, sin depender de orden accidental.
10. **Frontera humana:** la salida final será información estructurada para decisión; nunca una decisión empresarial.

No se modifica C0, PRICE, TCO, QTG, Decision Twin, Decision Versioning, Negotiation Intelligence ni Negotiation Ladder.

**DEPURAR → 🟢 COMPLETADO**
