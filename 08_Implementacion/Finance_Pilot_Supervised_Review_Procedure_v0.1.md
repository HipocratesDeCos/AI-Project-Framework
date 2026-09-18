# EIOS — FIN-PILOT-SUPERVISION-01 — Procedimiento supervisado

Fecha: 18/09/2026. Baseline remoto: `868e2759e4b3f082501af62fd44d6e26fe015f3d`; CI #876 SUCCESS.
Autoridad: autorización explícita del titular para diseñar revisión supervisada con mandato para tesorería y pagos, comprobaciones individuales sobre documentos conservados y conflictos/faltantes visibles.
Estado: diseño de procedimiento auditado; no revisión realizada, designación real, acreditación operativa ni habilitación QTG.

## DISEÑAR — alcance y precedencia

Consumidor delimitado: preparación de entradas para run_provenanced_finance_basic, proyección de tesorería al corte documental. No decisión de compra ni autorización/ejecución de pagos.
Fuentes: FIN-AUTH-02/05, FIN-PILOT-CUT-01, FIN-PILOT-TREASURY-SUFF-01, QTG v0.4, Evidence Contract, matriz QTG-FIN-G02-BASE-01, contratos DOC-PAY y FIN-TREASURY-SUPPORT/CONTEXT.
Preservar todos los contratos y componentes cerrados. Este procedimiento describe actos de revisión y sus requisitos, no un nuevo motor, registro genérico de autoridad, sistema IAM, API o esquema SQL.

### 1. Fijar el material examinado

Identificar preparación completa/fingerprint, complemento de tesorería completo/fingerprint y valoración contextual cuando se presente. Validar pertenencias exactas con los validadores existentes. Mostrar empresa, moneda, corte, contexto y versiones de criterios; conservar naturaleza de cada fuente sin colapsarla.
Registrar el inventario de documentos realmente recibidos, su origen presentado y contenido íntegro; localizar cada comprobación en documento/página/sección. Localizadores y hashes no prueban autenticidad o suficiencia del contenido.
Material sintético permite ensayar todo el procedimiento; nunca acredita una operación empresarial real.

### 2. Comprobar competencia antes de utilizar revisión autorizada

Identificar persona y soporte de designación, empresa, funciones, alcance específico de tesorería y/o pagos, vigencia aplicable, condiciones, otorgante y soporte de su facultad, así como cambios conocidos examinados. No inferir facultades por cargo, firma visible, nombre o aceptación de este procedimiento.
Una misma persona puede cubrir ambos ámbitos únicamente cuando el soporte lo permita; también pueden intervenir personas distintas con alcance separado. No se exige doble firma o independencia organizativa por defecto.
El mandato de revisión de pagos existente no se extiende a tesorería. DESIG-2026-004-v2 sigue siendo sintético y no acredita ninguno de estos actos operativos.
Si identidad, facultad, alcance o vigencia no se pueden establecer, conservar la revisión como declaración presentada y sus hallazgos; no consumirla como comprobación autorizada. No inventar fecha inclusiva, zona horaria, umbral monetario o facultad del otorgante.

### 3. Ejecutar comprobaciones individuales

| Ámbito | Acto de revisión requerido | Observación que debe quedar reproducible |
|---|---|---|
| Fuente de tesorería | Examinar origen, empresa/titularidad pertinente y magnitud representada; explicar correspondencia con el snapshot | Documento concreto, relación de identidad y soporte del origen; no igualdad aproximada de nombre |
| Corte/moneda/importe | Examinar fecha económica, moneda e importe de la magnitud y contrastarlos con snapshot | Coincidencias, desconocidos y discrepancias individuales; descarga/emisión no sustituye fecha económica |
| Disponibilidad/restricciones | Examinar si el importe es utilizable para pagos en el corte y qué restricciones/exclusiones lo afectan | Soporte explícito de disponibilidad y restricciones; omisión no demuestra inexistencia. Excluir crédito no dispuesto, financiación hipotética, cobros futuros y activos no monetarios |
| Alcance de saldo inicial | Examinar qué conjunto de saldos/cuentas representa la fuente y si sustenta la magnitud presentada | Alcance y limitaciones explícitos; un extracto aislado no demuestra completitud empresarial. No sumar/reconstruir sin transformación autorizada |
| Calendario de compra | Examinar pedido/confirmación y calendario requerido completo | Para COMPRA-2026-001: dos obligaciones de 605 EUR, vencimientos 30/09 y 30/10/2026, total 1210 EUR; calendario completo aunque una cuota quede fuera del horizonte |
| Cuota → flujo | Comparar cada obligación con su PAYMENT, importe, moneda, vencimiento y soportes asociados | Revisión individual de términos, asociación y consistencia entre fuentes; ausencia o contradicción se conserva |
| Duplicación económica | Rastrear pedido y confirmación a las mismas dos obligaciones y examinar flujos adicionales potencialmente duplicados | Justificación de identidad económica; IDs distintos no prueban obligaciones distintas. No eliminar por importe/fecha coincidentes ni presumir inocuos los PAYMENT no asociados |
| Cobros/otros flujos relevantes | Examinar los flujos presentados pertinentes para el uso, sus fuentes, estados y fechas | Limitaciones de evidencia y contradicciones; revisión de compra sola no acredita todos los cobros/pagos de la proyección |

Ningún acto puede resolverse mediante marca CONFIRMED_BY_REVIEW o DECLARED_CONSISTENT sin mostrar qué se examinó y por qué soporta el requisito. La revisión debe distinguir observación documental, conclusión presentada y condición no establecida.
Si una fuente requiere precisión adicional para establecer disponibilidad o pertenencia, documentar la necesidad y obtener soporte suficiente; no fabricar un procedimiento de autenticación, conciliación o transformación inexistente.

### 4. Conservar resultados, faltantes y desacuerdos

Registrar persona y momento de cada acto aportados, documentos/localizadores examinados, criterio/version utilizado, condición, resultado individual, justificación y limitaciones. No generar una persona ni afirmar que el procedimiento se ejecutó por existir este documento.
Usar los registros especializados existentes según su alcance: revisión de pagos, vínculo de designación de esa revisión, soporte de tesorería y valoración contextual. Sus outcomes siguen siendo declaraciones presentadas, no un certificado automático. El modelo de designación de pagos no demuestra un mandato de tesorería: ese soporte puede conservarse como documento adicional, pero su comprobación operativa sigue siendo un acto distinto.
Si un registro no representa un acto necesario, conservar ese pendiente y diseñar la extensión mínima antes de pretender consumo automático; no ocultarlo en una nota tomada como programa ni crear otro registro para simular observación.
Omisión, desconocido y contradicción permanecen diferenciados. Una conclusión favorable no borra material desfavorable. Resolver un conflicto requiere soporte/acto trazable, no prioridad por documento más reciente o revisión más favorable.

### 5. Frontera de conclusión y consumo

Una revisión supervisada sólo puede proponerse como soporte suficiente cuando estén establecidos competencia aplicable, fuente/origen y contenido pertinente, alcance, temporalidad y trazabilidad de los actos necesarios, sin conflicto crítico sin resolver. No se concede aprobación global desde checklist completo o firma aislada.
Falta o contradicción que impida acreditar tesorería inicial necesaria mantiene el tratamiento aprobado NO_APTO/BAJA para ese uso cuando exista productor completo capaz de justificarlo. Este procedimiento no llama al gate ni emite ese resultado.
Relevancia/criticidad/materialidad de otros hallazgos requieren determinación contextual. No mapear estados analíticos a QTG ni elevar CashFlow/Evidence por haber revisado documentos.
G02/G03 integrales siguen pendientes hasta cubrir inventario/criterios y observaciones suficientes. G04 sigue requiriendo productor determinista, recibo, recomputación y política de consumo. No aceptar checks suministrados, callback o resultado previo desprendido.

### 6. Cambio de material

Cambio de preparación, soporte, criterios, designación o hallazgo requiere revisar los actos afectados sobre el nuevo material y crear nuevo vínculo; no reutilizar conclusiones por IDs/fechas/importes coincidentes. Conservar antecedentes y discrepancias, sin actualizar retroactivamente la identidad examinada.

## AUDITAR

A1: cargo o designación de pagos no cubre tesorería. Separar mandatos y verificar facultad/alcance sin inventar designación real.
A2: supervisión puede degenerar en declaración positiva. Exigir acto y soporte localizable, justificación y límites por condición; no promoción automática.
A3: dos cuotas estructuralmente presentes no prueban deduplicación económica. Examinar soportes coincidentes y flujos adicionales.
A4: saldo coincidente no prueba disponibilidad o cobertura. Mantener restricciones, alcance y origen como comprobaciones separadas.
A5: revisar compra/tesorería no verifica todos los flujos. Mantener cobros y otros flujos pertinentes en el inventario.
A6: procedimiento aprobado no equivale a ejecución o productor habilitado. Dejar evidencia operativa y consumo como pendientes.

## DEPURAR

Se evita imponer una fuente bancaria única, ERP completo, conciliación automática, doble firma, umbral universal, FX o actualidad del saldo. No usar datos sintéticos como mandato o fuente empresarial. No extender registros cerrados por reinterpretación.

## AUDITAR 2

PASS de diseño: actos finitos ligados a material real conservado, competencia contextual separada, cuotas completas y duplicación económica explícitas, tesorería utilizable al corte, conflictos/faltantes y reevaluación preservados.
PASS de fronteras: sólo diseño autorizado; sin modificación de código ni reglas/contratos cerrados, sin actos operativos realizados ni nueva autoridad otorgada a personas.
PENDIENTE: ensayos sintéticos del procedimiento y comprobación de cobertura de actos en modelos existentes; observación empresarial supervisada; productor QTG integral y consumo seguro.

## CERRAR → MATERIALIZAR → CI

Cerrar únicamente este diseño del procedimiento, no la revisión de una operación. Materializar este documento con sus auditorías y verificar CI del HEAD exacto y post-merge; CI no prueba revisión ni mandato.
Siguiente unidad legítima: ensayar de extremo a extremo con Mock Data positivos/negativos, indicando qué actos son representables y cuáles siguen pendientes, sin emitir resultado operativo ni inventar extensión de autoridad. No exigir documentos reales para ese ensayo.
