# EIOS — Especificación de Pantalla de Interacción v0.1

**Estado:** DISEÑO — PENDIENTE DE AUDITORÍA
**Baseline:** `e4319d5a632a3810cfc14c59e0ed5a7b15a139c0`
**Fecha:** 2026-09-07

## 1. Propósito

Definir la estructura funcional de la pantalla de interacción de la app a partir del Registro Maestro y del mapping campo → componente ya cerrado. Este documento especifica zonas, orden funcional, comportamiento y estados de interfaz. No introduce nuevos campos ni lógica de negocio.

## 2. Principio de autoridad

`UI_Field_Registry_v0.1.md` es la autoridad de campos. `UI_Field_Component_Mapping_v0.2.md` determina la representación permitida. Esta especificación no puede crear, renombrar semánticamente, eliminar ni recalcular campos.

## 3. Estructura de pantalla

### ZONA A — Identificación y contexto

Contiene identificación de evaluación/propuesta y contexto temporal. Debe priorizar la trazabilidad y el contexto antes de la introducción de datos.

### ZONA B — Datos de propuesta

Agrupa artículo, proveedor, cantidades, precios, fechas y condiciones. Los componentes editables proceden exclusivamente del mapping autorizado.

### ZONA C — Contexto operativo

Presenta información de stock, demanda, cobertura, rotación y recepciones. La zona es predominantemente informativa.

### ZONA D — Ventas, rentabilidad y situación financiera

Presenta precio de venta, margen, ventas, tesorería, pagos, liquidez e impacto económico según los estados canónicos.

### ZONA E — Proveedores e histórico

Permite consultar proveedor, alternativas, condiciones, incidencias e histórico de compras. Los elementos históricos son de lectura.

### ZONA F — Configuración controlada

Contiene parámetros de configuración autorizados. Debe quedar separada de los datos de la propuesta para evitar confusión entre dato operativo y parámetro.

### ZONA G — Resultado de evaluación

Presenta el resultado autorizado, motivos, factores, reglas activadas, evidencia, excepciones, riesgos e información faltante. El resultado no es editable.

### ZONA H — Condiciones recomendadas

Presenta las condiciones resultantes de la evaluación como información de salida. No permite editar directamente el resultado calculado.

### ZONA I — Trazabilidad

Presenta ID de evaluación, datos utilizados, fecha de datos, parámetros, reglas, evidencia, excepciones, resultado consolidado y versión de componentes.

## 4. Flujo de interacción

```text
Identificación
      ↓
Datos de propuesta
      ↓
Contexto operativo
      ↓
Información económica y proveedores
      ↓
Configuración autorizada
      ↓
Evaluación
      ↓
Resultado
      ↓
Condiciones recomendadas
      ↓
Trazabilidad
```

## 5. Reglas de interacción

1. Los campos `INPUT` son los únicos susceptibles de entrada ordinaria.
2. Los campos `READONLY` no pueden convertirse en inputs por decisión de UI.
3. `CALCULATED` solo representa resultados autorizados.
4. `DECISION` solo puede mostrar resultados pertenecientes al catálogo autorizado.
5. `TRACE` es informativo y no editable.
6. `CONFIG` requiere controles restringidos y diferenciados visualmente de los datos operativos.
7. Los estados compuestos deben conservar el comportamiento definido en el mapping.
8. Los errores o datos insuficientes deben expresarse mediante estados explícitos sin crear campos auxiliares canónicos.

## 6. STK

Los campos STK pueden visualizarse como contexto cuando exista dato autorizado. La pantalla no puede convertir su mera presencia en autoridad para calcular M01–M10. Los indicadores cuya metodología no esté autorizada deben permanecer sin cálculo implementado.

## 7. Estados de pantalla

- `INITIAL`: pantalla preparada para recibir contexto.
- `INPUT_REQUIRED`: faltan entradas obligatorias.
- `READY`: entradas mínimas disponibles.
- `EVALUATING`: evaluación en curso.
- `RESULT`: resultado disponible.
- `INSUFFICIENT_DATA`: información insuficiente.
- `ERROR`: error técnico o de validación.

Estos estados son estados de UI, no nuevos campos del Registro Maestro.

## 8. Salvaguardas

No se crean `Field_ID`, `Test_ID`, fórmulas, reglas de negocio ni autoridad cuantitativa desde la interfaz. La especificación es exclusivamente de estructura y comportamiento visual autorizado.

**Siguiente gate: AUDITAR.**