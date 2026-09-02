# EIOS — O4 · AUDITORÍA 1 DE IMPLEMENTACIÓN

**Estado:** AUDITORÍA INICIAL — HALLAZGOS REQUIEREN DEPURACIÓN
**Diseño:** cerrado y autorizado para materialización
**Implementación revisada:** `eios/core/scenario_generation.py`
**Pruebas revisadas:** `tests/test_scenario_generation.py`

## Alcance

Auditar la primera materialización de O4 frente al diseño cerrado, sin ampliar el contrato.

## Hallazgos

### H1 — `max_total_combinations=0` y espacio base
El algoritmo inicializa la cardinalidad en 1. Con cero variables, un límite total de 0 bloquea el candidato base, aunque el diseño define explícitamente que cero variables producen un candidato base. Debe fijarse la precedencia contractual para que el límite no convierta el caso base válido en un falso bloqueo, o documentar una regla equivalente explícita.

### H2 — `allow_cartesian` no participa en la ejecución
La política expone `allow_cartesian`, pero `generate_scenarios()` no la consulta. El MVP es CARTESIAN y el campo no debe aparentar controlar una capacidad que no implementa.

### H3 — `structural_pruning` no participa en la ejecución
La política expone reglas de pruning estructural, pero no existe aplicación determinista de dichas reglas. Debe implementarse el subconjunto contractual o retirarse del modelo MVP; no puede quedar una configuración aparentemente operativa sin efecto.

### H4 — `value_type` no se valida contra los valores
`ScenarioVariable.value_type` se almacena pero no se comprueba. Si el diseño lo considera tipado, debe existir validación mínima; si no forma parte de la semántica MVP, debe declararse como metadata no ejecutiva.

### H5 — identidad padre/hijo
No se rechaza `parent_scenario_id == scenario_id`. Debe impedirse el auto-parentado para preservar la derivación estructural.

### H6 — deduplicación posterior a cardinalidad
La cardinalidad y los límites se calculan antes de deduplicar valores equivalentes. Un dominio con duplicados puede bloquear por cardinalidad aunque el conjunto efectivo de candidatos sea menor. Debe decidirse contractualmente si los dominios duplicados son inválidos o si la cardinalidad contractual se basa en valores declarados; no asumir una semántica nueva durante implementación.

### H7 — estados declarados sin camino determinista completo
`NOT_EVALUABLE` no tiene actualmente una condición de producción y `FAILED` solo puede aparecer mediante construcción directa del resultado, no desde el generador. Debe revisarse si esos estados pertenecen realmente al MVP de generación o deben quedar explícitamente fuera de la implementación inicial.

### H8 — `_canonical_value()` usa `repr()` para tipos no básicos
Para valores no básicos, la representación depende de `repr()`, que no constituye necesariamente una serialización canónica estable. Debe limitarse el dominio MVP a tipos soportados o definirse una canonicalización determinista.

## Dictamen

**AUDITORÍA 1: NO CERRABLE EN EL ESTADO ACTUAL.**

La implementación es conceptualmente coherente con el diseño, pero H1–H8 deben resolverse mediante depuración controlada antes de Audit 2. No se autoriza merge ni cierre de materialización mientras permanezcan hallazgos contractuales abiertos.
