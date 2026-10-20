# Carga de archivos: organización visual

La pantalla ofrece tres accesos internos: Recibir Excel/CSV/PDF, Organizar expedientes/versiones e Importar ZIP sintético preparado. Las rutas son distintas y conservan sus límites existentes. La recepción individual no cambia la empresa activa en Propuestas; los PDF siguen siendo soporte y la importación ZIP sigue limitada a paquetes sintéticos compatibles.

La recepción agrupa identificación de empresa y archivo en pasos numerados; los ajustes de hoja, cabecera y formato CSV pasan a un desplegable. Los paneles progresivos de relación de columnas y comprobación mantienen sus identificadores y lógica. Las casillas de archivo tienen un contenedor destacado y los mensajes de recepción y resumen del expediente un bloque visual.

Expedientes separa guardar versión, abrir/descargar/preparar entrada, comparar versiones, comprobar selección, consultar artículos y consultar tesorería. La comparación queda desplegable. Los botones usan estilos, tamaños y espaciado coherentes. Las tablas se desplazan en pantallas estrechas y mantienen cabeceras visibles y legibles. Las tarjetas de acceso pasan a una columna en móvil.

No cambia formatos, validación, límites, persistencia, admisión, reglas ni autoridad. No se escriben datos de ejemplo en la base del usuario. Verificación: pruebas existentes de recepción/versiones/importación; recorrido DOM/HTTP sobre bases desechables para comprobar ubicación e identidad única de controles, preparación de entrada, versiones, exportación, búsqueda de registros, consulta financiera y comparación. No se añaden dependencias.

## Indicaciones según la selección

El resumen muestra cuántos archivos están marcados y las condiciones para actuar. Comprobar y consultar requieren una selección de un mismo contexto (empresa, razón social, naturaleza y fecha de corte). Guardar versión requiere además un nombre. Abrir, exportar o preparar entrada requieren una versión elegida; comparar requiere dos versiones distintas. La explicación permanece visible y los botones inactivos incluyen un título con el requisito.

Los controles se actualizan al cambiar casillas, empresa, nombre o versión, al renderizar archivos/versiones y al terminar cada acción. Durante una solicitud, su botón sigue ocupado aunque cambie la selección. Las validaciones del servidor permanecen intactas; activar una acción no equivale a admisión o evaluación completa.

Comprobación DOM/HTTP: sin selección; archivo seleccionado sin/con nombre; mezcla de dos empresas y bloqueo; limpieza de selección; apertura/preparación desde versión guardada. Regresión de versiones, exportación, consulta financiera, registros y comparación sobre bases desechables.
