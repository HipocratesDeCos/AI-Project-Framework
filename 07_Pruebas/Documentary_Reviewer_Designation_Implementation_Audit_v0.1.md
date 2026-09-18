# EIOS — DOC-PAY-DESIG-01 — Auditoría de implementación v0.1

Fecha: 18/09/2026. Baseline exacto: ed44ed9140fe2ce5098d5abf7b78b9307c07db04, CI #849 SUCCESS.

## DISEÑAR

Materializar el contrato Documentary_Reviewer_Designation_Link_Contract_v0.1.md integrado en PR #169. Añadir únicamente módulo complementario, pruebas y este registro. No modificar componentes cerrados ni introducir directorio, API, firma o esquema SQL.

El constructor recibe revisión humana construida, documentos íntegros, transcripciones declaradas con localizadores, correspondencias explícitas de persona/empresa y observaciones individuales. Conserva payload completo e identidades calculadas; no cambia flujos, Evidence o hallazgos humanos.

## AUDITAR

A1: correspondencias técnicas no deben inferirse del nombre. Comparar reviewer_ref con revisión y company_scope con snapshot capturado; texto documental permanece una declaración separada.
A2: modelos frozen pueden tener copias inválidas. Revalidar material, transcripciones, observaciones y localizadores desde model_dump antes de conservarlos.
A3: observación vacía o parcial no implica éxito. Inventario fijo de siete condiciones, pendientes derivados de omisiones; resultados negativos/no establecidos conservados explícitamente.
A4: un localizador no acredita contenido ni autorización. Exigir soporte para declaración consistente, pero no afirmar lectura/autenticación efectiva.
A5: documento modificado debe cambiar identidad; revisión modificada no admite reutilizar el vínculo. Conservar material completo y ofrecer validación de pertenencia exacta.
A6: fecha y límite económico requieren interpretación empresarial no autorizada. Conservar texto sin evaluación automática; las notas/transcripciones pueden conservar material comparado aportado, no lo verifican. No convertir 50 000 EUR en umbral EIOS.

## DEPURAR

Salida limitada a PRESENTED_DECLARATIONS_ONLY; sin campo authorized o resultado global. Naturaleza de designación separada de case_kind de captura. Todas las observaciones consistentes y ninguna omitida tampoco producen prueba de mandato.

Las pruebas reutilizan la cadena FIN-DIP → captura documental → revisión humana. Contienen un sustituto de bytes explícitamente ficticio y transcripciones de ejemplo basadas en DESIG-2026-004-v2, no una copia del PDF aportado ni prueba de lectura de sus bytes. No incluyen DNI/NIF completos, firma o revisión real atribuida a las personas ficticias.

El constructor conserva declaraciones, no realiza comparaciones semánticas de documento, importes o vigencia. No establece una política temporal y no resuelve revocaciones/versiones contradictorias. No presenta una colección vacía de cambios como comprobación de inexistencia.

## AUDITAR 2

19 pruebas específicas satisfactorias: vacío/parcial, términos sintéticos sin interpretación, negativos/no establecidos, persona/empresa ajenas, naturaleza inválida, designación no conservada, colecciones incorrectas, duplicados, bypass de modelos/localizadores, exportaciones independientes, bytes/fingerprint, revisión cambiada y ausencia de motores/QTG.

Suite completa: 1053 pruebas satisfactorias, incluidas las 19 nuevas; cinco avisos en pruebas preexistentes de bypass/deprecación Pydantic. CI debe confirmar entorno de dependencias del proyecto y trabajos Python/SQL sobre HEAD exacto antes y después de integrar.

PASS técnico: integridad estructural y relación exacta. No equivale a identidad/mandato empresarial, persistencia operativa, coherencia semántica automáticamente verificada o autorización QTG.

## CERRAR → MATERIALIZAR → CI

Cierre técnico condicionado a CI completa satisfactoria. Material: eios/core/documentary_reviewer_designation.py y tests/test_documentary_reviewer_designation.py, más esta auditoría. Componentes previos intactos.

Continuidad: quedan pendientes los criterios autorizados de aplicabilidad/criticidad y consumo de hallazgos para QTG, así como evidencia operativa para afirmar autorización real. La designación sintética no cierra esos requisitos. No generar un productor positivo QTG desde observaciones declarativas.
