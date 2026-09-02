# EIOS — U1 · FRONTEND IMPLEMENTATION CONTRACT

**Estado:** 🟡 CONTRATO DE IMPLEMENTACIÓN — DISEÑO TÉCNICO
**Cierre de diseño:** `c6322e0bf50bd74f9a2c21e61cabf10f5c8dfc2d`

## 1. Propósito

Definir el contrato técnico mínimo para materializar la interfaz CEO sin introducir autoridad analítica, identidad paralela ni decisión automática.

## 2. Boundary

```text
Frontend
   ↓
Application Boundary
   ↓
O1
   ↓
Decision Support Package
   ↓
Frontend
```

El frontend no invoca directamente C0, PRICE, TCO, QTG, O2, O3, O4 o Decision Twin.

## 3. Entrada contractual

La Application Boundary recibe una solicitud estructurada con:

- datos autorizados de `PurchaseOperation`;
- referencias de evidencia admitidas;
- referencias de contexto autorizadas;
- acción técnica solicitada.

No acepta campos que creen una autoridad paralela, incluyendo `decision_version`.

## 4. Salida contractual

La respuesta hacia U1 conserva:

- `execution_context`;
- `execution_status`;
- resultados de capacidades ya autorizados;
- estado de evidencia;
- contexto de versiones;
- referencias de trazabilidad;
- elementos no resueltos.

La UI no altera estos resultados.

## 5. Acciones

Acciones técnicas MVP:

- crear/borrador de operación;
- actualizar datos antes de ejecución;
- adjuntar/referenciar evidencia;
- solicitar ejecución;
- consultar estado;
- consultar resultado;
- consultar escenarios/comparaciones disponibles.

Acciones no autorizadas:

- aprobar/rechazar compra automáticamente;
- seleccionar alternativa automáticamente;
- modificar reglas o parámetros maestros;
- alterar resultados;
- ejecutar compras o negociar.

## 6. Estados

La frontera debe conservar literalmente los estados técnicos definidos por O1: READY, RUNNING, COMPLETED, BLOCKED, PARTIALLY_COMPLETED, NOT_EVALUABLE y FAILED.

No se permite mapear `NOT_EVALUABLE` a negativo ni `FAILED` a decisión empresarial.

## 7. Identidad y versionado

La Application Boundary reutiliza las identidades y dimensiones canónicas existentes. No crea una segunda identidad de decisión, fingerprint, snapshot o trace.

## 8. Validación

La validación de frontend es sintáctica/presentacional. La validación de dominio permanece en los contratos existentes.

Debe distinguirse error de formulario, error de dominio, bloqueo técnico, no evaluable y fallo técnico.

## 9. Seguridad de interacción

Las operaciones mutables requieren confirmación explícita. El frontend debe presentar el alcance de la acción antes de ejecutarla.

## 10. Trazabilidad

Las referencias compatibles recibidas de O1 se muestran sin reinterpretarlas ni renombrar su semántica.

## 11. Pruebas mínimas

La materialización deberá cubrir como mínimo:

1. entrada válida;
2. rechazo de campos no autorizados;
3. preservación de identidad/contexto;
4. propagación de estados O1;
5. separación de errores de UI y dominio;
6. preservación de limitaciones;
7. no transformación de `NOT_EVALUABLE`;
8. no transformación de `FAILED`;
9. no mutación de resultados;
10. ausencia de decisión automática;
11. trazabilidad;
12. accesibilidad básica;
13. responsive escritorio/tablet.

## 12. Tecnología

Este contrato no fija framework, proveedor, base de datos, API pública ni SSO. La elección tecnológica deberá respetar este contrato y no podrá modificar su semántica.

**Contrato preparado para AUDITORÍA DE IMPLEMENTACIÓN.**