# Borrador comercial local v0.1

## Alcance
Botón «Preparar correo comercial» en la cabecera de una revisión guardada. Produce asunto y mensaje editables con cantidades, unidad, artículo y proveedor identificados por código, precio neto, IVA declarado, descuento, portes e importes y vencimientos separados. Datos ausentes permanecen pendientes.

La revisión actual es parcial y sintética, sin decisión humana registrada. Por tanto el texto solicita confirmar condiciones y se identifica como borrador de prueba no enviable; no afirma aceptación de la compra. La aceptación y envío futuros requieren un flujo de decisión humana y verificación de destinatario que este cambio no materializa.

## Contrato
POST /api/purchases/commercial-draft usa el token existente y la identidad exacta dataset_id/proposal_id/review_id. Comparte la lectura de revisión persistida con el informe. No consulta datos actuales ni ejecuta evaluación. recipient=null, recipient_status=NOT_VERIFIED, attachments=[], sent=false, acceptance_status=NOT_RECORDED, operational_path=FORBIDDEN y decision_authority=false.

El mensaje utiliza únicamente los campos comerciales permitidos de la propuesta conservada. No incorpora tesorería, existencias, mínimos, precios históricos, estrategia, fuentes ni informe interno.

## Interfaz
Asunto y mensaje se asignan como valores de controles, sin insertar HTML de usuario. Copiar texto o descargar TXT conserva la edición local, sin SMTP, mailto ni integración de correo. Las ediciones no se guardan en la base; se informa de ello. Cambiar de revisión/empresa limpia el borrador y se descartan respuestas tardías de otra revisión.

## Validación
Pruebas de importes, descuentos/portes/vencimientos, ausencias explícitas, exclusión de información interna, separación de versiones y empresas, estabilidad de la revisión y ausencia de mutación de propuesta. Recorrido HTTP con token y respuesta JSON, junto con prueba de sintaxis JavaScript existente. Ejecución mediante CI por entorno local desconectado. Interacción visual y portapapeles quedan pendientes de comprobación en navegador.
