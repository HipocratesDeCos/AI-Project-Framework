# EIOS — MATRIZ DE AGREGACIÓN PRICE INTELLIGENCE

**Fase:** 8.5 — Price Intelligence  
**Versión:** 1.0  
**Estado:** CERRADA — METODOLOGÍA ESPECIALIZADA  
**Autoridad:** subordinada a `Price_Intelligence_Methodological_Matrix.md`

## 1. Propósito

Definir la transformación final del conjunto seleccionado y suficiente en un único Precio de Referencia (PR).

## 2. Método MVP

El método autorizado es:

```text
MEDIAN_UNWEIGHTED
```

El PR se obtiene exclusivamente a partir de `normalized_unit_price` de las referencias seleccionadas y admitidas por suficiencia.

## 3. Regla matemática

Sea `P = {p1, p2, ..., pn}` el conjunto de precios normalizados seleccionados.

Ordenar ascendentemente:

```text
p(1) ≤ p(2) ≤ ... ≤ p(n)
```

Si `n` es impar:

```text
PR = p((n+1)/2)
```

Si `n` es par:

```text
PR = (p(n/2) + p(n/2+1)) / 2
```

## 4. Requisitos

La agregación requiere:

- referencias seleccionadas;
- `NORMALIZED`;
- temporalidad `ELIGIBLE`;
- `REPRESENTATIVE`;
- suficiencia compatible con emisión de PR;
- moneda homogénea.

## 5. N = 0

No se agrega ningún valor.

Resultado:

```text
PR = null
PR_STATUS = PR_NOT_JUSTIFIABLE
```

## 6. N = 1

La mediana matemática existe, pero el contrato metodológico no permite elevar por ello el resultado a `SUFFICIENT`.

Si suficiencia es `LIMITED`, el resultado puede ser `PR_LIMITED` únicamente si la matriz de suficiencia lo autoriza.

No se convierte N=1 en suficiente por aplicar la mediana.

## 7. Ponderación

No existe ponderación en el MVP.

Queda prohibido ponderar por:

- cantidad;
- volumen;
- proveedor;
- frecuencia;
- recencia;
- score;
- proximidad al objetivo.

## 8. Outliers

La agregación no elimina outliers.

La decisión de exclusión pertenece a representatividad/selección y debe haber ocurrido antes de la agregación.

## 9. Redondeo y precisión

La agregación se realiza sobre valores decimales exactos disponibles en C1.

No se aplica redondeo intermedio.

El redondeo de presentación, si procede, debe ser posterior al cálculo y estar definido por una regla de salida autorizada.

## 10. Moneda

Todos los valores agregados deben estar expresados en la misma moneda objetivo.

La agregación no realiza conversiones de moneda.

## 11. Trazabilidad

El resultado debe conservar:

- método `MEDIAN_UNWEIGHTED`;
- conjunto de referencias utilizado;
- moneda;
- snapshot de datos;
- versión metodológica;
- trazas de las reglas que permitieron la selección.

## 12. Prohibiciones

La agregación no puede:

- seleccionar referencias;
- modificar representatividad;
- modificar suficiencia;
- corregir normalización;
- corregir contradicciones;
- eliminar observaciones para obtener un PR deseado;
- utilizar C0 como almacén de resultado.

## 13. Invariante final

```text
PR = f(selected_normalized_prices)
```

y no:

```text
PR → selección
PR → representatividad
PR → suficiencia
```
