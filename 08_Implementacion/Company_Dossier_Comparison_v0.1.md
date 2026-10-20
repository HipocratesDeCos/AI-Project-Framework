# Comparación de versiones del expediente recibido

En **Carga de archivos → Expedientes recibidos**:

1. Elegir la versión de origen en **Versiones guardadas**.
2. Elegir la versión de destino en **Comparar con otra versión**.
3. Pulsar **Comparar versiones**.

La comparación no abre ni activa ninguna versión, modifica casillas, cambia la empresa activa o guarda decisiones. Las dos versiones deben corresponder a la misma empresa, razón social, naturaleza de datos y fecha de corte. Los nombres de origen/destino se muestran expresamente; no se deduce el orden temporal de los nombres.

## Archivos y filas

Los lotes se clasifican como incorporados, retirados o compartidos por identidad exacta de lote. Se muestran nombre original, bloque, hoja, filas guardadas, lote y SHA-256 del original. Un mismo archivo con otro mapeo puede dar lugar a otro lote; compartir nombre o hash de bytes no basta para considerarlo el mismo lote. No se emparejan automáticamente documentos como sustituciones.

Por bloque se muestran filas de origen/destino y cantidades de filas normalizadas exactas incorporadas/retiradas. Se procesan todos los registros conservados, no la vista previa de veinte. La comparación usa el contenido canónico de `data`, ignorando posición y procedencia de la fila, y conserva multiplicidades.

Por ello:

- Reordenar filas puede cambiar el archivo/lote sin cambiar su contenido normalizado.
- Corregir un dato manteniendo el número de filas produce una fila exacta retirada y otra incorporada.
- Una fila idéntica repetida dos veces cuenta dos veces; no se deduplica.
- Representaciones normalizadas diferentes se consideran distintas, aunque puedan describir importes económicamente equivalentes.

El resumen no identifica modificaciones de una entidad ni concilia facturas, stock o importes. Para examinar valores concretos se consultan los originales o las consultas de artículos/tesorería de cada selección.

## Comprobaciones conservadas

Se comparan los recuentos de avisos guardados por código y su descripción, sin ejecutar de nuevo la comprobación ni modificar sus instantáneas. Si sus esquemas difieren, se muestran los recuentos pero no su diferencia como comparable. Un menor número de avisos no implica mejora: puede haberse retirado documentación que originaba avisos.

Comparar una versión consigo misma está permitido y muestra archivos compartidos y cero cambios exactos. La ausencia de diferencias no acredita completitud ni admisión. Conserva `PENDING`, `FORBIDDEN` y `decision_authority=false`.

Cambiar cualquiera de las versiones elegidas, el contexto o las casillas limpia el resultado y descarta respuestas pendientes. El resultado no se persiste ni se incorpora a los ZIP ya existentes.

## API

`POST /api/reception/versions/compare`, con `before_id` y `after_id`, protegido por Host local y token de sesión. Verifica integridad de cada versión/comprobación y disponibilidad de sus lotes mediante los validadores existentes. Solo lee la SQLite.
