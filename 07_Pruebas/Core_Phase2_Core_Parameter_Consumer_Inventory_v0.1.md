# EIOS — FASE 2.2 · INVENTARIO DE CONSUMIDORES CANÓNICOS DE PARÁMETROS

**Fecha:** 16 de noviembre de 2026  
**Base de trabajo:** PR #581 · `phase2/parameter-binding-inventory-20261116 @ 52045e1`  
**Tipo de entrega:** registro técnico no autoritativo, basado en el código observado; no cambia cálculo ni configuración  
**Ámbito:** 17 relaciones de parámetros con funciones consumidoras **identificadas**, no auditoría exhaustiva de todo EIOS.

## 1. Hallazgo inicial

El repositorio contiene dos circuitos que deben permanecer distintos:

1. **Centro y reglas del Core:** `ResolvedConfiguration`, empresa, `DecisionContext.parameters_version`, instante efectivo y `Evidence` son comprobados por los consumidores autorizados de cada área. Estas funciones **ya están implementadas**, aunque ninguna entrada de este registro demuestra que una empresa determinada haya solicitado, resuelto o aplicado esos valores.
2. **Aplicación empresarial:** `eios/company_parameters.py` guarda solicitudes. La fase 2.1 ha acreditado una activación sintética local únicamente para P-FIN-001 y P-FIN-002. No existe evidencia de que todos los controles de PRICE/STK/MGE/PAG estén conectados al formulario de empresa.

Adicionalmente `eios/company_sales_negotiation.py::margin_policy`, `price_reference` y `analyze_offer` consultan los valores **preparados** de `P-MGE-001`, `P-MGE-002` y `P-MGE-004` en la aplicación comercial. `eios/company_sales_checks.py` consulta directamente `P-MGE-001`. Esa ruta **no** consume por sí sola las resoluciones y evidencias del Core MGE. `analyze_offer` declara `parameters_scope=EXPLICIT_PREPARED_VALUES_NOT_RULES_ACTIVATION`, `decision_authority=False` y `operational_path=FORBIDDEN`.

**Riesgo de producto:** trasladar esas comprobaciones comerciales a aprobaciones reales sin pasar por el Core y por una política activada de empresa podría atribuir autoridad improcedente a valores solo guardados. No se realiza tal promoción en esta unidad.

## 2. Registro físico incorporado

`eios/parameters/core_consumer_inventory.py` expone `CoreParameterConsumer`, el registro de alcance limitado `CORE_PARAMETER_CONSUMERS` y la consulta `get_core_parameter_consumers(parameter_id=None)`.

- Cada entrada especifica código de parámetro, dominio, módulo real, función consumidora, constante, tipo de relación con el cálculo y reglas descendentes identificadas.
- Todas son metadatos con estados `CORE_CONSUMER_SOURCE_IDENTIFIED` y `company_activation=NOT_ATTESTED`.
- No hay valores, umbrales, activación, cálculos, lecturas SQLite, dependencias de interfaz ni autenticación nueva.
- La ausencia de una entrada **no acredita ausencia de consumidor en otros módulos**: es un inventario deliberadamente no exhaustivo.
- Su test de regresión comprueba existencia de módulo, función y uso de la constante del parámetro mediante el AST de la función real. Eso detecta desviaciones del contrato registrado, pero **no es una prueba funcional adicional del cálculo ni una auditoría de autorización de extremo a extremo**.

## 3. Matriz del código comprobado

| Parámetro | Relación | Consumidor observado | Reglas downstream | Activación de empresa |
|---|---|---|---|---|
| P-FIN-001 | Derivada (horizonte Finance Basic) | `finance.provenance._validate_horizon_resolution` | R-FIN-001 | No inferida del Core |
| P-FIN-002 | Compuesta (tesorería mínima) | `rules.finance._treasury_minimum` | R-FIN-001 y R-FIN-003 | No inferida del Core |
| P-FIN-003 | Directa | `rules.finance._working_capital_minimum` | R-FIN-002 | No acreditada en app |
| P-FIN-004 | Directa | `rules.finance.evaluate_r_fin_003` | R-FIN-003 | No acreditada en app |
| P-PRE-001 | Directa | `rules.pricing.evaluate_r_pre_001` | R-PRE-001 | No acreditada en app |
| P-PRE-004 | Directa | `rules.pricing.evaluate_r_pre_001` | R-PRE-001 | No acreditada en app |
| P-PRE-005 | Directa | `rules.pricing.evaluate_r_pre_002` | R-PRE-002 | No acreditada en app |
| P-PRE-006 | Histórica directa | `rules.pricing._minimum_comparable_operations` | R-HIS-002 | No acreditada en app |
| P-DAT-002 | Histórica directa | `rules.pricing.evaluate_r_his_001` | R-HIS-001 | No acreditada en app |
| P-STK-004 | Directa | `rules.stock._coverage_maximum` | R-STK-002 | No acreditada en app |
| P-MGE-001 | Política compartida | `rules.profitability._resolve_policy` | R-MGE-001/002/003 | No acreditada en app |
| P-MGE-002 | Política compartida | `rules.profitability._resolve_policy` | R-MGE-001/002/003 | No acreditada en app |
| P-MGE-003 | Política compartida | `rules.profitability._resolve_policy` | R-MGE-001/002/003 | No acreditada en app |
| P-PAG-001 | Resolución del mínimo | `payment_term_minimum.resolve_minimum_payment_term` | R-PAG-002 | No acreditada en app |
| P-PAG-002 | Transformación del objetivo | `payment_term_tolerance.resolve_payment_term_tolerance` | R-PAG-001 | No acreditada en app |
| P-PAG-003 | Transformación de la tolerancia | `payment_term_tolerance.resolve_payment_term_tolerance` | R-PAG-001 | No acreditada en app |
| P-PAG-004 | Control habilitado/deshabilitado | `payment_term_control.resolve_payment_term_control` | R-PAG-001/002 | No acreditada en app |

**Matiz:** P-FIN-001/002 están activables **en el adaptador financiero local sintético** conforme a F2.1, pero su existencia en el registro del Core no certifica ningún registro de empresa ni una decisión financiera determinada.

**No se incorporan** P-STK-002, P-MGE-004 o P-PAG-005 a este conjunto, porque no se ha demostrado para esas identidades el mismo tipo de consumo canónico dentro del alcance elegido. No significa que sean inexistentes: se auditarán por su propia vía cuando proceda.

## 4. Comprobaciones de integridad por dominio

**PRICE / HIS:** `rules/pricing.py` coteja identidad de compra y contexto, versiones de parámetros, empresa, vigencia, unidades y evidencia de configuración; sus referencias calculadas pertenecen al contrato de sus reglas, no al valor estándar del catálogo.

**STOCK:** `rules/stock.py::_coverage_maximum` comprueba `company_scope`, fecha, versión, evidencia, unidad `días` y valor numérico; el resto de los parámetros y modelos STK tienen más mecanismos que deberán auditarse por separado.

**MGE:** `rules/profitability.py::_resolve_policy` reúne mínimo, objetivo y tolerancia, exige evidencia para los tres y rechaza mínimos superiores a objetivos o tolerancias negativas; no equivale al cálculo comercial directo de `company_sales_negotiation.py`.

**PAG:** `payment_term_minimum.py`, `payment_term_tolerance.py` y `payment_term_control.py` resuelven vigencia, empresa, versiones, evidencias y estados utilizables; la falta de respaldo no puede convertirse en umbral por defecto.

**FIN:** `finance/provenance.py` asegura identidad de horizonte financiero y `rules/finance.py` valida umbrales P-FIN-002/003/004 en las reglas autorizadas. La ejecución documental local solo realiza el cálculo financiero y **no ejecuta automáticamente todas esas reglas**.

## 5. Regresiones incorporadas

`tests/test_core_parameter_consumer_inventory.py` comprueba, sobre los módulos de origen:
- Los 17 códigos registrados existen en el catálogo.
- El módulo, la función y la constante de cada parámetro están presentes y la función **continúa usando esa constante**.
- Se mantienen las distinciones entre relación directa, derivada, compuesta, umbral derivado y política compartida.
- La consulta no devuelve valores de empresa, defaults ni permisos.
- Objetos y contratos del registro son inmutables.
- Se rechazan identificadores incorrectos.
- El inventario del Core no importa la aplicación ni SQLite.
- La vía comercial preparada conserva `decision_authority=False` y `operational_path=FORBIDDEN`.

## 6. Evaluación y siguiente unidad

**Resultado de F2.2:** mapa canónico de un primer conjunto de consumidores con trazabilidad a código real, reutilizable en múltiples proyectos **como metadato de arquitectura**. No es una política de empresa desplegada.

**Riesgo abierto prioritario:** antes de conectar EIOS-Sales a decisiones operacionales, su consumo de márgenes preparados deberá sustituirse o complementarse por la resolución empresarial canónica, respetando sus evidencias y estado de aprobación.

**F2.3 recomendada:** diseñar una API agnóstica de lectura y resolución de parámetros por `company_id`, `effective_at`, `parameters_version`, `Evidence` y consumidor autorizado, utilizando `ParameterConfigurationCenter` y `ResolvedConfiguration` existentes. No crear otro centro ni insertar valores por defecto. Probar dos empresas con identidades y políticas distintas y la independencia de escenarios.

**Condiciones de cierre F2.2:** CI de las pruebas nuevas y anteriores + SQL en verde en el HEAD definitivo; PR apilada, sin cambio a `main` antes de aceptar F2.1.
