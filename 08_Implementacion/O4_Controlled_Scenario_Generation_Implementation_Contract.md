# EIOS — O4 · CONTROLLED SCENARIO GENERATION

**Estado:** 🔒 CONTRATO DEPURADO — PENDIENTE DE AUDITORÍA 2
**Base funcional:** `O4_Diseno_Controlled_Scenario_Generation.md`
**Scope:** materialización técnica del MVP de generación controlada de escenarios.

## 1. Propósito

Materializar exclusivamente el O4 MVP autorizado: generación determinista, finita y estructural de candidatos de escenario, delegando identidad y versionado a O2.

Este contrato no amplía la autoridad de O4 ni crea persistencia, API, SQL, optimización o decisión empresarial.

## 2. Límites contractuales MVP

- `max_variables = 8`
- `max_cardinality_per_variable = 20`
- `max_total_cardinality = 1000`
- `max_depth = 3`
- `max_emitted_candidates = 1000`

Son límites duros. La cardinalidad conocida que exceda `max_total_cardinality` bloquea antes de expandir; `max_emitted_candidates` no permite truncamiento silencioso de una expansión conocida como excesiva.

## 3. Tipos de variables

La implementación acepta únicamente variables declaradas con:

- `variable_id: str` no vacío y único;
- `value_type: str` limitado a `string`, `integer`, `number`, `boolean`;
- `domain: finite sequence` explícita;
- `discretization: optional metadata`, sin generación implícita;
- `structural_exclusions: optional deterministic constraints`.

Los valores del dominio deben ser coherentes con `value_type`. No se permite coerción silenciosa. Un espacio malformado no se trata como dominio vacío.

No se derivan variables desde parámetros EIOS.

## 4. Entrada de generación

La operación de generación recibirá un contexto autorizado, un espacio de variables canónico, una versión identificable y no vacía de la política, un escenario padre opcional y límites efectivos.

La entrada deberá validarse sin mutar objetos recibidos.

El contexto autorizado conserva las identidades existentes de EIOS. O4 no crea IDs, fingerprints, snapshots ni traces paralelos.

## 5. Política de generación

MVP exclusivamente:

1. enumeración determinista;
2. producto cartesiano finito;
3. derivación controlada desde escenario padre.

No se implementarán heurísticas, aleatoriedad, adaptación, scoring, ranking, selección ni optimización.

## 6. Cardinalidad y precedencia

La cardinalidad se calcula antes de emitir candidatos.

Precedencia obligatoria:

1. validez estructural;
2. máximo de variables;
3. cardinalidad por variable;
4. cardinalidad total;
5. profundidad;
6. máximo de candidatos emitidos.

Un primer incumplimiento produce `BLOCKED`; no se permite expansión parcial.

Con cero variables, cardinalidad = 1.
Un dominio vacío en un espacio estructuralmente válido produce `EMPTY`.
Una entrada malformada produce `FAILED` con causa técnica; cuando la cardinalidad no puede determinarse de forma segura, produce `NOT_EVALUABLE`.

## 7. Estados

El resultado técnico debe representar:

- `GENERATED` — candidatos emitidos;
- `EMPTY` — espacio válido sin candidatos;
- `BLOCKED` — límite o restricción impide generar;
- `NOT_EVALUABLE` — no puede determinarse de forma segura el espacio;
- `FAILED` — fallo técnico con causa obligatoria.

No se transforman estos estados en estados empresariales.

## 8. Canonicalización y deduplicación

La representación canónica ordenará variables por `variable_id` y cambios por su clave canónica antes de deduplicar. La deduplicación se realizará antes de la emisión final usando:

`DecisionContext + parent_scenario_id + ordered canonical changes`

El orden incidental de entrada no podrá crear duplicados semánticos.

La identidad/versionado contractual definitivo del escenario será responsabilidad de O2.

## 9. Poda

Solo se permiten exclusiones estructurales declaradas previamente por la política.

Queda prohibida cualquier poda basada en rentabilidad, utilidad, preferencia, viabilidad, predicción, ranking o recomendación.

## 10. Profundidad

`depth=0` representa el escenario padre/base.
Cada derivación incrementa profundidad en una unidad.
Una derivación que exceda `max_depth` queda bloqueada antes de construirse o emitirse.

## 11. Seguridad y determinismo

- Ninguna expansión puede iniciarse si la cardinalidad conocida supera un límite duro.
- Si la cardinalidad no puede determinarse con seguridad, resultado `NOT_EVALUABLE`.
- La salida debe ser reproducible con la misma entrada canónica y política versionada.
- No se admite fallback ilimitado.
- La política debe estar versionada antes de ejecutar la generación; O4 no inventa una versión por defecto.

## 12. Integración

La implementación O4 será una capacidad pura de generación. No invocará O2 ni O3 internamente.

La eventual integración O4 → O2 → O3 queda fuera de este MVP y requerirá contrato específico posterior.

## 13. Exclusiones

No incluye:

- persistencia;
- SQL;
- API;
- optimización;
- ranking;
- selección automática;
- recomendación;
- negociación;
- aprendizaje;
- modificación de reglas/parámetros/RDM;
- ejecución de operaciones reales.

## 14. Criterios de aceptación

La materialización solo podrá cerrarse si existen pruebas deterministas que cubran:

1. cero variables;
2. dominio vacío;
3. producto cartesiano conocido;
4. límite de variables;
5. límite por variable;
6. límite de cardinalidad total;
7. límite de profundidad;
8. deduplicación canónica independiente del orden de entrada;
9. poda estructural;
10. `NOT_EVALUABLE` ante cardinalidad no determinable;
11. `FAILED` con causa;
12. inmutabilidad de entradas;
13. ausencia de ranking/selección/optimización;
14. delegación de identidad/versionado a O2;
15. política versionada obligatoria;
16. coherencia estricta de tipos;
17. reproducibilidad.

## 15. Autoridad

Este contrato no sustituye el diseño funcional O4 ni modifica la autoridad de O2, O3, Viability Frontier, Decision Twin, Negotiation, CRC o del humano.

**Estado:** contrato depurado y preparado para AUDITORÍA 2.
