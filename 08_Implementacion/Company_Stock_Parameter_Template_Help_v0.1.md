# Ayuda de parámetros de stock en la descarga de plantillas

Al elegir «Parámetros de stock y entrega» o «Inventario» en el panel de plantillas de Carga de archivos, se ofrece un desplegable con:

- Definiciones separadas de mínimo, seguridad, punto de pedido y plazo de entrega, vinculadas a sus cabeceras.
- Ejemplo orientativo de consumo previsto de 5 unidades/día, entrega de 4 días y seguridad de 10 unidades: punto de pedido de 30 unidades. Es explicación de la pantalla; no se escribe en el CSV.
- Reglas existentes para SKU, unidad, fecha de referencia igual al corte, datos desconocidos frente a cero, parámetros no negativos y días enteros.
- Alcance actual: valores recibidos conservados para revisión, ruta para consultarlos y ausencia de activación automática de alarmas de punto de pedido o compras. Los avisos activos siguen usando el mínimo aplicado de Stock.

La ayuda no cambia cabeceras, campos requeridos, validaciones, valores recibidos ni cálculos. La plantilla sigue siendo un CSV vacío con una sola fila de cabeceras. Se oculta al elegir otros contenidos.

## Validación

Comprobación DOM del JavaScript completo: visibilidad según plantilla, cuatro definiciones, ejemplo y alcance; descarga con las siete cabeceras originales de `stock_policy`, sin filas de ejemplo. Pruebas Python existentes de perfiles/plantillas, recepción e inventario seleccionado.
