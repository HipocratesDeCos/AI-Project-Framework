# Negotiation Ladder — Implementation Contract

**Estado:** CERRADO — contrato de implementación
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

## 3. Modelo canónico

### 3.1 Context references

`LadderContextReferences` mantiene únicamente referencias a autoridades upstream:

- `negotiation_result_id` — obligatorio;
- `decision_id` — obligatorio;
- `decision_version` — obligatorio;
- `scenario_id` — opcional;
- `source_references` — referencias de origen.

No crea un sistema paralelo de versionado.

### 3.2 Step

Cada `LadderStep` contiene:

- `step_id`;
- `step_type`;
- `source_content_reference` — obligatorio;
- `position` — entero positivo;
- `representation_metadata`.

El step no contiene una copia editable del contenido sustantivo.

Tipos permitidos:

`OBJECTIVE`, `OPENING_REQUEST`, `MOVE`, `CONCESSION`, `COUNTERPART_CONSIDERATION`, `CONDITION`, `ALTERNATIVE`, `FALLBACK`, `LIMIT`, `WALK_AWAY`.

### 3.3 Transition

Cada transición contiene:

- `transition_id`;
- `from_step_id`;
- `to_step_id`;
- `trigger_reference` opcional.

Solo puede referenciar steps existentes.

### 3.4 Route

Cada ruta contiene:

- `route_id`;
- `step_references`.

Todos los steps referenciados deben existir.

### 3.5 Result

`NegotiationLadderResult` contiene:

- `ladder_id`;
- `context_references`;
- `steps`;
- `transitions`;
- `routes`;
- `traceability_references`.

Debe contener al menos un step y es inmutable.

## 4. Invariantes

1. Los modelos son inmutables.
2. Los campos no declarados son rechazados.
3. `ladder_id` es obligatorio.
4. `negotiation_result_id`, `decision_id` y `decision_version` son obligatorios.
5. Cada `step_id` es único.
6. Cada step tiene `source_content_reference`.
7. `position` es entero positivo y único dentro del resultado.
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
19. La representación de `WALK_AWAY` no crea un nuevo límite.
20. Ladder no altera sustantivamente el contenido referenciado por `source_content_reference`.

## 5. Exclusiones explícitas

Este contrato no materializa:

- Negotiation Intelligence;
- Scenario Engine;
- Viability Frontier;
- Decision Twin;
- Strategy;
- Conflict Resolution;
- decisión empresarial;
- aprobación;
- ejecución.

## 6. Determinismo e identidad

Una misma entrada estructural debe producir una representación equivalente.

La identidad propia de Ladder es `ladder_id`. Las identidades de decisión, versión, escenario y resultado NI se referencian y no se redefinen.

Las representaciones históricas no deben sobrescribirse.

## 7. Criterios mínimos de prueba

La implementación debe probar:

- construcción válida;
- rechazo de campos desconocidos;
- inmutabilidad;
- identidad y contexto upstream obligatorios;
- step IDs únicos;
- referencias de origen obligatorias;
- posiciones positivas y únicas;
- rechazo de transiciones hacia steps inexistentes;
- rechazo de rutas hacia steps inexistentes;
- IDs únicos de transiciones y rutas;
- ausencia de campos estratégicos/decisionales;
- ausencia de creación de límites/escenarios;
- trazabilidad obligatoria;
- representación de walk-away sin mutación de límites;
- creación de nueva identidad para una nueva representación.
