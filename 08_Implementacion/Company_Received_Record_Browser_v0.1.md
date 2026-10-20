# Consulta completa de filas recibidas

En **Carga de archivos → Expedientes recibidos**, pulsar **Ver datos** en un archivo Excel o CSV para consultar todos los registros normalizados guardados. La vista de archivo deja de limitarse a las veinte filas de la vista previa de recepción; esa vista previa anterior al guardado mantiene su límite y función.

La consulta muestra cincuenta filas por página, botones **Anterior/Siguiente**, rango visible, número de coincidencias y total de filas del archivo. La columna **Fila de origen** conserva la referencia exacta de la hoja/CSV, aunque haya cabeceras o filas vacías. Los códigos con ceros iniciales y los datos guardados no se modifican.

**Buscar** o la tecla Enter filtran todas las filas guardadas, no solo la página visible. **Limpiar búsqueda** vuelve a la primera página del archivo completo. La búsqueda:

- Es una coincidencia de texto parcial sobre valores y número de fila, no sobre nombres de columnas.
- No distingue mayúsculas ni acentos.
- Admite tanto el punto como la coma decimal en los valores numéricos guardados.
- No calcula equivalencias económicas, reformatea códigos, modifica importes ni consulta otros archivos.

Editar la búsqueda limpia el resultado anterior y exige pulsar Buscar/Enter. Hasta la respuesta nueva se desactivan los botones de paginación. Abrir otro archivo o cambiar el contexto invalida respuestas pendientes y evita mostrar datos del archivo anterior.

Los PDF siguen siendo soporte sin extracción de filas ni búsqueda de texto. Su detalle lo indica expresamente y desactiva los controles de búsqueda. La descarga del original permanece disponible.

## Datos y alcance

Se lee `received_company_batch.records_json`, vinculado a empresa y lote. Se muestran las etiquetas de los campos mapeados, nombre/hoja de origen, huella y corte. Los totales se calculan a partir de las filas conservadas, no de `preview` ni de su recuento de metadatos.

Es una operación de lectura. No modifica documentos, mapeos, registros, versiones, propuestas o empresa activa y mantiene `PENDING`, `FORBIDDEN` y `decision_authority=false`. No admite documentación ni concilia datos. Los paquetes ZIP de la empresa activa continúan en sus pantallas actuales.

## API

`POST /api/reception/records`, protegido por Host local y token de sesión:

- `company_id`, `batch_id`: deben identificar un lote existente de esa empresa.
- `offset`: entero no negativo; los desplazamientos fuera del resultado se ajustan a su última página.
- `limit`: entero de 1 a 100; la pantalla usa 50.
- `query`: texto de hasta 200 caracteres.

Devuelve página, total/coincidencias, posición, campos y procedencia. Cero coincidencias no se interpreta como ausencia del archivo ni como un saldo cero.
