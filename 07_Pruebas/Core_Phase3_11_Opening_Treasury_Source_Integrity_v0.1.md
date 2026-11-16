# EIOS — F3.11 · SALDO INICIAL DE TESORERÍA: INTEGRIDAD LOCAL Y FRONTERA DE CONCILIACIÓN

**Fecha:** 2026-11-16  
**Base auditada:** `main @ 442232e7cbf01c56c3050455689923e9a719b188`, F3.10 integrada con CI pre y postmerge satisfactoria.

## DISEÑAR — HALLAZGO MATERIAL

`FinanceBasicInput.snapshot.available_treasury` representa la tesorería inicial utilizada por la proyección financiera. `FinancialSnapshot` valida su estructura y exige `treasury_evidence_ref` si existe importe, pero la aplicación `execute_documentary_finance` **no cotejaba el contenido completo del snapshot recibido con la fila original `financial_snapshot` conservada en el dataset SQLite** antes de ejecutar Finance Basic. Un expediente o captura intermedia con `available_treasury` alterado podía superar empresa y fecha de corte.

El módulo de ventas ya tiene su propia **selección de cuentas 570/572**, política de cortes, reglas que rechazan sumas padre-hijos y revisión humana `company_sales_treasury.py`, `company_sales_treasury_policy.py` y `company_sales_quality.py`; no se reimplementan.

**No es válido** suponer que sumando todas las cuentas 570/572 se conoce el efectivo disponible: pueden coexistir cuentas de mayor y subcuentas, saldos indisponibles, cortes diferentes o cifras no conciliadas con el extracto bancario.

## AUDITAR — CORRECCIÓN DE CONSUMO

El nuevo `eios/company_opening_treasury_guard.py`:

1. Exige usar la misma transacción de lectura SQLite del consumidor financiero; obtiene los registros `kind='financial_snapshot'` solo del dataset esperado y exige **exactamente uno**.
2. Comprueba el tipo, identidad del registro, JSON sin claves duplicadas y `FinancialSnapshot` completo. Coteja importe, moneda, fecha, identidad, referencia y demás campos contra el snapshot recibido, bajo empresa esperada independiente del ID del dataset.
3. Verifica que `treasury_evidence_ref`, cuando exista, esté vinculada una sola vez a las referencias `source_refs` de la **fila conservada**; eso no prueba la existencia/autenticidad del justificante.
4. Si existe inventario congelado de la propuesta (`documentary_context_at_save`), exige que la huella exacta del snapshot coincida con la registrada al guardarla. Un cambio coordinado de captura + SQLite después de guardar también se rechaza.
5. Examina los registros auxiliares `treasury_balances`, `account_balance`, `bank_statement_entry`, `cash_count` del dataset sin agregarlos. Expone códigos de incidencia ante cuentas 570/572 repetidas, nivel mayor + subcuenta simultáneo y contradicciones declaradas de moneda o fecha de corte; nunca asigna `opening_treasury_reconciled=True`.
6. Genera `LocalOpeningTreasuryReceipt` de correspondencia **local sintética**, con `opening_treasury_reconciled=None`, `account_balance_reconciliation=NOT_PERFORMED`, `source_authentication=NOT_EXTERNALLY_AUTHENTICATED`, `decision_authority=False`, `operational_path=FORBIDDEN`.

El consumidor `eios/company_finance_execution.py` invoca el verificador antes de crear el paquete FIN; si falla, produce `NOT_EXECUTED` y `opening_treasury_issue` sin resultado financiero ni configuraciones parciales. Las incidencias de soportes auxiliares solo **informan**, porque no existe una conciliación ni selección autónoma de cuentas equivalente en este contrato.

## DEPURAR — SUITE

`tests/test_company_opening_treasury_guard.py` utiliza únicamente la base y la fixture sintética de Finance Activation:

- Correspondencia de snapshot y referente de origen sin atribuir conciliación bancaria.
- Importe, divisa o referencia alterados en la captura: rechazo.
- Registro SQLite modificado después de capturar: rechazo.
- Captura y SQLite modificadas conjuntamente después de guardar: rechazo por huella congelada.
- Referencia del saldo incompatible con `source_refs`: rechazo.
- Situación financiera original ausente o múltiple: rechazo.
- JSON duplicado: rechazo.
- Cuenta 572 junto con subcuenta 572001: advertencia de solapamiento, nunca suma doble.
- Cuenta 570 repetida, moneda y corte distintos: advertencias.
- Soporte del dataset de otra empresa excluido.
- Reejecución determinista y `FORBIDDEN` inalterado.

## AUDITAR 2 — LÍMITES

La correspondencia de la fila financiera **no demuestra la existencia, disponibilidad o conciliación del efectivo real**. Si SQLite y la propuesta se construyen juntos por una fuente no confiable, no hay atestación externa; una huella SHA-256 local no equivale a identidad corporativa verificada. Las cuentas anuales históricas aún pendientes ayudarán al perfil financiero, pero no certifican el saldo bancario de hoy.

Se conservan el motor matemático `eios/finance/engine.py`, el esquema SQL, los límites de QTG/Rules y los controles F2.4/F3.1–F3.10 sin cambios.

## CERRAR — CRITERIO

Esta unidad se considera cerrada técnicamente solo tras CI integral Python + SQL Server PASS en el HEAD exacto de la PR, revisión de diff, merge controlado y CI postintegración en el commit exacto de `main`.

**Ruta operacional no habilitada**. Se documenta su dependencia separada en el acta de cierre técnico de Fase 3.
