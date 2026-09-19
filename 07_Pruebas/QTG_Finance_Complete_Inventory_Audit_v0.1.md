# EIOS — QTG-FIN-INVENTORY-01 — Auditoría del inventario completo

Fecha: 19/09/2026. Baseline remoto: `a490fd9f46ebf977de679f5dd13a74e122c3d51f`; CI #890 SUCCESS.
Estado: inventario físico/metodológico auditado; productor QTG todavía no diseñable en positivo.

## DISEÑAR — objetivo y fuentes

Contrastar todo FinanceBasicInput y las garantías necesarias para `run_provenanced_finance_basic` con FIN-AUTH-01…07, QTG v0.4, QTG-DIP-G01/G02/G04, FIN-PILOT-CUT/TREASURY-SUFF/SUPERVISION, y los registros físicos cerrados hasta TREASURY-PERSONAL-REVIEW-01.
No evaluar una operación, ejecutar Finance/QTG, cambiar modelos ni transformar estados analíticos en controles de calidad.

## Inventario auditado

| Entrada/garantía | Cobertura física actual | Criterio/observación autorizados | Estado para productor |
|---|---|---|---|
| Cinco campos de DecisionContext | FIN-DIP y preparación completos; igualdad técnica | Identidad contextual requerida | CUBIERTO técnicamente; presencia no prueba datos empresariales |
| company_scope/data_snapshot_id/as_of_date/currency | Snapshot completo y coherencias del modelo | Corte documental y correspondencia de fuente aprobados | PARCIAL: source/company/cutoff/currency necesitan observación suficiente |
| available_treasury | Soporte, contexto, mandato y revisión personal exactos | Empresa, moneda, corte, importe utilizable, disponibilidad, restricciones y suficiencia aprobados | CRITERIO CERRADO; operación real aún no observada |
| treasury_evidence_ref | Conservada en snapshot/FIN-DIP | Referencia sola no demuestra fuente | Cubierta como trazabilidad, no suficiencia |
| external_liquidity opcional | Capturada íntegra | FIN-AUTH-03 exige fuente competente, pero no hay perfil QTG especializado ni relevancia fijada para este uso | ABIERTO si se pretende consumir/publicar; ausencia no bloquea automáticamente proyección de tesorería |
| cash_flows completos | FIN-DIP conserva todos los flujos y estados | FIN-AUTH-05 prohíbe estimar/no evidenciado, FX y doble cómputo | PARCIAL: motor trata estados, pero QTG carece de criterio completo de suficiencia de todos los flujos |
| pagos de compra | Calendario, asociaciones, cobertura, revisión/designación | Dos cuotas necesarias para COMPRA-2026-001 y tratamiento de faltantes/conflictos aprobados | CUBIERTO para material presentado; deduplicación económica y soporte real aún requieren observación |
| cobros y otros pagos | Visibles en colección y flujos no asociados | Ninguna fuente especializada determina completitud empresarial, pertenencia económica o necesidad por caso | ABIERTO; principal bloqueo del inventario de proyección |
| evidencia/fecha de cada flujo | CashFlow conserva amount/currency/due_date/source_ref/state | Estados analíticos y exclusión fuera de horizonte definidos | PARCIAL: DEMONSTRATED físico no prueba admisibilidad empresarial QTG; no elevar ni duplicar Evidence |
| horizon_days / P-FIN-001 | Binding provenance-safe exacto y preparación completa | FIN-AUTH-01 y contrato de horizonte cerrados | CUBIERTO para coherencia técnica; selección empresarial ya procede de configuración resuelta |
| treasury_minimum / P-FIN-002 | FIN-DIP vincula valor suministrado; None preservado | FIN-AUTH-06/07 define uso, pero optional ausente requiere relevancia contextual | PARCIAL: falta criterio QTG de fuente/suficiencia del mínimo y tratamiento del caso None para el uso solicitado |
| working_capital_input opcional | Capturado íntegro; modelo comprueba referencias y coherencia analítica | FIN-AUTH-04 exige fuente autorizada y clasificación contable | ABIERTO si se pretende consumir/publicar; no hay revisión especializada ni criterio QTG de fuente/clasificación/completitud |
| configuración seleccionada | FIN-DIP conserva resoluciones y P-FIN-001/P-FIN-002 aplicables | Centro de Parametrización y contratos técnicos | CUBIERTO en binding; disponibilidad de resolución no prueba corrección empresarial universal |
| naturaleza y autoridad humana | Marcas sintéticas/presentadas, pagos y tesorería separados | Procedimientos/mandatos delimitados | CUBIERTO estructuralmente; Mock Data nunca operativo |
| inventario de controles QTG | QTG gate existe; preparación y registros no producen checks | QTG exige controles aplicables completos antes de gate | ABIERTO: aún no hay productor determinista ni catálogo integral autorizado |

## AUDITAR

A1: cerrar tesorería inicial no cierra todos los flujos de la proyección. Cobros y otros pagos son el mayor hueco G03/G02.
A2: CashFlow DEMONSTRATED es semántica financiera física; no equivale automáticamente a Evidence DEMONSTRATED o suficiencia QTG.
A3: elementos opcionales generan salidas analíticas independientes. Su ausencia no bloquea universalmente la proyección, pero tampoco permite APTO global si el uso pretende consumir esas salidas.
A4: treasury_minimum None puede dejar margen NOT_EVIDENCED sin invalidar la proyección determinada. El productor necesita conocer el alcance solicitado antes de decidir relevancia.
A5: working capital y external liquidity no deben añadirse al productor de proyección por arrastre. Requieren criterios especializados sólo si entran en el uso evaluado.
A6: un input completo físicamente no demuestra completitud empresarial de flujos. La colección explícita no prueba ausencia de obligaciones omitidas.
A7: ejecutar gate con subconjunto de checks puede producir APTO. La cuarentena permanece hasta cerrar alcance/inventario y productor.

## DEPURAR — perfiles necesarios

No existe un único inventario honesto sin indicar qué salidas se pretenden consumir. Se distinguen:

1. PROJECTION_ONLY: tesorería inicial, todos los flujos relevantes hasta horizonte, correspondencia/corte/moneda/evidencia, inclusión única de pagos de compra y P-FIN-001.
2. PROJECTION_PLUS_SAFETY_MARGIN: añade treasury_minimum/P-FIN-002 y criterio de su fuente; si falta, determinar tratamiento del margen sin recodificar la proyección.
3. FULL_FINANCE_BASIC: añade working capital y external liquidity cuando se pretendan publicar/consumir, con criterios especializados propios.

Esta separación no modifica FinanceBasicResult ni crea ejecuciones parciales: delimita qué calidad se afirma sobre sus componentes. El consumidor físico continúa siendo el mismo.

## AUDITAR 2

PASS de inventario: todos los campos y garantías del input examinados; cobertura física separada de suficiencia; opcionales y salidas independientes no colapsados; flujo completo no presumido; cuarentena preservada.
HALLAZGO: no es legítimo diseñar aún un productor positivo integral. Falta autoridad para seleccionar el perfil inicial y para determinar suficiencia/completitud de cobros y otros pagos. Para perfiles ampliados faltan además criterios de treasury_minimum, working capital y external liquidity.

## CERRAR → MATERIALIZAR → CI

Cerrar sólo esta auditoría diagnóstica. Materializar un documento; CI exact-head y post-merge. No implementar productor, checks ni resultado.

## Decisión siguiente

Recomendación: seleccionar PROJECTION_ONLY como primer productor QTG, coherente con el piloto financiero acotado. Antes de implementarlo se debe aprobar: (a) todos los cobros/pagos con vencimiento potencial dentro del horizonte deben estar inventariados o explícitamente declarados como no disponibles/incompletos; (b) cada flujo participante requiere fuente suficiente para importe, moneda, vencimiento y pertenencia económica; (c) la imposibilidad de demostrar completitud de flujos necesarios bloquea una afirmación de proyección determinada fiable; (d) flujos demostrablemente fuera del horizonte no bloquean la proyección, aunque sus conflictos se conservan según el motor cerrado. Esta propuesta no presume completitud ERP ni convierte ausencia en colección vacía.
