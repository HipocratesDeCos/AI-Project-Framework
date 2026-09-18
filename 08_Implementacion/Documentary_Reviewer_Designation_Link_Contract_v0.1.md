# EIOS — DOC-PAY-DESIG-01 — Vínculo de designación presentada v0.1

Fecha: 18/09/2026.
Baseline remoto verificado: 51b0c8bbc5466db6ad07d60f19947aa0d75c2283; CI #847 SUCCESS.
Estado: diseño técnico acotado; implementación y autorización empresarial real pendientes.

## DISEÑAR

Unidad: conservar una designación presentada y su vínculo con una DocumentaryPaymentHumanReview exacta. Precedentes: DOC-PAY-ROLE-01 y DOC-PAY-REVIEW-01. No modificar captura financiera, captura documental, revisión humana, motores ni QTG.

La fuente de prueba es DESIG-2026-004-v2, declarada sintética por el aportante. Su contenido permite preparar casos de coherencia, no acreditar identidad, mandato o facultades reales. Una revisión creada para estos casos será también ficticia; no se atribuirá su emisión efectiva a la persona nombrada.

## Material y relaciones mínimas

| Elemento | Obligación del futuro registro complementario |
|---|---|
| Referencia local | Referencia no vacía de vínculo y referencia/versiones documentales aportadas; sin crear una identidad global empresarial |
| Revisión examinada | Conservar payload completo de revisión construida y fingerprint calculado; incluye la captura examinada, sin editarla |
| Designación | Conservar bytes completos, referencia documental, hash calculado y naturaleza explícita SYNTHETIC o PRESENTED_OPERATIONAL |
| Persona y empresa | Conservar identificadores/nombres documentales y correspondencias declaradas explícitamente con reviewer_ref y company_scope; no resolver por similitud de nombre |
| Rol y alcance | Conservar texto presentado y soporte localizado; distinguir alcance documental, facultad de pagos y autoridad QTG |
| Vigencia y condiciones | Conservar condiciones tal como se aportan y sus localizadores, sin inventar zona horaria, inclusividad, revocación o efecto retrospectivo |
| Emisión | Conservar otorgante declarado y soportes adicionales si existen; su cargo escrito no demuestra facultad empresarial |
| Observaciones | Conservar condición examinada, nota, soporte y resultado declarado individual; nunca un booleano global de autorización |

Las transcripciones se etiquetan como declaraciones sobre el documento, no como extracción automáticamente verificada. Los localizadores referencian únicamente documentos conservados, con página positiva y sección no vacía. No prueban que el texto exista allí.

La naturaleza de la revisión/captura y la de la designación se conservan por separado. Ninguna marca PRESENTED_OPERATIONAL autentica una fuente; cualquier componente SYNTHETIC impide presentar el conjunto como prueba real.

## Comprobaciones acotadas

Inventario mínimo: PERSON_CORRESPONDENCE, COMPANY_CORRESPONDENCE, ROLE_AND_SCOPE, VALIDITY, DOCUMENT_CONDITIONS, ISSUER_AUTHORITY_SUPPORT y KNOWN_CHANGES. Son etiquetas locales, no controles ni criticidades QTG.

El registro conserva observaciones aportadas para cada condición con resultados DECLARED_CONSISTENT, DECLARED_INCONSISTENT o NOT_ESTABLISHED. Una condición omitida permanece pendiente. DECLARED_CONSISTENT describe una declaración de coherencia, no autorización demostrada ni una comprobación automática del documento.

La construcción comprueba únicamente integridad estructural, referencias existentes y vínculo exacto. Si una correspondencia declara un reviewer_ref o company_scope distinto del material examinado, se rechaza el vínculo técnicamente incoherente. Una discrepancia entre identidad documental y captura se puede conservar como observación negativa; no se corrige silenciosamente. Identidad real y facultad del otorgante siguen sin ser fabricables por el constructor.

Fecha/hora de revisión procede del registro humano. El documento sintético expresa fechas de vigencia, sin precisar zona ni extremos: se conservarán esas fechas y la incertidumbre. No se implementará una regla temporal universal ni se afirmará cobertura positiva de un instante ambiguo. Para pruebas se pueden suministrar observaciones ficticias de una fecha interior, siempre etiquetadas como tales.

El límite ficticio de 50 000 EUR no es un umbral EIOS. Si se declara una comprobación económica, debe conservarse el importe documental comparado, moneda y soporte; sin sustituir 1 210 EUR exigibles por 1 000 EUR de base o por los pagos dentro del horizonte financiero. Si falta ese material, la condición no se da por satisfecha. No introducir cálculo económico nuevo ni aprobación de pagos.

Revocaciones, sustituciones y contradicciones conocidas se conservan con su soporte. Una colección vacía significa que no se aportaron cambios, no que se comprobó su inexistencia. No seleccionar automáticamente la versión más reciente/favorable.

## AUDITAR

A1: hash aislado o referencia mutable desvinculan designación y revisión. Exigir material completo e identidad calculada.
A2: nombre de persona/empresa no equivale a identidad técnica o prueba de identidad real. Exigir correspondencias declaradas explícitas y conservar su límite.
A3: fecha documental no define instantes universales. Conservar precisión original y observaciones pendientes.
A4: límite económico sin total exigible documentado produciría comparación inventada. Exigir soporte del importe utilizado o mantener condición no establecida.
A5: cargo del otorgante y Mock Data no prueban mandato. Prohibir salida AUTHORIZED, DEMONSTRATED o APTO.
A6: añadir designación al registro humano cerrado cambiaría su identidad. Usar complemento independiente.

## DEPURAR

Se elimina cualquier agregación de observaciones a autorización global. El futuro constructor no realizará OCR, autenticación, revisión humana, cálculo financiero ni traducción a QualityCheck. No exige un directorio, firma electrónica, API o esquema SQL nuevos. Conservación técnica no se confunde con persistencia empresarial.

DESIG-2026-004-v2 habilita casos sintéticos. No cambia el estado de autoridad empresarial de DOC-PAY-ROLE-01: se ha presentado una designación ficticia, no una acreditación operativa.

## AUDITAR 2

PASS de diseño: relación complementaria sin ciclos ni reapertura de componentes cerrados; material íntegro; declaraciones individuales y pendientes explícitos.
PASS de fronteras: sin criterios temporales/económicos inventados, autenticación ficticia ni promoción de hallazgos a Evidence/QTG.
PENDIENTE: implementación ejecutable y pruebas; identidad/mandato operativos; matriz autorizada de aplicabilidad/criticidad y consumo QTG. La aceptación de definiciones generales no cierra esa matriz.

## CERRAR

Se cierra únicamente este diseño de conservación y vínculo declarativo. No se cierra autorización de una persona, verificación positiva empresarial o productor QTG.

## MATERIALIZAR / CI

Esta unidad materializa el contrato documental, no el registro ejecutable. CI debe verificarse sobre HEAD exacto; no sustituye prueba empresarial.

Siguiente unidad: constructor complementario inmutable con exportaciones independientes, revalidación de entradas y pruebas de material modificado, referencias ajenas, correspondencias incoherentes, condiciones omitidas/negativas, naturaleza sintética y ausencia de llamadas a motores/QTG. Reutilizar DOC-PAY-REVIEW-01 y sus controles de captura exacta. No publicar identificadores personales completos en fixtures si nombres/referencias ficticias bastan.
