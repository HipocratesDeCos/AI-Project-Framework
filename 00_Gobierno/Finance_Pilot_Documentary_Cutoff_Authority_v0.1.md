# EIOS — FIN-PILOT-CUT-01 — Alcance al corte documental v0.1

Fecha: 18/09/2026. Baseline remoto: 804d2a4d6f67acc59e2588463e654c9bb56542fa; CI #863 SUCCESS.
Autoridad: confirmación explícita del titular del proyecto del primer piloto como análisis financiero al corte documental, mostrando esa fecha y sin presentar el saldo como disponibilidad actual.
Estado: alcance temporal aprobado y auditado; soporte de tesorería, productor QTG y piloto real pendientes.

## DISEÑAR

El piloto analiza Finance Basic desde snapshot.as_of_date conforme al material conservado. No es un sistema de tesorería en tiempo real ni autoriza pagos, compras o una recomendación empresarial actual desde un saldo histórico.
Fuentes: Finance_Basic_Authority_v0.1.md FIN-AUTH-01/02/04/05; contratos Finance Basic y FinanceHorizonProvenance; perfil QTG-DIP-G01-FIN; matriz QTG-FIN-G02-BASE-01; diseño QTG-FIN-G04-01.
Se conserva sin modificación la semántica de motores, snapshots, contexto, parámetros, captura y preparación QTG ya cerrados.

## Criterios del corte

| Aspecto | Obligación y límite |
|---|---|
| Fecha analizada | Mostrar as_of_date junto a todo saldo/proyección del piloto; no sustituirla por la fecha de ejecución del software |
| Horizonte | P-FIN-001 aplicado desde as_of_date según contrato cerrado; configuración vinculada a empresa, versión e instante declarado |
| Tesorería inicial | Saldos monetarios efectivamente utilizables para pagos en ese corte, con fuente válida; no confundir saldo contable total con disponibilidad |
| Exclusiones | Conservar restricciones; no incluir crédito no dispuesto, financiación hipotética, cobros futuros o activos no monetarios como tesorería disponible |
| Correspondencia de fuente | Soporte que identifique empresa, moneda y fecha económica representada; fecha de emisión/extracción no equivale por sí sola a fecha del saldo |
| Datos de otra fecha | No interpolar, actualizar o conciliar automáticamente para fabricar saldo al corte; cualquier reconstrucción requiere transformación autorizada y soporte |
| Momento de conservación/revisión | Conservar los momentos aportados por sus contratos; una revisión posterior puede examinar un corte anterior, sin demostrar disponibilidad presente |
| Presentación | Indicar análisis al corte documental y ausencia de garantía de saldo actual; conservar naturaleza sintética cuando corresponda |

El corte se aporta explícitamente mediante el snapshot existente. No se impone fecha empresarial, hora/zona de corte, cierre diario ni catálogo universal de cuentas; si una fuente requiere precisión adicional para determinar disponibilidad, esa precisión debe aportarse y su ausencia permanece visible.
La autorización de alcance no acredita autenticidad del extracto, titularidad bancaria, conciliación contable, restricciones, completitud de cuentas o mandato humano. treasury_evidence_ref conserva referencia, no demuestra por sí sola esos hechos.
Importe None sigue desconocido, no cero. Cero demostrado sigue siendo valor válido, no ausencia. No elevar estados de Evidence/CashFlow por coincidir fechas o por haberse revisado un documento.

## Temporalidad: delimitación aprobada

No se define en este piloto una ventana de antigüedad para presentar el saldo como actual: esa afirmación está fuera de alcance. No se utiliza automáticamente el valor de seis semanas de P-DAT-001 ni se modifican R-DAT-001 o su productor pendiente.
Esto no exime de temporalidad necesaria: debe poder establecerse qué fecha económica representa la fuente y si soporta la magnitud del corte declarado. Fuente sin fecha suficiente no se considera suficiente por omitir el control de actualidad.
Si el resultado se quisiera usar para una compra o pago presentes, debe abrirse explícitamente ese alcance y cerrar los criterios de actualización/frescura y demás requisitos operativos. No reutilizar este piloto para ese uso por coincidencia de IDs.

## Relación con QTG

Se precisa parte de G02: la pretensión de disponibilidad actual no es el uso autorizado del piloto; la correspondencia temporal del saldo con el corte sí requiere observación suficiente. No se asigna por esta unidad un critical/material/applicable universal ni se produce QualityCheck.
Para una proyección determinada que dependa de tesorería inicial, debe existir soporte suficiente de disponibilidad al corte. Su falta conserva incertidumbre; Finance Basic mantiene sus estados analíticos originales y el productor QTG conserva su bloqueo mientras falten criterios o material necesarios.
Los controles sobre cuotas requeridas, duplicación, fuentes contradictorias y autorización de revisiones no se omiten por acotar temporalidad. G03 y ejecución/consumo G04 permanecen pendientes.

## AUDITAR

A1: corte histórico no demuestra saldo actual. Se prohíbe esa presentación y uso implícito para ejecución presente.
A2: fecha de descarga no demuestra fecha económica del saldo. Exigir identificación del corte representado sin inventar equivalencia temporal.
A3: mismo corte no demuestra disponibilidad o completitud. Mantener fuente válida, restricciones y soporte como requisitos separados.
A4: retirar actualidad del alcance no permite omitir temporalidad necesaria. Conservar correspondencia fuente/corte y límites de precisión.
A5: autorización temporal no autoriza nuevo estado QTG ni cambio de Finance Basic. Mantener bloqueos de productor y motores cerrados.

## DEPURAR

Se registra únicamente la delimitación aprobada y obligaciones ya derivadas de FIN-AUTH. No inventar tolerancia de días, zona de corte, fórmula de conciliación, fuente bancaria única o política de aprobación. Material sintético permite diseño/pruebas, no validación empresarial real.

## AUDITAR 2

PASS de alcance: análisis al corte claramente separado de disponibilidad actual; fuente/corte y restricciones aún necesarios; no confundir emisión con saldo; sin transformación o temporalidad inventadas.
PASS de fronteras: ninguno de los contratos/código cerrados se modifica; no se levanta cuarentena QTG ni se declara piloto real validado.
PENDIENTE: conservación/comprobación complementaria del soporte de tesorería al corte, criterios restantes de suficiencia y productor QTG, presentación ejecutable del alcance y validación supervisada.

## CERRAR → MATERIALIZAR → CI

Se cierra esta unidad documental de autoridad temporal, no la implementación de soporte o el piloto operativo. Materialización: únicamente este documento con auditorías. CI requerida sobre HEAD exacto y merge; su éxito no acredita tesorería real.
Siguiente unidad legítima: diseñar vínculo de fuente de tesorería presentada con preparación/corte exactos y observaciones individuales de disponibilidad/restricciones, manteniendo declaraciones y soporte separados de demostración operativa. No exigir saldo real para diseñar/probar ni convertir un Mock Data en acreditación.
