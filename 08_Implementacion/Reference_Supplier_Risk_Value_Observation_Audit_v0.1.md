# EIOS — Reference Supplier Risk/Value Observation: auditoría v0.1

**Base auditada:** `main @ 81853aafc9bad7d355a62987ebbff52f80387410`.
**Estado:** diseño de frontera; no incorpora observación al runtime.

## DISEÑAR

Determinar si el resultado `SupplierRiskValueResult` de la simulación de
referencia puede conservarse y presentarse de forma fiel, después de PRICE y
TCO, sin convertir una evaluación sintética externa en una conclusión factual
acerca de proveedores reales.

## AUDITAR — capacidad y material disponible

`evaluate_supplier_evidence` recibe en el caso ficticio `candidates=()`,
`observations=()`, `historical_facts=()`, `external_metrics=()`, `signals=()`
y `comparison_requests=()`. Produce un `SupplierEvidenceResult` ligado a
compra y contexto, pero no aporta hechos para comparar proveedores o medir su
fiabilidad. Ese resultado se calcula antes de la ejecución O1.

El caso añade explícitamente una evaluación externa sintética del proveedor
actual: dimensión `RELIABILITY`, estado `FAVORABLE`, autoridad, metodología,
referencia de evaluación, evidencia demostrada y traza declarada. No añade
evaluaciones de valor ni proveedores alternativos. El productor
`produce_supplier_risk_value` valida identidad, pertenencia del proveedor,
unicidad de dimensiones y evidencia demostrada de autoridad y referencias.
Ordena los elementos y deriva pendientes, referencias de evidencia y trazas.
No obtiene `FAVORABLE` de observaciones o métricas: acepta el estado de la
evaluación externa aportada. La evidencia sintética demuestra la declaración
de autoridad y la referencia de evaluación dentro del fixture, no un historial
objetivo de fiabilidad.

`build_provenanced_supplier_risk_value_invoker` congela las fuentes y produce
el resultado al invocarse. Devuelve a O1 únicamente `CapabilityExecution`:
`COMPLETED`, `result_available=true`, la traza declarada y ningún pendiente
para este fixture. `COMPLETED` significa que el productor terminó bajo las
fuentes suministradas; no prueba desempeño favorable en el mercado ni autoriza
seleccionar un proveedor.

La identidad validada por el productor cubre decisión, escenario, versiones,
snapshot, artículo, fecha y proveedor actual. No compara `quantity`,
`unit_price` o `currency` de la compra con una compra fuente completa: el
`SupplierEvidenceResult` no transporta esos campos. La fachada del caso sí
valida el runtime frente al bundle, pero un builder observado reutilizable
deberá recibir y congelar explícitamente la compra completa del fixture si
pretende prometer identidad exacta antes de llamar al productor.

## DEPURAR — riesgo de lectura y reutilización

- Una vista que diga simplemente «proveedor fiable» ocultaría que el estado
  `FAVORABLE` fue aportado por una evaluación externa ficticia, sin hechos
  subyacentes de proveedores en `SupplierEvidenceResult`.
- `trace_refs` identifica la evaluación declarada; no demuestra por sí sola
  una cadena causal hacia transacciones o métricas inexistentes.
- `value_dimensions=()` no significa valor nulo o equivalente, y la falta de
  candidatos impide una comparación de alternativas en este fixture.
- No repetir `produce_supplier_risk_value` al exportar ni reconstruir el
  resultado a partir de `CapabilityExecution`.
- Reutilizar la sesión genérica de un solo uso de PRICE/TCO, manteniendo el
  builder público y la validación específicos de Supplier Risk/Value.

## AUDITAR 2 — contrato mínimo para una futura captura

Una sesión observada congelaría la compra fuente completa,
`SupplierEvidenceResult`, evaluaciones y evidencias antes de O1; comprobaría
todos los campos de la compra antes de producir exactamente una vez y conservaría copias
defensivas de `SupplierRiskValueResult` y `CapabilityExecution` desde la misma
llamada. El cierre exigiría identidad exacta de compra y contexto, un único
registro `SUPPLIER_RISK_VALUE` en el terminal, igualdad de estado, pendientes
y trazas, y procedencia `SYNTHETIC` con ruta `FORBIDDEN`. El sidecar incluiría
huellas de fuentes, resultado y terminal, así como el inventario de fuentes
vacías y la procedencia explícita de la evaluación `FAVORABLE`.

La vista, si se implementa, deberá rotular «evaluación externa sintética
declarada» para `RELIABILITY=FAVORABLE`, mostrar que no hay dimensiones Value
ni comparaciones y evitar recomendaciones de proveedor. Pruebas exigidas:
una producción, rechazo previo de identidades ajenas, segundo uso/fallo,
conservación de estados incompletos y trazas, igualdad con O1, terminales sin
cambios y ausencia de regresión en PRICE/TCO.

## CERRAR

Se cierra el diseño de la frontera de observación. **No se afirma una
fiabilidad factual** del proveedor ficticio ni se concede autoridad decisional.
Permanecen `material_nature=SYNTHETIC`, `qtg_mode_policy=SYNTHETIC_TEST_ONLY`,
`operational_path=FORBIDDEN` y `effect_scope=NO_OPERATIONAL_EFFECT`.

## MATERIALIZAR / CI

Esta unidad solo documenta el hallazgo y el contrato de aceptación. La
captura, exportación y presentación serán unidades posteriores con pruebas y
CI propias. No se modifican productor, fachada, O1, terminal ni fixtures.
