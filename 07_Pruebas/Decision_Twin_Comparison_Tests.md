# EIOS — Decision Twin Comparison Tests

## 1. Propósito

Define la especificación de pruebas de comportamiento para `Decision Twin Comparison` derivada exclusivamente de `Decision_Twin_Comparison_Contract.md`.

No introduce reglas de negocio nuevas.

## 2. Fixture conceptual

Las pruebas utilizan alternativas representadas con atributos ya autorizados por sus fuentes. La fixture no atribuye pesos ni preferencias.

## 3. Pruebas funcionales

### DT-C01 — A/B

Entrada: dos alternativas con valores comparables.

Debe devolver valores observados y diferencias. No debe devolver preferencia.

### DT-C02 — A/B/C

Entrada: tres alternativas.

Debe ampliar la matriz comparativa sin generar ranking.

### DT-C03 — orden inverso

`compare(A,B)` frente a `compare(B,A)`.

Debe conservar contenido semántico equivalente.

### DT-C04 — dato faltante

Una alternativa carece de un valor.

Debe conservar la ausencia/no disponibilidad. No debe introducir cero, media, peor caso, mejor caso ni penalización.

### DT-C05 — no comparabilidad

Dos atributos no son directamente comparables.

Debe declararse la no comparabilidad sin fabricar equivalencia.

### DT-C06 — conflicto multidimensional

A es favorable en una dimensión y B en otra.

Debe conservar ambas observaciones sin resolver prioridad.

### DT-C07 — viabilidad

A = VIABLE; B = NOT_VIABLE.

Debe mostrar la diferencia de viabilidad sin producir selección empresarial.

### DT-C08 — redundancia

Se añaden referencias/evidencias redundantes para la misma observación.

El resultado semántico de la comparación no adquiere peso por conteo.

### DT-C09 — información adicional

Se incorpora un atributo nuevo correctamente autorizado.

La representación se amplía sin crear preferencia sobre las alternativas existentes.

### DT-C10 — trazabilidad múltiple

Una alternativa tiene varias referencias Trace.

Todas las referencias pertinentes se conservan sin crear un nuevo mecanismo Trace.

## 4. Pruebas de prohibición

### DT-P01 — score

Cualquier petición de convertir observaciones en puntuación debe producir ausencia de score.

### DT-P02 — ranking

La salida no puede ordenar alternativas por preferencia decisional.

### DT-P03 — ganador

La salida no puede declarar ganador.

### DT-P04 — alternativa preferente

La salida no puede declarar una alternativa preferente.

### DT-P05 — utilidad

La salida no puede calcular función de utilidad.

### DT-P06 — optimización

La comparación no puede ejecutar optimización.

### DT-P07 — decisión

La comparación no puede producir COMPRAR, NEGOCIAR, COMPRAR CONDICIONADO o NO COMPRAR.

### DT-P08 — conflicto por conteo

No puede resolver conflicto contando señales favorables.

### DT-P09 — ausencia como penalización

No puede convertir ausencia de información en una penalización automática.

### DT-P10 — mutación

La comparación no puede modificar Assessment, Evidence, Viability, Scenario, Trace o Decision State fuente.

## 5. Invariantes ejecutables

```text
I1: compare(A,B) ≡ compare(B,A) semánticamente
I2: output no contiene preferencia automática
I3: output no contiene score
I4: output no contiene ranking
I5: missing permanece missing/unavailable
I6: redundancia no crea peso decisional
I7: objetos fuente permanecen inmutados
I8: Trace se referencia, no se redefine
I9: estados de Viability conservan su semántica
I10: output no constituye decisión empresarial
```

## 6. Regresiones de integración

- Scenario Engine: una hipótesis debe regresar al motor de escenarios.
- Viability Frontier: Decision Twin consume el resultado sin redefinirlo.
- Assessment: permanece individual.
- Evidence: Decision Twin no determina suficiencia.
- Negotiation: recibe diferencias; no recibe una decisión ya tomada.
- CRC: recibe conflictos; Decision Twin no los resuelve.
- Decision Versioning: referencias históricas permanecen bajo su autoridad.

## 7. Criterio de paso

Todos los casos funcionales, prohibiciones e invariantes deberán poder convertirse en aserciones automatizadas antes de aceptar implementación productiva.

Una prueba que detecte una selección implícita deberá considerarse FALLIDA conforme al `Plan_Pruebas_MVP.md` y no podrá resolverse cambiando el test para acomodar el comportamiento.

**Estado:** ESPECIFICACIÓN IMPLEMENTADA Y MATERIALIZADA — validación CI completada en el HEAD `10e87954f744cecb6b6cb81dc49d47335d2b732c`.
