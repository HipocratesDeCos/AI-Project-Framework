# Pantalla local de empresa y entrada de compras

Desde PowerShell, en la raíz del repositorio actualizado:

```powershell
python -m eios.company_app --db "C:\ruta\a_monkey_documentary.sqlite3"
```

Abrir http://127.0.0.1:8765 en el navegador. Mantener PowerShell abierto; Ctrl+C detiene la pantalla. No requiere instalar librerías adicionales a las del proyecto.

La base es el archivo SQLite extraído del paquete de carga documental. También puede prepararse con `python -m eios.company_data load` siguiendo la guía del adaptador.

La pantalla muestra empresa, versión y fecha de corte, documentos y datos pendientes. El formulario permite seleccionar proveedor y artículo, escribir referencia, cantidad en la unidad documentada, precio unitario, IVA, fecha del pedido y vencimiento. Todos los importes deben introducirse explícitamente.

Guardar crea una propuesta sintética persistente PENDIENTE_DE_EVALUACION. El servidor valida proveedor/artículo, fechas, importes y referencias repetidas por versión. Las propuestas aparecen al reabrir y están separadas por dataset. Se guardan en la misma base, tabla manual_purchase_proposal; al trasladar el trabajo, conservar esa base actualizada.

Esta pantalla no ejecuta todavía los motores de evaluación. No emite pedidos, ni cambia stock, tesorería, documentos originales o autoridad decisional. No infiere demanda ni ofertas vigentes de facturas históricas. La ruta operacional sigue FORBIDDEN.

Validación: pruebas de persistencia, aislamiento entre versiones, cálculo de importes, datos inválidos y duplicados. Pantalla HTML servida localmente con API limitada a loopback y token de sesión para escritura; datos mostrados mediante textContent.
