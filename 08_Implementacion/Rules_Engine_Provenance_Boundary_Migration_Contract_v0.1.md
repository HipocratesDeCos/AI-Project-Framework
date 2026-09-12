# EIOS — Rules Engine Provenance Boundary Migration Contract v0.1

**Estado:** AUDITORÍA 2 SUPERADA — PENDIENTE CI  
**Baseline:** `main @ c986e97d395be6c386dcc0524b643346c5e1e433`  
**Ámbito:** cerrar las fronteras públicas que aceptan Assessments preproducidos sin Trace, preservando la ejecución legítima de reglas producidas dentro de la misma llamada/contexto.

## 1. Motivación

PR #105 demostró que un `Assessment` aislado no acredita decisión, escenario, versiones, snapshot ni input original. La reutilización entre fronteras requiere `AssessmentTraceBinding` y validación provenance-safe.

El facade público `RulesEngineInput/run_rules_engine` y el antiguo `build_rules_engine_c0_invoker(assessments=...)` mantenían un bypass que permitía introducir Assessments desconectados y generar la trazabilidad después.

## 2. Distinción obligatoria

### 2.1 Producción en la misma ejecución

`run_domain_rules` y verticales específicos producen sus Assessments dentro de la misma llamada, usando el mismo `PurchaseOperation`, `DecisionContext` y Rule autorizada, y los componen inmediatamente.

Ese flujo no reutiliza un Assessment entre contextos y conserva el runtime interno same-execution.

### 2.2 Reutilización entre fronteras

Toda frontera pública que reciba un Assessment ya producido debe exigir su Trace original y validar procedencia completa antes de reutilizarlo.

## 3. Facade público v0.2

`RulesEngineInput` contiene exclusivamente:
- `purchase: PurchaseOperation`;
- `context: DecisionContext`;
- `bindings: tuple[AssessmentTraceBinding, ...]`;
- `base_result`.

El campo público `assessments` desaparece y, por `extra="forbid"`, su uso falla explícitamente.

`run_rules_engine(...)` delega en `run_provenanced_assessments_vertical(...)`.

La salida `RulesEngineResult = RuleSetVerticalResult` se conserva.

## 4. Invoker E2E

`build_rules_engine_c0_invoker(...)` conserva su nombre de integración, pero acepta únicamente:
- `bindings: Sequence[AssessmentTraceBinding]`;
- `base_result`.

Delega al invoker provenance-safe de PR #105. No genera Trace nuevo ni acepta Assessments desconectados.

`build_domain_rules_c0_invoker(...)` mantiene su semántica: ejecuta los bundles de dominio dentro del contexto recibido.

## 5. run_domain_rules

`run_domain_rules` ya no atraviesa el facade público de reutilización. Tras producir los Assessments dentro de la misma ejecución, usa la composición interna `run_authorized_assessments_vertical(...)` con el mismo purchase/context.

Esto no convierte esa función interna en una frontera pública autorizada para material preproducido.

## 6. Cuarentena del namespace público

Dejan de exportarse desde `eios.rules`:
- `RuleAssessmentBinding`;
- `bind_authorized_assessment`;
- `run_assessment_set_vertical`;
- `run_assessment_vertical`;
- `run_authorized_assessments_vertical`.

Permanecen físicamente en `eios.rules.runtime` para consumidores internos same-execution. No se elimina ni cambia su semántica.

## 7. Ruptura controlada

La migración es deliberada:
- `RulesEngineInput(assessments=...)` debe ser inválido;
- `build_rules_engine_c0_invoker(assessments=...)` debe ser inválido;
- la ruta pública equivalente exige bindings provenance-safe.

No existe fallback silencioso.

## 8. Autoridades preservadas

- Rules específicas producen Assessment.
- Trace conserva procedencia y reproducibilidad.
- CRC conserva consolidación.
- O1 conserva empaquetado de soporte.
- `NOT_EVALUABLE != FALSE`.
- un fallo técnico/provenance no se convierte en rechazo empresarial.
- no se añade score, ranking, recomendación, selección, aprobación ni decisión.

## 9. Fail-closed

La frontera pública rechaza:
- el campo legacy `assessments`;
- Trace legacy sin `assessment_fingerprint`;
- bindings de otra decisión/escenario/versiones/snapshot/input;
- incoherencias Assessment/Trace;
- reglas no catalogadas;
- duplicados.

## 10. Fuera de alcance

- cambiar reglas empresariales;
- modificar C0 core, CRC u O1;
- modificar O2/O3/VF;
- eliminar físicamente runtime helpers internos;
- alterar verticales same-execution;
- UI, SQL o persistencia.

## 11. Criterios de aceptación

1. `RulesEngineInput` acepta bindings y rechaza `assessments`;
2. facade público valida procedencia completa;
3. binding extranjero/manipulado falla;
4. Trace legacy falla;
5. NOT_EVALUABLE se conserva;
6. empty bindings conserva `C0_NO_ASSESSMENTS`;
7. `build_rules_engine_c0_invoker` exige bindings y funciona en E2E;
8. el invoker no reutiliza bindings en otro contexto;
9. `run_domain_rules` conserva resultados, orden y cobertura;
10. `build_domain_rules_c0_invoker` conserva comportamiento;
11. helpers sin Trace no forman parte del facade `eios.rules`;
12. no cambia semántica empresarial ni autoridad decisional.

## 12. Auditoría 1

El inventario distinguió dos clases de consumidores:

- **same-execution legítimos:** `run_domain_rules`, `delivery_runtime` y tests del runtime, donde el Assessment se produce y consume inmediatamente en el mismo contexto;
- **reutilización insegura:** facade público con `Assessment` suelto y `build_rules_engine_c0_invoker(assessments=...)`, donde la procedencia original no podía demostrarse.

Se comprobó que la migración no crea circularidad: el facade depende de `provenance`; `provenance` depende del runtime interno; el orquestador de dominio depende directamente del runtime interno; el adapter genérico depende del invoker provenance-safe.

**DICTAMEN AUDITORÍA 1:** SUPERADA — migrar solo las fronteras de reutilización y preservar same-execution.

## 13. Auditoría 2

Comparación contra el baseline:
- 11 archivos afectados;
- contrato nuevo;
- cambios limitados a `eios/rules/__init__.py`, `engine.py`, `execution_adapter.py`, `orchestrator.py` y tests asociados;
- ningún archivo de reglas empresariales específicas modificado;
- ningún cambio en C0 core, CRC, O1, O2, O3, Viability Frontier, Vertical o presentación.

Comprobaciones:
- el schema público contiene `bindings` y no `assessments`;
- el invoker genérico ya no acepta `assessments`;
- la ruta de dominio sigue produciendo y componiendo Assessments dentro del mismo contexto;
- los helpers internos siguen probados desde `eios.rules.runtime`;
- el namespace público tiene tests explícitos que bloquean la reexportación accidental de helpers sin Trace;
- la cobertura pública incluye binding extranjero, Trace legacy, regla no catalogada, NOT_EVALUABLE, empty bindings y congelación del snapshot;
- no se introduce autoridad decisional.

**DICTAMEN AUDITORÍA 2:** SUPERADA — SIN BLOQUEADORES DE DISEÑO.  
**Cierre definitivo:** condicionado a CI completa sobre el head exacto de PR y CI post-merge sobre `main`. La CI actúa además como detector final de consumidores legacy no identificados por el inventario estático.
