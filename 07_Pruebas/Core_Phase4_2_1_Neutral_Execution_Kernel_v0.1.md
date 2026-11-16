# EIOS — F4.2.1 · FRONTERA NEUTRAL DE EJECUCIÓN (CON ADAPTADOR DE COMPRAS)

**Fecha:** 2026-11-16  
**Base:** `main @ 7c11a1c05acd36ad5403964d6180fef2a05720c5` — F4.1 auditada, integrada y validada.  
**Objetivo:** iniciar F4.2 mediante un único bucle técnico de ejecución independiente del dominio, **manteniendo** la API y el comportamiento de EIOS Compras.

## 1. DISEÑAR — DIFERENCIAR CONTRATO COMÚN Y NEGOCIO

El contrato `PurchaseOperation` de C0 exige artículo, proveedor, cantidad, precio y EUR; `eios/core/execution_boundary.py` invocaba directamente capacidades sobre él. `eios/core/mvp_execution.py` conserva una selección fija de capacidades comerciales. Esta estructura impide que una aplicación distinta utilice la misma infraestructura de ejecución **sin fingir una compra**.

Un motor reutilizable no necesita conocer los datos internos de ventas/compras; sí necesita recibir la identidad/versiones del caso, un payload tipado validado por su aplicación, un plan explícito, invocadores autorizados fuera del núcleo y resultados terminales técnicos. Ninguna ejecución equivale por sí sola a una decisión ni a autenticación del origen.

## 2. AUDITAR — IMPLEMENTACIÓN CONTROLADA

**Nuevo `eios/kernel/execution.py`** (biblioteca Pydantic independiente de `eios.core`, `company_*`, SQL y UI):

- `KernelContext`: `project_id`, `decision_id`, `scenario_id`, `rules_version`, `parameters_version` y `data_snapshot_id`, inmutables.
- `KernelOperation`: `decision_id`, `scenario_id` y `payload` **Pydantic tipado**. Los contratos de una empresa/sector son responsabilidad del adaptador, no del kernel; un diccionario anónimo no se acepta como operación canónica.
- `KernelPlan`: capacidades explícitas y versión de política, sin duplicados ni nombres inválidos.
- `KernelCapabilityResult` y `KernelOutcome`: resultados técnicos, traza, carencias y causas de fallo. En el resultado se fijan `provenance_status=UNVERIFIED_ADAPTER_RESPONSIBILITY`, `decision_authority=False` y `operational_path=FORBIDDEN`.
- `execute_kernel`: **único bucle de preflight, llamada, aislamiento por copia profunda, validación de resultados y consolidación terminal**. Catálogo de invocadores congelado al comenzar. Verificación previa de identidad y de presencia/callability de todas las capacidades; ninguna función se invoca ante bloqueos de preflight. Los invocadores reciben copias independientes para impedir mutaciones entre capacidades.
- `O1` y `QTG` quedan excluidos de este ejecutor genérico: exigen sus fronteras autorizadas/provenance-safe. Un invocador arbitrario con estos nombres no concede capacidad decisional.
- Excepción técnica, identidad de capacidad equivocada o `COMPLETED` sin resultado se devuelven como `FAILED` (no como un resultado comercial negativo).
- Los modelos no incluyen resultados económicos, scores, permisos, órdenes de compra, datos de clientes o decisiones.

**`eios/core/execution_boundary.py`** conserva **sus clases y firmas existentes**: `ExecutionPlan`, `ExecutionOutcome`, `BoundaryStatus`, `execute_plan(PurchaseOperation, DecisionContext,...)`. Su antiguo bucle se sustituye por **un adaptador de traducción** hacia `execute_kernel`, con devolución de los objetos `CapabilityExecution` ya conocidos. `run_mvp_execution` y el resto del vertical siguen utilizándolo **sin ser modificados**.

Esta estrategia evita duplicar el ejecutor y minimiza riesgos sobre las 3.417 pruebas previas.

## 3. DEPURAR — COMPROBACIONES

`tests/test_f4_2_neutral_execution_kernel.py` crea una operación **SalesProposal** completamente independiente de `PurchaseOperation` y comprueba:

1. Ejecución de un caso no relacionado con Compras bajo su propio proyecto y contexto versionado.
2. Rechazo de `decision_id`/`scenario_id` contradictorios antes de invocar.
3. Rechazo atómico ante capacidades ausentes, no invocables o reservadas `O1`/`QTG`.
4. Orden determinista y protección contra cambios del catálogo.
5. Aislamiento entre llamadas e invocadores del payload tipado y del contexto.
6. Estado `FAILED` ante excepciones, resultados no canónicos, identidad distinta o falsa disponibilidad.
7. Estado `PARTIALLY_COMPLETED` ante evidencia insuficiente; jamás autoridad decisional.
8. Conservación de motivos/errores, versiones y trazas.
9. Dos `project_id` diferentes sin estado compartido ni mezcla de contexto.
10. Rechazo de payloads sin contrato Pydantic y de resultados que intenten atribuir autorización operacional.
11. Test AST: el kernel no importa módulos de compras, verticales, aplicación o UI.

Se exige **toda la regresión de Compras** sin modificaciones a tests antiguos; F4.2 no autoriza relajar sus validaciones ni retirar pruebas fallidas.

## 4. AUDITAR 2 — QUÉ TODAVÍA NO SE DEMUESTRA

Un `SalesProposal` sintético de test demuestra que **la frontera técnica neutral admite un segundo tipo de dominio**. **No** demuestra todavía que una aplicación de ventas completa esté conectada, que la distribución sea independiente, que todas las capacidades sean plug-and-play, que las fuentes bancarias sean auténticas o que los permisos de otro proyecto estén verificados.

Los límites del kernel son expresos: autenticación corporativa, firma, confianza de fuentes, admisión operacional y autorización de cada invocador son responsabilidad de los **puertos/adaptadores de confianza** y de sus validaciones. El ejecutor técnico no implementa esas autoridades; si no existen, `decision_authority=False` y `operational_path=FORBIDDEN`.

**Este cambio no modifica `pyproject.toml`, `eios/parameters/local_finance_version_source.py`, `eios/finance/engine.py`, RULES, PRICE, SQL Server ni interfaces.** La siguiente unidad F4.2.2 debe invertir la dependencia específica de `parameters → company_*`. F4.3 separará la distribución. F4.4 verificará dos consumidores independientes del mismo artefacto instalado.

## 5. CERRAR → MATERIALIZAR → CI

Cierre de **F4.2.1** solo si:

- La suite Python y los tres validadores SQL Server son SUCCESS sobre el HEAD exacto de PR.
- El diff solo incorpora el kernel neutral, adaptador de compras, pruebas y documento.
- Se comprueba que ningún modelo o fuente del núcleo financiero/sistema decisional fue alterado para facilitar la ejecución de tests.
- Merge controlado y CI postintegración `main` SUCCESS sobre SHA exacto.

**Estado F4.2 global hasta completar el resto:** `neutral_execution_contract=IMPLEMENTED_AND_TESTED` (si CI termina correctamente), `reverse_parameter_dependency=PENDING`, `standalone_installability=NOT_PROVEN` y `cross_project_portability=NOT_PROVEN`.
