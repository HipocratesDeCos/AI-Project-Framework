# Designación presentada del revisor

Desde Propuestas, la revisión financiera permite conservar un registro de designación mediante DOC-PAY-DESIG-01. Requiere una revisión humana documental existente y reproduce exactamente su captura y sus comprobaciones mediante las factorías públicas.

El usuario indica la referencia del registro, naturaleza sintética o presentada como operativa, referencia exacta del revisor, empresa, documento y transcripción con página/sección. Esta primera versión admite únicamente documentos ya conservados en la captura de pagos; no incorpora documentos ajenos ni extrae su contenido. La API admite entre una y siete transcripciones; el formulario permite una por registro. Cada envío es un registro completo nuevo, no una acumulación implícita.

La tabla `company_reviewer_designation` conserva revisiones sucesivas, huella canónica y documento completo. Se rechazan revisiones concurrentes y anclas de revisión humana antiguas. Si cambia la revisión humana, el registro anterior aparece como histórico. El informe imprimible conserva la versión guardada y escapa las transcripciones; el borrador al proveedor excluye este material interno.

Las siete condiciones de designación comienzan sin anotación; los resultados explícitos se conservan sin verificar autoridad. Este registro no autentica identidad, mandato, emisor ni vigencia. Puede incorporarse expresamente a QTG-FIN-PREP-01 como material presentado; esto no verifica la designación ni eleva evidencia, no ejecuta calidad ni viabilidad y mantiene la vía operativa prohibida.

Validación: pruebas de reproducción, correspondencia de empresa/revisor, documentos ajenos, historial, concurrencia, revisión cambiada, informe y privacidad del borrador. La inspección visual en navegador queda pendiente porque el navegador disponible no accede al servidor local del contenedor.

## Inclusión expresa en la preparación financiera

El formulario de preparación ofrece una casilla opcional, inicialmente desmarcada, disponible solo para una designación de la revisión actual. La API recibe `include_designation` como booleano estricto; omitirlo mantiene la preparación sin designación. No se añade material retrospectivamente.

La inclusión reproduce DOC-PAY-DESIG-01 mediante su factoría pública y los bytes de la captura; exige coincidencia de la huella y del contenido íntegro. Una corrección de la designación incluida deja la preparación y el soporte de tesorería dependiente como históricos. Los intentos de guardar o reconstruir con una selección antigua se rechazan. Una preparación que no incluyó designación sigue sin incluirla aunque después exista un registro nuevo.

El informe distingue «incluida como material presentado» de «no incluida». Identidad, facultades, calidad y viabilidad permanecen sin verificar o evaluar según corresponda. La inspección visual continúa pendiente.

## Comprobaciones declaradas de designación

En Propuestas, el registro actual permite anotar o corregir una condición: persona, empresa, cargo y alcance, vigencia, condiciones documentales, facultades del emisor o cambios conocidos. Cada anotación exige nota y confirmación del alcance. Un resultado de coherencia declarada requiere localización en el soporte conservado de la designación; discrepancia y no establecido pueden carecer de localización. El formulario ofrece localizaciones ya transcritas; la API acepta localizaciones explícitas en los mismos documentos conservados.

Se reproduce la revisión humana y la designación exactas antes de guardar. Cada envío añade una revisión completa con las transcripciones, documentos y observaciones previas, sustituyendo únicamente la condición corregida. La sustitución completa de una designación mediante el formulario de transcripciones no hereda observaciones del registro anterior. Se rechazan anclas antiguas, documentos ajenos y cambios concurrentes.

La reconstrucción de QTG-FIN-PREP-01 conserva también estas observaciones. Cambiar una designación incluida exige preparar de nuevo el material y sus dependencias. El informe imprimible muestra resultados y notas escapadas; el borrador comercial los excluye. Cero condiciones sin anotación significa únicamente que se anotaron las siete: no acredita persona, emisor, mandato, calidad ni viabilidad. La comprobación visual sigue pendiente por la falta de acceso del navegador al servidor local del contenedor.
