# EIOS — MATRIZ DE SELECCIÓN PRICE INTELLIGENCE

**Fase:** 8.5 — Price Intelligence  
**Versión:** 1.0  
**Estado:** CERRADA — METODOLOGÍA ESPECIALIZADA  
**Autoridad:** subordinada a `Price_Intelligence_Methodological_Matrix.md`

## 1. Propósito

Definir la selección final de referencias que pueden formar parte del conjunto utilizado para calcular el Precio de Referencia (PR).

## 2. Regla de entrada

Una referencia solo puede ser seleccionada cuando cumple simultáneamente:

```text
COMPARABLE
AND
NORMALIZED
AND
TEMPORAL = ELIGIBLE
AND
REPRESENTATIVENESS = REPRESENTATIVE
```

## 3. Estados excluyentes

```text
NO_COMPARABLE       → excluir
PENDING             → excluir
NOT_NORMALIZABLE    → excluir
INELIGIBLE          → excluir
INDETERMINATE       → excluir
NON_REPRESENTATIVE  → excluir
REPRESENTATIVE      → candidato seleccionable
```

Excluir no significa que el dato sea erróneo. Significa que no satisface los criterios cerrados de entrada al conjunto PR.

## 4. Determinismo

La selección debe depender únicamente de los estados y criterios metodológicos ya determinados.

No puede depender de:

- valor del PR;
- mediana;
- distancia respecto de la mediana;
- necesidad de alcanzar un N deseado;
- proveedor habitual;
- frecuencia;
- último precio;
- mínimo o máximo precio;
- score.

## 5. Outliers

Un outlier no se excluye por ser estadísticamente extremo.

Solo queda excluido si la evaluación previa de representatividad determina `NON_REPRESENTATIVE` conforme a evidencia económica suficiente.

## 6. Contradicciones

Una contradicción material no resuelta impide `REPRESENTATIVE` y, por tanto, selección.

Una simple diferencia entre precios no constituye contradicción.

## 7. Duplicados

La selección opera sobre referencias ya deduplicadas por `source_transaction_id`.

Una repetición documental de una misma transacción no incrementa N.

## 8. N resultante

```text
N_selected = número de referencias seleccionadas
```

No se rellena artificialmente N mediante referencias `PENDING`, `INDETERMINATE` o `NON_REPRESENTATIVE`.

## 9. Casos límite

### N = 0

No existe conjunto seleccionable y no puede justificarse PR.

### N = 1

Existe una referencia seleccionada, pero no implica automáticamente suficiencia.

### N > 1

Puede existir base para evaluar suficiencia, pero N por sí mismo tampoco garantiza un PR suficiente.

## 10. Trazabilidad

El conjunto seleccionado debe conservar los `source_transaction_id` de las referencias incluidas y las trazas de las decisiones metodológicas que permitieron su inclusión.

## 11. Invariantes

1. La selección no cambia estados previos.
2. La selección no modifica precios.
3. La selección no modifica C0.
4. La selección no crea referencias.
5. La selección no duplica referencias.
6. La selección no utiliza el PR como criterio de entrada.
7. La selección no utiliza score.
8. La selección no transforma un estado indeterminado en positivo.
