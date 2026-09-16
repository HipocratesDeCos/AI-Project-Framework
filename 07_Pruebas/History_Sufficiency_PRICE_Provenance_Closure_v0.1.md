# EIOS — History Sufficiency PRICE Provenance · Closure v0.1

## Estado

**🔒 CIERRE CONCEPTUAL AUTORIZADO**

Unidad: `HIS-PRICE-PROV-01`

Baseline: `main @ 64ffacefc26f2199a9caa81ad58aa227c9dc4125`

Método completado hasta cierre:

**DISEÑAR ✅ → AUDITAR ✅ → DEPURAR ✅ → AUDITAR 2 ✅ → CERRAR ✅**

Pendiente: **MATERIALIZAR → CI**.

## 1. Decisión cerrada

`R-HIS-002` no podrá consumir un `PriceIntelligenceResult` desprendido suministrado por el llamador.

El número de operaciones comparables evaluado por la regla deberá proceder de una ejecución local de `run_price_intelligence(...)` construida exclusivamente desde:

- `PriceIntelligenceInput`;
- `PriceIntelligenceAssessmentContext`;

tras comprobar que el input PRICE pertenece exactamente a la `PurchaseOperation` y `DecisionContext` de la evaluación.

## 2. Semántica preservada

La condición de negocio permanece:

`n_comparable < P-PRE-006`

No se modifica ningún resultado, efecto, severidad, umbral, regla de agregación ni autoridad de CRC.

## 3. Contratos cerrados que se preservan

- Price Intelligence C1 y `run_price_intelligence`;
- `Price_Provenance_Invoker_Contract_v0.1` / PR #115;
- contrato provenance-safe de `P-PRE-006`;
- Matriz de Reglas;
- Rule Dependency Matrix;
- catálogo de parámetros;
- C0 / Rules runtime;
- CRC.

## 4. API autorizada

Se elimina `pricing_result` de:

- `evaluate_r_his_002(...)`;
- `HistorySufficiencyRuleInputs`;
- llamada de `run_domain_rules(...)`.

Se incorpora `pricing_assessment_context: PriceIntelligenceAssessmentContext`.

No se admite compatibilidad con el argumento eliminado.

## 5. Fail closed

Se preservan:

- errores estructurales como errores explícitos;
- mismatch de compra/contexto como rechazo;
- mismatch de evidencia `DEMONSTRATED` como rechazo;
- evidencia no válida como `NOT_EVALUABLE` donde corresponda;
- ausencia/configuración no utilizable de `P-PRE-006` como `NOT_EVALUABLE` donde corresponda;
- errores C1 sin fallback.

## 6. Delta físico autorizado

Código:

- `eios/rules/pricing.py`;
- `eios/rules/orchestrator.py`.

Tests:

- `tests/test_r_his_002_vertical.py`;
- otros tests solo si la suite demuestra un consumidor real afectado por el cambio de API.

Documentación:

- artefactos metodológicos de `HIS-PRICE-PROV-01`;
- auditoría de materialización.

No está autorizado modificar otros componentes salvo contradicción objetiva descubierta durante materialización, que obligaría a detener y reauditar alcance.

## 7. Pruebas obligatorias

La materialización no podrá considerarse cerrada sin demostrar:

- TRUE y FALSE desde C1 real;
- ausencia de `pricing_result` en las APIs afectadas;
- rechazo de input PRICE de otra compra/contexto;
- rechazo de evidencia `DEMONSTRATED` ligada a otro resultado;
- `NOT_EVALUABLE` para evidencia PRICE no válida;
- comportamiento de `P-PRE-006` preservado;
- CRC R3/R2 preservado;
- suite completa y CI verdes.

## 8. Prohibiciones de materialización

No se puede:

- volver a introducir un resultado PRICE raw;
- fabricar un assessment context por defecto;
- copiar parcialmente lógica C1 en Rules;
- modificar algoritmos de PRICE;
- cambiar la regla `R-HIS-002`;
- cambiar parámetros o relaciones documentales;
- degradar un fallo de procedencia a una inferencia o fallback.

## 9. Dictamen

El diseño depurado ha superado dos auditorías sin bloqueadores.

**HIS-PRICE-PROV-01 queda conceptualmente CERRADA y autorizada para MATERIALIZAR.**
