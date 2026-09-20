# EIOS — QTG Operational Consumption ↔ O1 Membership Readiness Audit v0.1

**Estado:** CERRADO — NO LISTO PARA INTEGRACIÓN O1/VERTICAL

**Baseline auditado:** `main @ 0d8a218423bd1ee38af9ee3de76af35ffecd67e8`

**Ámbito:** pertenencia verificable de un `ProjectionQualityConsumption` operacional a una ejecución O1 concreta.

## 1. DISEÑAR

### 1.1 Pregunta

Determinar si el consumo especializado `QTG-PROJECTION-CONSUMER-01` puede asociarse ya a una ejecución O1 concreta sin reducir el receipt, restaurar `quality_invoker`, modificar las fronteras cerradas o inventar una identidad de ejecución.

### 1.2 Condición de aceptación

La pertenencia solo sería suficiente si una frontera pudiera demostrar conjuntamente:

1. receipt y consumo recomputables;
2. modo y alcance `OPERATIONAL` exactos;
3. igualdad completa entre la compra del DIP y la compra de la ejecución;
4. igualdad completa entre el contexto del DIP y el contexto de la ejecución;
5. identidad explícita de la política de ejecución;
6. vínculo persistente entre consumo, material y ejecución terminal concreta;
7. conservación del resultado funcional QTG sin confundirlo con estado técnico O1;
8. ausencia de autoridad decisional.

## 2. AUDITAR

### 2.1 Mapa físico de identidad

| Artefacto | Compra completa | Contexto completo | Política MVP | Receipt/consumo | Identidad de invocación |
|---|---:|---:|---:|---:|---:|
| `DecisionInputPackage` anidado en el envelope | Sí | Sí | No | No | No |
| `ProjectionQualityReceipt` | Sí, dentro del envelope | Sí, dentro del envelope | No | Sí | No |
| `ProjectionQualityConsumption` | Sí, dentro del receipt | Sí, dentro del receipt | No | Sí | No |
| `ExecutionOutcome` | No | No | Sí | No | No |
| `O1ExecutionContext` | No | Sí | No | No | Derivada solo del contexto |
| `DecisionSupportPackage` | No | Sí | No | No | Derivada solo del contexto |
| `VerticalMVPSupportResult` | No | No | Sí, dentro de `execution` | No | No |

### 2.2 Hallazgos

**A1 — existe identidad material suficiente para un contraste en runtime.** La ruta `receipt.envelope.preparation.capture.finance_package.decision_input_package` conserva la compra y el `DecisionContext` completos. No es necesario inferirlos desde nombres de documentos, flujos o referencias parciales.

**A2 — el consumo no está ligado a la política MVP.** Ni envelope, receipt ni consumo contienen `policy_version`. No existe autoridad para identificarla con `rules_version`, versión del manifiesto, catálogo QTG o parámetros.

**A3 — `ExecutionOutcome` no permite recomprobar pertenencia.** Su payload terminal no conserva compra, contexto, huella de entrada, `execution_id`, receipt ni consumo. Dos ejecuciones con igual política y resultados reducidos pueden ser indistinguibles aunque sus entradas materiales difieran.

**A4 — `O1ExecutionContext.execution_id` no identifica una ocurrencia.** Se deriva exclusivamente de los cinco campos de `DecisionContext`. Repetir una ejecución con el mismo contexto produce el mismo identificador; cambiar compra sin cambiar contexto tampoco lo altera.

**A5 — `DecisionSupportPackage` no resuelve la compra.** Comprueba `decision_id` y `scenario_id` entre compra y contexto durante construcción, pero no conserva la compra completa ni su huella en la salida.

**A6 — `CapabilityExecution` degrada la evidencia.** No puede transportar perfil, modo, catálogo, receipt, consumo ni sus fingerprints. Convertir el consumo a `QTG / COMPLETED` perdería la prueba necesaria.

**A7 — una validación previa no prueba por sí sola el resultado terminal.** Comparar material antes de `execute_plan(...)` demuestra coherencia de entrada en ese momento, pero si la salida no conserva el vínculo no permite auditar posteriormente qué consumo acompañó a qué ejecución.

**A8 — no existe todavía material operacional positivo autorizado.** La rama `OPERATIONAL` es fail-closed y está implementada, pero la suite no contiene un caso real autorizado. Esta ausencia impide afirmar una integración operacional E2E, aunque no impide diseñar la futura frontera de pertenencia.

## 3. DEPURAR

Se rechazan estas alternativas:

1. **Usar solo `decision_id` y `scenario_id`**: identidad parcial, incapaz de detectar cambios de compra, versiones o snapshot.
2. **Usar solo `O1ExecutionContext.execution_id`**: no incorpora compra, política ni ocurrencia.
3. **Equiparar `policy_version` con `rules_version`**: son campos con autoridades distintas y no hay contrato de equivalencia.
4. **Adjuntar la huella del receipt como `trace_reference`**: una referencia no conserva ni valida el receipt y reutiliza un campo con semántica insuficiente.
5. **Convertir el consumo mediante `adapt_qtg`**: acepta un resultado desprendido y elimina toda la prueba especializada.
6. **Capturar el consumo en un `CapabilityInvoker`**: reabre exactamente el bypass genérico cerrado.
7. **Añadir QTG directamente a `ExecutionOutcome` o `CapabilityExecution`**: reabre contratos comunes antes de definir la pertenencia especializada.
8. **Considerar `APTO` equivalente a ejecución completada**: mezcla estado funcional de calidad con estado técnico.

### 3.1 Frontera mínima que sobrevive

La siguiente unidad legítima es diseñar un **binding especializado previo y posterior a la ejecución**, todavía externo al Vertical:

```text
ProjectionQualityConsumption operacional
+ ProjectionMaterialEnvelope
+ PurchaseOperation runtime
+ DecisionContext runtime
+ policy_version explícita
→ ProjectionQualityO1Binding
```

El binding deberá:

- revalidar consumo, receipt, envelope, modo y alcance;
- extraer compra y contexto desde el DIP anidado y exigir igualdad completa con los inputs runtime;
- conservar snapshots completos o fingerprints canónicos verificables de compra y contexto;
- conservar `policy_version` como identidad externa, sin equipararla a otras versiones;
- calcular una huella de binding sobre todos esos elementos;
- poder cerrarse contra el `ExecutionOutcome` terminal exacto mediante un snapshot o fingerprint canónico de la salida;
- distinguir `BOUND_INPUT` de `BOUND_TERMINAL_OUTCOME`;
- no producir `CapabilityExecution`, no invocar capacidades y no conceder autoridad decisional.

La definición de un identificador de ocurrencia nuevo queda fuera de esta auditoría. Si se considera necesario, requerirá autoridad explícita; no debe disfrazarse como el `execution_id` determinista existente.

## 4. AUDITAR 2

La segunda revisión confirma:

- la compra y el contexto necesarios existen físicamente dentro del material QTG;
- no hace falta modificar el productor ni el consumidor para recuperarlos;
- falta, sin embargo, una prueba persistente que los una a la política y al resultado terminal O1;
- el `execution_id` existente sirve para identidad reproducible de contexto, no para distinguir ejecuciones repetidas;
- un binding externo puede diseñarse sin habilitar QTG como capacidad Vertical;
- el cierre contra un resultado terminal debe ocurrir después de la ejecución y verificar que la política coincide;
- no existe fundamento para reabrir `quality_invoker`, `adapt_qtg` o el envelope común O1.

## 5. CERRAR

### 5.1 Decisión

**No aprobar la incorporación de QTG a O1 ni al Vertical.**

Sí se considera preparada para diseño la frontera `ProjectionQualityO1Binding`, con dos estados técnicos especializados —entrada vinculada y resultado terminal vinculado— y sin representación como `CapabilityExecution`.

### 5.2 Condición para una futura integración

Incluso después de materializar el binding, una integración Vertical requerirá una auditoría adicional que determine:

- dónde se conserva el artefacto especializado sin reducirlo;
- si la salida pública debe ampliarse o acompañarse mediante una fachada específica;
- cómo se representa un resultado QTG negativo o no evaluable sin falsear el estado técnico del plan;
- qué prueba operacional real autoriza el primer caso E2E.

## 6. MATERIALIZAR

Esta unidad materializa únicamente la presente auditoría. No modifica código, modelos, firmas, adaptadores, productores, consumidores ni rutas de ejecución.

La modificación local ajena de `08_Implementacion/Viability_Frontier_Scenario_Analytics_Integration_Contract_v0.1.md` queda fuera de alcance.

## 7. CI

El cierre integrado exige suite completa, PR limitado a este documento, CI exact-head, merge protegido por SHA y CI post-merge. El éxito de CI no habilita QTG.
