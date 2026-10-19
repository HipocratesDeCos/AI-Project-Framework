# Recepción asistida de archivos de empresa v0.1

La pantalla **Carga de archivos** permite recibir documentación de una empresa distinta de A Monkey, sin preparar previamente un ZIP ni modificar los nombres de sus columnas.

## Uso

1. Indicar código de empresa, razón social, naturaleza REAL o SYNTHETIC y fecha de corte. Para inventarios o saldos, esa fecha es la fecha de referencia declarada.
2. Seleccionar XLSX, CSV o PDF. En Excel, escoger hoja y fila de cabecera; en CSV, revisar codificación y separador. Pulsar **Leer archivo** después de cambiar estas opciones.
3. Seleccionar el contenido de la tabla y relacionar sus columnas con los campos de EIOS. Se muestran las primeras filas originales para comprobar la correspondencia.
4. Elegir formato numérico español o internacional y pulsar **Comprobar datos**. Revisar registros normalizados, errores y avisos. Si hay errores, no se permite guardar ninguna fila del archivo.
5. Pulsar **Guardar en expediente**. El archivo y los registros quedan disponibles en **Expedientes recibidos**, con empresa, corte, hoja, fila de origen y huella del archivo. Repetir la misma recepción no la duplica.

## Tablas admitidas

| Contenido | Campos obligatorios |
|---|---|
| Proveedores | Código, razón social |
| Clientes | Código, razón social |
| Artículos | SKU, descripción, unidad |
| Inventario | SKU, unidad, existencias físicas |
| Líneas de facturas de compra sin abonos | Factura, fecha, proveedor, SKU, cantidad, unidad, importe neto de línea y moneda |
| Previsión de cobros y pagos | Referencia, COBRO/PAGO, importe, moneda y vencimiento |
| Saldos contables | Código de cuenta, saldo con signo y moneda |
| PDF de soporte | Archivo y contexto de empresa; no se extraen cifras |

Los códigos numéricos de Excel se rechazan para evitar perder ceros iniciales; deben aportarse como texto. Las fórmulas y errores de Excel en columnas mapeadas requieren revisión y valores fijos. No se utilizan resultados de cálculo en caché. Las fechas de texto admitidas son AAAA-MM-DD o DD/MM/AAAA; las fechas nativas de Excel se conservan como fechas ISO. El formato numérico declarado controla los separadores de texto sin adivinarlos.

No se considera cero una reserva desconocida. El disponible sólo se calcula cuando se aportan físico y reservado. Las fechas de inventario/saldo, si se mapean, deben coincidir con el corte declarado. Las facturas posteriores al corte se rechazan; los vencimientos futuros de cobros/pagos son válidos. Los saldos negativos se conservan. No se consolidan líneas de compra ni se deduplican entre archivos distintos; las relaciones y posibles solapamientos entre archivos quedan para la admisión.

## Frontera de recepción

`CompanyReception` conserva el original, su SHA-256, contexto, mapeo, registros y procedencia en `received_company` y `received_company_batch`. Estos datos mantienen `admission_status=PENDING`, `operational_path=FORBIDDEN` y `decision_authority=false`. REAL no se transforma en SYNTHETIC. La recepción no crea un caso operacional admitido, un FinancialSnapshot ni evidencias demostradas.

Los expedientes recibidos se consultan en su propia sección; no aparecen automáticamente como empresa activa en Propuestas ni se mezclan con los datasets documentales sintéticos. La integración de un expediente admitido en los motores y el decisor es trabajo posterior. Tampoco se ejecuta OCR ni extracción de tablas PDF. Se conserva el PDF como soporte con aviso de extracción/verificación pendiente.

## Transporte y validación

`POST /api/reception/read` recibe el archivo; `preview` valida mapeo/contexto; `commit` guarda sólo una revisión válida ligada a un ticket. La sesión local, Host y límites de cuerpo se comprueban en el servidor. Los tickets son aleatorios, caducan y se invalidan al cambiar de archivo o revisión. Las vistas pendientes se invalidan también al modificar campos en el navegador.

Se admiten hasta 10 MiB, 5.000 filas de datos y 80 columnas por tabla. XLSX se lee con openpyxl, sin ejecutar fórmulas ni conservar enlaces externos; se limitan tamaño expandido y miembros y se rechazan macros y declaraciones XML no admitidas. XLS y XLSM deben convertirse a XLSX. Los originales no se modifican ni se escriben utilizando rutas aportadas por el archivo. La vista muestra hasta 20 registros y 100 errores/avisos, con sus cantidades totales. Se conservan todos los registros válidos del archivo cuando no hay errores.

El uso de Excel requiere actualizar las dependencias del proyecto: `python -m pip install -e .`.

## Verificación

Pruebas de números por convención, fechas, fórmulas, ceros iniciales, cabeceras desplazadas, reservas desconocidas, códigos duplicados, límites, XML no admitido, recepción REAL sin promoción, idempotencia, identidad de empresa, PDF de soporte y caducidad. La prueba DOM/HTTP carga CSV y XLSX de otra empresa, mapea columnas, bloquea una fórmula, guarda los expedientes y comprueba que la empresa activa original mantiene 18 artículos y 6 proveedores. La prueba DOM no acredita el aspecto visual exacto del navegador.
