# EIOS — FASE 2 · INVENTARIO DE PARAMETRIZACIÓN EFECTIVA v0.1

**Fecha:** 2026-11-16  
**Baseline:** `main @ 2c2807c9337fd70efd8e8a02ea3516386898e972`  
**Unidad:** F2.1 / separación entre definición, conexión y activación empresarial  
**Naturaleza:** auditoría basada en código + indicador de solo lectura; sin activar parámetros ni modificar motores decisionales.

## 1. Hallazgo técnico

El catálogo empresarial en `eios/company_parameters.py` declara todas sus filas con `consumer_status='PENDING_ENGINE_BINDING'` por diseño. Los valores del campo `standard` son **orientativos documentales**; no deben hacerse pasar por valores activos.

Sin embargo, existe ya una conexión **física y acotada**:

1. `eios/company_finance_parameters.py` activa expresamente las configuraciones `P-FIN-001` y `P-FIN-002` para **una empresa, dataset y fecha de corte sintéticos**. La activación es versionada, de vigencia diaria y con historial.
2. `eios/company_finance_execution.py::execute_documentary_finance` obtiene ambas configuraciones del `ParameterConfigurationCenter`, construye `FinanceBasicInput` con `horizon_days` y `treasury_minimum`, y realiza la ejecución mediante `build_finance_decision_input_package` y `run_provenanced_finance_basic`.
3. `eios/finance/provenance.py` obliga a que `P-FIN-001` y `FinanceBasicInput.horizon_days` coincidan en empresa, fecha, unidad y versión.
4. `eios/rules/finance.py` valida `P-FIN-002` por su resolución y evidencia antes de usarlo en reglas autorizadas. **La ejecución documental local no significa que esas reglas o QTG se hayan ejecutado.**

Por tanto, el estado `PENDING_ENGINE_BINDING` de todo el catálogo empresarial no distingue lo técnicamente conectado de lo **realmente activado para el corte**.

**No confundir** esta constatación con ausencia general de consumidores EIOS: `04_Reglas/Rule_Dependency_Matrix.md` y las reglas PRE/STK/MGE/FIN describen otros consumidores físicos o documentales, que no equivalen a su activación en `company_app`. Esta primera unidad evalúa exclusivamente el **adaptador empresarial local**.

## 2. Contrato materializado

`eios/parameters/company_binding_report.py` ofrece:

`describe_company_parameter_bindings(catalogue, activation, company_id, dataset_id, as_of_date, current_revision)`

Produce un estado de **solo lectura**, accesible a través de la nueva clave `read_parameters(...)["parameter_binding_report"]`. No modifica `CATALOGUE`, `BY_ID`, el esquema SQLite, valores, configuración, algoritmo, PR, QTG ni permisos.

Para cada parámetro:

| Situación | Estado |
|---|---|
| Existe en el catálogo empresarial pero no hay ruta local de consumo verificada en esta unidad | `PENDING_COMPANY_CONSUMER` |
| P-FIN-001/002 tienen una ruta local demostrada, pero no hay activación explícita | `AVAILABLE_NOT_ACTIVATED` |
| P-FIN-001/002 activados, con registro y contexto de corte consistentes | `ACTIVE_LOCAL_SYNTHETIC_AT_CUTOFF` |
| Existe activación anterior y después se guardó una revisión distinta, sin sobrescribir la anterior | `ACTIVE_LOCAL_SYNTHETIC_PRIOR_REQUEST` |
| Se encuentra un registro de activación cuyo contenido no pasa comprobaciones de integridad | `ACTIVATION_RECORD_UNVERIFIED` |

El informe aporta consumidor físico, valor **solo cuando ha sido activado y cotejado**, y huella del registro cuando corresponde. No reutiliza el campo `standard` como fallback.

La comprobación de consistencia revisa el alcance empresarial, dataset, fecha de corte, naturaleza sintética, autoridad siempre falsa, hash de contenido, dos configuraciones únicas, sus unidades, tipos, valores, vigencia y revisión declarada.

**Advertencia:** el SHA-256 del registro confirma consistencia local, NO acredita origen externo ni impide que un actor con permisos de escritura en SQLite sustituya valores y recalcule la huella. No es autenticación multiempresa ni prueba de calidad de fuentes.

## 3. Inventario de consumidores — corte de la primera unidad

| Parámetro | Evidencia de consumidor local | Estado de la conexión en el adaptador empresarial |
|---|---|---|
| `P-FIN-001` | `execute_documentary_finance` → `FinanceBasicInput.horizon_days` → `run_provenanced_finance_basic` | **Conectado, activación expresa y sintética** |
| `P-FIN-002` | `execute_documentary_finance` → `FinanceBasicInput.treasury_minimum` | **Conectado, activación expresa y sintética** |
| `P-FIN-003/004` | Reglas financieras del núcleo, según sus contratos individuales | **Conexión al formulario empresarial no demostrada en esta unidad** |
| `P-PRE-*` | Matriz de dependencias y reglas PRE del núcleo | **Conexión al formulario empresarial no demostrada en esta unidad** |
| `P-STK-*` | Modelos de stock y reglas específicas | **Conexión al formulario empresarial no demostrada en esta unidad** |
| `P-MGE-*`, `P-PAG-*`, otros | Contratos y reglas especializados | **Conexión al formulario empresarial no demostrada en esta unidad** |

**No se clasifica aquí como funcional ni inoperativo un consumidor del núcleo que no se haya auditado por su propia frontera.** `PENDING_COMPANY_CONSUMER` significa solo *conexión local no acreditada*, no inexistencia global de código.

## 4. Pruebas de regresión

`tests/test_company_parameter_binding_report.py` verifica:
- guardar valores no equivale a activarlos;
- activación explícita da estado/vigencia/valor y huella de registro;
- aislamiento entre dos empresas sintéticas;
- una revisión posterior no altera los valores activados anteriores;
- manipular el registro rompe la consistencia y no permite mostrarlo como activo;
- identidad de dataset y fecha de corte no se mezclan;
- rechaza catálogo duplicado o revisión de tipo incorrecto;
- no muta el catálogo ni emite autoridad decisional.

## 5. Próximos pasos de la fase 2

1. Verificar CI de F2.1 en la rama de revisión (sin fusionar automáticamente).
2. Auditar parametrización y consumidores del resto de grupos por contratos individuales, usando la RDM existente: no duplicar relaciones ya cerradas ni implantar valores iniciales como política.
3. Diseñar una API de consulta de parámetros **canónicos** desacoplada de la aplicación, con empresa, vigencia, versión y evidencia, consumible por otros proyectos.
4. Probar dos perfiles de empresa con valores distintos y ejecutar el mismo escenario bajo cada configuración sin contaminar el contexto.
5. Dejar la integración en `main` sujeta a CI, auditoría y aprobación.

**No autoriza operaciones reales, no activa parámetros adicionales ni cierra la fase 2 completa.**
