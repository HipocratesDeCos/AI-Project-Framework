# Revisión del recorrido de compra y síntesis v0.1

## Alcance comprobado

Revisión del recorrido de propuestas de compra en `company_app.py`, no una auditoría completa del repositorio. Se conserva la simulación sintética, sin autoridad de compra ni aceptación automática. No se alteran límites, parámetros ni contratos del núcleo.

| Capacidad existente | Conexión comprobada | Aportación en esta entrega |
|---|---|---|
| Importes y condiciones | `company_commercial_terms.commercial_terms` alimenta el borrador, la propuesta y las alternativas. | Reutiliza el total; distingue mercancía de operación completa cuando faltan portes. |
| Proyección documental de caja | `company_purchase_cash_preview.preview` compensa movimientos al cierre del día y comprueba reserva y horizonte. Puede invocar `_execute` de `company_sales_cash_plan`, conectado con Finance Basic y parámetros. | Explica reserva, saldo mínimo, déficit y acción pendiente sin equiparar previsión con disponibilidad real. |
| Referencias y cobertura de stock | `company_purchase_stock_review.review_quantity` consume inventario y planificación; `company_planning` usa `eios.stock.engine`. | Explicita carencias cuando no hay hipótesis de cobertura. |
| Hipótesis de reposición | `company_purchase_stock_scenario.calculate` conserva supuestos, responsable, fuente y puntos diarios. | Comprueba descriptivamente la cantidad actual frente a seguridad en todos los cierres desde recepción hasta fin objetivo; no confunde cantidad objetivo calculada con cantidad actual suficiente. Una falta anterior a recepción permanece visible. |
| Alternativas de negociación | `company_purchase_opportunities` y `company_purchase_scenario_search` producen hipótesis con procedencia; `company_purchase_negotiation.capture` conserva las columnas. | Resume referencias, volumen, total y condición pendiente de aceptación, sin elegir ganadora. |
| Persistencia e informe | `PurchaseDesk` conserva `cash_orientation_at_save`; `company_proposal_report` imprime el estudio persistido. | Conserva síntesis dentro de la misma huella y muestra su acción histórica al consultar e imprimir. Los estudios antiguos no se reconstruyen. |

Existen contratos del núcleo en `core/negotiation_intelligence.py`, `core/decision_twin*`, `core/scenario*` y `rules/scenario_integration.py`. La revisión del recorrido anterior no acredita una ejecución integral de esos contratos desde el formulario. La síntesis nueva no intenta invocarlos ni simular sus autoridades.

## Comportamiento añadido

`company_purchase_summary.summarize` transforma exclusivamente resultados ya calculados en datos de presentación: título, importes con origen, explicación de stock, sensibilidad al cobro, alternativas, comprobaciones pendientes, siguiente acción y referencias documentales/financieras. Forma parte de la huella del estudio, también en salidas pendientes.

La vista principal presenta la síntesis antes de la tabla de alternativas. Retira la anterior inmediatamente al editar y respeta la secuencia y cancelación existentes del cálculo asíncrono. La revisión guardada y el informe usan la captura histórica. Los textos y fuentes se insertan como texto o con escape HTML.

Prioridad de siguiente acción: completar el dato exacto que bloquea la simulación; resolver déficit comparando alternativas; revisar cobertura insuficiente o no declarada; contrastar condiciones con proveedor. Las comprobaciones documentales permanecen explícitas y separadas del cálculo. Un resultado verde se refiere solo a la reserva prevista.

## Validación

Pruebas de resumen: acción exacta con fecha fuera de horizonte; caja suficiente sin stock justificado; combinación con distinta cantidad y procedencia; falta anterior a recepción pese a caja suficiente; cantidad actual inferior al objetivo; informe antiguo sin reconstrucción y escape HTML. El recorrido de navegador comprueba síntesis de déficit, persistencia, informe imprimible y actualización tras aplicar una combinación.

## Siguiente paso fuera de esta entrega

Revisar y validar criterios de necesidad de compra (consumo, plazo, pedidos pendientes, cobertura y seguridad) antes de ampliar la integración de reglas. No se requieren nuevos documentos reales para completar esta entrega.
