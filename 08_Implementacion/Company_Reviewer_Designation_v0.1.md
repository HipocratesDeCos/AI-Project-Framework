# Designación presentada del revisor

Desde Propuestas, la revisión financiera permite conservar un registro de designación mediante DOC-PAY-DESIG-01. Requiere una revisión humana documental existente y reproduce exactamente su captura y sus comprobaciones mediante las factorías públicas.

El usuario indica la referencia del registro, naturaleza sintética o presentada como operativa, referencia exacta del revisor, empresa, documento y transcripción con página/sección. Esta primera versión admite únicamente documentos ya conservados en la captura de pagos; no incorpora documentos ajenos ni extrae su contenido. La API admite entre una y siete transcripciones; el formulario permite una por registro. Cada envío es un registro completo nuevo, no una acumulación implícita.

La tabla `company_reviewer_designation` conserva revisiones sucesivas, huella canónica y documento completo. Se rechazan revisiones concurrentes y anclas de revisión humana antiguas. Si cambia la revisión humana, el registro anterior aparece como histórico. El informe imprimible conserva la versión guardada y escapa las transcripciones; el borrador al proveedor excluye este material interno.

Las siete comprobaciones de designación permanecen pendientes. Este registro no autentica identidad, mandato, emisor ni vigencia. No se incorpora todavía a QTG-FIN-PREP-01, no eleva evidencia, no ejecuta calidad ni viabilidad y mantiene la vía operativa prohibida.

Validación: pruebas de reproducción, correspondencia de empresa/revisor, documentos ajenos, historial, concurrencia, revisión cambiada, informe y privacidad del borrador. La inspección visual en navegador queda pendiente porque el navegador disponible no accede al servidor local del contenedor.
