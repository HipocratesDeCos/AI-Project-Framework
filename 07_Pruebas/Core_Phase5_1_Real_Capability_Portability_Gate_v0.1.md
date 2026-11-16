# EIOS — F5.1 · AUDITORÍA DE CAPACIDADES REALES Y FRONTERA DE REUTILIZACIÓN

**Fecha:** 2026-11-16
**Base:** `main @ 1238339720a9d60da98b76b6b3c614eacf1e9bc8`, F4.4 completada y CI postmerge #43939229600 SUCCESS.
**Objetivo:** verificar las integraciones empresariales existentes antes de intentar llevarlas a otros proyectos; **no** crear otra capa de invocadores, modificar algoritmos ni publicar una capacidad sin pruebas de procedencia.

## 1. DISEÑAR — INVENTARIO DE PUERTOS Y DEPENDENCIAS

F4 demostró que un único wheel contiene los contratos neutrales `eios.kernel.execution` y `eios.parameters.center`, y lo consumen dos proyectos **sintéticos mínimos** en instalaciones separadas. No ha probado todavía portabilidad empresarial del conjunto EIOS.

Revisión de las rutas existentes:

| Capacidad | Productor existente | Dependencia de negocio | Frontera actual | Veredicto para otro dominio |
|---|---|---|---|---|
| PRICE | `eios.core.price_integration.build_provenanced_price_invoker` → `eios.pricing.engine.run_price_intelligence` | `PriceIntelligenceInput` contiene `PurchaseOperation` + `DecisionContext`, evaluación de suficiencia y evidencias | Compara todos los campos de compra y contexto antes de ejecutar | NO LISTA para reuso genérico; conservar adaptador sectorial |
| TCO | `eios.core.tco_integration.build_provenanced_tco_invoker` → `eios.tco.engine.calculate_tco` | `TCOInput` contiene `PurchaseOperation`; costes atribuibles de adquisición | Compara toda la compra y solo `decision_id`/`scenario_id` del contexto | NO LISTA para proclamar trazabilidad completa de versiones en otro proyecto |
| C0 / RULES | `eios.rules` y `eios.core` | Inventario, compra, proveedores, pagos y reglas comerciales | Adaptadores de la aplicación; no capacidad neutral por ubicación | NO LISTA sin separar contratos y política |
| QTG / O1 | Puertas de confianza propias | Decision Input Package y admisión/procedencia | `execute_kernel` las bloquea deliberadamente como invocadores genéricos | NO CONVERTIR EN PLUGINS |

La distinción entre «calculador reutilizable» y «capacidad aprobada para un proyecto» es esencial. Copiar un cálculo sin sus contratos, identidades y evidencias no demuestra portabilidad; confundir el resultado técnico `COMPLETED` con una aprobación sería un error de diseño.

## 2. AUDITAR — PRUEBA DE CONEXIÓN SIN REFACTORIZACIÓN

Se incorpora `tests/test_f5_1_real_purchase_capability_seam.py`. Utiliza los **productores reales** PRICE y TCO con entradas sintéticas y llama al API público `run_mvp_execution`, que delega en `execute_plan` y en el **único** `execute_kernel`.

Las pruebas verifican:

1. Un único paso por la función neutral para dos capacidades reales, con plan `PRICE → TCO` y contexto versionado íntegro.
2. TCO real de una compra sintética de 10 unidades × 5 euros = 50 euros, sin alterar el cálculo ni confundirlo con una orden de compra.
3. PRICE sin referencias: `NOT_EVALUABLE`, carencia `PRICE_NOT_JUSTIFIABLE`; TCO completo: `COMPLETED`; resultado técnico global: `PARTIALLY_COMPLETED`.
4. Diferencia en proveedor, cantidad o precio: rechazo de PRICE antes de ejecutar TCO.
5. Diferencia en `rules_version`, `parameters_version` o `data_snapshot_id`: rechazo de PRICE antes de ejecutar TCO.
6. TCO con porte aplicable pero importe ausente: carencia `TRANSPORT` preservada junto con `PRICE_NOT_JUSTIFIABLE`, sin fabricar importe.
7. El núcleo no importa `eios.*`, mientras que los contratos PRICE y TCO continúan importando expresamente `eios.core.models`.

**No se modifica producción**: ningún archivo `eios/`, ninguna regla, precio, resultado, artefacto F4, SQL, servicio ni configuración de CI. Las pruebas de F2, F3 y F4 se mantienen intactas.

## 3. DEPURAR — LÍMITES Y HALLAZGOS

**Hallazgo P1 — TCO:** el invocador de TCO compara la identidad completa de `PurchaseOperation`, pero su `TCOInput` no lleva una copia de `DecisionContext` para cotejar `rules_version`, `parameters_version` y `data_snapshot_id`. No debe describirse esta ruta como autenticación documental ni como procedencia empresarial completa. No cambiar TCO a ciegas: primero definir la autoridad documental aplicable a una versión futura del contrato, con compatibilidad y regresiones.

**Hallazgo P1 — salida neutral:** el `KernelOutcome` transporta **estados técnicos y trazas**, no cantidades de negocio, dictámenes económicos, datos firmados ni credenciales. Para reutilizar PRICE o TCO desde otro vertical se requiere su propio contrato de resultados analíticos, sin esconder los cálculos en un invocador genérico o degradar el seguimiento de procedencia.

**Hallazgo P2 — composición:** `run_mvp_execution` y `MVP_CAPABILITY_ORDER` siguen perteneciendo a Compras. No trasladarlos al paquete `eios-kernel`; otros proyectos eligen su propio plan.

## 4. AUDITAR 2 — DECISIÓN PARA F5.2

**Elegir una sola capacidad y justificar su extracción**. TCO es candidato a una primera separación de contratos *si* se asegura el contexto y se prueba compatibilidad sin tocar los resultados canónicos. PRICE tiene una frontera documental más extensa y requiere paquete adicional de evidencias, normalización y pruebas de suficiencia.

Antes de diseñar F5.2:

- Inventariar todas las dependencias transitivas del candidato y su contrato público.
- Diseñar el adaptador sectorial que mapea contexto/operación específicos a la capacidad, sin reclamar autoridad de negocio.
- Establecer pruebas de identidad, versiones, ausencia de evidencias, cálculo y regresión antes de proponer un wheel de capacidad opcional.
- Preservar `decision_authority=False` y `operational_path=FORBIDDEN` en el runtime genérico.

## 5. CERRAR → MATERIALIZAR → CI

F5.1 se cierra **solo** con suite Python completa y los tres controles SQL en el SHA exacto de la PR, revisión de diff estrictamente limitada a prueba + documento, merge controlado y CI postintegración `main` SUCCESS. Su resultado sería:

- `existing_real_capability_kernel_compatibility=VERIFIED`;
- `standalone_business_capability_distribution=NOT_BUILT`;
- `full_cross_domain_business_portability=NOT_PROVEN`.

**Cierre F5.1 NO implica cierre de F5 ni habilitación de operaciones empresariales.**
