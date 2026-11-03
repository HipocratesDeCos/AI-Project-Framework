# EIOS · Espacio de compras v0.1

Primera implementación del rediseño acordado: identidad del proveedor y artículo en una cinta compacta, seguida de cantidad, disponible, reservas, referencia de precio y cobertura. Las cintas permanecen visibles durante el recorrido de su formulario o revisión. Los importes destacan y el precio indica euros bajo la cifra.

La entrada se distribuye en cuatro pestañas que conservan los campos anteriores: proveedor/artículo, condiciones, cuotas/portes y guardar/documentos. Los detalles de artículo e historial quedan desplegables. El acceso «Ver stock, demanda y fuentes» los abre. La orientación de tesorería ocupa la columna lateral.

El descuento se edita mediante las modalidades comerciales existentes. Cambiar desde precio neto pide introducir el precio antes de descuentos; no reutiliza automáticamente un neto como precio bruto.

La revisión compara propuesta original, mi propuesta y respuesta del proveedor, con origen y referencia propios. Conserva el historial mediante el contrato existente, sin modificar el original. La cantidad y proveedor siguen siendo los mismos en una comparación. El calendario alternativo editable corresponde a «Mi propuesta»; la respuesta conserva el calendario original y puede requerir completar el estudio si cambia su importe.

No se calcula rotación a partir del stock. La cobertura solo muestra el resultado FINITE del motor existente cuando coinciden fecha y unidad del inventario; sin datos compatibles se indica pendiente. Disponible y reservado proceden de inventario documental. El precio de referencia exige una última compra única comparable. Las propuestas nuevas conservan descripción y referencia de precio al guardar; las antiguas sin esos campos no reconstruyen datos con el catálogo actual.

## Validación

- Suite completa del proyecto: 2.966 pruebas superadas antes de añadir dos casos de conservación documental.
- Pruebas específicas: persistencia de identidad y precio, ausencia de referencia cuando los últimos precios son ambiguos, comparación y totales.
- Navegador Chromium real: pestañas, activación explícita del descuento, total con IVA, guardado, dos alternativas y sus importes, cintas persistentes, independencia entre borrador y estudio, historial y anchura de 900 px.
- Datos sintéticos aislados: no se modifica la base de la empresa.

Esta entrega requiere revisión visual del usuario antes de integrar. No cambia decisiones financieras, saldos contables ni la autoridad de aceptación de ofertas.
