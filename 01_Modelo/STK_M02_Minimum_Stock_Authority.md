# EIOS — STK-M02 · Autoridad metodológica de stock mínimo

**Versión:** 1.0
**Estado:** APROBADO — STK-M02 CERRADO
**Fecha de decisión:** 10/09/2026
**Autoridad:** decisión humana expresa incorporada al gobierno metodológico STK

## 1. Decisión autorizada

En EIOS, `stock_minimum` representa la **cantidad mínima de existencias que debe mantenerse disponible para proteger la continuidad operativa de un artículo antes de que la reposición resulte necesaria**.

Se mide en la **unidad base normalizada del artículo**.

Se establece mediante una **política o cálculo explícito, trazable y autorizado basado en la demanda esperada, el plazo de reposición (`lead_time`), su variabilidad y el nivel de protección requerido**.

## 2. Relaciones cerradas

### Relación con `safety_stock`

`Safety_stock` constituye la reserva destinada a absorber incertidumbre y puede formar parte de `stock_minimum`, pero ambos conceptos no son equivalentes.

La inclusión, exclusión o forma de composición debe quedar declarada por la política vigente. No se presupone por nomenclatura.

### Relación con cobertura

`Stock_minimum`, combinado con la demanda esperada, permite expresar cuántos días o periodos de consumo quedan protegidos antes de alcanzar el umbral definido.

Esta relación no fija todavía la fórmula de cobertura, su unidad temporal ni el tratamiento del denominador nulo o desconocido; esos elementos permanecen en `STK-M04`.

### Relación con demanda

La demanda esperada es una de las variables que justifican y dimensionan `stock_minimum`.

Una variación de demanda no modifica automáticamente el valor vigente. El cambio solo puede producirse cuando la política correspondiente recalcule o autorice un nuevo valor, conservando versión, evidencia y vigencia.

## 3. Evidencia y estados de ausencia

Cada valor vigente de `stock_minimum` debe permitir reconstruir como mínimo:

- artículo y organización o unidad operativa;
- cantidad y unidad base normalizada;
- política o cálculo aplicado y su versión;
- demanda esperada utilizada;
- `lead_time` utilizado;
- evidencia de variabilidad considerada;
- nivel de protección requerido;
- fecha de cálculo o autorización;
- periodo de vigencia;
- procedencia de los datos y parámetros.

Si falta el valor o la evidencia que justifica su procedencia, el estado es `UNKNOWN / NOT_EVIDENCED`. No se sustituye por cero ni por una estimación implícita.

`UNKNOWN / NOT_EVIDENCED ≠ 0`.

## 4. Frontera de autoridad

Que el stock disponible alcance o atraviese `stock_minimum` indica una condición evaluable conforme a reglas posteriores; no constituye por sí mismo una orden de reposición.

EIOS no puede utilizar un valor ausente o no evidenciado como fundamento de una decisión automática de reposición. La decisión empresarial final permanece en la persona autorizada.

## 5. Límites

Esta decisión cierra la definición y relaciones de `STK-M02`, pero no autoriza:

- una fórmula concreta de `stock_minimum`;
- un valor inicial o por defecto para `STK-001`;
- equivalencia entre `stock_minimum` y `safety_stock`;
- una fórmula de cobertura;
- actualización silenciosa ante cambios de demanda;
- estimación implícita de entradas ausentes;
- reposición o decisión empresarial automática;
- implementación del motor cuantitativo STK.

## 6. Estado de continuidad

`STK-M01…M02` quedan cerrados. `STK-M03…M10` permanecen pendientes y continúan bloqueando el contrato técnico y la implementación cuantitativa STK.
