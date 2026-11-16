# EIOS — F3.10 · COHERENCIA DE REFERENCIAS EXPLÍCITAS FACTURA–CUOTA–MOVIMIENTO

**Fecha:** 2026-11-16  
**Baseline auditado:** `main @ 741a5f06f5f8aa2a5378ed7a584b58fe9180b99b`, F3.9 cerrada, CI postintegración 3.372 pruebas correctas.

## 1. DISEÑAR — RIESGO Y REUTILIZACIÓN

F3.8 coteja la integridad del inventario `cash_flow`; F3.9 revisa la presencia e integridad de sus documentos de origen. Ninguna prueba exige que las referencias explícitas entre `purchase_invoice`/`sales_invoice`, `purchase_installment`/`sales_installment` y `CashFlow` correspondan a registros compatibles del mismo expediente.

**No reconstruir mecanismos existentes:**
- `eios/company_payment_matching.py`: coincidencias numéricas, no asociaciones.
- `eios/company_payment_associations.py`: declaraciones humanas de cuotas de **una propuesta**.
- `eios/core/documentary_payment_capture.py` y `eios/company_payment_review.py`: evidencias conservadas y declaraciones de revisión.
- `eios/company_sales_quality.py` / `eios/company_sales_receivables.py`: controles independientes de ventas y previsiones **recibidas** en sus propios ámbitos.

**Hueco acotado:** auditoría transversal de **referencias canónicas explícitas** de factura–cuota–flujo en la aplicación local sintética, no motor de conciliación contable nuevo.

## 2. AUDITAR — SOLUCIÓN

Módulo `eios/company_invoice_flow_links.py`, función `audit_local_invoice_installment_links`.

La comprobación se invoca **después de F3.8 y F3.9, dentro de la misma transacción SQLite**, tras verificar que el dataset de la ejecución es sintético y pertenece a la empresa/corte esperados. Lee exclusivamente las cuatro clases de registros `purchase_invoice`, `sales_invoice`, `purchase_installment`, `sales_installment` del dataset exacto.

A cada cuota solo le corresponde una factura si existe una referencia **explícita** (`invoice_id` en compras; `invoice_number` en ventas), resoluble de manera unívoca contra su cabecera. Solo se conecta a un movimiento si declara `flow_id` y este aparece en el inventario ya contrastado por F3.8. **No** se enlaza por parecido en fecha, importe, cliente o proveedor.

Se comprueba:
- Existencia y unicidad de la cabecera de factura, identidad del registro y contexto congelado en la propuesta.
- Incompatibilidad de `supplier_id`/`customer_id` o `currency` entre factura y cuota.
- Vinculación explícita a flujo y sentido adecuado (`PAYMENT` para compra, `COLLECTION` para venta).
- Coincidencia del **importe pendiente al corte** `pending_amount`/`pending`, moneda y vencimiento efectivo declarado con el `CashFlow`.
- No utilización de un mismo `flow_id` para cubrir cuotas distintas.
- Ausencia de vinculación, saldo pendiente no declarado, falta de fecha o contraparte como **comprobación incompleta**, no como relación inventada.
- Contradicciones de JSON o fila alterada desde el guardado de la propuesta como **enlace contradictorio**.

**Se prohíbe sustituir el pendiente por el importe original `amount` de la cuota.** La fecha revisada declarada tiene precedencia sobre la fecha original.

El resultado `invoice_installment_flow_links` presenta cada cuota con estados:
- `EXPLICIT_LINK_CONSISTENT_NOT_RECONCILED`: coherencia de campos declarados y del contexto local; no se certifica contenido, saldo ni pago real.
- `EXPLICIT_LINK_INCOMPLETE`: referencia o dato necesario ausente, sin inferirlo.
- `EXPLICIT_LINK_CONTRADICTED`: referencias duplicadas, ajenas, cambiadas o incompatibles.

Si no hay cuotas canónicas, el estado es `NO_RECORDED_INSTALLMENTS`, **no** cobertura completa. Se publican conteos, información de las contradicciones y huella determinista. Se mantienen `invoice_totals_reconciled=NOT_PERFORMED`, `bank_payment_reconciliation=NOT_PERFORMED`, `source_authentication=NOT_EXTERNALLY_AUTHENTICATED`, `accounting_completeness=NOT_ESTABLISHED`, `evidence_upgrade_status=NOT_PERFORMED`, `decision_authority=False`, `operational_path=FORBIDDEN`.

## 3. DEPURAR — MATRIZ DE PRUEBAS

`tests/test_company_invoice_flow_links.py` reutiliza la fixture sintética real de la aplicación y cubre:

1. Inventario sin facturas/cuotas: no inferir enlaces por mera coincidencia.
2. Compra y venta correctamente referenciadas: reporte de coherencia **no conciliada** y cálculo FIN sin cambio.
3. Pago con igual importe/fecha sin `flow_id`: enlace pendiente.
4. Cuota con importe original pero sin saldo pendiente: no asumir pendiente igual al original.
5. Factura conservada solo para otro dataset: no admitir pertenencia cruzada.
6. `flow_id` inexistente: no seleccionar el pago parecido.
7. Reutilización de un flujo en dos cuotas.
8. Sentido `PAYMENT/COLLECTION` distinto del de la cuota.
9. Proveedor/cliente incompatibles.
10. Vencimiento contradictorio.
11. Saldo pendiente contradictorio.
12. Moneda contradictoria.
13. Modificación del registro después de congelar la propuesta.
14. Factura inexistente o referencia de venta inválida.
15. Orden de presentación distinto: informe y resultado financiero estables.

## 4. AUDITAR 2 — BORDES QUE NO SE TOCAN

No se modifica ningún `CashFlow` ni el `FinanceBasicInput`, se crean cuotas nuevas, se infiere pago realizado, se añade a la proyección la compra, ni se promueve evidencia documental. Las facturas no se consideran autenticadas y no se concilian las sumas de líneas y cuotas contra el total ni se comprueban extractos bancarios.

Las cuentas anuales que se están tramitando permitirán el futuro perfil financiero histórico, pero no aportarán por sí solas los vínculos documentales de facturas y cuotas de una fecha concreta.

Esta fase **no** produce decisiones: `purchase_effect_status=NOT_EVALUATED`, `viability_status=NOT_EVALUATED`, `decision_authority=False`, `operational_path=FORBIDDEN`.

## 5. CERRAR / MATERIALIZAR / CI

Cierre condicionado a CI de Python integral y las tres validaciones SQL en el HEAD de PR, revisión de diff, merge controlado y CI postintegración de `main`.

F3.10 completa una comprobación transversal de **coherencia local de referencias**, no una conciliación sustantiva, un expediente operacional real ni el cierre total de Fase 3.
