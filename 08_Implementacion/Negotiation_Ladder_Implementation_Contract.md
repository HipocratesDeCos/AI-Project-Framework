# Negotiation Ladder — Implementation Contract

**Estado:** CERRADO — RECONCILIADO Y MATERIALIZADO  
**Autoridad funcional:** `05_Motor/Negotiation_Ladder.md`  
**Dependencia upstream principal:** `08_Implementacion/Negotiation_Intelligence_Implementation_Contract.md`

## 1. Propósito

Este contrato materializa exclusivamente la representación estructural y secuencial del contenido negociador previamente determinado por una autoridad competente.

Ladder no determina ni modifica el contenido sustantivo de negociación.

## 2. Frontera de autoridad

```text
Negotiation Intelligence / autoridad competente
                    ↓
          contenido previamente determinado
                    ↓
             Negotiation Ladder
                    ↓
       estructura / representación / secuencia
```

La transformación es estructural, no sustantiva.

## 3. Contexto e identidad autorizados

`LadderContextReferences` conserva únicamente referencias upstream:

- `negotiation_result_id` — obligatorio;
- `decision_id` — obligatorio;
- `scenario_id` — opcional;
- `source_references` — referencias de origen.

**`decision_version` no forma parte del contrato.** No se crea una identidad o versión de decisión paralela. La continuidad decisional se conserva mediante las identidades autorizadas de Decision Context y las referencias upstream.

La identidad propia de Ladder es `ladder_id`.

## 4. Modelo canónico

Cada `LadderStep` contiene `step_id`, `step_type`, `source_content_reference`, `position` y metadatos de representación.

Las transiciones y rutas solo referencian steps existentes.

`NegotiationLadderResult` contiene `ladder_id`, contexto, steps, transitions, routes y referencias de trazabilidad.

## 5. Invariantes

1. Los modelos son inmutables.
2. Los campos no declarados son rechazados.
3. `ladder_id` es obligatorio.
4. `negotiation_result_id` y `decision_id` son obligatorios.
5. Cada `step_id` es único.
6. Cada step tiene `source_content_reference`.
7. `position` es positivo y único.
8. Las transiciones solo conectan steps existentes.
9. Cada `transition_id` es único.
10. Las rutas solo contienen referencias a steps existentes.
11. Cada `route_id` es único.
12. No existe contenido estratégico autónomo.
13. Ladder no crea ni modifica límites.
14. Ladder no crea escenarios.
15. Ladder no calcula viabilidad.
16. Ladder no recalcula Decision Twin.
17. Ladder no crea decisiones, aprobaciones ni ejecuciones.
18. La trazabilidad del resultado es obligatoria.
19. `WALK_AWAY` no crea un nuevo límite.
20. Ladder no altera sustantivamente el contenido referenciado.
21. Ladder no introduce `decision_version` como identidad paralela.

## 6. Determinismo e identidad

Una misma entrada estructural debe producir una representación equivalente.

La identidad propia de Ladder es `ladder_id`. Las identidades de decisión, escenario y resultado NI se referencian y no se redefinen.

Las representaciones históricas no deben sobrescribirse.

## 7. Criterios mínimos de prueba

La implementación prueba construcción válida, campos desconocidos, inmutabilidad, identidad y contexto upstream, unicidad de steps/posiciones/transiciones/rutas, referencias de origen, ausencia de campos estratégicos y decisionales, trazabilidad y rechazo explícito de `decision_version`.

## 8. Estado

**Implementación física:** materializada en `eios/core/negotiation_ladder.py`.  
**Tests físicos:** materializados en `tests/test_negotiation_ladder.py`.  
**Estado:** CERRADO — RECONCILIADO Y MATERIALIZADO.  
**Tipo de cambio:** corrección de frontera documental/técnica; sin nueva autoridad funcional.  
**Decision Versioning:** NO ALTERADO.  
**C0:** NO ALTERADO.  
**O2:** NO ALTERADO.  
**Método:** DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI.
