# EIOS — QTG-PROJECTION-INSTALLMENT-TRACE-01 — Extensión de trazabilidad v0.1

Fecha: 19/09/2026. Baseline remoto: `ccf918881268e3f09fb52ae9d8a51b6f0d7f8220`; PR #195 y CI #901/#902 SUCCESS.
Autoridad: aprobación explícita del titular para ampliar la revisión especializada de flujos.
Estado: diseño, auditorías e implementación completados; integración condicionada a CI.

## DISEÑAR

Ampliar `FlowInventoryReviewFinding` para que `PURCHASE_PAYMENT_COHERENCE` conserve una observación individual por cada `installment_ref` del calendario requerido contenido en la preparación exacta.

Nuevo objeto `FlowInstallmentReviewFinding`:

- `installment_ref`;
- `outcome`: `CONFIRMED_BY_REVIEW`, `NOT_CONFIRMED` o `CONFLICT_REPORTED`;
- `note`;
- `locators` hacia material del inventario o captura de pagos;
- `flow_ids` capturados relacionados.

`installment_findings` solo es válido en `PURCHASE_PAYMENT_COHERENCE`. Su conjunto debe coincidir exactamente con todas las cuotas del `RequiredInstallmentCalendar`: sin omisiones, duplicados ni referencias ajenas.

Cada confirmación/no confirmación individual exige locator o `flow_id`. Los conflictos pueden carecer de soporte cuando la carencia sea el conflicto descrito. Los `flow_id` deben existir en el `FinanceBasicInput` capturado.

El outcome agregado mantiene precedencia determinista:

```text
NOT_CONFIRMED > CONFLICT_REPORTED > CONFIRMED_BY_REVIEW
```

El caller conserva el campo por compatibilidad del modelo, pero el builder rechaza cualquier discrepancia con el resultado derivado de las cuotas. Schema de revisión: `FLOW-INVENTORY-REVIEW-01/v0.2`.

No se modifica calendario, coverage, bindings, CashFlow, mandato, Finance, QTG o Evidence. La extensión conserva declaraciones humanas; no prueba por sí sola exigibilidad, soporte o inclusión económica.

## AUDITAR

A1: una tupla plana de referencias con outcome global permitiría ocultar diferencias entre cuotas. Se crean subhallazgos individuales.

A2: citar solo algunas cuotas podría presentarse como coherencia total. Se exige igualdad exacta con el calendario requerido.

A3: una cuota ajena o repetida rompería identidad. Se rechazan referencias desconocidas y duplicadas.

A4: un `flow_id` ajeno podría aparentar inclusión. Se contrasta contra todos los flujos de la preparación.

A5: outcome global suministrado podría contradecir detalles. Se deriva la precedencia y se exige coincidencia.

A6: permitir cuotas en otras condiciones contaminaría su alcance. `installment_findings` queda prohibido fuera de `PURCHASE_PAYMENT_COHERENCE`.

A7: confirmaciones individuales sin soporte serían afirmaciones desnudas. Se exige locator o flujo capturado relacionado.

A8: actualizar schema podría confundirse con autoridad nueva. v0.2 amplía trazabilidad, no eleva hallazgos ni habilita productor QTG.

## DEPURAR

A1–A8 incorporados. La revisión global conserva exactamente un hallazgo de coherencia, pero este contiene cobertura y outcome individual reproducibles para cada cuota. No se duplica el mandato ni se atribuye autoridad a la designación documental de pagos.

## AUDITAR 2

Pruebas específicas: **34 satisfactorias**. Se verifican omisión, duplicado, cuota ajena, flujo ajeno, soporte ausente, uso en condición incorrecta, discrepancia agregada y conservación de conflicto individual, además de toda la regresión previa de mandato/revisión.

Suite completa: **1.249 pruebas satisfactorias**, seis avisos preexistentes/no bloqueantes.

PASS técnico: el bloqueador `QTG-PROJECTION-INSTALLMENT-TRACE-01` queda resuelto físicamente dentro de las garantías descritas.

## CERRAR → MATERIALIZAR → CI

Material: `eios/core/flow_inventory_review.py`, `tests/test_flow_inventory_review_records.py` y este documento.

Cierre integrado condicionado a CI exact-head y post-merge. QTG continúa inhabilitado.

Siguiente unidad legítima: `QTG-PROJECTION-CRITERIA-MANIFEST-01`, diseño del manifiesto cerrado de criterios autorizados, versiones y hashes que el futuro productor podrá aceptar sin ejecutar texto arbitrario.
