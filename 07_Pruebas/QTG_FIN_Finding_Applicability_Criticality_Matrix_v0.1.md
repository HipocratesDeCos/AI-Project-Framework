# EIOS — QTG-FIN-G02-BASE-01 — Matriz acotada de hallazgos v0.1

Fecha: 18/09/2026. Baseline remoto: 8fe040b5a67e3d3af722d6bc126435fadda59085; CI #851 SUCCESS.
Autoridad: confirmación explícita del titular de la base propuesta para desarrollar y auditar la matriz Finance Basic.
Estado: base autorizada, matriz documental auditada; productor QTG no cerrado ni habilitado.

## DISEÑAR — alcance y fuentes

Uso: preparación de entradas para run_provenanced_finance_basic, según QTG_DIP_G01_Finance_Basic_Intended_Use_v0.1.md. No cubre Rules FIN, CRC, decisión de compra ni Vertical completo.
Fuentes: Quality_Trust_Implementation_Contract.md v0.4 §§5,8,9; Finance_Basic_Authority_v0.1.md FIN-AUTH-05; FIN-DIP-01; DOC-PAY-CAP-01; DOC-PAY-REVIEW-01; DOC-PAY-ROLE-01; DOC-PAY-DESIG-01.
La confirmación autoriza los cuatro tratamientos siguientes, no una política universal ni una traducción automática de declaraciones a QualityCheck.

## Matriz de la base confirmada

| Hallazgo concreto | Aplicabilidad | Observación/material necesario | Criterio confirmado | Consumo y límite |
|---|---|---|---|---|
| Asociación de cuota no establecida | Cuando la inclusión de esa obligación sea necesaria para interpretar pagos de la compra en este uso | Compra/pedido/confirmación, binding cuota→PAYMENT y comprobación del contenido sobre captura exacta | Bloqueante cuando comprometa la interpretación de pagos de la compra | Condición crítica no evaluable: corresponde NO_APTO/BAJA conforme a QTG §9, únicamente cuando aplicabilidad e impacto estén establecidos; ausencia no es FALSE |
| Importe, moneda o vencimiento contradictorios | Cuando la contradicción afecte a una cuota necesaria para interpretar los pagos de compra | Flujos originales, términos exigibles, soportes contradictorios y revisión individual vinculada | Bloqueante cuando comprometa esa interpretación | Contradicción crítica no resuelta: NO_APTO/BAJA bajo el mismo requisito de justificación; no elegir documento más reciente ni promediar |
| Designación insuficiente | Cuando se pretenda utilizar una revisión como comprobación humana autorizada | Persona, empresa, rol/alcance, vigencia, acto y facultad del otorgante con soporte operativo, vinculados a revisión exacta | No utilizar la revisión como comprobación autorizada; conservar sus hallazgos | No asignar NO_APTO por el nombre del control; examinar qué condición necesaria queda sin soporte admisible y aplicar su criterio. No borrar hallazgos ni declarar que son falsos |
| Dato opcional ausente | Cuando exista ausencia explícita en el input y se haya establecido su relevancia para el uso | Input capturado, condición a la que sirve y explicación de relevancia | Mantener ausencia; advertencia solo cuando sea relevante | Si la limitación es relevante y no crítica, corresponde APTO_CON_ADVERTENCIAS; si es necesaria y crítica, aplicar QTG §9 con justificación. Optional no significa automáticamente irrelevante o crítico |
| Material sintético | Cuando cualquier soporte/captura/revisión/designación esté declarado sintético | Marcas de naturaleza y material íntegro conservados | Exclusivamente pruebas, nunca acreditación operativa | No utilizar como soporte de un APTO empresarial. Las pruebas pueden verificar comportamiento con datos ficticios, sin emitir ni registrar un resultado operativo |

Las dos primeras filas desglosan el primer tratamiento confirmado. No hacen universalmente críticos todos los controles de asociación/importes/monedas/vencimientos.
Si no se puede determinar relevancia, necesidad o impacto, la matriz permanece incompleta para ese caso: no asignar critical=False, material=False o applicable=False por defecto. Esto es un bloqueo del diseño/observación del productor, no un cuarto estado QTG.
Advertencia no crítica no fija por sí sola MEDIA o BAJA: la distinción material de confianza continúa requiriendo criterio y observación conforme al contrato cerrado. No se inventa un umbral monetario de materialidad.

## Requisitos para consumir un hallazgo

1. Identificar captura exacta, compra y los cinco campos del contexto; conservar fuente y vínculo completo, no hash suministrado aislado.
2. Identificar condición, cuota/objetivo y observación original. Pendiente por omisión, NOT_CONFIRMED, CONFLICT_REPORTED, DECLARED_INCONSISTENT y NOT_ESTABLISHED mantienen su significado local; no se sustituyen por FALSE o un resultado QTG.
3. Explicar por qué la condición es aplicable y necesaria/relevante para este uso y por qué el hallazgo compromete su interpretación. La mera presencia de un PAYMENT o su caída fuera del horizonte no resuelve esas cuestiones automáticamente.
4. Examinar soporte suficiente y, si se utiliza revisión autorizada, identidad/mandato operativo; CONFIRMED_BY_REVIEW o DECLARED_CONSISTENT solos no demuestran suficiencia. Fingerprint conserva identidad de material, no su autenticidad.
5. Conservar conflictos y faltantes. No convertir revisión/designación en Evidence DEMONSTRATED, elevar estados de CashFlow ni corregir datos para conseguir cumplimiento.
6. Invocar el gate solamente después de cubrir el inventario requerido por el caso y determinar los controles. Este documento no permite APTO desde una colección parcial/vacía ni autoriza levantar la cuarentena.

## Cobertura y pendientes explícitos

G02 avanza únicamente en el tratamiento de esta base de hallazgos. Aún faltan determinaciones caso/uso suficientemente precisas para producir controles: necesidad e impacto de cada cuota, relevancia/materialidad de faltantes opcionales, suficiencia especializada de tesorería/clasificación contable y condiciones temporales cuando sean necesarias. No copiar Criticality RDM a critical de QualityCheck.
G03: los registros físicos conservan FinanceBasicInput, asociaciones declaradas, revisiones y designaciones presentadas, pero no acreditan por sí solos acuerdo documental, inclusión económica sin duplicación, identidad ni mandato reales. La cobertura de cuotas listadas no garantiza completitud empresarial.
G04: los vínculos exactos entre registros existen; falta diseñar el binding de evaluación/reevaluación QTG al conjunto completo de entrada y a criterios utilizados. No aceptar QualityTrustResult desprendido ni callback opaco.
Los errores técnicos rechazados por constructores siguen siendo errores técnicos; esta matriz no los recodifica como NO_APTO.

## AUDITAR

A1: clasificación universal por nombre de control contradice QTG §9.1. Se condicionan las filas a necesidad e impacto concretos.
A2: designación insuficiente no equivale automáticamente a bloqueo global. Se invalida su uso como revisión autorizada, no sus hallazgos; se examina el requisito afectado.
A3: dato opcional no justifica omisión de un control requerido. Se conserva ausencia y se exige criterio de relevancia, sin valores por defecto.
A4: todo positivo declarado no acredita origen ni suficiencia. Se separan declaración, comprobación autorizada y consumo QTG.
A5: horizonte y materialidad económica no tienen nueva política autorizada. No se deduce inaplicabilidad por fecha ni un umbral de importe.
A6: completar esta tabla no cierra todos los controles QTG §5. Se documentan G02/G03/G04 todavía pendientes.

## DEPURAR

Se mantienen estas precisiones y los límites de la confirmación. No se introduce catálogo global, esquema SQL, API, Evidence nuevo, estados QTG ni reglas empresariales. DESIG-2026-004-v2 continúa siendo Mock Data; 50 000 EUR no se adopta como umbral EIOS. El criterio aprobado no fabrica soporte operativo inexistente.

## AUDITAR 2

PASS documental: los cuatro tratamientos confirmados se conservan; aplicación contextual, precedencia QTG y límites de confianza respetados; declaraciones no promovidas a evidencia; componentes cerrados y cuarentenas intactos.
PENDIENTE: productor ejecutable y pruebas de esa producción, criterio suficientemente determinado para cada control aplicable, observación verificable G03 y binding QTG G04. No se declara G02 completo ni resultado empresarial emitido.

## CERRAR → MATERIALIZAR → CI

Se cierra esta unidad documental de base autorizada, no la matriz integral del productor ni su implementación. Materialización: únicamente este registro y sus auditorías. CI requerida sobre HEAD exacto y merge; prueba regresión, no autoriza criterios adicionales ni acredita fuentes.
Siguiente unidad legítima: precisar cobertura y necesidad de cuotas para este consumidor con fuentes existentes, distinguiendo conjunto listado de completitud del calendario de la operación; someter cualquier nueva política no deducible a autorización explícita. No implementar integración positiva antes de resolver los pendientes del productor.
