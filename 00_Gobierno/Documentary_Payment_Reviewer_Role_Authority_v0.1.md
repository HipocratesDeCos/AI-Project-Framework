# EIOS — DOC-PAY-ROLE-01 — Autoridad del revisor documental inicial v0.1

Fecha: 18/09/2026.
Baseline remoto verificado: a44f44686df72e30b9e957364764ae72f0f79c9f.
Decisión del titular del proyecto: confirmado el rol responsable de administración/finanzas de la empresa compradora.
Estado: autoridad de rol aprobada; persona concreta y designación empresarial no aportadas.

## DISEÑAR — autoridad confirmada
El rol inicial autorizado para revisar el contenido documental es el responsable de administración/finanzas de la empresa compradora.
Su alcance es comprobar correspondencia de compra y documentos, cuotas, importes exigibles, moneda y vencimientos, y registrar insuficiencias o contradicciones.
Incluye las comprobaciones de coherencia y duplicación de cuotas listadas ya definidas por DOC-PAY-REVIEW-01, sin afirmar completitud empresarial.
No tiene por esta autoridad facultad para declarar APTO QTG, aprobar una compra, ejecutar pagos, autenticar un proveedor o modificar reglas/parámetros.
La aprobación del rol en EIOS no designa a una persona para una empresa concreta ni demuestra su identidad, empleo o mandato.

## Fuentes y compatibilidad
Precedentes: Documentary_Payment_Human_Review_Contract_v0.1.md, Documentary_Payment_Human_Review_Implementation_Audit_v0.1.md, Evidence_Contract v1.0 y FIN-AUTH-05.
DocumentaryPaymentHumanReview conserva reviewer_ref y reviewed_at. Sus hallazgos siguen siendo declaraciones suministradas; este documento no convierte ese registro en comprobación automática de autorización.
Company_scope y material de compra proceden de la captura examinada; no se permite deducir empresa desde el nombre del revisor.
No modifica C0, Finance Basic, DOC-PAY-CAP-01, DOC-PAY-REVIEW-01 ni QTG.

## Designación empresarial — evidencia necesaria
| Elemento | Obligación antes de afirmar autorización de una revisión |
|---|---|
| Empresa | Identificar expresamente la empresa compradora cubierta y su correspondencia con el company_scope capturado |
| Persona | Identificación concreta y correspondencia demostrable con reviewer_ref; no copiar sólo el nombre del rol |
| Función y alcance | Designación como responsable de administración/finanzas y facultad documental dentro del alcance aprobado |
| Acto de designación | Documentación o registro empresarial identificable, conservable y verificable; referencia sola no autentica el acto |
| Emisión | Identificar quién emitió la designación y el soporte de su facultad empresarial; EIOS no inventa a ese otorgante |
| Vigencia | Comprobar si la designación cubría reviewed_at conforme a sus condiciones documentadas, sin inventar expiración o fecha de efecto |
| Cambios | Conservar revocaciones, sustituciones, límites y contradicciones conocidos; sin elección automática de la versión más conveniente |

La forma del acto de designación procede de la empresa; no se impone una firma electrónica, certificado, ERP o directorio nuevos.
Una ficha rellenada o una declaración de rol aportada se puede conservar como material presentado, pero no basta por sí misma para afirmar autorización verificada.
La correspondencia de identidad y la facultad del otorgante necesitan evidencia operativa. Ningún constructor de Python puede fabricar esas garantías.

## Uso y tratamiento de faltantes
La revisión técnica ya registrada no se sobrescribe para añadir designación. La futura comprobación de autorización deberá vincular registro exacto, persona, empresa y material de designación en un registro complementario.
La ausencia de designación no borra hallazgos, los convierte en falsos ni cambia el estado de flujos/Evidence. Impide afirmar que se ha demostrado autorización empresarial.
Una revisión de otra empresa, fuera del alcance documentado o sin vigencia demostrable no podrá presentarse como autorizada para la captura examinada.
Si la evidencia de vigencia o identidad es insuficiente, la conclusión de autorización permanece pendiente/no demostrada; no se rellena con True o una aprobación del rol genérico.
Las revocaciones y revisiones históricas se evalúan según su efecto documentado. No se aplica retrospectividad automática ni se selecciona sólo el último registro.
No se define aquí una traducción de estos faltantes o conflictos a NO_APTO, advertencia, criticidad o confianza QTG.

## AUDITAR
A1: aprobar un rol no acredita mandato de una persona. Se separan rol, designación e identidad.
A2: reviewer_ref no incluye empresa ni prueba de mandato. La futura comprobación debe tomar empresa y tiempo de la revisión/captura, no de una etiqueta libre.
A3: introducir designación dentro de la captura o revisión cerradas cambiaría su identidad. Se conserva vínculo complementario exacto.
A4: vigencia y revocación sin condiciones documentadas producirían política inventada. Se remite al efecto efectivamente documentado.
A5: aprobar el rol no concede autoridad QTG ni autoriza pagos. Las exclusiones permanecen explícitas.

## DEPURAR
Este documento registra sólo la autoridad confirmada y los requisitos de evidencia de designación.
No crea una designación real, no asigna a Andrés u otra persona, no elige otorgante empresarial ni inventa firma/fecha.
No declara autenticación, almacenamiento persistente empresarial o integración IAM cerrados.
No requiere reabrir contratos existentes para conservar un acto externo de designación.

## AUDITAR 2
PASS: alcance idéntico a la decisión del titular y al contrato de revisión humana.
PASS: empresa, persona, momento y alcance necesarios; sin identidad deducida por nombre de rol.
PASS: faltantes y conflictos conservados; sin transición automática a Evidence o QTG.
PASS: no modifica componentes cerrados ni crea política temporal universal.
PENDIENTE: evidencia de designación real, verificación de identidad/facultad y contrato ejecutable de comprobación complementaria.

## CERRAR
Se cierra la materialización documental del rol aprobado y sus obligaciones de designación. No se cierra designación concreta, autorización verificada de una revisión o productor QTG.

## MATERIALIZAR / CI
Esta unidad añade únicamente el presente documento de gobierno y sus auditorías.
CI completa requerida sobre HEAD exacto previa/posterior a integración; no valida una designación empresarial inexistente.
Continuidad legítima: diseñar captura/comprobación complementaria de designación presentada, distinguiendo coherencia técnica de autorización demostrada. No afirmar verificación positiva sin evidencia operativa.
