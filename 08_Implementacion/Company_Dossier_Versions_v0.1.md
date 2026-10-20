# Versiones guardadas del expediente recibido

En **Carga de archivos → Expedientes recibidos**:

1. Marcar expresamente los archivos de una empresa y fecha de corte.
2. Escribir un nombre de hasta 120 caracteres, por ejemplo `Recepción inicial septiembre`.
3. Pulsar **Guardar selección como versión**.
4. Más adelante, elegir la versión en **Versiones guardadas** y pulsar **Abrir versión**.

Abrir una versión restaura el contexto, las casillas exactas y la comprobación conservada al guardarla. Las consultas de artículos y tesorería usarán esa selección. No cambia la empresa activa de Propuestas. Puede repetirse la comprobación mediante su botón habitual; la comprobación nueva no sobrescribe la guardada.

## Inmutabilidad e identificación

La tabla local `received_company_dossier` conserva nombre, fecha UTC, manifiesto y comprobación de referencias. El manifiesto identifica empresa, razón social, naturaleza de datos, fecha de corte, lotes, nombres/hojas/tipos y hashes de originales. También vincula SHA-256 de la comprobación y su esquema. El identificador SHA-256 de la versión deriva del manifiesto canónico; el nombre y el instante no alteran la identidad de la selección.

Guardar de nuevo los mismos archivos y la misma comprobación es idempotente: devuelve la versión existente con su nombre y fecha originales. No crea un alias ni una copia. Un nombre ya usado para otra selección de la misma empresa/corte se rechaza; hay que proporcionar otro nombre. Agregar o sustituir un archivo requiere guardar una versión nueva. No existe edición ni borrado de versiones desde esta interfaz.

Se permite guardar una selección con incidencias o documentación incompleta. La comprobación conservada limita su alcance a referencias y unidades; no acredita conciliación financiera ni integridad del expediente. Los avisos se muestran expresamente al reabrir.

Al cambiar contexto o casillas se limpia la identificación de versión seleccionada y se invalidan consultas pendientes. No se sobreescribe el contenido de la versión. El nombre puede mantenerse en el campo para que el usuario lo cambie al guardar otra selección.

## Alcance y almacenamiento

El guardado crea únicamente un registro de versión en la misma SQLite indicada por `--db`. Los originales y registros normalizados permanecen intactos; se referencian por sus lotes. No se importa un nuevo dataset documental, crea compras, modifica propuestas o admite datos reales/sintéticos. La versión conserva `PENDING`, `FORBIDDEN` y `decision_authority=false`.

Esta funcionalidad aplica a archivos recibidos individualmente. El paquete ZIP de A Monkey ya importado conserva sus pantallas y no necesita cargarse de nuevo. Una copia de seguridad de toda la base, con EIOS cerrado, incluye las versiones guardadas.

## API local

- `GET /api/reception/versions`: listado resumido, protegido por Host local.
- `POST /api/reception/versions/save`: `batch_ids` y `name`, protegido por Host y token.
- `POST /api/reception/version`: `dossier_id`, protegido por Host y token.

La selección comparte la validación de 1–100 lotes del mismo contexto. El guardado serializa la escritura y no sobrescribe filas existentes. La apertura verifica hashes del manifiesto y comprobación y disponibilidad de los lotes; las consultas no modifican la base.
