# EIOS — TREASURY-MANDATE-VERIFY-01 — Comprobación manual del mandato

Fecha: 19/09/2026. Baseline remoto: `116028197dde98dae1c1177e6c8ec1dac0ede135`; CI #880 SUCCESS.
Autoridad: aprobación explícita del titular del proyecto del mecanismo manual de contraste propuesto para el mandato de tesorería.
Estado: mecanismo metodológico aprobado y auditado; no existe por esta aprobación una designación real, una comprobación ejecutada ni una fuente empresarial reconocida concreta.

## DISEÑAR — alcance

Uso exclusivo: determinar si una revisión humana puede utilizarse como comprobación autorizada de tesorería en el piloto financiero al corte documental. No autoriza pagos, compras, disposición bancaria, administración general ni decisión empresarial.
Fuentes y precedencia: FIN-PILOT-SUPERVISION-01, FIN-PILOT-TREASURY-SUFF-01, Evidence Contract, QTG v0.4 y límites de DOC-PAY-ROLE/DESIG. Los contratos cerrados mantienen su autoridad.

El mecanismo aprobado consta de cuatro elementos inseparables:

1. comprobación manual supervisada de identidad, empresa, facultad del otorgante, alcance de tesorería y vigencia;
2. contraste mediante canal empresarial previamente reconocido, independiente de los datos de contacto aportados únicamente por el documento examinado;
3. conservación de soporte del contraste, persona que lo realizó, momento y material exacto examinado;
4. resultado no acreditado cuando el contraste falte o sea inconcluyente, sin habilitación automática de QTG.

## Canal empresarial previamente reconocido

Un canal sólo puede utilizarse si su relación con la empresa fue establecida antes de este contraste o mediante una fuente empresarial independiente y trazable. Ejemplos admisibles en principio, sujetos a soporte: directorio corporativo gobernado, contacto ya validado en una relación empresarial previa o canal oficial verificable de la entidad.

No se considera reconocido por sí solo:

- teléfono, correo, enlace, código QR o dominio indicado únicamente en la designación recibida;
- respuesta de la propia persona cuya facultad se comprueba sin confirmación independiente;
- apariencia del documento, firma escaneada, cargo declarado, coincidencia de nombre o logotipo;
- conversación del proyecto, Mock Data, hash, nombre de archivo o naturaleza PRESENTED_OPERATIONAL;
- búsqueda pública aislada que no demuestre la relación del canal con la empresa y el acto concreto.

El procedimiento no crea un directorio corporativo ni prescribe una tecnología. Si no existe un canal reconocido demostrable, el resultado es mandato no acreditado; no se fabrica confianza con el canal del propio documento.

## Actos mínimos de contraste

| Condición | Comprobación manual | Soporte que debe conservarse |
|---|---|---|
| Identidad | Correspondencia entre persona designada y persona a la que se atribuye la revisión | Referencia del contraste y explicación; no mera igualdad nominal |
| Empresa | Relación de la designación, otorgante y revisor con el company_scope aplicable | Fuente independiente/canal reconocido y resultado observado |
| Facultad del otorgante | Capacidad del otorgante para delegar el alcance examinado | Base presentada y confirmación por canal reconocido; el cargo aislado no basta |
| Alcance | Inclusión explícita de revisión de tesorería al corte y límites aplicables | Texto/acto confirmado; no extensión desde revisión de pagos |
| Vigencia | Aplicación al momento/corte pertinente y ausencia de revocación conocida examinada | Fechas/condiciones y comprobación de cambios; no inventar inclusividad o zona horaria |
| Integridad contextual | Correspondencia del mandato con revisión, empresa y material concretos | Identificadores y payload/fingerprint del material examinado cuando exista |

La comprobación puede concluir ACREDITADO_POR_CONTRASTE, NO_ACREDITADO o INCONCLUYENTE como resultado local del procedimiento de mandato. Son estados de comprobación del mandato, no estados de Evidence, QTG, Rule o Assessment. ACREDITADO_POR_CONTRASTE requiere todas las condiciones necesarias satisfechas con soporte reproducible y sin conflicto no resuelto.

NO_ACREDITADO se utiliza cuando existe soporte suficiente de que una condición necesaria no se cumple. INCONCLUYENTE se utiliza ante falta de soporte, imposibilidad de contraste o conflicto no resuelto. Ausencia no se convierte en afirmación negativa.

## Registro mínimo del acto

Conservar de forma inmutable:

- referencia única del contraste y finalidad acotada;
- empresa y persona/mandato examinados;
- identidad de quien realiza el contraste y momento con zona, ambos aportados;
- tipo/referencia del canal reconocido y soporte de su reconocimiento previo o independiente;
- documentos y material exactos examinados, con contenido preservado cuando el contrato lo permita;
- una observación individual por condición, resultado, justificación y localizadores/referencias;
- conflictos, limitaciones, cambios/revocaciones examinados y condiciones pendientes;
- vínculo exacto con la revisión de tesorería que pretenda consumir el mandato.

No registrar contraseñas, secretos, tokens, datos bancarios innecesarios ni contenido de comunicaciones más allá de lo requerido para trazabilidad. Este diseño no define retención legal, protección de datos o firma electrónica; deberán aplicarse las obligaciones competentes cuando exista uso real.

## Frontera de consumo

ACREDITADO_POR_CONTRASTE permite tratar la revisión vinculada como realizada por una persona con mandato comprobado únicamente dentro del alcance y vigencia observados. No demuestra que sus conclusiones técnicas sean correctas, que la fuente de tesorería sea suficiente o que los fondos estén disponibles.

La suficiencia de cada acto de revisión continúa requiriendo material y observación según FIN-PILOT-SUPERVISION-01. Una revisión autorizada no eleva automáticamente declaraciones a Evidence DEMONSTRATED ni genera QualityCheck, APTO o confianza.

Todo cambio de persona, empresa, otorgante, alcance, vigencia, canal/soporte, revisión o material vinculado exige nuevo contraste o reevaluación explícita de los actos afectados. No escoger la confirmación más favorable ni actualizar retroactivamente un registro anterior.

## AUDITAR

A1: confirmar por un contacto incluido en el mismo documento crea una confianza circular. Se exige canal previamente reconocido o fuente independiente trazable.
A2: la respuesta de la persona designada no demuestra facultad del otorgante. Se separan identidad, empresa, delegación, alcance y vigencia.
A3: ACREDITADO podría confundirse con suficiencia financiera. Se limita estrictamente al mandato y se prohíbe promoción automática a Evidence/QTG.
A4: falta de confirmación no prueba ausencia de mandato. Se distingue INCONCLUYENTE de NO_ACREDITADO.
A5: exigir una tecnología concreta inventaría infraestructura. Se define propiedad del canal y soporte, no API, IAM, firma o directorio.
A6: conservar comunicaciones completas aumentaría exposición innecesaria. Se exige evidencia mínima reproducible, sin secretos ni datos excedentes.

## DEPURAR

Se mantienen tres resultados locales para evitar ausencia→negación. Se exige vínculo a la revisión exacta y reconocimiento del canal demostrable. No se adopta DESIG-2026-004-v2 como prueba real, no se nombra revisor operativo, no se fija doble firma, plazo universal, proveedor de identidad ni autoridad bancaria.

## AUDITAR 2

PASS metodológico: rompe la circularidad documental; condiciones y soporte individuales; mandato separado de conclusión técnica; cambios y conflictos conservados; minimización de datos explícita.
PASS de fronteras: autorización del método, no ejecución; sin cambio a modelos, Evidence, QTG, Finance, Rules o componentes cerrados.
PENDIENTE: contrato técnico del registro y pruebas sintéticas; identificación/soporte de un canal empresarial real; ejecución de una comprobación real; G02/G03/G04 restantes.

## CERRAR → MATERIALIZAR → CI

Se cierra únicamente la autoridad metodológica del mecanismo manual. Materialización: este documento con auditorías. CI del HEAD exacto y post-merge obligatoria antes de comunicar integración; CI no acredita personas, canales ni mandatos.

Siguiente unidad legítima: diseñar el contrato técnico inmutable del acto de contraste, reutilizando documentos/localizadores existentes donde proceda y sin almacenar secretos. Después se implementará con Mock Data positivos, negativos e inconcluyentes; ningún caso sintético será acreditación empresarial.
