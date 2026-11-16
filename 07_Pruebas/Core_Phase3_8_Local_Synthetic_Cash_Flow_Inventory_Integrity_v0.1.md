# EIOS — F3.8 · INTEGRIDAD DEL INVENTARIO DE COBROS Y PAGOS

**Fecha:** 2026-11-16  
**Base:** `main @ d3511cc585d20064f308f9e6cb193327fbb7d28e`, F3.7 integrada y CI satisfactoria.  
**Objetivo:** garantizar que el consumidor financiero local procesa exactamente los movimientos sintéticos conservados en su dataset SQLite, sin admitir importes, vencimientos, estados de evidencia o referencias modificados por una captura intermediaria. No inventa conciliación contable.

## 1. DISEÑAR — RIESGO MATERIAL IDENTIFICADO

`financial_context` obtiene de `CompanyDataStore.records(dataset, "cash_flow")` una lista de movimientos canónicos que la aplicación transmite a `execute_documentary_finance`.

Hasta esta unidad, el consumidor verificaba el número indicado por `documentary["record_counts"]["cash_flow"]`, la identidad `flow_id`/`record_id` y la ausencia de identificadores duplicados, **pero no comprobaba que esos importes, fechas, monedas, tipos de flujo, estado de evidencia y referencias documentales coincidieran con `documentary_company_record`**. La captura entregada y sus contadores podían modificarse conjuntamente manteniendo una lista estructuralmente válida. Tampoco se rechazaban cambios de filas persistidas posteriores a capturar el contexto.

La ausencia de conciliación entre facturas, bancos y caja es otra frontera; no se puede concluir completitud contable por haber cotejado las filas de una SQLite editable.

## 2. AUDITAR — CONTRATO MINIMALISTA

Se introduce `eios/company_cash_flow_inventory_guard.py`: `verify_local_cash_flow_inventory(connection, dataset_id, recorded_count, captured_flows)`.

- Exige la **transacción de lectura SQLite ya abierta** por el consumidor tras comprobar el dataset sintético y la activación de parámetros F3.1; no abre otro almacén ni consulta una lista externa.
- Lee las filas `kind='cash_flow'` del dataset exacto con consulta parametrizada. Exige simultáneamente que `len(filas persistidas) = recorded_count = len(captura)\`, sin tomar el contador facilitado por la aplicación como autoridad.
- Verifica `record_json.kind`, `record_id` y `CashFlow.flow_id`; rechaza JSON con claves duplicadas, formatos no canónicos y referencias de origen malformadas.
- Valida y compara **cada `CashFlow` completo** con el registro original mediante el modelo canónico `CashFlow`: tipo, importe, moneda, vencimiento, fecha evidenciada, `source_ref`, `evidence_state`; exige también igualdad completa de `source_refs` y conjunto exacto de identificadores.
- Rechaza cambios, ausencias, elementos adicionales, duplicados, claves de origen distintas y movimientos sin registro. Acepta distinto **orden de presentación** siempre que el conjunto y contenido sean exactamente iguales.
- Genera una huella SHA-256 determinista de la selección de registros **por identidad, contenido y referencias documentales**, para cotejo local, no como certificado ni autenticación de origen.
- Devuelve `LocalCashFlowInventoryReceipt` inmutable con `status=MATCHED_RECORDED_LOCAL_FLOWS_NOT_RECONCILED`, `source_authentication=NOT_EXTERNALLY_AUTHENTICATED`, `inventory_completeness=NOT_ESTABLISHED`, `decision_authority=False`, `operational_path=FORBIDDEN`.

`eios/company_finance_execution.py` llama obligatoriamente al verificador **antes de construir el paquete financiero**, en la misma transacción y usando exclusivamente las filas comprobadas. Si hay contradicción, publica `status=NOT_EXECUTED`, `cash_flow_inventory_status=REJECTED`, un código `cash_flow_inventory_issue` y **ningún `finance_result`, `finance_input` ni configuraciones parciales**.

Si coincide el inventario, identifica la comprobación como correspondencia **local**, no como conciliación de todos los movimientos empresariales.

## 3. DEPURAR — CASOS DE PRUEBA

Se amplía `tests/test_company_finance_activation_source_guard.py` para verificar:

1. Captura fiel: ejecución financiera local conservada, sin decisión ni promoción de evidencias.
2. Alteración de **importe, vencimiento, moneda, tipo, origen y estado de evidencia** manteniendo idénticos el número de filas y sus identificadores.
3. Alteración de `source_refs` sin alterar `CashFlow`.
4. Modificación posterior del registro persistido; eliminación de una fila después de capturar el contexto.
5. Aparición de un movimiento no contemplado en la captura original.
6. Mismo conjunto con otro orden: sin falsos positivos y con fingerprint estable.
7. Duplicado o fila externa manteniendo la longitud declarada.

La suite existente continúa cubriendo F3.1, F3.7, precondiciones, datos no sintéticos y estados no evaluables.

## 4. AUDITAR 2 — LO QUE NO SE DECLARA

**No se acredita la completitud de los cobros/pagos reales**, porque una fila omitida tanto de la captura como de la SQLite no se detecta sin comparar con otras fuentes independientes. Tampoco se atestigua que `evidence_state=DEMONSTRATED` tenga realmente un justificante válido: solo se preserva fielmente el estado de la fuente conservada. Tampoco se detecta que dos movimientos diferentes representen la misma obligación económica sin revisar sus documentos de soporte.

El motor `eios/finance/engine.py` mantiene su semántica: información no evidenciada produce estado no evidenciado, sin calcular capacidad financiera completa. No se modifican reglas decisionales, QTG, PRICE, SQL Server, interfaz ni fórmulas, ni se habilita la vía operacional.

**Límite constante:** solo SQLite sintético, `source_authentication=NOT_EXTERNALLY_AUTHENTICATED`, `decision_authority=False`, `operational_path=FORBIDDEN`.

## 5. CERRAR → MATERIALIZAR → CI

F3.8 se considerará cerrada únicamente con CI Python completa + validaciones SQL verdes en SHA exacto de la PR, diff acotado, merge controlado y CI postintegración en `main`.

La conciliación real del inventario contra extractos bancarios, facturas y obligaciones, así como la admisión documental empresarial y autenticación del emisor, quedan expresamente fuera de esta unidad y **no** se suplirán inventando registros.
