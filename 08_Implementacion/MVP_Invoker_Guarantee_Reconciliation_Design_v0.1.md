# EIOS — MVP Invoker Guarantee Reconciliation · Diseño v0.1

## Estado

**DISEÑAR — COMPLETADO**

Unidad: `MVP-INVOKER-GUARANTEE-RECON-01`

Baseline: `main @ d79e27cad7c557c382d6f86dc5336073db8eede6`

## 1. Problema objetivo

`eios/core/mvp_execution.py` declara actualmente que PRICE, TCO, Decision Twin, Scenario Coordination, Negotiation Intelligence y Negotiation Ladder deben llegar mediante `explicit provenance-safe invokers`.

Esa frase excede la garantía autorizada para varias fronteras.

La regresión fue introducida por el commit `d5c4f5f239e1f1b08a530d69bace279650ae3670` durante la cuarentena QTG. Antes de ese cambio el mismo docstring establecía correctamente:

- las capacidades afectadas entran mediante invocadores explícitos;
- el boundary no re-etiqueta resultados raw desprendidos;
- la mera presencia de un invocador no constituye prueba de procedencia.

La modificación QTG sustituyó esa última salvaguarda por una afirmación global `provenance-safe` que no pertenecía al alcance QTG.

## 2. Autoridad contrastada

### 2.1 E2E Execution Boundary

`E2E_Execution_Boundary_Implementation_Contract.md` exige un catálogo explícito `capability -> invoker`, identidad/contexto canónicos y resultados `CapabilityExecution`. No declara que cualquier callable del catálogo sea por sí mismo provenance-safe.

### 2.2 NI + Ladder

`Vertical_MVP_NI_Ladder_Opaque_Result_Quarantine_Contract_v0.1.md` establece expresamente:

- eliminar resultados NI/Ladder desprendidos de las fronteras públicas;
- aceptar invocadores explícitos;
- un invocador explícito **no constituye por sí solo certificación provenance-safe**;
- productores NI/Ladder realmente provenance-safe requerirían contratos posteriores.

No existe en el baseline un builder posterior que cierre esa política positiva.

### 2.3 Scenario Coordination

`Vertical_MVP_Scenario_Coordination_Opaque_Result_Quarantine_Contract_v0.1.md` establece el mismo principio: un invocador explícito separa composición y producción, pero su presencia no prueba procedencia.

La ruta especializada desde orquestación puede reconstruir soporte a partir de material congelado, pero tampoco certifica por sí sola la procedencia de toda la orquestación upstream.

### 2.4 PRICE / TCO

PRICE y TCO disponen de contratos/builders específicos provenance-safe. Esta unidad no los modifica ni degrada. Su garantía positiva sigue perteneciendo a sus contratos especializados, no al tipo genérico `CapabilityInvoker`.

### 2.5 Decision Twin / QTG

Decision Twin conserva el slot estructural del boundary, pero su wrapper público dependiente de Stage 2 está en cuarentena por la ausencia de productor VF provenance-safe.

QTG permanece en `MVP_CAPABILITY_ORDER` pero la frontera genérica no acepta `quality_invoker` hasta existir un `Decision Input Package` físico, agregado y trazable y un productor autorizado.

## 3. Clasificación

El defecto es una **regresión de garantía documental embebida en código**.

No se ha demostrado:

- fallo del algoritmo de `execute_plan`;
- reintroducción de raw results;
- cambio de identidad/contexto;
- necesidad de productor NI/Ladder nuevo;
- necesidad de modificar signatures o adapters.

Por tanto no se autoriza una corrección funcional.

## 4. Diseño de corrección

Modificar exclusivamente el docstring de `run_mvp_execution(...)` para recuperar la garantía estrecha y correcta:

1. PRICE, TCO, Decision Twin, Scenario Coordination, Negotiation Intelligence y Negotiation Ladder deben entrar por **explicit invokers**;
2. el boundary no re-etiqueta detached raw results;
3. **invoker presence alone is not provenance proof**;
4. QTG permanece en el orden arquitectónico pero no se acepta en la frontera genérica hasta disponer de su productor provenance-safe autorizado.

No se afirmará que todos los invokers genéricos son provenance-safe.

## 5. Alcance autorizado

Producción/documentación embebida:

- `eios/core/mvp_execution.py` — únicamente docstring.

Trazabilidad de esta unidad:

- diseño;
- Audit 1;
- depuración;
- Audit 2;
- cierre;
- auditoría de materialización.

## 6. Cambios prohibidos

Esta unidad no puede:

- cambiar firmas públicas;
- añadir o retirar capacidades;
- modificar `MVP_CAPABILITY_ORDER`;
- crear builders NI/Ladder;
- reactivar Decision Twin;
- reactivar QTG;
- modificar PRICE/TCO/Scenario Coordination;
- cambiar `execute_plan`;
- modificar tests funcionales salvo contradicción objetiva descubierta por auditoría/CI;
- reescribir artefactos históricos para ocultar la regresión;
- crear autoridad empresarial.

## 7. Criterios de aceptación

1. El texto operativo deja de afirmar que todos los invokers son provenance-safe.
2. Se conserva la prohibición de detached raw results.
3. Se conserva la cuarentena QTG.
4. No cambia ninguna línea ejecutable de producción.
5. No cambia ninguna firma/API.
6. No cambia el orden canónico.
7. PRICE/TCO conservan sus garantías especializadas.
8. NI/Ladder y Scenario Coordination conservan explícitamente que invoker presence no prueba procedencia.
9. Decision Twin no se reabre.
10. CI Python + SQL permanece verde.

## 8. Resultado

**DISEÑO v0.1 COMPLETADO.**

Procede **AUDITAR** antes de modificar `mvp_execution.py`.