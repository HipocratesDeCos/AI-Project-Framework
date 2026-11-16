# EIOS — F3.9 · COBERTURA DOCUMENTAL DE COBROS Y PAGOS

**Fecha:** 2026-11-16  
**Base:** `main @ 5431431ae8e914a15d531afcb3b8c0151e568177` — F3.8 cerrada con CI postintegración satisfactoria.

## 1. DISEÑAR — QUÉ EXISTE Y QUÉ FALTA

No es necesario volver a construir la conciliación de cuotas que ya está delimitada por:

- `eios/company_payment_matching.py`: coincidencias de importe, moneda y fecha **no equivalen** a asociaciones.
- `eios/company_payment_associations.py`: declaraciones humanas por cuota y documento, limitadas a un contexto congelado; no autoriza la compra.
- `eios/company_payment_capture.py`: conserva las referencias y **bytes exactos** para las asociaciones declaradas.
- `eios/core/documentary_payment_review.py` y `eios/company_payment_review.py`: resultados humanos declarados sin autenticación empresarial ni promoción de evidencia.
- `eios/company_cash_flow_inventory_guard.py` (F3.8): asegura que los movimientos entregados al cálculo coincidan exactamente con los registros de la SQLite sintética.

**Hueco detectado:** F3.8 preserva las referencias `source_refs` del movimiento, pero no informa de si los documentos que identifican **siguen estando en `documentary_source`**, si sus bytes corresponden al contexto congelado de la propuesta ni si sus metadatos declarados contradicen su contenido.

Se trabaja sobre **todos los movimientos** del inventario, no solo cuotas de la nueva compra. Tampoco se presupone un modelo de asignación de facturas/bancos que todavía no existe o no está verificado.

## 2. AUDITAR — CONTRATO DE LECTURA SIN PROMOCIÓN

`eios/company_flow_documentary_coverage.py` introduce `audit_local_flow_documentary_coverage`, invocado **solo después** de F3.8 y dentro de la misma transacción de lectura SQLite, con la empresa/dataset validada previamente.

- Lee exclusivamente `documentary_source` del dataset correspondiente; la consulta no usa datos de otra empresa.
- Examina cada `source_refs[].document_ref` de cada flujo validado por F3.8.
- Distingue documento ausente, almacenamiento antiguo sin columnas documentales, referencia repetida/ambigua, bytes faltantes, metadatos inválidos, hash o tamaño incoherente, documento incorporado después de guardar la propuesta y bytes modificados después de congelar su contexto.
- Contrasta `sha256(content)` con el `stored_bytes_sha256` congelado en la propuesta; cuando el origen trae metadatos `sha256` o `bytes`, también comprueba esos valores.
- Diferencia `CashFlow.source_ref` declarado de las referencias realmente ligadas al registro; advierte cuando no aparece el enlace.
- Ordena resultados por `flow_id`; devuelve conteos, problemas, filas y huella determinista, sin incluir los bytes en el informe.

### Estados sin interpretación engañosa

- `SOURCE_BYTES_PRESENT_NOT_RECONCILED`: se localizaron los bytes y el contexto coincide. **No** indica que se hayan leído o validado importes, cuentas, factura, vencimiento o autenticidad.
- `SOURCE_LINKS_PENDING_OR_CONFLICTING`: referencias o integridad no comprobables, cambiadas, no disponibles o contradictorias.
- `documentary_content_review=NOT_PERFORMED`.
- `invoice_and_bank_reconciliation=NOT_PERFORMED`.
- `inventory_completeness=NOT_ESTABLISHED`.
- `source_authentication=NOT_EXTERNALLY_AUTHENTICATED`.
- `evidence_upgrade_status=NOT_PERFORMED`.
- `decision_authority=False`, `operational_path=FORBIDDEN`.

La salida contiene el número de flujos cuyo estado **declarado** incluye `DEMONSTRATED` o vencimiento evidenciado: esto permite advertir que tales marcas **no están autenticadas ni respaldadas por una revisión independiente** en este consumidor.

No se cambian `CashFlow.evidence_state`, `due_date_evidenced` ni los cálculos de Finance Basic. La correspondencia de bytes no permite certificar la contabilidad. La ejecución financiera sintética sigue separada de la conciliación real.

## 3. DEPURAR — PRUEBAS SINTÉTICAS

`tests/test_company_flow_documentary_coverage.py` cubre:

1. Bytes de soporte presentes y con hash coherente, pero **revisión documental todavía pendiente**.
2. Dataset de pruebas antiguo sin campos de documentos, que no se etiqueta como documentado.
3. Modificación de bytes posteriores al guardado y contradicción frente al hash/longitud de metadatos.
4. Cambio de bytes sin metadatos: se detecta contra el contexto de la propuesta.
5. Documento añadido después de guardar la propuesta (no vale como soporte congelado).
6. Documento del otro dataset (no se reutiliza como evidencia propia).
7. Reordenación de movimientos (huella y resultados estables).
8. Flujos con `DEMONSTRATED` autoconsignado: se expone la declaración, **no** se autentica ni se mejora su estado.
9. Metadatos inválidos y `source_ref` sin correspondencia con las referencias del flujo.

Las suites existentes continúan verificando F3.8, el circuito de cuotas y la preservación de los documentos capturados.

## 4. AUDITAR 2 — LÍMITES Y RELACIÓN CON EL FUTURO PILOTO

Esta unidad es la **comprobación de presencia e integridad local de referencias documentales**. No constituye conciliación sustantiva de facturas con cobros/pagos: no verifica la procedencia fiscal de una factura, el extracto bancario, el vencimiento contractual, la identidad del acreedor ni la existencia de otras obligaciones no registradas.

Los contenidos descargados del Registro Mercantil pueden servir para el **análisis financiero histórico** cuando lleguen, pero no suplen extractos, facturas y vencimientos reales. No se han inventado documentos empresariales ni autoridades de firma.

No se modifica `eios/finance/engine.py`, PRICE, Rules, QTG, el centro de parámetros, el SQL Server canónico ni la interfaz.

## 5. CERRAR → MATERIALIZAR → CI

Cierre técnico condicionado a CI Python+SQL completa con SHA exacto, auditoría de diff, merge controlado y CI postintegración sobre `main`.

F3.9 **no** habilita ejecución operacional ni cierra la fase 3 global: `operational_path=FORBIDDEN` permanece.
