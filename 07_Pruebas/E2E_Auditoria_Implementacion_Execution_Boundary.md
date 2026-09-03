# EIOS — AUDITORÍA DE IMPLEMENTACIÓN E2E EXECUTION BOUNDARY

**Estado:** AUDITORÍA 1 — HALLAZGOS ABIERTOS
**Branch:** `implement/e2e-execution-boundary`
**Baseline de diseño cerrado:** `9667837247f5de031662d111ce110db42d1f5902`
**Implementación auditada:** `eios/core/execution_boundary.py`
**Tests auditados:** `tests/test_execution_boundary.py`

## 1. Alcance

Se contrasta exclusivamente la implementación materializada contra el diseño E2E cerrado. No se autoriza integración con `main` en esta fase.

## 2. Hallazgos

### E2E-IMP-01 — Falta contrato de implementación específico

**Severidad: BLOQUEADOR.**

El diseño cerrado exige una materialización posterior sometida a auditoría independiente, pero no existe todavía un `08_Implementacion/*Implementation_Contract.md` específico para Execution Boundary. La implementación actual no debe considerarse contractual hasta que dicho contrato sea definido, auditado y cerrado.

**Acción:** crear contrato de implementación específico antes de Audit 2 de implementación.

### E2E-IMP-02 — El catálogo/política de ejecución no forma parte del plan

**Severidad: BLOQUEADOR.**

El diseño exige que solo se invoquen capacidades declaradas como `invocable` mediante un catálogo/política contractual y un contexto de ejecución controlado. La implementación recibe únicamente `capabilities` e `invokers`; no existe representación contractual de política, versión de política ni catálogo autorizado. La existencia de una clave en `invokers` no demuestra por sí sola autorización contractual.

**Acción:** incorporar al contrato e implementación una representación explícita y versionada del catálogo/política autorizada, sin introducir autoridad de negocio ni descubrimiento dinámico.

### E2E-IMP-03 — La validación previa del plan es incompleta

**Severidad: BLOQUEADOR.**

El diseño exige validar el plan completo antes de iniciar ejecución. El código valida identidad y ausencia de invocadores, pero no valida previamente la autorización contractual, versión/política, coherencia completa de la declaración ni otras precondiciones que el contrato deberá cerrar.

**Acción:** completar validación pre-ejecución y demostrar que cualquier fallo conocido bloquea sin invocaciones parciales.

### E2E-IMP-04 — Estados READY/RUNNING no están materializados como ciclo observable

**Severidad: MAYOR.**

`BoundaryStatus` declara `READY` y `RUNNING`, pero `execute_plan()` solo devuelve el estado final y no expone transición ni evento de ejecución para dichos estados. Debe decidirse contractualmente si el boundary es una operación síncrona cuyo resultado solo materializa estados terminales, o si READY/RUNNING forman parte de una interfaz observable. No se puede dejar una enumeración sin semántica implementada.

**Acción:** cerrar la semántica en el contrato y ajustar implementación/tests.

### E2E-IMP-05 — Salida no incorpora contexto de ejecución/versiones para transporte directo

**Severidad: MAYOR.**

`ExecutionOutcome` contiene resultados, unresolved y fallo, pero no transporta explícitamente el contexto canónico/versiones. El diseño exige preservar `decision_id`, `scenario_id`, `rules_version`, `parameters_version` y `data_snapshot_id` hasta O1/U1.1. Aunque las capacidades reciben `DecisionContext`, el resultado de frontera no demuestra por sí mismo esa conservación.

**Acción:** definir en contrato el mecanismo de propagación y verificarlo con tests; preferentemente sin duplicar identidad ni crear una nueva autoridad.

### E2E-IMP-06 — Pruebas insuficientes para invariantes críticos

**Severidad: MAYOR.**

Los tests cubren orden, ausencia de invocador, excepción, identidad y parcialidad, pero no demuestran: política/catálogo autorizado, versión de política, validación completa antes de ejecución, preservación explícita de versiones, reproducibilidad, ausencia de mutación de entradas, fallo de una capacidad ya ejecutada y conservación de trazas/unresolved en escenarios múltiples.

**Acción:** ampliar matriz de aceptación una vez cerrado el contrato.

## 3. Aspectos SUPERADOS en esta auditoría

- No se observa scoring, ranking, selección, recomendación ni optimización en la implementación.
- No se observa persistencia, SQL, API pública, compra real ni negociación automática.
- El orden de invocación sigue el orden declarado del plan.
- Un invocador ausente produce `BLOCKED` antes de invocar los presentes.
- Una excepción técnica no se convierte en conclusión empresarial.
- `CapabilityExecution` se utiliza como tipo de salida, preservando el contrato O1 existente.
- Se rechazan inconsistencias entre `PurchaseOperation` y `DecisionContext` para `decision_id`/`scenario_id`.

## 4. Decisión

**NO APROBADA PARA AUDITORÍA 2.**

Los hallazgos E2E-IMP-01, E2E-IMP-02 y E2E-IMP-03 deben resolverse antes de Audit 2. E2E-IMP-04, E2E-IMP-05 y E2E-IMP-06 requieren cierre contractual y pruebas correspondientes.

La rama permanece aislada. `main` no se modifica.
