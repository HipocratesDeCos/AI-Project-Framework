# Recepción conjunta de un libro de empresa

En Carga de archivos, «Cargar un libro con varias hojas» utiliza la empresa,
naturaleza, corte y formato numérico del formulario de recepción. El XLSX incluye
`97_Guia_Carga` con cuatro columnas: Hoja, Tipo EIOS, Campo EIOS y Columna del archivo.
Cada fila declara una asignación explícita; las tablas tienen cabecera en fila 1.
No se deduce el contenido por parecido del nombre de la hoja ni por sus importes.

Comprobar prepara hasta veinte hojas con el lector y normalizador existentes,
verifica referencias y unidades mediante la revisión de expediente, y muestra las
hojas auxiliares que se conservarán únicamente en el archivo original. La guía
del libro de cierre sintético preparado en octubre es compatible con este recorrido.
La validación financiera, impuestos, suficiencia de costes y disponibilidad real
no quedan acreditadas por esta comprobación estructural.

La comparación se limita a recepciones de la misma empresa, naturaleza y corte.
Una tabla con idénticos registros normalizados se conserva sin duplicarse, incluso
si cambia el nombre del archivo. Identidades o facturas solapadas con otro contenido
bloquean el lote para revisión manual: no se reemplazan silenciosamente ni se
combinan versiones. La coincidencia no depende de las descripciones de artículos.

El usuario confirma el lote completo. Todos los nuevos lotes se guardan en una
transacción y conservan los bytes originales, hoja, fila, mapeo y huella del XLSX.
Un fallo revierte todas las inserciones. Si cambia el expediente desde la revisión,
se exige comprobar de nuevo; el ticket caduca a los diez minutos y es de un uso.
El formulario descarta respuestas de una revisión anterior al cambiar archivo o
datos de empresa. Los endpoints mantienen los controles existentes de sesión,
Host y tamaño máximo de 10 MiB.

Este paso recibe datos, no los activa: no modifica el catálogo documental, stock,
propuestas ni motor de decisiones. Los selectores existentes de catálogo, inventario,
compras y ventas siguen requiriendo una selección expresa. Las referencias de precio
sin vigencia no son tarifas; las cuotas históricas sin saldo pendiente no generan
flujos. `admission_status=PENDING`, `decision_authority=false` y
`operational_path=FORBIDDEN` se conservan.

Validación: pruebas de idempotencia, conservación del original, referencias ausentes,
conflictos, columnas ambiguas, identidad de empresa, caducidad, concurrencia y rollback
tras un fallo de inserción. Comprobación del libro preparado con diez hojas en una
base desechable. No se publica documentación de empresa ni se modifica la base del usuario.
