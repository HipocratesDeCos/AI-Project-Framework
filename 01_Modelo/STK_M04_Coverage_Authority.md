# EIOS — STK-M04 · Autoridad metodológica de cobertura

**Versión:** 1.0
**Estado:** APROBADO — STK-M04 CERRADO
**Fecha de decisión:** 11/09/2026
**Autoridad:** decisión humana expresa incorporada al gobierno metodológico STK

## 1. Decisión autorizada

En EIOS, `coverage` representa el **tiempo estimado durante el cual el stock disponible puede cubrir la demanda o consumo esperado de un artículo**.

La relación base autorizada es:

`coverage = stock_available / authorized_average_demand_or_consumption_per_time_unit`

El numerador es el stock disponible válido y normalizado en la fecha de referencia. El denominador es la demanda o consumo medio autorizado para el cálculo, expresado en la misma unidad base del artículo por unidad de tiempo.

## 2. Unidad temporal

La unidad estándar es días de cobertura. Otra unidad temporal solo puede utilizarse cuando una política autorizada del artículo o negocio la parametrice y permita reconstruir su conversión.

Numerador y denominador deben ser dimensionalmente compatibles. El valor de cobertura conserva la unidad temporal del denominador.

## 3. Fuente del denominador

La demanda o consumo debe proceder de datos históricos o previsiones explícitamente autorizadas, normalizadas, trazables y con evidencia suficiente. No se mezclan fuentes sin una regla documentada.

La política vigente debe identificar la magnitud elegida, fuentes, ventana temporal, método de promedio, unidad de tiempo y transformaciones. Esta decisión no valida por sí misma los 12 meses de `STK-006` ni permite sustituir consumo real por demanda prevista.

## 4. Numerador y fecha de referencia

El stock disponible debe ser válido, normalizado y vigente para una fecha explícita `as_of_date`. Solo se utiliza información válida y vigente para esa fecha.

Esta autoridad no determina si stock comprometido, pedidos pendientes o compras en tránsito forman parte del numerador. Su tratamiento permanece reservado a `STK-M06`; no se incorpora ni descuenta ninguna magnitud por inferencia.

`as_of_date` es la fecha empresarial de referencia del cálculo. Su correspondencia con la identidad técnica canónica `evaluation_date` deberá declararse en el contrato posterior sin crear fechas paralelas o ambiguas.

## 5. Cero, ausencia y estados

Si el denominador es cero confirmado y el resto de entradas está evidenciado, el resultado es `UNBOUNDED / NOT_APPLICABLE`. EIOS no representa artificialmente un número infinito.

Si la demanda, consumo o stock necesarios están ausentes o carecen de evidencia suficiente, el resultado es `UNKNOWN / NOT_EVIDENCED`, nunca cero por defecto.

`UNKNOWN / NOT_EVIDENCED ≠ 0`.

Un cero solo es confirmado cuando existe evidencia explícita suficiente conforme a la política aplicable. La ausencia no puede clasificarse como cero confirmado.

## 6. Umbrales y vigencia

`coverage_minimum` y `coverage_maximum` son parámetros empresariales explícitos, documentados, versionados y autorizados. EIOS puede evaluar la cobertura frente a ellos y generar estados, alertas o evidencia, pero no puede crearlos, modificarlos ni reinterpretarlos automáticamente.

Los valores de 30 y 90 días consignados en el catálogo continúan pendientes de validación y no se convierten en política por esta decisión.

Todo cambio en fórmula, fuente, ventana temporal, unidad o umbrales debe quedar versionado, trazable y con fecha efectiva de entrada en vigor. Una nueva versión no altera resultados históricos ni entra en vigor silenciosamente.

## 7. Frontera de autoridad

Una cobertura inferior, superior o comprendida entre umbrales es un resultado analítico evaluable; no constituye por sí misma una decisión automática de compra, reposición o rechazo. La autoridad decisional final permanece en la persona autorizada.

## 8. Límites y continuidad

Esta decisión no autoriza la composición cuantitativa de `stock_available`; una ventana de promedio concreta; los valores 30/90 días; la tolerancia de exceso; el tratamiento de recepciones futuras; ni el motor cuantitativo STK.

`STK-M01…M04` quedan cerrados. `STK-M05…M10` permanecen pendientes y continúan bloqueando el contrato técnico y la implementación cuantitativa STK.
