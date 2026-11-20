# EIOS Compras — Adaptador Odoo `purchase.order` (solo lectura v0.1)

**Propósito:** convertir una exportación de pedidos de compra de Odoo a una vista JSON normalizada, **sin modificar el Motor neutral ni importar automáticamente registros en EIOS**. Se trata de una primera integración externa con la aplicación empresarial.

## Uso

Con las dependencias habituales de la aplicación EIOS instaladas y desde la raíz del repositorio:

```powershell
python -m integrations.odoo.purchase_orders "C:\ruta\Pedido de compra (purchase.order) (2).xlsx" --output odoo_preview.json
python -m unittest discover -s tests -p test_odoo_purchase_orders_preview.py -v
```

El ejecutable usa `eios.company_tables.read_table`, el lector acotado que ya utiliza la recepción de empresa. No actualiza SQLite, no modifica propuestas ni activa decisiones. Guarda un JSON solo si se indica `--output`, con SHA-256 del archivo original. Código de salida 2 si hay errores de lectura/validación de negocio.

## Contrato comprobado en la exportación recibida

Campos obligatorios: ID externo, Referencia del pedido, Proveedor, Estado, Moneda/Nombre, Líneas del pedido/Referencia del pedido/Producto, Producto/Referencia interna, Líneas del pedido/Cantidad, Líneas del pedido/Precio unitario, Líneas del pedido/Subtotal y Total.

Campos opcionales: Impuestos; Fecha del pedido. Fecha ausente no se inventa. La fecha falta en los tres pedidos de la exportación analizada.

Esta versión reconoce explícitamente `SdP` como **solicitud de presupuesto**, no compra confirmada. Normaliza Euro a EUR y valida moneda y estado contra valores admitidos. Las comprobaciones de subtotal e impuestos usan Decimal y rechazan fórmulas, valores no finitos, cambios de cabecera entre líneas y duplicados ambiguos sin identificador propio de línea.

**Muestra recibida:** solo tres registros, 001, 003 y 010; 1.083,60 EUR de base y 1.311,16 EUR con IVA. La presencia de 001 confirma que no desapareció; el archivo no acredita la situación de 004–009 ni permite afirmar que los haya eliminado Odoo.

## Frontera técnica y trabajo siguiente

Se conserva `admission_status=PENDING`, `decision_authority=false` y `operational_path=FORBIDDEN`. Los cuatro paquetes neutrales 0.1.0 permanecen intactos.

El campo de proveedor es **texto**, no ID de `res.partner`; el SKU no acredita por sí mismo la identidad de la variante `product.product`. Todavía **no** hay reconciliación contra exportaciones completas de proveedores, variantes y líneas con ID externo. La coincidencia textual dentro de una fila es solo una comprobación interna, no conciliación empresarial.

Para pasar a recepción con guardado y para un futuro adaptador multi-ERP se requieren: identificador estable de línea, fecha de corte, claves de empresa, validación referencial contra maestros, estado exacto y un proceso de revisión/confirmación humana, usando los controles existentes. No inferir facturas, pagos, stock ni admisión productiva a partir de SdP.
