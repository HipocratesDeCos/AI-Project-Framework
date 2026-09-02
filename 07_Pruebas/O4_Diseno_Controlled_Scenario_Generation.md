# EIOS — O4 · CONTROLLED SCENARIO GENERATION & EXPLORATION

**Estado:** 🟡 DISEÑO DEPURADO — NO IMPLEMENTADO
**Baseline:** `ad7961935cc19ca4ab0a19dbef0ac9d4721c8374`
**Rama:** `design/o4-controlled-scenario-generation`

## 1. Propósito

Definir una capacidad futura de generación y exploración controlada de escenarios que amplíe O2 sin modificar su autoridad ni convertirse en motor de optimización o decisión.

O4 produce únicamente candidatos de escenario dentro de un espacio de hipótesis explícitamente autorizado. La evaluación permanece separada y podrá utilizar O3 mediante una integración contractual posterior.

## 2. Modelo contractual mínimo

```text
AuthorizedScenarioSpace + GenerationPolicy + DecisionContext
                         ↓
                         O4
                         ↓
                 CandidateScenario
                         ↓
                         O2
                         ↓
                  ScenarioVersion
                         ↓
                         O3
```

O4 no crea una segunda identidad ni un segundo versionado de escenario.

## 3. Variables autorizadas

Cada variable debe declarar externamente:

- identificador estable;
- tipo de valor;
- dominio finito permitido;
- cardinalidad;
- discretización, si aplica;
- límites específicos, si existen.

Una variable no declarada no puede ser generada.

Un parámetro EIOS nunca se convierte implícitamente en variable de escenario.

## 4. Cardinalidad

Sea `D_i` el dominio finito de cada una de `n` variables.

Para producto cartesiano:

`|S| = Π |D_i|`

Con cero variables, el espacio contiene un único escenario base candidato: `|S| = 1`.

Un dominio vacío produce `|S| = 0` y no genera candidatos.

La cardinalidad se calcula **antes** de materializar candidatos.

## 5. Límites y precedencia

Los límites son restricciones duras y se comprueban antes de expandir el espacio.

Precedencia:

```text
1. validez estructural del espacio
2. límite de variables
3. cardinalidad por variable
4. cardinalidad total del espacio
5. profundidad de derivación
6. máximo de candidatos emitidos
```

El primer límite incumplido determina el bloqueo. No se inicia una expansión parcial que pueda producir resultados ambiguos.

Los valores numéricos definitivos permanecen pendientes de aprobación contractual.

## 6. Estados técnicos de generación

O4 deberá distinguir, como mínimo:

- `GENERATED`: candidatos emitidos satisfactoriamente;
- `EMPTY`: espacio válido pero sin candidatos;
- `BLOCKED`: generación impedida por una restricción o límite;
- `NOT_EVALUABLE`: no existe información suficiente para determinar el espacio de forma válida;
- `FAILED`: fallo técnico explícito con causa obligatoria.

Estos estados son técnicos y no constituyen estados de viabilidad ni resultados empresariales.

## 7. Generación MVP

Se autoriza conceptualmente únicamente:

- enumeración determinista de valores;
- producto cartesiano finito y explícitamente permitido;
- derivación controlada desde un escenario padre.

Las combinaciones no cartesianas quedan fuera del MVP hasta disponer de semántica contractual específica.

No se autoriza generación probabilística, adaptativa o heurística.

## 8. Deduplicación

La identidad candidata se determinará por la representación canónica de:

`DecisionContext + parent_scenario_id + ordered canonical changes`

La deduplicación ocurre antes de la emisión final.

El orden de entrada de variables o cambios no puede crear candidatos distintos cuando su representación canónica sea equivalente.

O4 delegará la identidad/versionado contractual definitivo a O2.

## 9. Poda

El MVP solo permite poda **estructural**, definida por la propia política de generación antes de iniciar la exploración.

Ejemplos válidos: dominio excluido explícitamente, incompatibilidad estructural declarada, límite de profundidad.

No son poda válida:

- rentabilidad;
- utilidad;
- preferencia;
- ranking;
- predicción;
- resultado de viabilidad usado como criterio implícito de selección.

La poda deberá ser determinista y trazable.

## 10. Trazabilidad

Una ejecución de generación deberá poder reproducirse a partir de:

```text
execution context autorizado
+ espacio canónico de variables
+ generation policy version
+ límites efectivos
+ escenario padre
```

La trazabilidad utilizará las identidades/contextos ya existentes. O4 no crea `Decision_ID`, `Trace_ID`, `input_fingerprint` o `data_snapshot_id` paralelos.

La política de generación debe tener versión identificable antes de materializarse.

## 11. Seguridad de expansión

Nunca se permite expandir un espacio cuyo tamaño conocido supere un límite contractual.

Si el tamaño no puede determinarse de forma segura antes de la expansión, el resultado será `NOT_EVALUABLE`.

No existe fallback silencioso a una búsqueda ilimitada.

## 12. Relaciones de autoridad

```text
O4 → genera candidatos
O2 → representa/versiona escenarios
O3 → consume resultados de evaluación
Viability Frontier → determina viabilidad
Decision Twin → representa/compara alternativas
CRC → resuelve conflictos posteriores
HUMANO → decisión empresarial
```

O4 no modifica reglas, parámetros, evidencia, RDM, operación real ni decisiones.

## 13. Invariantes

```text
OPERACIÓN REAL ≠ ESCENARIO
PARÁMETRO ≠ VARIABLE DE ESCENARIO
CANDIDATO ≠ ALTERNATIVA
ALTERNATIVA ≠ DECISIÓN
O4 ≠ O2
O4 ≠ O3
O4 ≠ VIABILITY FRONTIER
O4 ≠ DECISION TWIN
O4 ≠ NEGOTIATION
O4 ≠ CRC
O4 ≠ OPTIMIZATION
NOT_EVALUABLE ≠ NOT_VIABLE
```

Además:

1. escenario padre inmutable;
2. operación real inmutable;
3. reglas inmutables;
4. parámetros inmutables;
5. RDM inmutable;
6. evidencia no inventada;
7. determinismo;
8. límites finitos;
9. trazabilidad reproducible;
10. sin selección empresarial.

## 14. Fuera de alcance

Quedan fuera del O4 MVP:

- optimización;
- ranking;
- selección automática;
- recomendación;
- negociación automática;
- aprendizaje adaptativo;
- búsqueda ilimitada;
- SQL;
- persistencia;
- API;
- nuevo modelo de datos.

## 15. Criterios de entrada a implementación

Antes de implementar deben quedar aprobados:

1. tipos y dominios de variables;
2. valores definitivos de límites;
3. política de generación;
4. contrato de estados;
5. contrato de deduplicación;
6. poda estructural;
7. trazabilidad y versión de política;
8. pruebas deterministas de cardinalidad y límites;
9. integración contractual O4 → O2 → O3, si se decide incluirla;
10. AUDITORÍA 2 sin hallazgos bloqueantes.

**No se autoriza implementación por este documento.**