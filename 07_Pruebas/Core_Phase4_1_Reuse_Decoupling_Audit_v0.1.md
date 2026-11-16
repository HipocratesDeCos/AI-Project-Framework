# EIOS — F4.1 · AUDITORÍA DE DEPENDENCIAS Y PORTABILIDAD DEL MOTOR

**Fecha:** 2026-11-16  
**Repositorio:** `HipocratesDeCos/AI-Project-Framework`  
**Baseline:** `main @ 2d2b117ffd7a4c1c157c70d5b532b9278d8849c3`, cierre técnico F3 confirmado (PR #596, CI postintegración #43913556600).  
**Unidad:** F4.1 — **auditar**, no refactorizar ni cambiar contratos canónicos, reglas, datos, cálculos o vías operacionales.

## 1. VEREDICTO Y ALCANCE

**Resultado arquitectónico:** EIOS tiene capacidades, controles y pruebas aprovechables, pero **no está demostrada la independencia del motor para nuevos proyectos**. «Fase 3 técnica cerrada» acredita las fronteras ejecutadas y verificadas, no la portabilidad entre dominios.

Inspección directa del árbol de GitHub en el SHA indicado:
- **287** archivos Python bajo `eios/`.
- **65** archivos Python bajo `eios/core/`.
- **111** módulos Python con prefijo `eios/company*`, pertenecientes a la aplicación y su tratamiento de datos.
- `pyproject.toml` declara `name = "eios-mvp"`, `openpyxl` como dependencia obligatoria, y `include = ["eios", "eios.*"]`, por lo que **distribuye el árbol de aplicación y las capacidades juntas**.

La clasificación «núcleo», «servicio de dominio» y «aplicación» **no** se deduce automáticamente de la carpeta: hay capacidades especializadas dentro de `eios/core/` y lógica de integración de empresa dentro de `eios/parameters/`.

## 2. HALLAZGOS SOPORTADOS POR CÓDIGO

| ID | Prioridad | Evidencia exacta en GitHub | Interpretación y consecuencia |
|---|---|---|---|
| ARQ-01 | **P0** | `eios/core/models.py`: `PurchaseOperation` exige `article_id`, `supplier_id`, `quantity`, `unit_price`; `InputContract=PurchaseOperation`; moneda literal `EUR` | El contrato denominado «Core» contiene **semántica de compras** y no sirve sin adaptación como contrato genérico de ventas u otros casos |
| ARQ-02 | **P0** | `eios/core/execution_boundary.py`: `execute_plan(purchase_operation: PurchaseOperation, context: DecisionContext, ...)` y llamadas a invocadores con ese mismo tipo; `eios/core/orchestration.py` también importa `PurchaseOperation` | La orquestación común está tipada sobre compras. Se necesita un límite neutral y un **adaptador de compatibilidad**, sin romper el servicio actual |
| ARQ-03 | **P1** | `eios/core/mvp_execution.py`: `MVP_CAPABILITY_ORDER` fijo (QTG, PRICE, TCO, SUPPLIER_RISK_VALUE, C0, DECISION_TWIN, SCENARIO_COORDINATION, NEGOTIATION_INTELLIGENCE, NEGOTIATION_LADDER) | La secuencia de capacidades corresponde al vertical de compras. No debe imponerse como catálogo universal del núcleo |
| ARQ-04 | **P1** | `eios/parameters/local_finance_version_source.py` importa directamente `eios.company_finance_activation_guard`, `eios.company_finance_parameters` y `eios.company_parameter_bindings`; también `sqlite3` | Existe **dependencia inversa** desde una capa candidata a común hacia la aplicación. Debe moverse el adaptador específico o introducirse puerto, sin duplicar el centro de parámetros |
| ARQ-05 | **P1** | `eios/core/price_integration.py` importa `eios.pricing.*`; `eios/core/tco_integration.py` importa `eios.tco.*`; `eios/core/reference_c0_observation.py` importa `eios.rules.*`; `eios/core/reference_supplier_risk_observation.py` importa `eios.supplier.*` | El directorio físico «Core» incluye **composición de capacidades del vertical**. Estos módulos deben quedar tras adaptadores, no dentro de un futuro runtime compartido |
| ARQ-06 | **P1** | `pyproject.toml`: distribución `eios-mvp` y todos los paquetes `eios.*`; dependencia base `openpyxl` | No existe una **distribución independiente mínima** del núcleo. Requiere prueba de instalación aislada y separación de dependencias cuando proceda |
| ARQ-07 | **P2** | `eios/rules/orchestrator.py` concentra importaciones de FIN, PRICE, stock, proveedores, delivery, rotación y pagos | Composición transversal del vertical. No debe presentarse como un motor de reglas universal sin extraer sus contratos de capacidad |
| ARQ-08 | **P2** | `eios/core/reference_*_observation.py` y `eios/core/projection_mock_dataset.py` son material de observación/simulación | Los expedientes, demos y pruebas sintéticas deben quedarse como **fixtures o adaptadores**, sin formar parte de la API necesaria para cualquier aplicación |

**Hallazgo favorable:** existe una frontera de invocadores en `eios/core/execution_boundary.py` con validación previa y aislamiento de copias; también existen piezas de parametrización, evidencia, trazabilidad y quality gate que pueden servir de base. Su **portabilidad real no está acreditada** hasta comprobar tipos, dependencias transitivas, aislamiento y comportamiento en consumidores distintos.

## 3. MAPA ACTUAL Y FRONTERA OBJETIVO

```text
ACTUAL (constatado por importaciones y firmas)
eios.company_* / eios.frontend  --> eios.mvp / eios.core.*
                                               |
                                               +--> PurchaseOperation, DecisionContext
                                               +--> composition: PRICE, TCO, RULES...
eios.parameters.local_finance_version_source --> eios.company_*  [dependencia inversa]

OBJETIVO (F4.2-F4.4; NO implementado por esta auditoría)
App Compras  --> adaptador Compras --+
                                     |
App Ventas   --> adaptador Ventas  ---+--> EIOS KERNEL
                                     |    contrato de ejecución neutral,
Otro proyecto--> adaptador propio ---+    registry/capability ports,
                                          parámetros, validación,
                                          procedencia y trazabilidad

Módulos especializados: PRICE/STOCK/SUPPLIER/TCO/FIN se integran
mediante puertos y configuración explícita, no como dependencia
obligatoria de todos los proyectos.
```

### Política de dependencia propuesta

- **Kernel → contratos neutrales / bibliotecas necesarias**: permitido.
- **Vertical o aplicación → kernel**: permitido mediante puertos públicos.
- **Kernel → `company_*` / interfaz / MVP de compras / reglas específicas**: prohibido en el **núcleo extraído**.
- **Adaptador de aplicación → implementaciones concretas**: permitido, sin conceder autoridad decisional por su mera presencia.
- Toda migración debe mantener `decision_authority=False` y `operational_path=FORBIDDEN` mientras no se satisfaga la admisión operacional vigente.

**Importante:** lo anterior describe una **frontera futura**. No debe aplicarse como regla que rompa el `eios/core` físico actual: se migrará gradualmente con compatibilidad y pruebas.

## 4. INVENTARIO AUTOMÁTICO REPRODUCIBLE

Archivo incluido: `tools/audit_eios_dependencies.py`. Utiliza **solo la biblioteca estándar de Python 3.11+**: `ast` para importaciones, `tomllib` para empaquetado; no importa ni ejecuta módulos EIOS, no modifica archivos y no requiere conexión a Internet.

```powershell
cd C:\proyectos\AI-Project-Framework
python tools/audit_eios_dependencies.py
python tools/audit_eios_dependencies.py --json > f4-1-importaciones.json
python -m pytest tests/test_f4_1_dependency_audit.py -q
```

Emite inventario de archivos Python, familias, aristas internas de importación, dependencias explícitas `core/parameters → company/frontend/vertical`, composiciones `core → specialized`, módulos `core` que mencionan `PurchaseOperation` y el empaquetado declarado.

**Limitaciones de este instrumento:** los imports estáticos no muestran invocaciones por reflexión, imports construidos dinámicamente, inyección de dependencia real, side effects de importación, tamaño de distribución, compatibilidad binaria, aislamiento entre procesos, ni si una clase está conceptualmente desacoplada. Las cifras son **observaciones de sintaxis**, no una certificación de independencia. La auditoría humana de contratos, ejecución y empaquetado sigue siendo necesaria.

La suite `tests/test_f4_1_dependency_audit.py` verifica lectura estática sin ejecutar código, resolución relativa, paquetes `__init__`, detección de importaciones inversas, errores de sintaxis y ejecución del escáner sobre el repositorio real **sin congelar el número de acoplamientos** (para permitir reducirlos después).

## 5. PLAN DE REPARACIÓN MÍNIMA, SIN RECONSTRUIR EL MOTOR

| Orden | Bloque siguiente | Intervención acotada | Criterio objetivo |
|---|---|---|---|
| 1 | **F4.2 — Frontera neutral de ejecución** | Introducir contrato y puertos neutrales **junto al servicio existente**; mantener adaptador Compras sobre `run_mvp_execution` | Un consumidor que no representa una compra puede enviar entrada tipada sin crear `PurchaseOperation`; toda la regresión de compras sigue verde |
| 2 | **F4.2 — Inversión de parámetros** | Mover `local_finance_version_source` a la capa adaptadora o inyectar su proveedor, sin duplicar F2/F3 | Los módulos que integren la distribución compartida no importan `company_*` |
| 3 | **F4.3 — Distribución independiente** | Construir paquete instalable separado y dependencias opcionales del vertical | Instalación de kernel en entorno limpio, imports de su API sin Excel/UI/SQLite de la aplicación |
| 4 | **F4.4 — Doble consumidor** | Dos adaptadores mínimos (Compras y un flujo no relacionado), suites contractuales compartidas | Mismo artefacto/versionado de kernel ejecuta ambos sin parche específico al núcleo; aislamiento de empresa, entradas y políticas |

La fase 4 no debe transformarse en once unidades pequeñas si no hay fallos materiales nuevos. La prioridad es **comprobar el contrato de portabilidad**, no acumular documentación o tests redundantes.

## 6. CRITERIOS PARA CERRAR F4.1

- Inventario sobre SHA conocido y evidencias por archivo verificables.
- Riesgos **P0/P1** priorizados y responsables arquitectónicos identificados (núcleo vs adaptador).
- Herramienta de lectura y tests incorporados sin tocar el motor de negocio.
- CI completa de Python y SQL verde en HEAD de PR y en `main` postmerge.
- Prohibido declarar `core_reusable=VERIFIED`: esta unidad solo produce `reuse_architecture_audit=COMPLETE`, dejando `cross_project_portability=NOT_PROVEN`.

**El cierre F4.1 no autoriza cambios de dominio ni operaciones empresariales.**
