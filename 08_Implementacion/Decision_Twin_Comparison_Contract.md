# EIOS — Decision Twin Comparison Contract

## 1. Propósito

Define la semántica mínima de comparación estructural de `Decision Twin` sin introducir scoring, ranking, selección, optimización ni decisión.

La autoridad funcional permanece en `05_Motor/Decision_Twin.md`.

## 2. Entrada

Una comparación recibe dos o más alternativas representables y los datos ya autorizados asociados a ellas:

- resultados;
- estado de viabilidad;
- condiciones;
- consecuencias conocidas;
- riesgos ya determinados;
- referencias de trazabilidad.

No genera información nueva de las capas fuente.

## 3. Salida

La salida contiene exclusivamente información comparativa descriptiva:

```text
Comparison
├── alternatives represented
├── comparable observations
├── differences
├── common values
├── missing / unavailable values
├── viability differences
├── consequence differences
└── traceability references
```

La salida no contiene por defecto:

- score;
- ranking;
- utilidad;
- peso;
- ganador;
- alternativa preferente;
- decisión.

## 4. Regla de comparación

Para cada atributo comparable, el resultado debe conservar el valor o estado observado por alternativa y, cuando sea posible, describir la diferencia.

```text
A = valor X
B = valor Y

→ diferencia: X ≠ Y
```

La existencia de una diferencia no implica que uno de los valores sea superior.

## 5. Heterogeneidad

Si dos alternativas presentan atributos no directamente comparables, el sistema debe preservar la diferencia de disponibilidad o comparabilidad y no fabricar una equivalencia.

```text
A = disponible
B = no disponible

→ estado comparativo: información asimétrica
```

No se transforma automáticamente en peor/mejor.

## 6. Viabilidad

Los estados producidos por `Viability Frontier` pueden mostrarse como diferencias descriptivas.

```text
A = VIABLE
B = NOT_VIABLE

→ diferencia de viabilidad
```

No se genera selección automática.

## 7. Conflictos

Cuando atributos relevantes apunten en direcciones distintas:

```text
A → mejor resultado X
B → mejor resultado Y
```

la comparación debe conservar ambas observaciones.

No se crea una prioridad mediante conteo, suma, ponderación o inferencia.

## 8. Monotonicidad de representación

Añadir información correcta puede ampliar la representación comparativa, pero no puede cambiar por sí mismo la semántica de una observación existente.

Añadir atributos no crea automáticamente mayor preferencia.

Añadir referencias de trazabilidad no altera resultados.

Añadir información redundante no aumenta su peso decisional.

## 9. Información faltante

La ausencia de un valor se representa como ausencia/no disponibilidad según el contrato de la fuente.

Nunca se sustituye silenciosamente por:

- cero;
- peor caso;
- mejor caso;
- valor medio;
- valor estimado;
- penalización.

## 10. Orden de alternativas

El orden de entrada no implica preferencia.

Cambiar el orden de A y B debe producir la misma información comparativa salvo el orden de presentación.

## 11. Multiplicidad

La comparación admite dos o más alternativas.

La incorporación de una nueva alternativa amplía el conjunto comparado, pero no convierte ninguna alternativa existente en preferente por el mero hecho de la cardinalidad.

## 12. Prohibiciones

La implementación no podrá derivar de esta comparación:

```text
score
ranking
winner
preferred_alternative
utility
optimization
selection
business_decision
```

Si alguna capa posterior necesita alguno de estos conceptos, deberá disponer de autoridad y contrato propios.

## 13. Trazabilidad

Cada observación comparada debe conservar, cuando exista, la referencia a su fuente. La comparación no crea un nuevo mecanismo de Trace ni altera Evidence, Assessment, Viability o Scenario.

## 14. Invariantes

1. Comparar no selecciona.
2. Diferencia no significa superioridad.
3. Viable no significa comprar.
4. Ausencia no significa peor.
5. El orden de entrada no crea preferencia.
6. Más atributos no crean preferencia.
7. Más evidencia no crea peso decisional por conteo.
8. Un conflicto entre atributos no se resuelve mediante inferencia.
9. La comparación no modifica objetos fuente.
10. La trazabilidad no adquiere autoridad decisional.

## 15. Casos adversariales mínimos

### A/B con conflicto de dimensiones

```text
A: coste favorable
B: plazo favorable
→ conflicto descriptivo; no ganador
```

### A viable / B no viable

```text
→ diferencia de viabilidad; no selección automática
```

### A/B con datos faltantes

```text
→ asimetría informativa; no penalización inventada
```

### A/B/C

```text
→ matriz comparativa; no ranking implícito
```

### Reordenación

```text
compare(A,B) ≡ compare(B,A)
```

en contenido semántico, aunque cambie la posición de presentación.

## 16. Límites

Este contrato no define:

- qué atributos globales deben compararse en todos los dominios;
- función de utilidad;
- política de selección;
- ranking;
- optimización;
- recomendación empresarial;
- persistencia;
- SQL;
- API concreta.

**DICTAMEN:** comparación estructural autorizada; selección y decisión permanecen fuera de autoridad.