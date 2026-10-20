# Exportación documental de una versión recibida

En **Carga de archivos → Expedientes recibidos**, elegir una versión en **Versiones guardadas** y pulsar **Descargar versión en ZIP**. La descarga corresponde a esa versión inmutable, no a modificaciones posteriores de las casillas. Para exportar otra selección, guardarla primero como una versión distinta.

El ZIP contiene:

- `indice.html`: índice legible, con empresa, corte, nombre/fecha de versión, naturaleza de datos, documentos, enlaces locales, hashes y comprobación conservada.
- `originales/`: bytes exactos de cada archivo seleccionado. Nombres numerados y saneados para evitar colisiones o rutas problemáticas; el nombre de origen se conserva en el índice y manifiesto.
- `expediente_manifest.json`: envoltorio de exportación con identificador, manifiesto íntegro de la versión y rutas de los originales en el ZIP.
- `comprobacion_referencias.json`: comprobación guardada en la versión, no una comprobación nueva ejecutada durante la exportación.

Descomprimir el ZIP completo y abrir `indice.html` con el navegador. Los enlaces funcionan sobre los archivos locales extraídos; el índice no carga recursos de red ni ejecuta scripts. Se escapan los nombres y textos de origen antes de incorporarlos al HTML.

## Integridad y alcance

Antes de generar el ZIP se verifica la integridad del manifiesto/comprobación y disponibilidad de los lotes. Cada original debe coincidir tanto con su hash actual de recepción como con el hash conservado en la versión; si no coincide, se cancela toda la respuesta. No se entrega un archivo parcial.

El manifiesto de exportación conserva el manifiesto de versión sin alterarlo. Su identificador se verifica sobre la representación JSON canónica del manifiesto interno; `check_sha256` vincula la comprobación guardada. Las entradas `files` del envoltorio añaden las rutas de exportación sin cambiar esa identidad.

La exportación es de lectura, no modifica la SQLite, originales, propuestas ni empresa activa. Mantiene `PENDING`, `FORBIDDEN` y `decision_authority=false`. El índice indica que no acredita integridad documental, conciliación financiera o autorización decisional.

Es una copia documental de una versión, no una copia completa de la base de datos: no incluye todos los registros normalizados, mapeos de recepción, otras versiones o propuestas. Tampoco es un paquete de importación de empresa activa ni ofrece restauración automática. Para respaldar toda la instalación local, cerrar EIOS y copiar la base SQLite.

El contenido sin comprimir (originales, manifiesto, comprobación e índice) tiene un límite de 100 MiB por exportación. Si lo supera, la aplicación indica que se descarguen los originales por separado. Se comprueba el tamaño antes de construir el archivo.

## API

`POST /api/reception/version/export`, con `dossier_id`, protegido por Host local y token de sesión. Devuelve `application/zip`, adjunto `EIOS_Expediente_<12 caracteres del ID>.zip`, `no-store` y `nosniff`. El navegador decide la ubicación de descarga; el servidor no escribe un ZIP permanente en disco ni lo envía a GitHub.
