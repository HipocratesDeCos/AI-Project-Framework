# EIOS — Projection Quality ↔ O1 Causal Binding Contract v0.1

**Estado:** 🔒 CERRADO — IMPLEMENTACIÓN MATERIALIZADA / E2E OPERACIONAL POSITIVO PENDIENTE

**Baseline:** `main @ 714cb0c3423c4418f6cd307be284e3297701f033`

**Ámbito:** binding causal entre un consumo QTG `PROJECTION_ONLY / OPERATIONAL` y una ejecución técnica O1, sin convertir QTG en capacidad Vertical.

## 1. DISEÑAR

### 1.1 Objetivo

Crear una prueba reproducible de que:

- un consumo QTG operacional fue validado contra su receipt y envelope exactos;
- la compra y el contexto de ese material coinciden completamente con los usados en ejecución;
- la política MVP fue declarada explícitamente;
- el `ExecutionOutcome` conservado fue producido por la misma llamada que realizó el binding.

El binding informa coexistencia causal y trazable. No convierte el estado QTG en decisión, regla, capacidad O1 ni autorización de compra o pago.

### 1.2 Corrección del diseño preliminar

La auditoría anterior expresó conceptualmente:

```text
consumption + envelope + purchase + context + policy → binding
```

La firma completa debe incluir también el `ProjectionQualityReceipt`. `validate_projection_quality_consumption(...)` recompone el consumo a partir de consumption, receipt, envelope, modo y alcance; extraer un payload anidado no permite reconstruir legítimamente el tipo factory-built ni sustituye esa recomputación.

### 1.3 Dos fases, una sola autoridad de cierre

#### Fase A — `BOUND_INPUT`

Un builder especializado podrá producir `ProjectionQualityO1InputBinding` desde:

```text
ProjectionQualityConsumption
+ ProjectionQualityReceipt
+ ProjectionMaterialEnvelope
+ PurchaseOperation
+ DecisionContext
+ policy_version
```

Deberá:

1. exigir `execution_mode=OPERATIONAL` y `consumption_scope=OPERATIONAL` como constantes internas, no como valores promocionables por el caller;
2. ejecutar `validate_projection_quality_consumption(...)`;
3. comprobar que consumption, receipt y envelope conservan fingerprints coincidentes;
4. extraer del DIP anidado la compra y el contexto completos;
5. revalidarlos como `PurchaseOperation` y `DecisionContext`;
6. exigir igualdad completa con los snapshots runtime;
7. validar `policy_version` como identificador explícito no vacío;
8. conservar snapshots canónicos y fingerprints de compra, contexto, receipt, envelope y consumo;
9. declarar `binding_status=BOUND_INPUT` y `decision_authority=false`.

`BOUND_INPUT` solo acredita coherencia antes de ejecutar. No puede contener ni afirmar un resultado terminal.

#### Fase B — `BOUND_TERMINAL_OUTCOME`

No existirá un builder público que acepte un `ExecutionOutcome` ya producido.

La única autoridad para crear `ProjectionQualityO1BoundExecution` será una fachada síncrona especializada que:

1. construya y revalide el input binding;
2. invoque exactamente una vez `run_mvp_execution(...)` con los mismos snapshots de compra, contexto y política;
3. reciba el `ExecutionOutcome` directamente de esa llamada;
4. lo revalide como `ExecutionOutcome` y exija igualdad de `policy_version`;
5. preserve completos el input binding y el outcome;
6. calcule sus fingerprints canónicos y el fingerprint terminal conjunto;
7. declare `binding_status=BOUND_TERMINAL_OUTCOME` y `decision_authority=false`.

La causalidad procede de que la fachada posee la transición validación→ejecución→cierre. No se infiere a posteriori por similitud de campos.

### 1.4 Firma conceptual de la fachada

```text
run_mvp_execution_with_projection_quality_binding(
    consumption,
    receipt,
    envelope,
    purchase,
    context,
    policy_version,
    <los mismos invocadores explícitos ya autorizados por run_mvp_execution>
) -> ProjectionQualityO1BoundExecution
```

La fachada deberá delegar en `run_mvp_execution(...)`; no copiará `execute_plan(...)`, no recibirá un callable de ejecución genérico y no aceptará `quality_invoker`.

QTG no se añadirá a `MVP_CAPABILITY_ORDER` mediante esta frontera, no aparecerá en `capability_results` y no alterará el estado calculado para las capacidades ejecutadas. Su resultado funcional se conservará separadamente dentro del consumo.

### 1.5 Resultado terminal especializado

`ProjectionQualityO1BoundExecution` conservará como mínimo:

- schema, binding ID/versión y `binding_status`;
- input binding completo y fingerprint;
- consumo completo y fingerprint;
- receipt y envelope fingerprints;
- compra y contexto completos con fingerprints canónicos;
- `policy_version` explícita;
- `O1ExecutionContext` derivado como identidad reproducible del contexto, etiquetado expresamente como no identificador de ocurrencia;
- `ExecutionOutcome` completo y fingerprint;
- resultado funcional QTG accesible sin reducir su prueba;
- `decision_authority=false`;
- fingerprint canónico del artefacto terminal.

No se creará un identificador nuevo de ocurrencia en v0.1. El artefacto prueba una transición síncrona poseída por la fachada; no pretende distinguir dos repeticiones materialmente idénticas.

## 2. AUDITAR

**A1 — cierre post hoc falso.** Una función pública `close(input_binding, outcome)` podría recibir un outcome ajeno. Se elimina; solo la fachada que ejecuta puede cerrar.

**A2 — receipt anidado no equivale a objeto validable.** El consumo conserva el payload, pero el validador exige el receipt factory-built exacto. La firma lo recibe explícitamente.

**A3 — duplicación de ejecución.** Reimplementar `execute_plan(...)` crearía una frontera paralela. La fachada delegará una vez en `run_mvp_execution(...)`.

**A4 — callable genérico.** Aceptar `runner: Callable` desplazaría la confianza al caller. Se prohíbe.

**A5 — promoción de modo.** Exponer modo y scope como opciones permitiría intentar una promoción. La fachada causal v0.1 será exclusivamente operacional.

**A6 — QTG técnico frente a QTG funcional.** `APTO`, `APTO_CON_ADVERTENCIAS` y `NO_APTO` permanecen en el consumo; no se traducen a `COMPLETED`, `FAILED` o decisión.

**A7 — policy no derivable.** `policy_version` se conserva como entrada independiente. No se equipara a `rules_version`, parámetros, catálogo ni manifiesto.

**A8 — ejecución sin capacidades.** La fachada heredará el fail-closed de `run_mvp_execution(...)`; el binding QTG no cuenta como capacidad ejecutable y no permite un plan vacío.

**A9 — errores de ejecución.** Un `ExecutionOutcome.FAILED`, `BLOCKED` o parcial puede quedar causalmente vinculado. El binding no lo promociona ni lo sustituye; conserva exactamente el resultado terminal.

**A10 — invocadores futuros.** La firma especializada deberá reflejar solo los invocadores explícitos autorizados por `run_mvp_execution(...)`. Cualquier deriva se detectará mediante prueba de paridad de firmas excluyendo los parámetros QTG especializados.

**A11 — material operacional no demostrado.** El repositorio no contiene una fixture operacional positiva autorizada. Construirla cambiando etiquetas `SYNTHETIC` por `PRESENTED_OPERATIONAL` falsearía la naturaleza del material.

**A12 — ejecución identificable frente a repetición.** `O1ExecutionContext.execution_id` no distingue repeticiones. El contrato no le atribuye esa función ni inventa nonce, timestamp o UUID.

## 3. DEPURAR

Se eliminan del diseño:

- cierre terminal post hoc;
- `quality_invoker` y `adapt_qtg`;
- runner o callback genérico;
- conversión a `CapabilityExecution`;
- equivalencia entre versiones heterogéneas;
- identificador de ocurrencia inventado;
- modificación de `ExecutionOutcome`, `DecisionSupportPackage` o `VerticalMVPSupportResult`;
- fixture supuestamente operacional creada con fuentes ficticias.

La forma depurada es una fachada causal especializada, externa al Vertical, que acompaña una ejecución ya autorizada sin presentar QTG como capacidad del plan.

## 4. AUDITAR 2

La segunda revisión confirma:

- la igualdad completa de compra y contexto puede verificarse desde el DIP anidado;
- receipt y consumo pueden recomputarse con sus objetos factory-built exactos;
- la política se conserva sin inferencia;
- la fachada puede poseer causalmente la llamada a `run_mvp_execution(...)`;
- el outcome terminal puede conservarse sin alterar su semántica;
- no existe constructor público capaz de grapar un outcome ajeno;
- QTG permanece fuera de `capability_results`, del orden ejecutado y de las firmas Vertical;
- el diseño no concede autoridad decisional ni financiera.

### Bloqueo confirmado

La implementación positiva permanece bloqueada hasta disponer de material operacional explícitamente autorizado y trazable para una prueba E2E. La suite actual solo permite demostrar rechazos operacionales y comportamiento sintético `TEST_ONLY`; ninguno basta para acreditar la rama causal operacional.

No se autoriza resolver el bloqueo cambiando etiquetas de fixtures sintéticas.

## 5. CERRAR

Se cierra el contrato de `ProjectionQualityO1Binding` con esta decisión:

- **diseño causal aprobado**;
- **builder `BOUND_INPUT` definido**;
- **cierre terminal reservado a la fachada ejecutora**;
- **implementación aplazada**, no por carencia arquitectónica, sino por ausencia de caso operacional positivo autorizado.

## 6. MATERIALIZAR

Esta unidad materializa únicamente el contrato. No modifica código, tests, modelos, invocadores ni rutas O1/Vertical.

La modificación local ajena de `08_Implementacion/Viability_Frontier_Scenario_Analytics_Integration_Contract_v0.1.md` queda excluida.

## 7. CI

La integración documental exige suite completa, PR de un solo archivo, CI exact-head, merge protegido por SHA y CI post-merge.

El éxito de CI no elimina el bloqueo operacional ni habilita QTG.


## 8. Reactivación técnica — 23/09/2026

Tras el cierre del Operational Admission Preflight y del intake manifest, se materializa el contrato físico sin fabricar un caso operacional positivo.

Implementado:

- `ProjectionQualityO1InputBinding`;
- `ProjectionQualityO1BoundExecution`;
- `build_projection_quality_o1_input_binding(...)`;
- `run_mvp_execution_with_projection_quality_binding(...)`.

La fachada:
- revalida consumo QTG exclusivamente OPERATIONAL;
- comprueba fingerprints receipt/envelope/consumption;
- recupera PurchaseOperation + DecisionContext desde el DIP anidado;
- exige igualdad completa con runtime;
- conserva policy_version explícita;
- delega una sola vez en `run_mvp_execution(...)`;
- no expone cierre terminal post-hoc;
- no añade QTG al catálogo de invocadores;
- mantiene `decision_authority=false`.

Permanece pendiente únicamente el **E2E positivo con expediente operacional real autorizado**. La suite no crea una fixture `PRESENTED_OPERATIONAL` artificial.
