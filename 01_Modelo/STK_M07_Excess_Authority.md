# EIOS — STK-M07 · Autoridad metodológica de exceso de stock

**Versión:** 1.0
**Estado:** APROBADO — STK-M07 CERRADO
**Fecha de decisión:** 11/09/2026
**Autoridad:** decisión humana expresa incorporada al gobierno metodológico STK

## 1. Decisión autorizada

STK-M07 representa la cantidad de stock que supera el nivel máximo autorizado para un artículo una vez aplicada la tolerancia empresarial de exceso correspondiente.

La evaluación utiliza la unidad base normalizada del artículo y el stock válido para el momento evaluado.

## 2. Relaciones autorizadas

Una vez expresados máximo y tolerancia en la misma unidad base:

`excess_threshold = stock_maximum + excess_tolerance`

`excess_quantity = max(0, stock_reference - excess_threshold)`

La tolerancia es una magnitud adicional sobre el máximo, no una sustitución del máximo ni un cambio implícito de severidad.

## 3. Estados de evaluación

- Si `stock_reference ≤ stock_maximum`, el estado es `NO_EXCESS` y `excess_quantity = 0`.
- Si `stock_maximum < stock_reference ≤ excess_threshold`, el estado es `WITHIN_TOLERANCE` y `excess_quantity = 0`.
- Si `stock_reference > excess_threshold`, el estado es `EXCESS` y solo se cuantifica la cantidad situada por encima del umbral.

Los ceros anteriores son resultados calculados con entradas conocidas y evidenciadas; no sustituyen datos ausentes.

## 4. Referencia actual y futura

Para una evaluación actual, `stock_reference` es el stock válido y evidenciado en el momento evaluado. Para una evaluación futura consume la proyección autorizada de STK-M05.

Cuando consume una proyección M05, no vuelve a sumar pedidos pendientes o tránsito de STK-M06. La identidad del escenario, `as_of_date`, instante proyectado, fuentes y versión metodológica deben quedar trazables.

Si una cantidad propuesta forma parte del escenario evaluado, su incorporación debe estar explícita y trazada en la proyección; STK-M07 no la añade de nuevo ni presume su aprobación.

## 5. Tolerancia

`excess_tolerance` es un parámetro empresarial explícito, documentado, versionado y autorizado.

Si se expresa como cantidad, debe estar en la unidad base del artículo. Si se expresa porcentualmente, se convierte previamente respecto a `stock_maximum`:

`excess_tolerance_quantity = stock_maximum * authorized_tolerance_rate`

La tasa debe estar explícitamente identificada como porcentaje o proporción y normalizada antes del cálculo. EIOS no infiere su significado a partir del nombre o valor del parámetro.

El 10 % de `STK-005` permanece pendiente de validación y no se convierte en política por esta decisión.

## 6. Máximo gobernado por cobertura

Cuando el máximo se gobierna mediante `coverage_maximum`, su conversión a cantidad utiliza la política autorizada de cobertura STK-M04 y la demanda aplicable a la fecha de referencia.

La fuente de demanda, unidad temporal, fecha, versión y evidencia deben conservarse. Los 90 días de `STK-004` permanecen pendientes de validación.

## 7. Ausencia y evidencia

Si faltan `stock_maximum`, `coverage_maximum` cuando sea necesario, `excess_tolerance`, `stock_reference` o evidencia suficiente, el resultado es `UNKNOWN / NOT_EVIDENCED`, nunca `NO_EXCESS` por defecto.

`UNKNOWN / NOT_EVIDENCED ≠ NO_EXCESS`.

Tampoco se calcula `excess_quantity` con entradas dimensionalmente incompatibles o no normalizadas.

## 8. Frontera de autoridad y continuidad

STK-M07 identifica y cuantifica exceso. No autoriza automáticamente cancelaciones de compra, devoluciones, liquidaciones, transferencias o reducciones de inventario.

Sus resultados alimentan reglas posteriores de evaluación y la decisión humana. La excepción por pedido confirmado permanece en `STK-M08`.

`STK-M01…M07` quedan cerrados. `STK-M08…M10` permanecen pendientes y continúan bloqueando el contrato técnico y la implementación cuantitativa STK.
