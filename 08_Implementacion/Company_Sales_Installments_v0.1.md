# Ventas ampliadas y vencimientos de cobro

## Recorrido desde Carga de archivos

1. Descarga la plantilla de ventas históricas y la de vencimientos de venta. Son CSV compatibles con Excel y Google Sheets, no documentos de Google creados automáticamente.
2. En ventas conserva una fila por artículo de factura. Puedes declarar descripción, número de línea, precio unitario antes de descuento, descuento porcentual y/o importe de descuento de línea, IVA porcentual y/o importe documentado, y total documentado de factura con IVA.
3. El neto ya contiene el descuento: EIOS no lo resta de nuevo. Porcentaje e importe representan el mismo descuento. No se admiten descuentos sucesivos mediante esos dos campos. El IVA calculado desde un tipo declarado se identifica como calculado.
4. En vencimientos conserva una fila por cuota, sin límite fijo de tres. Aporta referencia única, cliente, factura, número de cuota, fecha, importe original con IVA, moneda y forma de cobro. Declara el pendiente al corte expresamente; cero significa cobrada. Si ya existe una previsión, indica su referencia de cobro.
5. Recibe y guarda ambas tablas con la misma empresa, naturaleza y fecha de corte. Si están en hojas del mismo Excel, lee y guarda cada hoja por separado. Incluye las previsiones existentes que quieras contrastar.
6. Marca los archivos en Expedientes recibidos y pulsa **Conciliar ventas, cuotas y cobros marcados**. No marques maestros u otros tipos en esta comprobación específica.
7. Revisa el detalle por factura. Deben coincidir cliente, factura y moneda. La suma de netos e IVA y la suma de cuotas originales se contrastan con un total de factura documentado único. Repetir el mismo total en varias líneas no lo suma varias veces. Los portes u otros conceptos deben estar representados para cuadrar; no se inventan.
8. Tras confirmar la revisión, descarga el CSV de cobros nuevos. Solo incluye pendientes de facturas completamente conciliadas. Recíbelo después como **Previsión de cobros y pagos** con las columnas de vínculo y formato numérico EN (decimal con punto).

## Controles y límites

- Tolerancia monetaria de un céntimo; sin IVA predeterminado, pendientes supuestos ni total documental deducido de líneas parciales.
- Los ficheros anteriores de ventas y previsiones siguen siendo válidos; campos opcionales no mapeados no alteran sus registros ni fingerprints.
- Detecta números de línea/cuota y referencias duplicados entre archivos seleccionados, monedas y fechas contradictorias, referencias de cobro reutilizadas y discrepancias con cobros existentes.
- Un cobro vinculado y compatible se excluye de la descarga. Una coincidencia no vinculada en fecha, moneda e importe bloquea la factura para revisión; no se asigna automáticamente. Solo pueden comprobarse los cobros documentales del mismo expediente/corte y las previsiones recibidas que se seleccionen, no archivos omitidos o datos externos.
- Identificadores de cobro estables permiten reconocer una descarga anterior al volver a incluirla en la selección. Seleccionar dos copias del mismo cobro exige resolver su duplicidad.
- Máximo 100 archivos y 20.000 filas combinadas; descarga hasta 5.000 cobros para poder recibirla mediante el lector ordinario. Caducidad de preparación: diez minutos, un solo uso y nueva comprobación de integridad antes de descargar.
- No cambia históricos comerciales activos, facturas, stock, caja/bancos, cobros contables ni motores financieros. Recepción y descarga mantienen `decision_authority=false` y `operational_path=FORBIDDEN`. La recepción posterior sigue pendiente de admisión y activación explícitas.
