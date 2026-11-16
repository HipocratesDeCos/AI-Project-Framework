# EIOS — F3.7 · CONSISTENCIA DE LA EJECUCIÓN FINANCIERA DOCUMENTAL LOCAL

**Fecha:** 2026-11-16  
**Baseline:** `main @ 55ffacced4f77e547dea518416339f24dd826e29` (F3.6 cerrada y CI verde).  
**Alcance:** reparar una incoherencia de consumo documental en la aplicación local **sintética**, sin modificar `FinanceBasicInput`, el motor de cálculo ni contratos de decisión.

## 1. DISEÑAR — HALLAZGO REPRODUCIBLE

El Motor Finance Basic (`eios/finance/engine.py`) ya protege el cálculo de capital circulante: si `WorkingCapitalInput` pertenece a otra empresa, fecha o moneda, devuelve `working_capital.status=NOT_EVALUABLE` y no publica su importe.

Sin embargo, el consumidor local `execute_documentary_finance` podía **marcar la ejecución como `EXECUTED`** incluso si el documento de activo/pasivo corriente pertenecía a una empresa, fecha de corte o moneda distinta del `FinancialSnapshot`. Esto produce una lectura ambigua de un expediente financiero documental, aun cuando el módulo matemático se comporta correctamente.

Además, `parameter_configurations` se publicaba antes de validar el inventario de cobros/pagos y otros requisitos del paquete: si esos requisitos fallaban, el resultado podía devolver `NOT_EXECUTED` con una selección de configuraciones ya publicada.

**No era necesario cambiar fórmulas ni replantear el núcleo del Motor.** La frontera correcta es el consumidor documental, donde se comprueba la coherencia del conjunto entregado.

## 2. AUDITAR — CAMBIO MINIMALISTA

`eios/company_finance_execution.py`:

1. Tras validar `WorkingCapitalInput` con Pydantic, si existe se exige coincidencia exacta de `company_scope`, `as_of_date` y `currency` con el `FinancialSnapshot`.
2. Si hay contradicción, se rechaza la ejecución sin publicar `finance_result`, `finance_input`, `finance_package_fingerprint`, `parameter_version` ni `parameter_configurations`.
3. El estado de activación de parámetros `MATCHED_LOCAL_SYNTHETIC_ACTIVATION` sigue siendo una constatación independiente y **no** se presenta como identidad corporativa autenticada.
4. `parameter_configurations` solo se adjunta a la salida **después** de finalizar la ejecución financiera.
5. Si faltan datos de capital circulante (`working_capital_input=None`), se conserva el contrato preexistente de Finance Basic: la proyección puede calcularse con sus propios requisitos y el capital circulante queda `NOT_EVIDENCED`, sin inventar cifras.

## 3. DEPURAR — PRUEBAS

Se amplía `tests/test_company_finance_activation_source_guard.py` con casos de:

- Empresa ajena, fecha de corte ajena y moneda ajena en `WorkingCapitalInput`, todos rechazados y sin resultado parcial.
- Reejecución válida posterior con la documentación intacta, que conserva cálculo de capital circulante.
- Identidad duplicada de movimientos, rechazo sin lista parcial de configuraciones.
- Ausencia de capital circulante como `NOT_EVIDENCED`, sin pérdida de la proyección independiente.
- Contratos invariantes: `purchase_effect_status=NOT_EVALUATED`, `viability_status=NOT_EVALUATED`, `decision_authority=False`, `operational_path=FORBIDDEN`.

## 4. AUDITAR 2 — FRONTERAS NO ALTERADAS

La ejecución solo acepta `material_nature=SYNTHETIC` y sigue cotejando la activación local con F3.1 en la misma transacción SQLite. No se introducen nuevas versiones, fuentes autorizadas, evidencia C0, autenticación real, recálculo de QTG ni recomendación de compra. No se modifica `eios/finance/engine.py` ni `eios/finance/models.py` ni el cálculo del horizonte; tampoco las cuentas anuales del usuario, aún pendientes.

El registro local puede ser manipulado por quien controla la base SQLite. Esta unidad no cambia el límite `NOT_EXTERNALLY_AUTHENTICATED`. El inventario de cobros/pagos, su conciliación y su cobertura completa continúan siendo requisitos independientes.

## 5. CIERRE → MATERIALIZAR → CI

Aprobar únicamente con CI de Python completa y controles SQL Server (C0, Decision Versioning y Centro de Parametrización) verdes sobre HEAD de PR, revisión acotada del diff, merge controlado y CI post-merge satisfactoria sobre `main`.

**El cierre F3.7 es del comportamiento del consumidor documental sintético** y no implica que la fase 3 global esté cerrada ni que exista una empresa real operacional admitida.
