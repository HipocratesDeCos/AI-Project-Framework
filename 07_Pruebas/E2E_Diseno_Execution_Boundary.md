# EIOS — DISEÑO E2E EXECUTION BOUNDARY

**Versión:** 0.1
**Estado:** DISEÑO INICIAL — PENDIENTE DE AUDITORÍA
**Baseline:** `40b4646df76426117779fe6aaa318e734ea49f41`

## 1. Propósito

Resolver exclusivamente la discontinuidad identificada entre la entrada autorizada por U1/U1.1 y la entrega de resultados ya materializados a O1.

La capacidad propuesta constituye una frontera de ejecución controlada. No sustituye O1, O2, O3 ni ninguna capacidad analítica existente.

## 2. Flujo objetivo

```text
CEO
 ↓
U1.1 Visual
 ↓
U1 Application Boundary
 ↓
Execution Boundary
 ↓
capacidades previamente autorizadas
 ↓
O1 Decision Support Package
 ↓
U1.1 Visual
```

## 3. Principios

1. La entrada debe ser un `PurchaseOperation` y un `DecisionContext` canónicos.
2. La frontera no crea identidad paralela ni versionado paralelo.
3. Debe preservar `decision_id`, `scenario_id`, `rules_version`, `parameters_version` y `data_snapshot_id`.
4. No puede aprobar, rechazar, comprar, negociar ni seleccionar automáticamente.
5. No puede introducir ranking, scoring u optimización.
6. No puede alterar reglas, parámetros, evidencia ni datos de entrada.
7. Debe distinguir ejecución técnica de resultado empresarial.
8. Los resultados parciales, bloqueados, no evaluables y fallidos deben permanecer explícitos.
9. O1 continúa siendo el sobre operacional y de trazabilidad.
10. La interfaz visual solo presenta el resultado; no interpreta ni recalcula.

## 4. Alcance candidato

La frontera podrá recibir una solicitud de ejecución autorizada y delegar en capacidades existentes cuyos contratos ya estén cerrados.

Debe devolver resultados de ejecución suficientemente estructurados para que O1 construya el `DecisionSupportPackage` sin reinterpretarlos.

No se autoriza todavía una lista fija de capacidades E2E. Debe determinarse durante la auditoría si existe una secuencia contractual necesaria y segura.

## 5. Exclusiones

Quedan fuera de este diseño:

- API pública;
- persistencia;
- SQL;
- SSO/permisos de infraestructura;
- ejecución real de compras;
- automatización de negociación;
- ranking de escenarios;
- selección automática;
- nuevo sistema de identidad/versionado;
- integración O4→O2→O3 salvo que una auditoría posterior demuestre que constituye una dependencia necesaria y sea objeto de contrato propio.

## 6. Preguntas de auditoría obligatorias

Antes de cerrar el diseño debe verificarse:

- qué capacidades pueden ser invocadas realmente y bajo qué contrato;
- qué precondiciones necesita cada una;
- cómo se propagan identidad, versiones y snapshot;
- cómo se agregan estados sin convertir un resultado técnico en decisión empresarial;
- qué ocurre ante fallo, bloqueo o resultado parcial;
- si existe dependencia funcional de O2/O3;
- si el boundary debe ser secuencial, declarativo o mediante otro mecanismo controlado;
- cómo se garantiza determinismo y trazabilidad;
- si el alcance constituye realmente un único scope o debe dividirse.

## 7. Regla de autorización

Este documento **NO autoriza implementación**.

La implementación solo podrá comenzar después de:

**DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR**.
