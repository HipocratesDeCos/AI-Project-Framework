# EIOS — MATRIZ DE BASE ECONÓMICA OBJETIVO — PRICE INTELLIGENCE

**Fase:** 8.5 — Price Intelligence  
**Versión:** 1.0  
**Estado:** CERRADA — METODOLOGÍA ESPECIALIZADA  
**Autoridad:** subordinada a `01_Modelo/Price_Intelligence_Methodological_Matrix.md`

## 1. Propósito

Define la base económica común sobre la que debe expresarse una referencia antes de poder formar parte del conjunto seleccionado para el cálculo del Precio de Referencia (PR).

No modifica C0 ni crea una segunda operación de compra.

## 2. Base objetivo MVP

Una referencia normalizada debe expresar el precio en una base común determinada por:

```text
PRODUCTO / IDENTIDAD ECONÓMICA
+ UNIDAD OBJETIVO
+ BASE DE CANTIDAD
+ MONEDA OBJETIVO
+ BASE FISCAL
+ BASE DE TRANSPORTE
+ BASE DE DESCUENTOS
+ BASE DE RECARGOS
+ CONDICIONES COMERCIALES RELEVANTES
```

La base solo puede considerarse definida cuando cada dimensión aplicable tenga una fuente o regla autorizada.

## 3. Dimensiones

### EB-01 — Unidad

Debe existir una `target_unit` explícita. La igualdad directa no requiere conversión. Una conversión requiere relación de conversión demostrable y trazable.

### EB-02 — Cantidad / base de precio

Debe quedar determinada la base sobre la que se expresa el precio unitario. La proporcionalidad solo puede utilizarse cuando sea demostrable y no existan componentes fijos, mínimos, escalados o condiciones que la alteren.

### EB-03 — Moneda

La moneda objetivo MVP es EUR. Una moneda distinta requiere una fuente/regla de conversión autorizada, tasa identificable, criterio temporal y trazabilidad.

### EB-04 — Fiscalidad

Debe conocerse si la base objetivo es con impuestos, sin impuestos o la base documentada. No se elimina ni incorpora fiscalidad por defecto.

### EB-05 — Transporte

Debe conocerse si el transporte forma parte de la base económica objetivo. No se estima su importe.

### EB-06 — Descuentos

Debe determinarse si el precio objetivo es bruto, neto o documentado. Solo se aplican descuentos demostrados y atribuibles a la operación/referencia.

### EB-07 — Recargos

Debe determinarse si los recargos forman parte de la base objetivo. Solo se incorporan o excluyen mediante regla autorizada y evidencia suficiente.

### EB-08 — Condiciones comerciales

Las condiciones materialmente relevantes deben estar identificadas. Si alteran el precio y no pueden normalizarse de forma demostrable, la referencia no puede declararse `NORMALIZED`.

## 4. Estado de cada dimensión

Cada dimensión aplicable debe poder clasificarse como:

```text
RESOLVED
NOT_APPLICABLE
PENDING
NOT_RESOLVABLE
```

`NORMALIZED` exige que todas las dimensiones aplicables estén en `RESOLVED` o `NOT_APPLICABLE`.

## 5. Regla de cierre

```text
TODAS LAS DIMENSIONES APLICABLES
        ↓
RESOLVED / NOT_APPLICABLE
        ↓
NORMALIZED
        ↓
normalized_unit_price válido
```

Si al menos una dimensión necesaria está `PENDING` o `NOT_RESOLVABLE`:

```text
normalized_unit_price = null
```

## 6. Regla de no inferencia

La base económica nunca se completa mediante:

- valores por defecto no autorizados;
- estimaciones;
- promedios;
- medianas;
- último precio;
- proveedor habitual;
- condiciones comerciales supuestas;
- tipo de cambio implícito.

## 7. Relación con C0

C0 continúa siendo la autoridad sobre `PurchaseOperation`.

Esta matriz no añade campos a `PurchaseOperation`. Define qué información adicional necesita C1 para demostrar que una referencia histórica puede expresarse sobre una base económica común.

Si esa información no está disponible por una fuente autorizada, C1 debe conservar el estado pendiente o no resoluble.

## 8. Relación con las matrices anteriores

```text
Methodological Matrix
        ↓
Comparability Matrix
        ↓
Economic Basis Matrix
        ↓
Normalization Matrix
        ↓
Selection
        ↓
Aggregation
```

Comparabilidad determina si existe una base común demostrable o potencialmente resoluble.

Esta matriz define cuál es esa base común.

Normalización ejecuta las transformaciones necesarias para alcanzarla.

## 9. Invariantes

1. No se modifica C0.
2. No se inventa una base económica.
3. No se declara `NORMALIZED` con dimensiones pendientes.
4. No se convierte moneda sin regla/fuente autorizada.
5. No se presume proporcionalidad de cantidad cuando pueda existir no proporcionalidad.
6. No se presume tratamiento fiscal.
7. No se presume tratamiento de transporte.
8. No se presume efecto de descuentos o recargos.
9. Cada transformación ejecutada debe ser trazable.
10. La base económica no determina representatividad.
11. La base económica no determina suficiencia.
12. La base económica no determina el PR final.
