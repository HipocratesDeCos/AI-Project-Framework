# EIOS — Matriz Campo → Componente UI v0.2

**Estado:** DISEÑO COMPLETADO — PENDIENTE DE AUDITORÍA
**Autoridad:** `UI_Field_Registry_v0.1.md`
**Baseline funcional:** `9f5db07d55b9665286f6a8ef821ad7046b232a98`
**Fecha:** 2026-09-06

## 1. Regla de cobertura

Cada `UI-*` del Registro Maestro debe tener exactamente una definición primaria de componente UI. El componente no modifica la semántica ni el estado canónico del campo.

## 2. Convenciones de componente

- `TEXT_READONLY`: texto/valor no editable.
- `TEXT_INPUT`: entrada de texto.
- `SELECT_INPUT`: selección controlada.
- `NUMBER_INPUT`: entrada numérica.
- `DATE_INPUT`: entrada de fecha.
- `DATE_READONLY`: fecha no editable.
- `NUMBER_READONLY`: valor numérico mostrado.
- `METRIC_CARD`: métrica calculada o contextual.
- `DECISION_BADGE`: resultado de evaluación.
- `TRACE_PANEL`: trazabilidad.
- `CONFIG_CONTROL`: configuración.
- `DATA_TABLE`: colección histórica.
- `STATUS_MESSAGE`: insuficiencia/error/estado.

## 3. Reglas por estado

| Estado | Componentes permitidos |
|---|---|
| INPUT | TEXT_INPUT / SELECT_INPUT / NUMBER_INPUT / DATE_INPUT |
| READONLY | TEXT_READONLY / DATE_READONLY / NUMBER_READONLY / METRIC_CARD / DATA_TABLE |
| CALCULATED | NUMBER_READONLY / METRIC_CARD |
| DECISION | DECISION_BADGE |
| TRACE | TRACE_PANEL / TEXT_READONLY / DATE_READONLY |
| CONFIG | CONFIG_CONTROL |
| INPUT/READONLY | Componente de entrada con modo READONLY determinado por origen autorizado |
| INPUT/CONFIG | CONFIG_CONTROL con edición controlada |
| READONLY/CALCULATED | Componente de lectura cuyo valor puede proceder de cálculo autorizado |

## 4. Matriz individual

### Propuesta

| Field_ID | Campo | Estado | Componente | Editable |
|---|---|---|---|---|
| UI-PROP-001 | ID propuesta | TRACE | TEXT_READONLY | No |
| UI-PROP-002 | Artículo | INPUT | SELECT_INPUT | Sí |
| UI-PROP-003 | Descripción artículo | READONLY | TEXT_READONLY | No |
| UI-PROP-004 | Proveedor | INPUT | SELECT_INPUT | Sí |
| UI-PROP-005 | Cantidad propuesta | INPUT | NUMBER_INPUT | Sí |
| UI-PROP-006 | Precio unitario | INPUT | NUMBER_INPUT | Sí |
| UI-PROP-007 | Importe total | CALCULATED | NUMBER_READONLY | No |
| UI-PROP-008 | Fecha propuesta | INPUT | DATE_INPUT | Sí |
| UI-PROP-009 | Fecha prevista de entrega | INPUT | DATE_INPUT | Sí |
| UI-PROP-010 | Plazo de entrega | INPUT/READONLY | NUMBER_INPUT / NUMBER_READONLY | Según origen |
| UI-PROP-011 | Plazo de pago | INPUT | NUMBER_INPUT | Sí |
| UI-PROP-012 | Condiciones de pago | INPUT | SELECT_INPUT | Sí |
| UI-PROP-013 | Descuento | INPUT | NUMBER_INPUT | Sí |
| UI-PROP-014 | Rappel | INPUT | NUMBER_INPUT | Sí |
| UI-PROP-015 | Otras condiciones | INPUT | TEXT_INPUT | Sí |

### Contexto operativo

| Field_ID | Campo | Estado | Componente | Editable |
|---|---|---|---|---|
| UI-STK-001 | Stock actual | READONLY | NUMBER_READONLY | No |
| UI-STK-002 | Stock comprometido | READONLY | NUMBER_READONLY | No |
| UI-STK-003 | Pedidos pendientes | READONLY | NUMBER_READONLY | No |
| UI-STK-004 | Compras en tránsito | READONLY | NUMBER_READONLY | No |
| UI-STK-005 | Consumo histórico | READONLY | NUMBER_READONLY | No |
| UI-STK-006 | Demanda | READONLY | NUMBER_READONLY | No |
| UI-STK-007 | Cobertura | CALCULATED | METRIC_CARD | No |
| UI-STK-008 | Rotación | CALCULATED | METRIC_CARD | No |
| UI-STK-009 | Recepciones previstas | READONLY | DATA_TABLE | No |
| UI-STK-010 | Fecha de evaluación | INPUT/TRACE | DATE_INPUT / DATE_READONLY | Según origen |
| UI-STK-011 | Periodo de referencia | INPUT/CONFIG | CONFIG_CONTROL | Sí, controlado |

### Ventas y rentabilidad

| Field_ID | Campo | Estado | Componente | Editable |
|---|---|---|---|---|
| UI-VTA-001 | Precio de venta | READONLY | NUMBER_READONLY | No |
| UI-VTA-002 | Margen | CALCULATED | METRIC_CARD | No |
| UI-VTA-003 | Margen porcentual | CALCULATED | METRIC_CARD | No |
| UI-VTA-004 | Ventas | READONLY | NUMBER_READONLY | No |
| UI-VTA-005 | Evolución de demanda | READONLY/CALCULATED | METRIC_CARD | No |

### Situación financiera

| Field_ID | Campo | Estado | Componente | Editable |
|---|---|---|---|---|
| UI-FIN-001 | Tesorería disponible | READONLY | NUMBER_READONLY | No |
| UI-FIN-002 | Pagos previstos | READONLY | NUMBER_READONLY | No |
| UI-FIN-003 | Liquidez | READONLY/CALCULATED | METRIC_CARD | No |
| UI-FIN-004 | Impacto económico estimado | CALCULATED | METRIC_CARD | No |
| UI-FIN-005 | Capacidad financiera relevante | READONLY/CALCULATED | METRIC_CARD | No |

### Proveedores

| Field_ID | Campo | Estado | Componente | Editable |
|---|---|---|---|---|
| UI-PRV-001 | Proveedor actual | READONLY | TEXT_READONLY | No |
| UI-PRV-002 | Proveedor alternativo | READONLY | TEXT_READONLY | No |
| UI-PRV-003 | Histórico del proveedor | READONLY | DATA_TABLE | No |
| UI-PRV-004 | Condiciones proveedor | READONLY | TEXT_READONLY | No |
| UI-PRV-005 | Incidencias proveedor | READONLY | DATA_TABLE | No |

### Histórico de compras

| Field_ID | Campo | Estado | Componente | Editable |
|---|---|---|---|---|
| UI-HIS-001 | Fecha compra | READONLY | DATE_READONLY | No |
| UI-HIS-002 | Artículo | READONLY | TEXT_READONLY | No |
| UI-HIS-003 | Proveedor | READONLY | TEXT_READONLY | No |
| UI-HIS-004 | Cantidad | READONLY | NUMBER_READONLY | No |
| UI-HIS-005 | Precio | READONLY | NUMBER_READONLY | No |
| UI-HIS-006 | Condiciones | READONLY | TEXT_READONLY | No |
| UI-HIS-007 | Descuento | READONLY | NUMBER_READONLY | No |
| UI-HIS-008 | Rappel | READONLY | NUMBER_READONLY | No |
| UI-HIS-009 | Incidencias | READONLY | DATA_TABLE | No |
| UI-HIS-010 | Comparabilidad | READONLY | TEXT_READONLY | No |

### Configuración

| Field_ID | Campo | Estado | Componente | Editable |
|---|---|---|---|---|
| UI-CFG-001 | Periodo de referencia | CONFIG | CONFIG_CONTROL | Sí, controlado |
| UI-CFG-002 | Límites | CONFIG | CONFIG_CONTROL | Sí, controlado |
| UI-CFG-003 | Tolerancias | CONFIG | CONFIG_CONTROL | Sí, controlado |
| UI-CFG-004 | Niveles de stock | CONFIG | CONFIG_CONTROL | Sí, controlado |
| UI-CFG-005 | Márgenes | CONFIG | CONFIG_CONTROL | Sí, controlado |
| UI-CFG-006 | Criterios financieros | CONFIG | CONFIG_CONTROL | Sí, controlado |
| UI-CFG-007 | Reglas | CONFIG | CONFIG_CONTROL | Sí, controlado |
| UI-CFG-008 | Excepciones | CONFIG | CONFIG_CONTROL | Sí, controlado |
| UI-CFG-009 | Versión de configuración | TRACE | TEXT_READONLY | No |
| UI-CFG-010 | Vigencia de configuración | TRACE | DATE_READONLY | No |

### Resultado

| Field_ID | Campo | Estado | Componente | Editable |
|---|---|---|---|---|
| UI-RES-001 | Resultado | DECISION | DECISION_BADGE | No |
| UI-RES-002 | Principales motivos | READONLY | TEXT_READONLY | No |
| UI-RES-003 | Factores relevantes | READONLY | TEXT_READONLY | No |
| UI-RES-004 | Reglas activadas | READONLY | DATA_TABLE | No |
| UI-RES-005 | Evidencia utilizada | READONLY | DATA_TABLE | No |
| UI-RES-006 | Excepciones | READONLY | DATA_TABLE | No |
| UI-RES-007 | Riesgos | READONLY | DATA_TABLE | No |
| UI-RES-008 | Información faltante | READONLY | DATA_TABLE | No |

### Condiciones recomendadas

| Field_ID | Campo | Estado | Componente | Editable |
|---|---|---|---|---|
| UI-NEG-001 | Cantidad recomendada | READONLY | NUMBER_READONLY | No |
| UI-NEG-002 | Precio objetivo | READONLY | NUMBER_READONLY | No |
| UI-NEG-003 | Plazo de pago recomendado | READONLY | NUMBER_READONLY | No |
| UI-NEG-004 | Plazo de entrega recomendado | READONLY | NUMBER_READONLY | No |
| UI-NEG-005 | Descuento/condición requerida | READONLY | TEXT_READONLY | No |
| UI-NEG-006 | Otras condiciones | READONLY | TEXT_READONLY | No |

### Trazabilidad

| Field_ID | Campo | Estado | Componente | Editable |
|---|---|---|---|---|
| UI-TRZ-001 | ID evaluación | TRACE | TEXT_READONLY | No |
| UI-TRZ-002 | Datos utilizados | TRACE | TRACE_PANEL | No |
| UI-TRZ-003 | Fecha de los datos | TRACE | DATE_READONLY | No |
| UI-TRZ-004 | Parámetros vigentes | TRACE | TRACE_PANEL | No |
| UI-TRZ-005 | Reglas aplicadas | TRACE | TRACE_PANEL | No |
| UI-TRZ-006 | Evidencia | TRACE | TRACE_PANEL | No |
| UI-TRZ-007 | Excepciones | TRACE | TRACE_PANEL | No |
| UI-TRZ-008 | Resultado consolidado | TRACE | TRACE_PANEL | No |
| UI-TRZ-009 | Versión de componentes | TRACE | TEXT_READONLY | No |
| UI-TRZ-010 | Fecha/hora de evaluación | TRACE | DATE_READONLY | No |

## 5. Salvaguarda

La asignación de componente no constituye autoridad de cálculo. En particular, `UI-STK-007` y `UI-STK-008` permanecen visualmente definidos pero bloqueados para implementación cuantitativa hasta disponer de autoridad para sus fórmulas/metodología.

**Estado:** listo para AUDITAR.
