# EIOS — Price Intelligence / Precio de Referencia (PR)

## Estado

Diseño canónico en evolución controlada. Las decisiones metodológicas aún no autorizadas permanecen explícitamente abiertas y no deben inferirse.

## 1. Propósito

El Precio de Referencia (PR) es un indicador de referencia para el análisis posterior de una compra. No constituye por sí mismo una recomendación, una regla de decisión ni una autorización empresarial.

PR se deriva de referencias históricas de precio que hayan superado las condiciones de calidad/evidencia, comparabilidad, representatividad y selección aplicables.

## 2. Unidad económica de PR — decisión cerrada

**Decisión de diseño: B — Precio de transacción comparable normalizado.**

El PR representa una magnitud derivada de precios de transacciones históricas comparables, después de aplicar únicamente las normalizaciones económicas que estén expresamente autorizadas por la metodología vigente.

Por tanto:

- PR no es TCO.
- PR no es PO.
- PR no es PMR.
- PR no es PPV.
- PR no es una recomendación ni una decisión empresarial.
- El precio observado de una referencia no puede transformarse implícitamente mediante ajustes no autorizados.

## 3. Cadena conceptual

```text
DIP
 ↓
QTG
 ↓
REFERENCIAS HISTÓRICAS
 ↓
COMPARABILIDAD
 ↓
NORMALIZACIÓN AUTORIZADA
 ↓
REPRESENTATIVIDAD
 ↓
SELECCIÓN
 ↓
SUFICIENCIA
 ↓
[PONDERACIÓN, si existe regla autorizada]
 ↓
AGREGACIÓN
 ↓
PR
```

## 4. Comparabilidad y normalización

Unidad y cantidad actúan principalmente en comparabilidad y normalización. No constituyen por sí mismas dimensiones independientes de representatividad ni pesos automáticos.

Moneda, descuentos, rappels, transporte, impuestos y demás condiciones económicas solo pueden modificar la magnitud de referencia mediante reglas de normalización explícitamente autorizadas.

No se permiten normalizaciones implícitas.

## 5. Temporalidad

Para `R-PRE-001`, la condición funcional de referencia **reciente** se interpreta en el MVP mediante `P-PRE-001` (periodo principal de comparación, valor inicial: 3 meses).

`P-PRE-002` mantiene su función de periodo ampliado de comparación/histórico.

`P-DAT-002` mantiene su función de antigüedad máxima de referencia y su relación con `R-HIS-001`.

La antigüedad máxima no constituye por sí misma un peso de recencia.

## 6. Representatividad

La representatividad es criterial y explicable; no requiere un `representativeness_score` en el MVP.

Una referencia previamente comparable puede evaluarse como:

- `REPRESENTATIVA`;
- `NO REPRESENTATIVA`;
- `INDETERMINADA`.

Estos estados son semánticos hasta que los criterios concretos sean formalizados. `INDETERMINADA` no equivale automáticamente a representativa ni a no representativa.

El proveedor, la cantidad, la unidad, el precio, las condiciones comerciales y la evidencia no se convierten automáticamente en criterios de representatividad ni en pesos.

## 7. Selección y suficiencia

La selección determina qué referencias participan en el conjunto final. La suficiencia determina si el conjunto seleccionado proporciona base justificable para construir PR.

Representatividad y suficiencia son propiedades distintas.

`N = 1` no implica automáticamente suficiencia ni rechazo automático. Su tratamiento metodológico permanece abierto.

## 8. Ponderación

La ponderación es una capacidad metodológica opcional. No existe obligación de asignar pesos diferenciados en el MVP.

No se introducen pesos por recencia, volumen, proveedor, calidad u otras variables sin una regla explícitamente autorizada.

La ponderación nunca corrige una deficiencia de comparabilidad o representatividad.

## 9. Outliers

Un valor extremo no equivale automáticamente a un error, una contradicción o una referencia no comparable.

La exclusión o tratamiento de outliers requiere una metodología explícita y trazable. No se permite excluir una referencia únicamente por su magnitud.

## 10. Contradicciones

Una diferencia de precio no constituye por sí misma una contradicción.

Existe contradicción cuando dos o más evidencias pretenden representar el mismo contexto operativo relevante y contienen valores incompatibles que no pueden reconciliarse mediante reglas de normalización autorizadas.

Una contradicción no se resuelve mediante heurísticas implícitas como último valor, menor valor, mayor valor o promedio.

QTG puede determinar la calidad de cada evidencia sin asumir la función de árbitro económico entre valores contradictorios.

## 11. Fronteras arquitectónicas

```text
PR   → referencia de precio comparable normalizado
TCO  → coste total de adquisición
PO   → objetivo de precio
PMR  → límite/referencia superior según metodología correspondiente
PPV  → variación respecto de una referencia/base
```

Las variables de stock, demanda, margen, tesorería, fondo de maniobra y riesgo empresarial pertenecen a sus respectivas capas y no se incorporan automáticamente al cálculo de representatividad de PR.

## 12. Invariantes

1. Dato disponible ≠ criterio metodológico.
2. Evidencia fiable ≠ referencia representativa.
3. Comparabilidad precede a representatividad.
4. Representatividad precede a selección.
5. Selección precede a ponderación.
6. Ponderación no corrige comparabilidad ni representatividad.
7. Representatividad ≠ suficiencia.
8. `N` referencias ≠ `N` referencias suficientes.
9. Outlier ≠ error.
10. Contradicción ≠ outlier.
11. Precio no puede utilizarse retrospectivamente para aumentar la representatividad de una referencia en función del PR resultante.
12. Ninguna normalización económica puede introducirse implícitamente.
13. PR no incorpora por defecto TCO ni otras decisiones empresariales posteriores.

## 13. Metodología todavía abierta

Permanece pendiente de autoridad metodológica explícita:

- criterios concretos de representatividad;
- reglas concretas de normalización;
- suficiencia operativa y tratamiento de `N=1`;
- selección concreta cuando existen múltiples referencias;
- tratamiento de contradicciones;
- tratamiento de outliers;
- ponderación concreta;
- método de agregación final de PR.
