# Revisión de referencias del expediente recibido

En **Carga de archivos → Expedientes recibidos**, marcar expresamente los archivos que se desea cruzar y pulsar **Comprobar expediente seleccionado**. Se admiten hasta 100 archivos de una sola empresa, naturaleza de datos y fecha de corte. Las versiones alternativas no se seleccionan ni sustituyen automáticamente.

La comprobación lee todos los registros conservados, no solo los veinte de la vista previa. Comprueba:

- Referencias de artículos a proveedores; compras a proveedor y artículo; ventas a cliente y artículo; inventario y parámetros a artículo.
- Coincidencia exacta de las unidades documentadas con el catálogo. No convierte palets, cajas o unidades automáticamente.
- IDs repetidos o contradictorios entre catálogos; líneas de factura idénticas; fecha o moneda contradictorias dentro de una misma factura y contraparte.
- Valores incompatibles de existencias o parámetros para el mismo artículo y unidad. Los números equivalentes se comparan como decimales.

Cada incidencia muestra archivo, hoja, fila, campo y origen relacionado cuando exista. Una referencia ausente puede deberse a que no se seleccionó el catálogo correspondiente. No se deducen IDs por descripción, ni se impone que un artículo solo pueda comprarse a su proveedor habitual.

El resultado se limita a los archivos seleccionados. Un resultado sin conflictos no acredita que se haya aportado toda la documentación, ni concilia balances, tesorería, impuestos, totales de facturas o cifras de PDFs. Los archivos fuera de ese alcance y los avisos de recepción se identifican expresamente. El identificador de revisión deriva del conjunto de lotes inmutables seleccionado.

La operación es de lectura: no altera los archivos ni sus datos, no carga la empresa activa, no modifica propuestas y mantiene `PENDING`, `FORBIDDEN`, `decision_authority=false`. La revisión no admite automáticamente documentación real ni sintética para decisiones.
