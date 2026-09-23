# EIOS — NI + Ladder Provenance Producer Completion Package v0.1

**Baseline:** `main @ 65d1ed3930ba81c739f420e3cb2cc58396500107`  
**Fecha:** 23/09/2026  
**Estado:** PROPUESTA CONSOLIDADA — NO AUTORIZADA / NO VIGENTE

## 1. Objetivo

Cerrar la frontera provenance-safe de:

- `NEGOTIATION_INTELLIGENCE`;
- `NEGOTIATION_LADDER`;

sin inventar estrategia negociadora, objetivos, concesiones, límites o fallback desde Decision Twin, Rules o datos.

El paquete no convierte al sistema en decisor de negociación. Materializa únicamente contenido negociador ya determinado por una autoridad explícita y lo estructura después en Ladder.

## 2. Principio de autoridad

```text
Decision Twin ≠ Negotiation Strategy
Rule TRUE ≠ Negotiation Move
Viability ≠ Opening Request
Evidence ≠ Concession
```

NI no inferirá automáticamente:

- objective;
- opening_request;
- moves;
- concessions;
- counterpart_requirements;
- tradeoffs;
- packages;
- fallback;
- conditions.

Esos elementos deberán llegar explícitamente como contenido autorizado y trazable.

## 3. Carrier upstream propuesto

```text
NegotiationContentEvidence
├── decision_id
├── scenario_id?
├── authority_ref
├── decision_twin_reference?
├── viability_reference?
├── negotiation_content
├── justification
├── evidence_refs
├── trace_refs
└── authority_state
```

`authority_state`:

```text
AUTHORIZED
NOT_AUTHORIZED
NOT_DETERMINABLE
CONFLICTING
```

Solo `AUTHORIZED` puede producir NI.

## 4. Binding

Para producir NI se exige:

- decision_id igual al DecisionContext;
- scenario_id, si existe, igual al contexto;
- rules_version / parameters_version / data_snapshot_id heredados del contexto;
- authority_ref demostrada mediante C0 Evidence;
- todas las evidence_refs demostradas;
- trace_refs no vacías;
- contenido NI válido según `NegotiationContent`;
- justificación válida según `NIAssertion`.

No se aceptan `NegotiationIntelligenceResult` desprendidos.

## 5. negotiation_result_id

Se propone identidad determinista:

```text
ni:{decision_id}:{scenario_id-or-none}:{content_fingerprint}
```

El fingerprint se calcula sobre:

- contexto canónico;
- authority_ref;
- negotiation_content;
- justification;
- evidence_refs;
- trace_refs.

No sustituye DecisionContext ni crea Decision Versioning paralelo.

## 6. Productor NI

API propuesta:

```text
produce_negotiation_intelligence(
    purchase,
    context,
    content_evidence,
    evidences
) -> NegotiationIntelligenceResult
```

Comportamiento:

- valida identidad;
- valida Evidence;
- construye `NIContextReferences`;
- conserva decision_twin_reference y viability_reference si están presentes;
- conserva evidence_references;
- copia literalmente el contenido negociador autorizado;
- no añade contenido nuevo;
- no reescribe epistemología;
- no calcula Strategy.

## 7. Invocador NI

```text
build_provenanced_negotiation_intelligence_invoker(...)
→ (PurchaseOperation, DecisionContext) -> CapabilityExecution
```

El invocador congela snapshots y produce internamente NI antes de `adapt_ni(...)`.

No acepta resultado NI crudo.

## 8. Ladder — alcance MVP

Ladder puede estructurar únicamente el subconjunto de `NegotiationContent` representable por sus StepType existentes.

Orden estructural propuesto:

```text
1 OBJECTIVE
2 OPENING_REQUEST
3 MOVE[*]
4 CONCESSION[*]
5 COUNTERPART_CONSIDERATION[*]
6 CONDITION[*]
7 ALTERNATIVE[*]
8 FALLBACK
```

Dentro de cada colección se conserva el orden original del contenido NI.

Campos NI sin StepType equivalente:

- tradeoffs;
- packages;
- convenience_analysis;

se preservan en referencias/trazabilidad del resultado NI, pero no generan steps Ladder v0.1.

No se inventa StepType nuevo.

## 9. source_content_reference

Formato determinista:

```text
ni:{negotiation_result_id}:content:{field}:{index}
```

Para campos singulares:

```text
index = 0
```

Ejemplos:

```text
ni:NI123:content:objective:0
ni:NI123:content:moves:1
```

## 10. ladder_id

Identidad determinista:

```text
ladder:{negotiation_result_id}:{structure_fingerprint}
```

No sustituye NI ni DecisionContext.

## 11. Transiciones y rutas

v0.1 no inventa lógica condicional.

Se propone:

- transitions = secuencia lineal entre steps consecutivos;
- trigger_reference = None;
- routes = una única ruta lineal si existen 2 o más steps;
- si existe un solo step, routes = vacío.

No se infieren bifurcaciones.

## 12. Productor Ladder

```text
produce_negotiation_ladder(
    negotiation_result,
    purchase,
    context
) -> NegotiationLadderResult
```

Debe validar:

- negotiation_result.context_references.decision_id == context.decision_id;
- scenario_id, si existe, coincide;
- purchase/context coinciden;
- resultado NI contiene traceability_references;
- contenido representable no vacío.

Si NI no contiene ningún campo representable:

```text
→ error técnico / no se produce Ladder
```

No se acepta Ladder desprendida como provenance-safe.

## 13. Invocador combinado

Se propone un productor conjunto opcional:

```text
build_provenanced_ni_ladder_invokers(...)
→ {
    negotiation_intelligence_invoker,
    negotiation_ladder_invoker
  }
```

Ambos comparten material congelado.

El invocador Ladder reconstruye internamente NI desde el mismo carrier autorizado antes de producir Ladder.

Así se garantiza:

```text
Ladder.context_references.negotiation_result_id
==
NI.negotiation_result_id
```

sin depender de resultados crudos externos.

## 14. Relación con Decision Twin

Decision Twin puede aportar referencia upstream:

```text
decision_twin_reference
```

pero no determina automáticamente contenido NI.

Una comparación Twin no se convierte por sí misma en objetivo, movimiento, concesión o fallback.

## 15. O1

Los invocadores producidos son compatibles con:

```text
run_mvp_execution(
  negotiation_intelligence_invoker=...,
  negotiation_ladder_invoker=...
)
```

No se reintroducen:

- negotiation_intelligence_result;
- negotiation_ladder_result.

## 16. Fail closed

No se produce NI/Ladder cuando exista:

- authority_state != AUTHORIZED;
- authority_ref no demostrada;
- Evidence GAP;
- decision/scenario mismatch;
- contenido inválido;
- trace_refs vacías;
- contenido Ladder no representable;
- manipulación del carrier tras freeze;
- contexto de ejecución distinto al autorizado.

## 17. No alcance

No autoriza:

- generación automática de estrategia;
- inferencia desde Rule/CRC/Twin;
- creación automática de concesiones;
- creación automática de límites;
- walk-away sustantivo;
- scoring/ranking;
- selección de alternativa;
- negociación autónoma;
- aprobación;
- ejecución;
- LLM generando contenido decisional.

## 18. Tests consolidados

1. AUTHORIZED produce NI;
2. NOT_AUTHORIZED → fail closed;
3. authority_ref GAP → fail closed;
4. identity mismatch → fail closed;
5. contenido copiado literalmente;
6. epistemología preservada;
7. deterministic negotiation_result_id;
8. invocador NI O1;
9. Ladder ordena objective/opening/moves/concessions/etc.;
10. orden interno preservado;
11. tradeoffs/packages/convenience no generan step;
12. transiciones lineales;
13. ruta lineal única;
14. deterministic ladder_id;
15. Ladder referencia negotiation_result_id exacto;
16. invocador combinado reconstruye misma NI;
17. NI/Ladder O1 orden canónico;
18. raw results siguen fuera de firmas;
19. freeze protege mutaciones;
20. ninguna generación estratégica automática.

## 19. Efecto de una autorización única

```text
AUTORIZAR
→ AUDITAR
→ MATERIALIZAR
   - carrier autorizado
   - productor NI
   - productor Ladder
   - invocadores O1
   - tests
→ CI
→ merge
→ CI main
```

## 20. Estado

**NI + LADDER PROVENANCE PRODUCER COMPLETION PACKAGE v0.1 — PROPUESTA / NO VIGENTE.**
