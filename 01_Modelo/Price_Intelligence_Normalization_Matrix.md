# EIOS — MATRIZ DE NORMALIZACIÓN PRICE INTELLIGENCE

**Fase:** 8.5 — Price Intelligence  
**Versión:** 1.0  
**Estado:** CERRADA — METODOLOGÍA ESPECIALIZADA  
**Autoridad:** subordinada a `01_Modelo/Price_Intelligence_Methodological_Matrix.md`

## 1. Propósito

Define las transformaciones autorizadas para llevar una referencia comparable a una base económica común antes de su selección y agregación.

No crea equivalencias económicas no demostradas y no sustituye la evidencia.

## 2. Principio rector

Una transformación solo puede ejecutarse cuando es:

1. económicamente válida;
2. reproducible;
3. suficientemente informada;
4. autorizada;
5. trazable.

La ausencia de cualquiera de estas condiciones impide ejecutar la transformación.

## 3. Estado de normalización

```text
NORMALIZED
PENDING
NOT_NORMALIZABLE
```

`NORMALIZED` significa que todas las transformaciones necesarias han sido ejecutadas y trazadas.

`PENDING` significa que existe una transformación potencialmente aplicable pero falta información, regla o evidencia para ejecutarla.

`NOT_NORMALIZABLE` significa que la referencia no puede llevarse a una base económica común mediante las transformaciones autorizadas del MVP.

## 4. N-01 — Unidad

### Autorizado

Igualdad exacta de la unidad de referencia y de la base de precio requerida por la operación.

### Conversión

Una conversión entre unidades solo está autorizada si existe una relación de conversión explícita, estable y demostrable para el producto/concepto concreto.

La relación debe quedar registrada mediante `NormalizationRecord`.

### No autorizado

- conversión inferida por contexto;
- conversión basada en una aproximación;
- conversión usando una equivalencia no demostrada.

Si no existe relación autorizada → `PENDING` o `NOT_NORMALIZABLE`, según pueda resolverse posteriormente dentro del contrato.

## 5. N-02 — Cantidad / base de precio

El precio debe quedar expresado sobre la misma base económica que la operación actual.

Una diferencia de cantidad puede normalizarse únicamente cuando la unidad y la relación matemática sean demostrables y no exista una condición comercial que altere la proporcionalidad.

No se permite asumir proporcionalidad cuando el precio incorpora componentes fijos, mínimos, escalados o condiciones no conocidas.

## 6. N-03 — Moneda

La moneda objetivo del MVP es EUR, coherente con C0.

Una referencia en EUR no requiere conversión monetaria.

Una referencia en moneda distinta de EUR solo puede normalizarse si existe una regla/fuente de conversión autorizada, con:

- tasa identificable;
- fecha o criterio temporal identificable;
- fuente trazable;
- relación reproducible con la referencia.

No se permite:

- tipo de cambio implícito;
- tipo de cambio actual aplicado retroactivamente sin autorización;
- tasa estimada;
- tasa manual sin fuente trazable.

Si falta cualquiera de los elementos necesarios → `PENDING`.

## 7. N-04 — Impuestos

No se elimina ni incorpora IVA/impuestos mediante una suposición.

Una transformación fiscal solo puede ejecutarse cuando la referencia contiene información suficiente sobre:

- importe fiscal;
- base correspondiente;
- naturaleza del impuesto;
- regla fiscal aplicable.

Si la operación actual y la referencia no pueden llevarse a una misma base fiscal de forma demostrable → `PENDING` o `NOT_NORMALIZABLE`.

## 8. N-05 — Transporte

El transporte solo puede incorporarse o excluirse del precio cuando la evidencia permita identificarlo y exista una regla autorizada que determine la base económica objetivo.

No se estima transporte por distancia, proveedor, histórico o promedio.

## 9. N-06 — Descuentos

Un descuento solo puede normalizarse cuando:

- está documentado;
- su importe o porcentaje es determinable;
- su aplicación al precio es reproducible;
- corresponde a la transacción analizada.

No se reconstruye un descuento desconocido.

## 10. N-07 — Rappels

Los rappels solo pueden normalizarse si existe evidencia suficiente para determinar su efecto económico sobre la transacción o periodo correspondiente y una regla autorizada que establezca cómo aplicarlo.

No se asignan rappels por proveedor habitual ni por comportamiento histórico inferido.

## 11. N-08 — Recargos y condiciones comerciales

Los recargos y otras condiciones comerciales materialmente relevantes solo pueden normalizarse cuando estén documentados y exista una transformación autorizada.

Una condición comercial desconocida que pueda alterar materialmente la comparabilidad impide declarar la referencia normalizada.

## 12. Regla de no inferencia

Nunca se permite convertir un valor desconocido en:

```text
0
media
mediana
estimación
último valor
valor del proveedor habitual
valor de mercado supuesto
```

## 13. Registro obligatorio

Toda transformación ejecutada debe producir:

```text
NormalizationRecord
├── field
├── original_value
├── normalized_value
├── rule_reference
└── trace_reference
```

La trazabilidad debe permitir reconstruir qué se transformó, mediante qué regla y sobre qué evidencia/contexto.

## 14. Precio normalizado

El `normalized_unit_price` solo puede existir cuando todas las transformaciones necesarias para expresarlo sobre la base económica objetivo hayan sido ejecutadas satisfactoriamente.

```text
NORMALIZED
→ normalized_unit_price != null

PENDING / NOT_NORMALIZABLE
→ normalized_unit_price = null
```

## 15. Frontera con comparabilidad

Comparabilidad determina si la referencia puede pertenecer al espacio de referencias candidatas y si las diferencias son resolubles mediante una transformación autorizada.

Normalización ejecuta la transformación.

Por tanto:

```text
COMPARABILITY
    ↓
¿se puede resolver?
    ↓
NORMALIZATION
    ↓
¿se ha resuelto efectivamente?
    ↓
NORMALIZED
```

Una referencia no se considera plenamente normalizada por el mero hecho de ser potencialmente normalizable.

## 16. Frontera con temporalidad

La conversión monetaria debe conservar su fecha/criterio temporal cuando sea aplicable.

La temporalidad de una referencia histórica se evalúa en su propia etapa y no se convierte en ponderación.

## 17. Invariantes

1. No existe normalización implícita.
2. No existe estimación silenciosa.
3. No existe sustitución por cero.
4. No existe conversión monetaria sin fuente/regla autorizada.
5. Toda transformación es trazable.
6. La normalización no decide representatividad.
7. La normalización no decide suficiencia.
8. La normalización no decide selección.
9. `normalized_unit_price` solo existe para una referencia completamente normalizada.
10. Una referencia no normalizada no entra en el conjunto seleccionado.
11. No se modifica C0.
