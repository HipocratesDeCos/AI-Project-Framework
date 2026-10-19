# Recuperación de originales recibidos

En **Carga de archivos → Expedientes recibidos**, cada fila dispone de **Descargar original** junto a **Ver datos**. El navegador guarda una copia del archivo Excel, CSV o PDF recibido, con su nombre original. No se necesita abrir SQLite ni buscar una carpeta de documentos extraídos.

Los originales se conservan en `received_company_batch.content`, dentro de la base indicada mediante `--db`. Con la ejecución habitual en Windows: `C:\proyectos\AI-Project-Framework\data\a_monkey_documentary.sqlite3`.

La descarga usa `POST /api/reception/original`, protegido por Host local y token de sesión. Identifica el lote y su empresa, recupera sus bytes y verifica SHA-256 antes de responder. Si el archivo no pertenece a esa empresa, no existe o su integridad no coincide, rechaza la descarga. El nombre del adjunto elimina rutas y caracteres de control y se codifica como UTF-8 en Content-Disposition. La respuesta es un adjunto binario con `no-store` y `nosniff`.

La descarga no altera el original, los registros normalizados, el expediente o su estado de admisión. No sube nada a GitHub. Esta opción corresponde a los archivos recibidos individualmente; no exporta toda la base ni constituye una copia de seguridad completa. Para respaldar la instalación local, cerrar EIOS y copiar la base SQLite a una ubicación segura.
