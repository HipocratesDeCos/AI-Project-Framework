# Carga de archivos: organización visual

La pantalla ofrece tres accesos internos: Recibir Excel/CSV/PDF, Organizar expedientes/versiones e Importar ZIP sintético preparado. Las rutas son distintas y conservan sus límites existentes. La recepción individual no cambia la empresa activa en Propuestas; los PDF siguen siendo soporte y la importación ZIP sigue limitada a paquetes sintéticos compatibles.

La recepción agrupa identificación de empresa y archivo en pasos numerados; los ajustes de hoja, cabecera y formato CSV pasan a un desplegable. Los paneles progresivos de relación de columnas y comprobación mantienen sus identificadores y lógica. Las casillas de archivo tienen un contenedor destacado y los mensajes de recepción y resumen del expediente un bloque visual.

Expedientes separa guardar versión, abrir/descargar/preparar entrada, comparar versiones, comprobar selección, consultar artículos y consultar tesorería. La comparación queda desplegable. Los botones usan estilos, tamaños y espaciado coherentes. Las tablas se desplazan en pantallas estrechas y mantienen cabeceras visibles y legibles. Las tarjetas de acceso pasan a una columna en móvil.

No cambia formatos, validación, límites, persistencia, admisión, reglas ni autoridad. No se escriben datos de ejemplo en la base del usuario. Verificación: pruebas existentes de recepción/versiones/importación; recorrido DOM/HTTP sobre bases desechables para comprobar ubicación e identidad única de controles, preparación de entrada, versiones, exportación, búsqueda de registros, consulta financiera y comparación. No se añaden dependencias.

## Indicaciones según la selección

El resumen muestra cuántos archivos están marcados y las condiciones para actuar. Comprobar y consultar requieren una selección de un mismo contexto (empresa, razón social, naturaleza y fecha de corte). Guardar versión requiere además un nombre. Abrir, exportar o preparar entrada requieren una versión elegida; comparar requiere dos versiones distintas. La explicación permanece visible y los botones inactivos incluyen un título con el requisito.

Los controles se actualizan al cambiar casillas, empresa, nombre o versión, al renderizar archivos/versiones y al terminar cada acción. Durante una solicitud, su botón sigue ocupado aunque cambie la selección. Las validaciones del servidor permanecen intactas; activar una acción no equivale a admisión o evaluación completa.

Comprobación DOM/HTTP: sin selección; archivo seleccionado sin/con nombre; mezcla de dos empresas y bloqueo; limpieza de selección; apertura/preparación desde versión guardada. Regresión de versiones, exportación, consulta financiera, registros y comparación sobre bases desechables.

## Selección conjunta del expediente

Seleccionar todos los archivos del expediente se activa únicamente al elegir una empresa/fecha de corte en el selector de contexto. Marca los lotes recibidos de ese contexto, sin mezclar naturaleza ni otras empresas. Si ya están todos marcados se desactiva; se pueden desmarcar filas individualmente. Limpiar selección desmarca las casillas sin borrar archivos o versiones.

Ambas acciones aplican la misma invalidación que un cambio manual: limpian versión abierta, comparación, preparación de entrada y consultas vinculadas a la selección, y solicitan repetir la comprobación del expediente. El contador y las acciones disponibles se sincronizan. No ejecutan llamadas de escritura ni modifican la empresa activa.

Verificación DOM/HTTP en dos empresas: selección conjunta desactivada en Todos los expedientes, selección de cinco archivos de un contexto, desmarcado y reselección, limpieza conservando las filas y retorno a los seis archivos recibidos de ambas empresas. Regresión de versiones, exportación, consulta financiera y comparación.

## Resumen visual por bloques de documentación

Al elegir empresa/fecha, el resumen presenta tres cifras (archivos, filas y avisos de recepción) y tarjetas de las categorías de documentación admitidas por la recepción. Cada tarjeta conserva el estado del servicio: sin archivos recibidos, archivo sin filas, datos recibidos pendientes de revisión o solo soporte PDF sin extracción de cifras. Varios archivos del mismo bloque muestran el aviso de posibles solapamientos.

La ausencia de un bloque no se presenta como incumplimiento ni se calcula porcentaje de preparación: la suficiencia depende de la operación. Recibido no equivale a admitido. Los parámetros de stock presentes en archivos pasan a un desplegable; sus recuentos no se convierten en políticas activas.

Las tarjetas se muestran en tres columnas o una en pantallas pequeñas. Se conserva el filtrado por empresa y corte y el comportamiento de selección/versiones. Pruebas: 23 pruebas locales de resumen/recepción/versiones y recorrido DOM/HTTP de tres indicadores, diez bloques, ausencia de archivos y bloque inventario, seguido de selección conjunta y preparación desde versión guardada sobre base desechable.
