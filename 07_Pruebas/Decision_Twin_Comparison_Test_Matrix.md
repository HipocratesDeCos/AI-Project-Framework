# EIOS — Decision Twin Comparison Test Matrix

## 1. Propósito

Matriz ejecutable para verificar el contrato `Decision_Twin_Comparison_Contract.md` antes de implementar comportamiento productivo.

Objetivo principal: demostrar tanto el comportamiento permitido como la imposibilidad de introducir selección implícita.

## 2. Casos funcionales

| ID | Caso | Resultado esperado |
|---|---|---|
| DT-C01 | Comparación A/B | Diferencias descriptivas; sin preferencia |
| DT-C02 | Comparación A/B/C | Matriz descriptiva; sin ranking |
| DT-C03 | Orden inverso A/B | Misma semántica; solo cambia presentación |
| DT-C04 | Valor ausente en A o B | Ausencia/asimetría; sin penalización inventada |
| DT-C05 | Atributos no comparables | Se conserva no comparabilidad |
| DT-C06 | Conflicto multidimensional | Se conservan observaciones; no prioridad |
| DT-C07 | VIABLE vs NOT_VIABLE | Se muestra diferencia de viabilidad; no selección |
| DT-C08 | Evidencia redundante | No aumenta peso por conteo |
| DT-C09 | Información adicional | Amplía representación; no crea preferencia |
| DT-C10 | Múltiples referencias Trace | Se conservan referencias; no se crea Trace nuevo |

## 3. Casos de prohibición

| ID | Intento | Resultado esperado |
|---|---|---|
| DT-P01 | Solicitar score | Rechazado/no producido |
| DT-P02 | Solicitar ranking | Rechazado/no producido |
| DT-P03 | Solicitar ganador | Rechazado/no producido |
| DT-P04 | Solicitar alternativa preferente | Rechazado/no producido |
| DT-P05 | Solicitar utilidad | Rechazado/no producido |
| DT-P06 | Solicitar optimización | Rechazado/no producido |
| DT-P07 | Intentar convertir VIABLE en COMPRAR | No permitido |
| DT-P08 | Intentar resolver conflicto por conteo | No permitido |
| DT-P09 | Intentar penalizar ausencia automáticamente | No permitido |
| DT-P10 | Intentar modificar objeto fuente | No permitido |

## 4. Invariantes

### I1 — Simetría semántica

`compare(A,B)` y `compare(B,A)` deben contener la misma información semántica.

### I2 — No selección

Ningún resultado comparativo puede contener una conclusión de alternativa preferente salvo que una autoridad posterior independiente la produzca.

### I3 — No scoring

No existe transformación automática de observaciones a puntuación.

### I4 — No ranking

La cardinalidad o el orden de las alternativas no crea clasificación.

### I5 — No penalización por ausencia

Un dato ausente permanece ausente/no disponible según la semántica de su fuente.

### I6 — No ponderación por redundancia

Repetir evidencia o señales equivalentes no incrementa automáticamente su influencia.

### I7 — Inmutabilidad de fuentes

La comparación no modifica Assessment, Evidence, Viability, Scenario ni Trace.

### I8 — Trazabilidad conservativa

Las referencias se conservan sin crear una autoridad de Trace paralela.

### I9 — Separación de viabilidad

El estado de Viability Frontier se representa sin alterar su semántica.

### I10 — Separación de decisión

La salida de comparación no constituye una decisión empresarial.

## 5. Casos de regresión de integración

| ID | Integración | Condición |
|---|---|---|
| DT-R01 | Scenario Engine | Una hipótesis vuelve al Scenario Engine; Twin no recalcula escenario |
| DT-R02 | Viability Frontier | Twin consume el resultado; no redefine estados |
| DT-R03 | Assessment | Twin no consolida Assessment |
| DT-R04 | Evidence | Twin no determina suficiencia/admisibilidad |
| DT-R05 | Negotiation | Diferencias pueden alimentar negociación; Twin no decide condición |
| DT-R06 | CRC | Conflictos pueden pasar a CRC; Twin no los resuelve |
| DT-R07 | Decision Versioning | Referencias históricas no se duplican ni sobrescriben |

## 6. Criterio de aprobación

El contrato solo pasa a implementación cuando:

1. todos los casos funcionales son verificables;
2. todos los casos de prohibición son verificables;
3. todos los invariantes se pueden expresar como aserciones o controles;
4. las regresiones de integración no introducen autoridad nueva;
5. la prueba no requiere crear persistencia propia de `Alternative`.

**Estado:** PREPARADA PARA IMPLEMENTACIÓN DE TESTS; NO AUTORIZA TODAVÍA CÓDIGO PRODUCTIVO.