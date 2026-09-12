# EIOS — Rules Engine Provenance Boundary Migration Contract v0.1

**Estado:** DISEÑO PARA AUDITORÍA 1  
**Baseline:** `main @ c986e97d395be6c386dcc0524b643346c5e1e433`  
**Ámbito:** cerrar las fronteras públicas que aceptan Assessments preproducidos sin Trace, preservando la ejecución legítima de reglas producidas dentro de la misma llamada/contexto.

## 1. Motivación

PR #105 demostró que un `Assessment` aislado no acredita decisión, escenario, versiones, snapshot ni input original. La reutilización entre fronteras requiere `AssessmentTraceBinding` y validación provenance-safe.

Sin embargo, el facade público actual `RulesEngineInput/run_rules_engine` y `build_rules_engine_c0_invoker` todavía aceptan Assessments sueltos. Ese diseño permite omitir la nueva frontera segura.

## 2. Distinción obligatoria

No todo uso de un Assessment sin Trace previo es inseguro.

### 2.1 Producción en la misma ejecución

`run_domain_rules` produce cada Assessment mediante bridges de reglas dentro de la misma llamada, con el mismo `PurchaseOperation`, `DecisionContext` y Rule autorizada, y acto seguido compone Trace/CRC/O1.

Ese flujo no reutiliza un Assessment desconectado y puede seguir usando una rutina interna de composición same-execution.

### 2.2 Reutilización entre fronteras

Toda API pública que reciba un resultado Assessment ya producido debe exigir su Trace original y validar procedencia antes de reutilizarlo.

## 3. Nuevo contrato del facade público

`RulesEngineInput` pasa a contener:
- `purchase: PurchaseOperation`;
- `context: DecisionContext`;
- `bindings: tuple[AssessmentTraceBinding, ...]`;
- `base_result`.

Ya no acepta el campo `assessments`.

`run_rules_engine(...)` delega exclusivamente en `run_provenanced_assessments_vertical(...)`.

La salida `RulesEngineResult = RuleSetVerticalResult` permanece sin cambios.

## 4. Invoker E2E

`build_rules_engine_c0_invoker(...)` conserva el nombre de integración, pero su entrada cambia a:
- `bindings: Sequence[AssessmentTraceBinding]`;
- `base_result`.

Delega al invoker provenance-safe ya cerrado por PR #105. No crea Trace nuevo ni acepta Assessments desconectados.

`build_domain_rules_c0_invoker(...)` permanece sin cambios semánticos: evalúa los bundles de dominio dentro del contexto recibido.

## 5. Migración de run_domain_rules

`run_domain_rules` deja de atravesar el facade público con Assessments recién producidos.

En su lugar utiliza la composición interna same-execution ya existente (`run_authorized_assessments_vertical`) inmediatamente después de producir los Assessments y dentro del mismo `purchase/context`.

Esto no convierte dicha rutina en frontera pública autorizada para reutilización externa.

## 6. Cuarentena del facade de eios.rules

Los helpers que aceptan Assessment sin Trace y generan Trace posteriormente dejan de exportarse desde `eios.rules` cuando su función es interna/compatibilidad:
- `RuleAssessmentBinding`;
- `bind_authorized_assessment`;
- `run_assessment_set_vertical`;
- `run_assessment_vertical`;
- `run_authorized_assessments_vertical`.

Pueden permanecer físicamente en `eios.rules.runtime` para consumidores internos same-execution existentes. Esta unidad no los elimina ni altera su semántica.

Los tipos de resultado pueden permanecer exportados si no crean una vía de entrada insegura.

## 7. Compatibilidad y ruptura controlada

Es una migración contractual intencionada de una API preproducción:
- `RulesEngineInput(assessments=...)` debe fallar por `extra="forbid"`/campo ausente;
- `build_rules_engine_c0_invoker(assessments=...)` deja de ser válido;
- la ruta equivalente segura utiliza bindings con Trace.

No se mantiene un fallback silencioso porque restablecería el bypass que se pretende cerrar.

## 8. Autoridades preservadas

- Rules específicas siguen produciendo Assessment.
- C0/Trace conserva procedencia.
- CRC conserva consolidación.
- O1 conserva soporte.
- `NOT_EVALUABLE` permanece distinto de FALSE.
- Ningún fallo técnico/provenance se convierte en rechazo empresarial.

## 9. Fail-closed

La frontera pública debe rechazar:
- Assessment suelto mediante el antiguo campo `assessments`;
- Trace legacy sin `assessment_fingerprint`;
- binding de otra decisión/escenario/versiones/snapshot/input;
- Assessment/Trace incoherentes;
- rule_id no catalogado;
- duplicados.

## 10. Fuera de alcance

- modificar reglas empresariales;
- cambiar CRC/O1;
- cambiar O2/O3/VF;
- retirar físicamente runtime helpers internos;
- convertir same-execution en un sistema de tokens/autorizaciones artificial;
- introducir score/ranking/recomendación/decisión;
- UI, SQL o persistencia.

## 11. Criterios de aceptación

1. `RulesEngineInput` acepta bindings y no acepta `assessments`;
2. facade público valida procedencia completa;
3. binding extranjero/manipulado falla;
4. Trace legacy falla;
5. NOT_EVALUABLE se conserva;
6. empty bindings conserva la semántica explícita previa de C0 sin Assessments;
7. `build_rules_engine_c0_invoker` exige bindings y funciona en E2E;
8. el invoker no puede reutilizar bindings en otro contexto;
9. `run_domain_rules` conserva resultados/orden/cobertura existentes;
10. `build_domain_rules_c0_invoker` conserva comportamiento;
11. helpers sin Trace dejan de formar parte del facade `eios.rules`;
12. no se modifica semántica empresarial ni autoridad decisional.

**DICTAMEN DE DISEÑO:** pendiente de Auditoría 1.
