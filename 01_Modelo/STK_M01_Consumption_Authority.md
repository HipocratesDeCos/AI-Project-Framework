# EIOS — STK-M01 · Autoridad metodológica de consumo

**Versión:** 1.0
**Estado:** APROBADO — STK-M01 CERRADO
**Fecha de decisión:** 10/09/2026
**Autoridad:** decisión humana expresa incorporada al gobierno metodológico STK

## 1. Decisión autorizada

En EIOS, `consumption` representa la **cantidad real consumida de un artículo por la organización o unidad operativa correspondiente**.

Se mide en la **unidad base normalizada del artículo** y se agrega mediante **suma de los consumos registrados durante periodos mensuales**.

Los periodos sin datos se tratan como **`UNKNOWN` y nunca como consumo cero salvo evidencia explícita**.

La política entra en vigor **desde la puesta en producción de EIOS** y se aplica también **de forma retrospectiva a los datos históricos incorporados al sistema**.

## 2. Semántica cerrada

### Magnitud

`consumption` es consumo real registrado. No equivale por defecto a:

- ventas;
- demanda prevista;
- pedidos;
- compras;
- salidas de inventario cuya naturaleza de consumo real no esté demostrada.

Una transformación desde otra magnitud solo podrá utilizarse si una fuente autorizada demuestra que representa consumo real y conserva su trazabilidad.

### Unidad

Todo valor se expresa en la unidad base normalizada del artículo. Si el dato fuente utiliza otra unidad, la conversión debe ser explícita, reproducible y trazable. Sin una conversión demostrada, el valor normalizado permanece `UNKNOWN`.

### Periodo y agregación

La granularidad autorizada es mensual. Para cada combinación de artículo y organización o unidad operativa se suman los consumos reales registrados dentro del periodo mensual correspondiente. Esta decisión no determina que el periodo deba coincidir con el mes natural ni fija por sí sola sus fechas de corte.

Esta decisión no fija todavía el número de meses que consumirá una fórmula posterior de media, cobertura o proyección. El posible horizonte asociado a `STK-006` permanece pendiente de validación y pertenece a los gaps posteriores.

### Ausencia y cero

La ausencia de registros o la falta de evidencia suficiente produce `UNKNOWN`. Solo puede representarse consumo cero cuando exista evidencia explícita de que el consumo real del periodo fue cero.

`UNKNOWN ≠ 0`.

### Vigencia y retrospectividad

La política es vigente desde la puesta en producción de EIOS. Los datos históricos que se incorporen al sistema se evalúan con la misma semántica, sin reescribir el hecho fuente ni su fecha original.

La aplicación retrospectiva debe conservar al menos:

- artículo;
- organización o unidad operativa;
- periodo mensual y sus fechas de corte;
- cantidad fuente;
- unidad fuente;
- unidad base normalizada;
- conversión aplicada, si existe;
- procedencia y fecha del dato;
- estado `KNOWN` o `UNKNOWN`;
- versión metodológica aplicada.

## 3. Límites de autoridad

Esta decisión cierra únicamente `STK-M01`. No autoriza:

- convertir ventas en consumo;
- utilizar demanda prevista como consumo real;
- imputar periodos ausentes;
- asumir conversiones de unidad;
- validar el horizonte de `STK-006`;
- definir medias, cobertura, stock de seguridad, exceso o proyección;
- implementar el motor cuantitativo STK.

## 4. Estado de continuidad

`STK-M01` queda cerrado. `STK-M02…STK-M10` permanecen pendientes y continúan bloqueando el contrato técnico y la implementación cuantitativa STK.
