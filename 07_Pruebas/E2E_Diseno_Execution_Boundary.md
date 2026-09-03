# EIOS — DISEÑO E2E EXECUTION BOUNDARY

**Versión:** 0.2
**Estado:** DISEÑO DEPURADO — PENDIENTE DE AUDITORÍA 2
**Baseline:** `40b4646df76426117779fe6aaa318e734ea49f41`

## 1. Propósito

Resolver exclusivamente la discontinuidad entre la entrada autorizada por U1/U1.1 y la entrega a O1 de resultados producidos por capacidades ya autorizadas.

La frontera es una capa de coordinación de ejecución; no sustituye O1, O2, O3 ni ninguna capacidad analítica.

## 2. Flujo

```text
CEO → U1.1 → U1 → Execution Boundary → capacidades autorizadas → O1 → U1.1
```

## 3. Catálogo y autoridad

El boundary no define una nueva autoridad de negocio. Solo podrá invocar capacidades cuyo contrato ya esté cerrado y que se declaren explícitamente como `invocable` para este boundary.

El catálogo de invocación será una configuración contractual, no una inferencia dinámica. Una capacidad no declarada no se invoca.

O1 no se considera una capacidad analítica invocable: recibe resultados y compone el paquete operacional.

O2 y O3 mantienen sus contratos actuales. La integración O4→O2→O3 queda fuera salvo contrato específico posterior.

## 4. Entrada y contexto

Entrada mínima:

- `PurchaseOperation` canónico;
- `DecisionContext` canónico;
- catálogo/política de ejecución autorizada;
- contexto de ejecución controlado.

Se preservan sin modificación `decision_id`, `scenario_id`, `rules_version`, `parameters_version` y `data_snapshot_id`.

No se crea `decision_version`, `decision_fingerprint` ni otro identificador paralelo.

## 5. Plan de ejecución

La ejecución será **declarativa y determinista**: el plan autorizado define las capacidades y sus dependencias. El boundary no descubre dependencias por heurística ni genera un orden dinámico basado en resultados de negocio.

Antes de ejecutar debe validarse el plan completo. Si una precondición estructural conocida impide una ejecución segura, no se inicia parcialmente el plan.

El boundary no calcula resultados de las capacidades; las invoca conforme a sus contratos y transporta sus resultados.

## 6. Estados

La frontera debe distinguir:

- `READY`: plan válido, aún no iniciado;
- `RUNNING`: ejecución en curso;
- `COMPLETED`: todas las capacidades requeridas por el plan han producido resultados contractualmente completos;
- `PARTIALLY_COMPLETED`: existe resultado válido parcial o una capacidad no evaluable/bloqueada;
- `NOT_EVALUABLE`: no puede determinarse de forma segura el resultado técnico requerido;
- `BLOCKED`: una precondición o límite contractual impide iniciar/continuar;
- `FAILED`: fallo técnico explícito con causa.

Estos estados describen **ejecución técnica**, nunca una conclusión de compra.

## 7. Errores

Un `FAILED`, `BLOCKED` o `NOT_EVALUABLE` no puede transformarse en `NO COMPRAR`, `COMPRAR`, `NEGOCIAR` ni otra conclusión empresarial.

`failure_reason` solo describe el fallo técnico. Las limitaciones deben conservarse hasta O1/U1.1.

## 8. Trazabilidad

La ejecución debe reutilizar la identidad contextual canónica y conservar las referencias de trazabilidad producidas por las capacidades.

El identificador de ejecución del boundary, si resulta necesario técnicamente, será un identificador operacional subordinado a la identidad O1 y no una nueva identidad de decisión.

La materialización deberá demostrar reproducibilidad con la misma entrada, plan y versiones.

## 9. Salida

La salida es un conjunto ordenado de resultados de capacidades compatible con `CapabilityExecution`/O1. El boundary no los interpreta para producir una recomendación.

O1 seguirá siendo responsable del `DecisionSupportPackage` y de su composición de estado. U1.1 solo presenta el paquete recibido.

## 10. Exclusiones

Fuera de alcance:

- API pública;
- persistencia/SQL;
- SSO/permisos de infraestructura;
- ejecución real de compras;
- automatización de negociación;
- ranking/scoring/optimización;
- selección automática;
- recomendación automática;
- nuevo sistema de identidad/versionado;
- modificación de reglas, parámetros o RDM;
- integración implícita O4→O2→O3.

## 11. Criterio de división

Si la auditoría demuestra que una capacidad requiere un contrato de integración propio, esa integración se separará en un scope posterior. El boundary no absorberá contratos no cerrados para completar artificialmente el E2E.

## 12. Autorización

Este documento **NO autoriza implementación**.

La autorización requiere Auditoría 2 superada y cierre formal del diseño.
