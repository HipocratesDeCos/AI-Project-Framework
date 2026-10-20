# Aceptación integrada del circuito de recepción

Prueba reproducible: `tests/test_company_reception_workflow.py`.

Ejecutar desde la raíz del repositorio:

```powershell
python -m unittest tests.test_company_reception_workflow -v
```

La prueba inicia la aplicación local en un puerto libre, utiliza sus endpoints HTTP reales y cierra el servidor al terminar. Toda la ejecución usa una SQLite temporal aislada; no abre ni modifica la base de A Monkey ni una instalación de cliente.

## Caso ficticio

Se reciben diez archivos sintéticos mediante lectura, mapeo, vista previa y guardado: proveedores, clientes, artículos, líneas de compra, inventario, parámetros de stock, líneas de venta, cobros/pagos, saldos y PDF de soporte. Contienen quince filas normalizadas. Los CSV se generan solo como fixtures de prueba y el PDF mínimo sirve exclusivamente para verificar conservación, sin extracción.

La primera selección incluye un error deliberado: inventario en palets para un artículo documentado en unidades. La comprobación debe señalarlo y la consulta del artículo debe abstenerse de mostrar existencias únicas. Esta selección se guarda como una versión pendiente de admisión.

Después se recibe un inventario corregido, se selecciona en lugar del anterior y se guarda una segunda versión. La primera se conserva. La consulta debe mostrar:

| Dato | Resultado esperado |
|---|---:|
| Último importe neto de línea | 5.140,00 EUR |
| Cantidad de la última línea | 40 uds |
| Precio neto efectivo | 128,50 EUR/ud |
| Existencias físicas | 75 uds |
| Reservadas | 15 uds |
| Disponibles | 60 uds |
| Líneas de venta consultables | 2 |

Los cobros/pagos se consultan separados por moneda, sentido y vencimiento. Los saldos se mantienen por cuenta, sin inferir liquidez ni capacidad de compra. Los avisos fuera del alcance de conciliación financiera permanecen aunque se corrija la unidad del inventario.

## Comprobaciones del recorrido

- Recepción HTTP de diez originales, mapeos explícitos, estado y recuentos de cobertura.
- Revisión de referencias y bloqueo de resumen de stock ante unidades incompatibles.
- Consulta de precio/cantidad, existencias, parámetros, historial de ventas y datos financieros.
- Búsqueda de una factura conservando su fila de origen.
- Guardado y reapertura de la selección corregida; guardado repetido idempotente.
- Comparación de versiones: un lote incorporado, uno retirado y nueve compartidos.
- ZIP final con diez originales, índice, manifiesto y comprobación guardada. Los bytes y hashes de cada original coinciden con los recibidos; el inventario antiguo no aparece en ese ZIP.
- La base conserva once lotes y dos versiones. El número de datasets activos y propuestas de compra permanece en cero.
- Una petición de guardado sin token de sesión se rechaza.

## Resultado y límite de la aceptación

El caso valida el circuito de recepción y consulta de extremo a extremo, a través de la API HTTP. Complementa las pruebas de pantalla con jsdom y las pruebas unitarias existentes; no sustituye una revisión visual en un navegador real ni un piloto con datos de cliente.

No acredita conciliación contable, previsión de liquidez, conexión automática de los archivos recibidos con un dataset activo ni evaluación operacional. Mantiene `PENDING`, `FORBIDDEN`, `decision_authority=false`. No reabre contratos C0/Rules ni modifica reglas de precio, stock o finanzas.
