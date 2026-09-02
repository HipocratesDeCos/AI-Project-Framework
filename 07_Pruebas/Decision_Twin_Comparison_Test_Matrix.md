# EIOS — Decision Twin Comparison Test Matrix

## 1. Propósito

Matriz de pruebas para verificar `Decision_Twin_Comparison_Contract.md` antes de aceptar implementación productiva.

Objetivo principal: demostrar comportamiento comparativo permitido y ausencia de selección implícita.

## 2. Casos funcionales

| ID | Caso | Resultado verificable |
|---|---|---|
| DT-C01 | Comparación A/B | Valores observados + diferencias; ningún campo de preferencia |
| DT-C02 | Comparación A/B/C | Matriz descriptiva; ningún orden decisional |
| DT-C03 | Orden inverso A/B | Mismo conjunto de hechos; puede invertirse la orientación de presentación de la diferencia |
| DT-C04 | Valor ausente en A o B | Ausencia/no disponibilidad conservada; sin valor sintético |
| DT-C05 | Atributos no comparables | No comparabilidad explícita; sin equivalencia fabricada |
| DT-C06 | Conflicto multidimensional | Observaciones conservadas; sin prioridad derivada |
| DT-C07 | VIABLE vs NOT_VIABLE | Estados conservados; sin selección empresarial |
| DT-C08 | Evidencia redundante | Mismo significado comparativo; sin peso por conteo |
| DT-C09 | Información adicional | Se amplía la representación; no aparece preferencia |
| DT-C10 | Múltiples referencias Trace | Referencias conservadas; no se crea Trace nuevo |

## 3. Casos de prohibición observable

| ID | Propiedad prohibida | Aserción |
|---|---|---|
| DT-P01 | score | La salida no contiene campo/valor de score generado por Comparison |
| DT-P02 | ranking | La salida no contiene clasificación ordinal generada por Comparison |
| DT-P03 | ganador | La salida no contiene ganador generado por Comparison |
| DT-P04 | alternativa preferente | La salida no contiene preferencia generada por Comparison |
| DT-P05 | utilidad | La salida no contiene función/valor de utilidad generado por Comparison |
| DT-P06 | optimización | Comparison no ejecuta optimización |
| DT-P07 | decisión | La salida no contiene decisión empresarial generada por Comparison |
| DT-P08 | conflicto por conteo | El número de señales favorables no produce prioridad |
| DT-P09 | ausencia como penalización | Missing no se transforma automáticamente en penalización |
| DT-P10 | mutación | Objetos fuente permanecen sin modificación |

## 4. Invariantes

### I1 — Simetría semántica

`compare(A,B)` y `compare(B,A)` deben referirse al mismo conjunto de observaciones y diferencias. La orientación o signo de una diferencia puede invertirse por el cambio de referencia, sin alterar su contenido factual.

### I2 — No selección

Ningún resultado comparativo puede contener una conclusión de alternativa preferente generada por Comparison.

### I3 — No scoring

No existe transformación automática de observaciones a puntuación.

### I4 — No ranking

La cardinalidad o el orden de las alternativas no crea clasificación decisional.

### I5 — No penalización por ausencia

Un dato ausente permanece ausente/no disponible según la semántica de su fuente.

### I6 — No ponderación por redundancia

Repetir evidencia o señales equivalentes no incrementa automáticamente su influencia.

### I7 — Inmutabilidad de fuentes

La comparación no modifica Assessment, Evidence, Viability, Scenario, Trace ni Decision State.

### I8 — Trazabilidad conservativa

Las referencias se conservan sin crear una autoridad de Trace paralela.

### I9 — Separación de viabilidad

El estado de Viability Frontier se representa sin alterar su semántica.

### I10 — Separación de decisión

La salida de Comparison no constituye una decisión empresarial.

## 5. Casos de regresión de integración

| ID | Integración | Condición verificable |
|---|---|---|
| DT-R01 | Scenario Engine | Una hipótesis se deriva hacia Scenario Engine; Comparison no recalcula escenario |
| DT-R02 | Viability Frontier | Comparison consume el resultado; no redefine estados |
| DT-R03 | Assessment | Assessment conserva su individualidad |
| DT-R04 | Evidence | Comparison no determina suficiencia/admisibilidad |
| DT-R05 | Negotiation | Las diferencias pueden transmitirse; Comparison no decide condiciones |
| DT-R06 | CRC | Los conflictos pueden transmitirse; Comparison no los resuelve |
| DT-R07 | Decision Versioning | Referencias históricas permanecen bajo su autoridad |

## 6. Criterio de aprobación

El contrato solo pasa a implementación cuando:

1. todos los casos funcionales son observables;
2. todos los casos de prohibición pueden expresarse como aserciones o controles;
3. todos los invariantes tienen una prueba verificable;
4. las regresiones de integración no introducen autoridad nueva;
5. las pruebas no requieren persistencia propia de `Alternative`;
6. ningún test depende de una petición textual al sistema como sustituto de una aserción sobre la salida o los efectos.

Una prueba que detecte selección implícita deberá considerarse FALLIDA y no podrá resolverse relajando la aserción para acomodar el comportamiento.

**Estado:** MATRIZ IMPLEMENTADA Y MATERIALIZADA — validación CI completada en el alcance actual; pendiente únicamente de la nueva ejecución CI del commit de reconciliación documental.
