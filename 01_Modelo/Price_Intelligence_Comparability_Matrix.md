# EIOS — MATRIZ DE COMPARABILIDAD PRICE INTELLIGENCE

**Fase:** 8.5 — Price Intelligence  
**Versión:** 1.0  
**Estado:** CERRADA — METODOLOGÍA ESPECIALIZADA  
**Autoridad:** subordinada a `01_Modelo/Price_Intelligence_Methodological_Matrix.md`

## 1. Propósito

Define los criterios observables para determinar si una referencia histórica puede considerarse económicamente comparable con la operación de compra evaluada.

No define representatividad, suficiencia ni agregación.

## 2. Principio de identidad económica

La identidad técnica de una referencia es `source_transaction_id`.

La comparabilidad económica no se determina únicamente por igualdad textual de identificadores. Debe demostrarse que la referencia corresponde al mismo concepto económico evaluado o a un concepto cuya equivalencia esté explícitamente autorizada.

## 3. Gate de comparabilidad

Una referencia solo puede alcanzar `COMPARABLE` cuando todos los gates aplicables estén resueltos positivamente:

```text
C-01 Identidad económica
C-02 Unidad y base de medida
C-03 Cantidad y alcance
C-04 Moneda
C-05 Condiciones económicas
C-06 Evidencia
```

Una discrepancia que pueda resolverse mediante una transformación autorizada pasa a la etapa de normalización; no se declara `COMPARABLE` anticipadamente por asumir dicha transformación.

## 4. C-01 — Identidad económica

Debe existir correspondencia demostrable entre el `article_id` de la operación actual y la `article_identity` de la referencia, o una regla documental autorizada que establezca equivalencia.

Estados:

- **MATCH:** correspondencia demostrada.
- **MISMATCH:** conceptos económicamente distintos.
- **UNRESOLVED:** información insuficiente para determinar equivalencia.

Solo `MATCH` permite continuar como candidata comparable.

## 5. C-02 — Unidad y base de medida

La unidad de la referencia debe ser:

- igual a la unidad de la operación; o
- transformable mediante una regla de conversión autorizada y trazable.

Una conversión no demostrable produce `PENDING`, no una equivalencia inventada.

## 6. C-03 — Cantidad y alcance

La cantidad y el alcance comercial deben ser interpretables respecto de la operación actual.

Una diferencia de cantidad no implica automáticamente no comparabilidad si existe una normalización autorizada que permita obtener un precio comparable sobre la misma base.

Si no puede determinarse la base económica, el estado es `PENDING`.

## 7. C-04 — Moneda

La moneda debe ser EUR para ser directamente comparable con C0.

Una moneda distinta de EUR solo puede alcanzar comparabilidad mediante una regla de conversión autorizada, reproducible, trazable y suficientemente informada.

En ausencia de dicha regla o de los datos necesarios, el resultado es `PENDING`.

No se utiliza un tipo de cambio implícito ni una cotización inventada.

## 8. C-05 — Condiciones económicas

Deben poder identificarse las condiciones que afectan materialmente al precio, cuando sean relevantes:

- descuentos;
- rappels;
- impuestos;
- transporte;
- recargos;
- condiciones comerciales específicas.

Si una diferencia es normalizable mediante una regla autorizada, permanece en el flujo para normalización.

Si la diferencia impide determinar una base económica común y no existe regla autorizada, la referencia es `PENDING`.

## 9. C-06 — Evidencia

La referencia debe contener referencias de evidencia suficientes para poder demostrar su identidad y los hechos necesarios para las etapas posteriores.

`evidence_refs` demuestra existencia de referencias documentales, pero no equivale por sí mismo a evidencia validada ni a suficiencia.

La ausencia de evidencia necesaria produce `PENDING` cuando no permite concluir; no se transforma automáticamente en `NO_COMPARABLE`.

## 10. Estados finales

### COMPARABLE

Todos los gates necesarios están resueltos y no existe una diferencia económica pendiente que requiera una decisión no autorizada.

### NO_COMPARABLE

Existe evidencia suficiente de que la referencia corresponde a un concepto o condición económicamente incompatible con la operación y que no puede resolverse mediante una normalización autorizada.

### PENDING

La comparabilidad no puede determinarse todavía por falta de información o porque requiere una transformación cuya aplicabilidad todavía debe resolverse en la etapa de normalización.

## 11. Orden de evaluación

```text
IDENTIDAD
→ UNIDAD / BASE
→ CANTIDAD / ALCANCE
→ MONEDA
→ CONDICIONES ECONÓMICAS
→ EVIDENCIA
→ ESTADO DE COMPARABILIDAD
```

La implementación debe conservar el motivo de cualquier `NO_COMPARABLE` o `PENDING`.

## 12. Prohibiciones

No se determina comparabilidad mediante:

- precio cercano;
- precio mínimo o máximo;
- frecuencia;
- proveedor habitual;
- último precio;
- score;
- conveniencia de obtener un PR;
- representatividad estimada;
- resultado de la mediana.

## 13. Frontera con normalización

Comparabilidad responde:

> **¿Existe una base económica común demostrable o resoluble mediante una transformación autorizada?**

Normalización responde:

> **¿Cómo se transforma materialmente esa referencia a la base común autorizada?**

Por tanto, la comparabilidad no ejecuta conversiones ni altera precios.

## 14. Frontera con representatividad

Una referencia puede ser comparable y posteriormente ser:

- `REPRESENTATIVE`;
- `NON_REPRESENTATIVE`;
- `INDETERMINATE`.

`COMPARABLE` no implica `REPRESENTATIVE`.

## 15. Invariantes

1. `NO_COMPARABLE` nunca entra en selección.
2. `PENDING` nunca entra en selección como comparable.
3. `COMPARABLE` no implica representatividad.
4. La comparabilidad no depende del PR calculado.
5. La comparabilidad no depende de la mediana.
6. La ausencia de evidencia necesaria no se sustituye por un valor por defecto.
7. Una transformación pendiente no se trata como transformación ejecutada.
8. No se modifica C0.
