# EIOS — STK-M03 · Autoridad metodológica de stock de seguridad

**Versión:** 1.0
**Estado:** APROBADO — STK-M03 CERRADO
**Fecha de decisión:** 10/09/2026
**Autoridad:** decisión humana expresa incorporada al gobierno metodológico STK

## 1. Decisión autorizada

En EIOS, `safety_stock` representa la **cantidad adicional de existencias mantenida como reserva para proteger la continuidad operativa frente a variaciones no previstas** y se mide en la **unidad base normalizada del artículo**.

Se establece mediante una **política o método explícito, documentado, trazable y autorizado**, usando variables como variabilidad de demanda, variabilidad del `lead_time`, nivel de servicio o protección requerido y calidad de evidencia disponible.

## 2. Incertidumbre y evidencia

Absorbe incertidumbre de la demanda y/o del plazo y fiabilidad de reposición. Su base son datos históricos y previsiones válidas, normalizadas y suficientemente evidenciadas sobre consumo o demanda y comportamiento de suministro.

La política debe declarar variables, horizonte, estadístico, nivel de servicio y fórmula. Nada se infiere por nombre, disponibilidad técnica o valor histórico del catálogo.

## 3. Relación con `stock_minimum`

Puede constituir una parte del umbral mínimo de protección, pero `safety_stock` y `stock_minimum` son conceptos distintos y no deben asumirse equivalentes. Su composición debe declararse en la política vigente, en coherencia con `STK-M02`.

## 4. Versión y vigencia

Cada valor debe hacer reconstruibles artículo y unidad operativa; cantidad y unidad base; política y versión; variables, fuentes, periodos y transformaciones; variabilidad; nivel de protección; calidad de evidencia; fechas de cálculo y aprobación; y vigencia.

Se recalcula cuando lo establezca una política autorizada o cambien materialmente sus variables. Un cambio no activa silenciosamente un valor: debe quedar versionado, trazable y solo entra en vigor desde su aprobación o materialización correspondiente.

## 5. Ausencia y autoridad

Si falta el valor o su evidencia, el estado es `UNKNOWN / NOT_EVIDENCED`. Nunca se sustituye por cero ni por un valor inferido automáticamente.

`UNKNOWN / NOT_EVIDENCED ≠ 0`.

Puede informar una evaluación, pero no constituye una decisión automática de reposición. La autoridad decisional final permanece en la persona autorizada.

## 6. Límites

No se autoriza una fórmula concreta; que `STK-002` sea el 15 % del consumo; una base única; valores por defecto; equivalencia con `stock_minimum`; activación silenciosa; sustitución de ausencia; reposición automática; ni implementación cuantitativa STK.

## 7. Continuidad

`STK-M01…M03` quedan cerrados. `STK-M04…M10` permanecen pendientes y continúan bloqueando el contrato técnico y la implementación cuantitativa STK.
