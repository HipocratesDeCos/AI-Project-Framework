# EIOS — QTG-DIP-G01 — Finance Basic Intended Use v0.1
Fecha: 17/09/2026
Baseline: main @ 5dfbf75961752f4732d7147d90c2794f7fbfbb0e.
Estado: diseño de uso y obligaciones auditado; sin productor QTG ejecutable.
Unidad: QTG-DIP-G01-FIN.
Fuente previa: 07_Pruebas/QTG_DIP_Control_Coverage_Design_Audit_v0.1.md.

## DISEÑAR — uso acotado
Consumidor físico seleccionado: eios/finance/provenance.py::run_provenanced_finance_basic.
Uso previsto: preparar y comprobar las entradas para el análisis Finance Basic ya autorizado, con horizonte vinculado a P-FIN-001.
El resultado analítico continúa siendo FinanceBasicResult. QTG no determina capacidad, viabilidad, efecto de regla ni resultado de compra.
Quedan fuera de este uso: Rules FIN, CRC, Vertical MVP completo, PRICE, STK, supplier scoring, negociación y selección decisional.
No se crea un consumidor ficticio ni se modifica el consumidor cerrado. Este perfil define requisitos para una integración futura, no anuncia que DIP ya lo alimenta.

## Fuentes y precedencia
- 01_Modelo/Finance_Basic_Authority_v0.1.md FIN-AUTH-01…07;
- 08_Implementacion/Finance_Basic_Implementation_Contract_v0.3.md y corrección v0.3.1;
- 08_Implementacion/Finance_Horizon_Provenance_Contract_v0.1.md;
- eios/finance/models.py, engine.py y provenance.py;
- contrato QTG v0.4; Evidence_Contract; contrato DIP-AGG-01.
Los contratos financieros gobiernan datos/cálculos; QTG gobierna calidad; este perfil no redefine ninguno.

## Obligaciones de entrada y cobertura actual
| Entrada/requisito del uso | Fuente existente | Cobertura DIP-AGG-01 | Obligación previa al productor QTG |
|---|---|---|---|
| Compra y contexto completo | PurchaseOperation / DecisionContext | Presente y vinculada técnicamente | Preservar contexto; no confundir existencia con pago demostrado |
| FinanceBasicInput.context | FinanceBasicInput | Contexto raíz presente | Capturar el input completo y comparar los cinco campos, sin un segundo contexto autónomo |
| FinancialSnapshot | FinanceBasicInput.snapshot | Opcional en DIP | El argumento snapshot es necesario para construir el input; valores desconocidos se conservan como None |
| available_treasury y su referencia | FIN-AUTH-02 / FinancialSnapshot | Representables | No incorporar saldos restringidos, crédito no dispuesto o financiación hipotética; referencia sola no certifica esa clasificación |
| cash_flows completos presentados | CashFlow / FIN-AUTH-05 | No representados en el DIP actual | Capturar la colección y estados originales; no convertir ausencia de captura en colección vacía conocida |
| Pagos de la compra | FIN-AUTH-05 | Compra presente, vínculo a sus flujos no demostrado | Productor/asociación verificable que demuestre inclusión sin doble cómputo; no inferir pagos del importe de compra |
| horizon_days y P-FIN-001 | FIN-AUTH-01 / FinanceHorizonProvenance | Configuración seleccionada representable; horizon_days no capturado como input financiero | Seleccionar P-FIN-001 explícitamente y vincular horizonte conforme al contrato cerrado |
| Instante/empresa del horizonte | FinanceHorizonProvenance | Metadatos conservados | Para este consumidor, effective_at.date() = snapshot.as_of_date, empresa y versión coincidentes; esa condición no se generaliza al DIP |
| Monedas y datos de vencimiento | CashFlow / contrato v0.3.1 | Moneda snapshot presente; flujos ausentes | Conservar None y estados; no FX ni fechas/monedas heredadas por inferencia |
| treasury_minimum | FIN-AUTH-07 / P-FIN-002 | Resolución seleccionable; valor del input no capturado | Para un mínimo suministrado, vincularlo a P-FIN-002; no fijar valor inicial/default. None se conserva |
| working_capital_input | WorkingCapitalInput / FIN-AUTH-04 | No representado | Capturar None o input existente; clasificación procede de fuente autorizada, sin reclasificación ni efecto postcompra inventado |
| external_liquidity | FIN-AUTH-03 / FinancialSnapshot | Representable dentro del snapshot | Conservar contexto externo; no calcular ratio ni activar reglas |
| Configuración seleccionada disponible/ausente | Centro de Parametrización / ResolvedConfiguration | Presente | Selección describe consulta, no garantiza disponibilidad ni completitud empresarial |

La futura captura puede reutilizar FinanceBasicInput existente, sin reconstruir cash_flows o working_capital_input mediante un diccionario empresarial nuevo. Eso exige contrato de extensión DIP y su ciclo; este documento no aprueba todavía una API ni su implementación.
No se exige un resultado FinanceBasicResult previo a QTG: sería invertir el orden del control de entrada.
El modelo financiero no transporta un payment-to-purchase binding explícito. source_ref, flow_id o igualdad de importe aislados no lo sustituyen.

## Distinciones obligatorias
1. Argumento/modelo requerido no equivale a información económicamente demostrada.
2. FinanceBasicInput.cash_flows tiene default vacío en su dominio; no se inventa ese default al integrar un DIP que no capturó la colección. Un input explícitamente recibido conserva su semántica existente.
3. Horizonte inválido o binding incoherente continúa siendo error técnico según FinanceHorizonProvenance; no se convierte en NO_APTO.
4. Finance Basic conserva NOT_EVIDENCED, NOT_EVALUABLE y CONFLICTING_DATA conforme al motor. No se convierten automáticamente en NO_APTO, advertencia o confianza QTG.
5. Optional/None no autoriza a omitir del inventario un control necesario para el uso. Tampoco obliga a bloquear todos los resultados analíticos por ausencia de un dato opcional.
6. La criticidad QTG se determina por hallazgo y aplicabilidad conforme a QTG §9.1. Las categorías RDM no se copian a QualityCheck.
7. El perfil no exige completar ERP, autenticación, atomicidad o todos los dominios EIOS de forma universal; si un control necesario depende de esa garantía, debe demostrarse para ese uso.

## AUDITAR
Se contrastó el perfil con las firmas y modelos físicos y las autoridades indicadas.
A1: el DIP actual no contiene FinanceBasicInput completo; no puede declararse entrada financiera equivalente.
A2: la fecha de resolución del horizonte es una restricción especializada, no una nueva restricción global DIP.
A3: FIN-AUTH-05 exige pagos de compra incorporados una sola vez, pero CashFlow no demuestra esa asociación por identidad de compra.
A4: la presencia de una referencia no demuestra disponibilidad monetaria, clasificación contable o suficiencia.
A5: ejecutar el consumidor puede producir resultados analíticos parciales; eso no autoriza juicio QTG automático.
No se modifica Finance Basic para resolver estos hallazgos.

## DEPURAR
La tabla conserva esas cinco precisiones y separa captura, binding y calidad.
No se inventa una función de importe/plazo→pagos, ni proveedor de clasificación contable, ni valores de parámetros.
Para este perfil se define el consumidor y su inventario de entrada; las determinaciones QTG permanecen separadas.

## AUDITAR 2
Comprobación del perfil depurado:
- consumidor real y alcance finito;
- inventario basado en modelos/autoridad existentes;
- datos capturados y faltantes distinguidos;
- ninguna ausencia convertida en certeza, colección vacía o estado QTG;
- pagos de compra no inferidos;
- semántica analítica y motores cerrados preservados;
- sin aprobación de política económica por continuación genérica.
Resultado: SUPERADA para delimitación de uso e inventario. No equivale a cierre del productor.

## CERRAR
QTG-DIP-G01 queda resuelto únicamente para el perfil Finance Basic aquí delimitado.
G01 global/multi-dominio no se declara resuelto.
G02 (aplicabilidad/criticidad), G03 (observaciones suficientes) y G04 (reutilización segura) permanecen abiertos para este perfil.
Subpendientes concretos de G03: captura del FinanceBasicInput completo, vinculación de mínimo suministrado a P-FIN-002 y demostración de pagos de compra sin doble cómputo.
Siguiente unidad legítima: diseñar la extensión seleccionada del agregado que capture FinanceBasicInput completo y bindings de parámetros disponibles, con sus límites explícitos. No levantará por sí sola QTG ni resolverá la asociación de pagos.

## MATERIALIZAR / CI
Un único documento en 07_Pruebas; ningún cambio ejecutable, fuente normativa, regla, parámetro, motor o API.
CI #829 SUCCESS corresponde al baseline. Se verificará CI del HEAD documental y CI postintegración antes de declarar esta unidad integrada.
CI no demuestra criticidad, suficiencia de datos externos ni pago de compra.
