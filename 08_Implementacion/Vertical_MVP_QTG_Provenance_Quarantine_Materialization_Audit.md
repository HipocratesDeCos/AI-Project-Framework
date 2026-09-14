# EIOS — Vertical MVP QTG Provenance Quarantine · Materialization Audit

**Baseline:** `main @ fe03a6da407490705207f579bcd45a4b384d8bc2`  
**Rama:** `fix/vertical-mvp-qtg-provenance-quarantine`  
**Resultado estático:** SUPERADO — 0 BLOQUEADORES.  
**Gate ejecutable:** PENDIENTE DE CI.

## 1. Archivos productivos modificados

### `eios/core/mvp_execution.py`

Comprobado:

- `quality_invoker` eliminado de la firma de `run_mvp_execution(...)`;
- eliminado el registro `invokers["QTG"] = quality_invoker`;
- `QTG` permanece primero en `MVP_CAPABILITY_ORDER`;
- los invocadores PRICE, TCO, C0, Decision Twin, Scenario Coordination, NI y Ladder permanecen disponibles;
- `ExecutionPlan` y `execute_plan(...)` no se modifican;
- el fail-closed de ejecución sin capacidades permanece intacto.

### `eios/mvp.py`

Comprobado:

- `quality_invoker` eliminado de `run_vertical_mvp_support(...)`;
- eliminado su reenvío a `run_mvp_execution(...)`;
- Rules/CRC, PRICE, TCO, Decision Twin, Scenario Coordination, NI y Ladder conservan su composición;
- no se modifica `VerticalMVPSupportResult`;
- no se añade estado, ranking, recomendación o decisión.

## 2. Tests modificados

### `tests/test_mvp_execution_service.py`

Comprobado:

- deja de fabricar QTG mediante callable genérico;
- exige ausencia de `quality_invoker` en la firma;
- prueba fallo explícito si un consumidor intenta reutilizar el keyword antiguo;
- prueba que `QTG` sigue presente una sola vez y en primera posición de `MVP_CAPABILITY_ORDER`;
- conserva pruebas de orden/contexto para capacidades autorizadas, estados parciales, fail-closed y mismatch contextual.

### `tests/test_vertical_mvp_support.py`

Comprobado:

- elimina el fake `_quality_invoker`;
- deja de esperar QTG en resultados construidos por la fachada genérica;
- exige ausencia de `quality_invoker` en la firma;
- prueba fallo explícito ante el keyword legacy;
- conserva Rules/CRC y capacidades autorizadas.

## 3. Fronteras no modificadas

El delta no modifica:

- `eios/quality/`;
- `QualityCheck`, `QualityTrustResult` ni `evaluate_quality(...)`;
- modelos de `DecisionContext` o `PurchaseOperation`;
- `ExecutionOutcome`, `CapabilityExecution` ni `execute_plan(...)`;
- SQL;
- PRICE, TCO, Rules/C0, Decision Twin, Scenario Coordination, NI o Ladder;
- frontend;
- autoridad humana final.

No se crea `DecisionInputPackage` ni productor QTG.

## 4. Consumidores adicionales

La búsqueda de código de GitHub respondió con `incomplete_results=true`, por lo que no se utiliza como evidencia de ausencia de consumidores adicionales.

La suite completa de CI es el gate autorizado para detectar cualquier consumidor físico residual de `quality_invoker`. Si la CI revelara uno, no se considerará la unidad cerrada; solo podrá reconciliarse si el cambio consiste estrictamente en retirar la dependencia insegura dentro de esta misma frontera.

## 5. Dictamen

La materialización coincide con el contrato cerrado y no amplía alcance.

**MATERIALIZATION AUDIT: SUPERADA ESTÁTICAMENTE — 0 BLOQUEADORES.**

La unidad permanece **NO INTEGRADA** hasta superar CI pre-merge, reconciliación de rama, merge protegido por SHA exacto y CI post-merge.
