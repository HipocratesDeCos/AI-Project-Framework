# EIOS — Registro Maestro de Campos de Interfaz v0.1

**Estado:** DISEÑO FUNCIONAL DE UI / NO IMPLEMENTACIÓN
**Baseline:** `3c4d5cb7e02d5d7d88bb8bcf1a20a3992dc06c38`
**Rama:** `reconcile/stk-authority-baseline-2026-09-05`
**Fecha:** 2026-09-06

## 1. Propósito

Definir el inventario funcional de campos que la interfaz EIOS deberá presentar o manejar, sin convertir este registro en contrato cuantitativo ni en Plan de Pruebas.

Los identificadores `UI-*` de este documento son **identificadores de interfaz** y no son `Test_ID`.

## 2. Estados de campo

- **INPUT:** dato introducido o seleccionado por el usuario.
- **READONLY:** dato mostrado sin edición directa.
- **CALCULATED:** valor calculado por lógica autorizada.
- **DECISION:** salida de evaluación.
- **TRACE:** dato de trazabilidad/auditoría.
- **CONFIG:** dato de configuración.

## 3. Propuesta de compra

| ID UI | Campo | Estado | Nota |
|---|---|---|---|
| UI-PROP-001 | ID propuesta | TRACE | Identificador de la propuesta |
| UI-PROP-002 | Artículo | INPUT | Selección de artículo |
| UI-PROP-003 | Descripción artículo | READONLY | Derivada de la ficha del artículo |
| UI-PROP-004 | Proveedor | INPUT | Selección de proveedor |
| UI-PROP-005 | Cantidad propuesta | INPUT | Unidad según artículo |
| UI-PROP-006 | Precio unitario | INPUT | Moneda definida por configuración |
| UI-PROP-007 | Importe total | CALCULATED | Solo lectura |
| UI-PROP-008 | Fecha propuesta | INPUT | Fecha de la propuesta |
| UI-PROP-009 | Fecha prevista de entrega | INPUT | Fecha indicada por proveedor |
| UI-PROP-010 | Plazo de entrega | INPUT/READONLY | Según origen del dato |
| UI-PROP-011 | Plazo de pago | INPUT | Condición propuesta |
| UI-PROP-012 | Condiciones de pago | INPUT | Texto/selección |
| UI-PROP-013 | Descuento | INPUT | Según unidad definida |
| UI-PROP-014 | Rappel | INPUT | Según unidad definida |
| UI-PROP-015 | Otras condiciones | INPUT | Observaciones |

## 4. Contexto operativo

| ID UI | Campo | Estado | Estado STK |
|---|---|---|---|
| UI-STK-001 | Stock actual | READONLY | Canónico; metodología pendiente |
| UI-STK-002 | Stock comprometido | READONLY | Canónico; metodología pendiente |
| UI-STK-003 | Pedidos pendientes | READONLY | Canónico; metodología pendiente |
| UI-STK-004 | Compras en tránsito | READONLY | Canónico; metodología pendiente |
| UI-STK-005 | Consumo histórico | READONLY | Canónico; fórmula pendiente |
| UI-STK-006 | Demanda | READONLY | Canónico; definición pendiente |
| UI-STK-007 | Cobertura | CALCULATED | Fórmula pendiente; no implementar |
| UI-STK-008 | Rotación | CALCULATED | Metodología pendiente |
| UI-STK-009 | Recepciones previstas | READONLY | Definición pendiente |
| UI-STK-010 | Fecha de evaluación | INPUT/TRACE | Contexto temporal |
| UI-STK-011 | Periodo de referencia | INPUT/CONFIG | Debe quedar trazable |

## 5. Ventas y rentabilidad

| ID UI | Campo | Estado |
|---|---|---|
| UI-VTA-001 | Precio de venta | READONLY |
| UI-VTA-002 | Margen | CALCULATED |
| UI-VTA-003 | Margen porcentual | CALCULATED |
| UI-VTA-004 | Ventas | READONLY |
| UI-VTA-005 | Evolución de demanda | READONLY/CALCULATED |

## 6. Situación financiera

| ID UI | Campo | Estado |
|---|---|---|
| UI-FIN-001 | Tesorería disponible | READONLY |
| UI-FIN-002 | Pagos previstos | READONLY |
| UI-FIN-003 | Liquidez | READONLY/CALCULATED |
| UI-FIN-004 | Impacto económico estimado | CALCULATED |
| UI-FIN-005 | Capacidad financiera relevante | READONLY/CALCULATED |

## 7. Proveedores

| ID UI | Campo | Estado |
|---|---|---|
| UI-PRV-001 | Proveedor actual | READONLY |
| UI-PRV-002 | Proveedor alternativo | READONLY |
| UI-PRV-003 | Histórico del proveedor | READONLY |
| UI-PRV-004 | Condiciones proveedor | READONLY |
| UI-PRV-005 | Incidencias proveedor | READONLY |

## 8. Histórico de compras

| ID UI | Campo | Estado |
|---|---|---|
| UI-HIS-001 | Fecha compra | READONLY |
| UI-HIS-002 | Artículo | READONLY |
| UI-HIS-003 | Proveedor | READONLY |
| UI-HIS-004 | Cantidad | READONLY |
| UI-HIS-005 | Precio | READONLY |
| UI-HIS-006 | Condiciones | READONLY |
| UI-HIS-007 | Descuento | READONLY |
| UI-HIS-008 | Rappel | READONLY |
| UI-HIS-009 | Incidencias | READONLY |
| UI-HIS-010 | Comparabilidad | READONLY |

## 9. Configuración y parámetros

| ID UI | Campo | Estado |
|---|---|---|
| UI-CFG-001 | Periodo de referencia | CONFIG |
| UI-CFG-002 | Límites | CONFIG |
| UI-CFG-003 | Tolerancias | CONFIG |
| UI-CFG-004 | Niveles de stock | CONFIG |
| UI-CFG-005 | Márgenes | CONFIG |
| UI-CFG-006 | Criterios financieros | CONFIG |
| UI-CFG-007 | Reglas | CONFIG |
| UI-CFG-008 | Excepciones | CONFIG |
| UI-CFG-009 | Versión de configuración | TRACE |
| UI-CFG-010 | Vigencia de configuración | TRACE |

**Restricción STK:** estos campos no constituyen por sí mismos autoridad para asignar valores ni fórmulas M01–M10.

## 10. Resultado de evaluación

| ID UI | Campo | Estado |
|---|---|---|
| UI-RES-001 | Resultado | DECISION |
| UI-RES-002 | Principales motivos | READONLY |
| UI-RES-003 | Factores relevantes | READONLY |
| UI-RES-004 | Reglas activadas | READONLY |
| UI-RES-005 | Evidencia utilizada | READONLY |
| UI-RES-006 | Excepciones | READONLY |
| UI-RES-007 | Riesgos | READONLY |
| UI-RES-008 | Información faltante | READONLY |

Resultados funcionales permitidos:

- `COMPRAR`
- `NEGOCIAR`
- `COMPRAR CONDICIONADO`
- `NO COMPRAR`
- `INFORMACIÓN INSUFICIENTE`

## 11. Condiciones recomendadas

| ID UI | Campo | Estado |
|---|---|---|
| UI-NEG-001 | Cantidad recomendada | READONLY |
| UI-NEG-002 | Precio objetivo | READONLY |
| UI-NEG-003 | Plazo de pago recomendado | READONLY |
| UI-NEG-004 | Plazo de entrega recomendado | READONLY |
| UI-NEG-005 | Descuento/condición requerida | READONLY |
| UI-NEG-006 | Otras condiciones | READONLY |

Estas salidas son recomendaciones y no órdenes de compra.

## 12. Trazabilidad

| ID UI | Campo | Estado |
|---|---|---|
| UI-TRZ-001 | ID evaluación | TRACE |
| UI-TRZ-002 | Datos utilizados | TRACE |
| UI-TRZ-003 | Fecha de los datos | TRACE |
| UI-TRZ-004 | Parámetros vigentes | TRACE |
| UI-TRZ-005 | Reglas aplicadas | TRACE |
| UI-TRZ-006 | Evidencia | TRACE |
| UI-TRZ-007 | Excepciones | TRACE |
| UI-TRZ-008 | Resultado consolidado | TRACE |
| UI-TRZ-009 | Versión de componentes | TRACE |
| UI-TRZ-010 | Fecha/hora de evaluación | TRACE |

## 13. Reglas de materialización

1. Ningún campo `CALCULATED` se implementará con una fórmula no autorizada.
2. Los campos STK pueden existir como estructura visual o fuente de datos, pero no ejecutarán M01–M10 mientras la autoridad cuantitativa siga pendiente.
3. Los `UI-*` no se incorporan al Plan de Pruebas como `Test_ID`.
4. La interfaz debe distinguir visualmente INPUT, READONLY, CALCULATED y DECISION.
5. Los estados `INFORMACIÓN INSUFICIENTE` y las excepciones deben ser visibles y trazables.
6. Toda evaluación debe conservar contexto temporal y versión de configuración.

## 14. Estado de aprobación

**Diseño:** apto como inventario funcional de interfaz.

**Implementación:** pendiente de materialización técnica.

**STK cuantitativo:** bloqueado hasta resolución de autoridad M01–M10.
