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

- `decision_id`
- `decision_version`
- `scenario_id` opcional
- `viability_reference` opcional
- `decision_twin_reference` opcional
- `negotiation_result_id` opcional

No crea un sistema paralelo de versionado.

### 3.2 Step

Cada `LadderStep` contiene:

- `step_id`
- `step_type`
- `source_content_reference`
- `position`
- `representation_metadata`

`source_content_reference` es obligatorio.

`step_type` permitido:

`OBJECTIVE`, `REQUEST`, `MOVE`, `CONCESSION`, `COUNTERPART_CONSIDERATION`, `CONDITION`, `ALTERNATIVE`, `FALLBACK`, `LIMIT`, `WALK_AWAY`.

El step no contiene una copia editable del contenido sustantivo.

### 3.3 Transition

Cada transición contiene:

- `transition_id`
- `from_step_id`
- `to_step_id`
- `trigger_reference` opcional
- `condition_reference` opcional

Solo puede referenciar steps existentes.

### 3.4 Route

Cada ruta contiene:

- `route_id`
- `step_references`

Todos los steps referenciados deben existir.

### 3.5 Result

`NegotiationLadderResult` contiene:

- `ladder_id`
- `context_references`
- `steps`
- `transitions`
- `routes`
- `traceability_references`

Es inmutable.

## 4. Invariantes

1. Los modelos son inmutables.
2. Los campos no declarados son rechazados.
3. `ladder_id` es obligatorio.
4. Cada `step_id` es único.
5. Cada step tiene `source_content_reference`.
6. `position` es entero positivo.
7. Las transiciones solo conectan steps existentes.
8. Las rutas solo contienen referencias a steps existentes.
9. No existe contenido estratégico autónomo.
10. Ladder no crea ni modifica límites.
11. Ladder no crea escenarios.
12. Ladder no calcula viabilidad.
13. Ladder no recalcula Decision Twin.
14. Ladder no crea decisiones, aprobaciones ni ejecuciones.
15. La trazabilidad del resultado es obligatoria.
16. La representación de `WALK_AWAY` no crea un nuevo límite.
17. Ladder no altera sustantivamente el contenido referenciado por `source_content_reference`.

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
- step IDs únicos;
- referencias de origen obligatorias;
- posiciones válidas;
- rechazo de transiciones hacia steps inexistentes;
- rechazo de rutas hacia steps inexistentes;
- ausencia de campos estratégicos/decisionales;
- ausencia de creación de límites/escenarios;
- trazabilidad obligatoria;
- representación de walk-away sin mutación de límites;
- creación de nueva identidad para una nueva representación.
