# EIOS — QTG-PROJECTION-ONLY-01 — Base de completitud de flujos v0.1

Fecha: 19/09/2026. Baseline remoto: `480f213fdf9cb9bc5dd68bcbdc0ae4e6f23a0e94`; PR #190 y CI #891/#892 SUCCESS.
Autoridad: aprobación explícita del titular del proyecto de `PROJECTION_ONLY` como primer alcance productor QTG y de sus cuatro criterios de inventario, acreditación, bloqueo por incompletitud y tratamiento de flujos fuera del horizonte.
Estado: base metodológica diseñada, auditada y cerrada; no implementa ni habilita el productor QTG.

## DISEÑAR — alcance y precedencia

Uso: valorar la calidad de las entradas necesarias para presentar la proyección de tesorería de `run_provenanced_finance_basic` como determinada y fiable en el piloto al corte `snapshot.as_of_date`.

`PROJECTION_ONLY` comprende exclusivamente:

1. tesorería inicial al corte;
2. cobros y pagos potencialmente relevantes hasta el horizonte autorizado;
3. correspondencia de empresa, corte, moneda, fuente y pertenencia económica;
4. inclusión única de los pagos de la compra;
5. `P-FIN-001` vinculado mediante la frontera de horizonte cerrada.

No comprende el margen de seguridad, `P-FIN-002`, fondo de maniobra ni liquidez externa. Su eventual ausencia no bloquea este perfil, pero tampoco queda valorada ni autorizada para publicación o consumo. El perfil no crea una ejecución parcial de Finance Basic: delimita únicamente la afirmación de calidad sobre el componente `projection` del resultado existente.

Fuentes y fronteras: FIN-AUTH-01/02/05/06; QTG v0.4 §§5–11; Evidence Contract; QTG-DIP-G01-FIN; QTG-FIN-G02-BASE-01; FIN-DIP-01; FIN-PILOT-CUT-01; FIN-PILOT-TREASURY-SUFF-01; QTG-FIN-INVENTORY-01 y contratos físicos cerrados de preparación, soporte, valoración, mandato, revisión de tesorería, calendario y cobertura de cuotas.

No se modifican `FinanceBasicInput`, `FinanceBasicResult`, el motor, `QualityCheck`, `evaluate_quality`, C0, Rules, PRICE, Scenario, Decision Twin ni ninguna frontera cerrada. QTG continúa en cuarentena.

## Base aprobada

| Criterio aprobado | Determinación para `PROJECTION_ONLY` | Límite obligatorio |
|---|---|---|
| Inventario del horizonte | Deben inventariarse todos los cobros y pagos potencialmente relevantes o declararse expresamente la incompletitud | Una colección recibida, incluso vacía, no demuestra por sí sola completitud empresarial |
| Acreditación individual | Cada flujo participante debe acreditar importe, moneda, vencimiento y pertenencia económica | `CashFlow.evidence_state = DEMONSTRATED`, `source_ref`, igualdad de importe o `flow_id` no sustituyen la observación QTG suficiente |
| Incompletitud necesaria | Si no puede demostrarse la completitud necesaria, queda bloqueada la afirmación de proyección determinada fiable | Para este uso constituye condición crítica no evaluable: `NO_APTO / BAJA` conforme a QTG §9, sin alterar el resultado analítico de Finance Basic |
| Fuera del horizonte | Un flujo demostrablemente posterior a `horizon_end` no bloquea la proyección del perfil | Su soporte, conflictos y trazabilidad se conservan; no se elimina ni se declara irrelevante para otros usos |

La base no presume completitud ERP, no interpreta ausencia como cero y no convierte una declaración de completitud en prueba autosuficiente.

## Horizonte y relevancia potencial

El intervalo gobernado es `snapshot.as_of_date < due_date <= horizon_end`, con `horizon_end` derivado de `P-FIN-001` por el contrato cerrado.

Un flujo es potencialmente relevante cuando no se ha demostrado que quede fuera del intervalo y puede alterar cobros o pagos de la empresa dentro de él. En particular:

- vencimiento desconocido, no evidenciado o contradictorio no permite clasificar el flujo como externo al horizonte;
- un vencimiento igual o anterior a `as_of_date` requiere conservar su tratamiento y conflicto, pero esta base no inventa una política de vencidos ni modifica el motor;
- solo una fecha suficientemente soportada permite excluir un flujo por ser posterior a `horizon_end`;
- la fecha de emisión, captura o revisión no sustituye automáticamente al vencimiento económico.

La pertenencia económica exige justificar que el flujo corresponde —o no corresponde— al `company_scope` y al perímetro financiero evaluado. Para pagos de la compra exige además la cadena de cuota y cobertura ya cerrada. No se deduce por coincidencia de proveedor, importe, texto, `flow_id` o `source_ref`.

## Completitud del inventario

La completitud es una propiedad del inventario respecto del alcance declarado, sus fuentes y el horizonte; no una propiedad automática de `tuple[CashFlow, ...]`.

Una futura observación suficiente deberá conservar como mínimo:

- captura/preparación financiera exacta y su identidad;
- empresa, corte, horizonte y moneda examinados;
- fuentes o perímetros consultados y su cobertura declarada;
- flujos encontrados, ausencias o limitaciones detectadas;
- flujos potencialmente relevantes cuya determinación permanece pendiente;
- justificación y soporte de exclusiones por fecha o pertenencia;
- conflictos y riesgos de duplicación económica;
- naturaleza sintética/presentada y, si se usa comprobación humana autorizada, su mandato exacto.

Una declaración humana o de sistema puede formar parte del material, pero no se valida a sí misma. Su suficiencia requiere contraste reproducible con soporte admisible para el perímetro afirmado. Esta base no exige un ERP concreto, número universal de fuentes, conciliación bancaria completa, OCR, firma digital ni catálogo contable; cuando el perímetro no pueda demostrarse, la incompletitud permanece explícita.

## Acreditación y cómputo único

Para participar como flujo fiable deben quedar suficientemente soportados importe, moneda, vencimiento y pertenencia económica. La moneda debe ser compatible con la del snapshot o disponer de una normalización FX expresamente autorizada; este perfil no crea esa normalización.

La identidad técnica única de `flow_id` evita duplicados de identificador dentro de `FinanceBasicInput`, pero no demuestra cómputo económico único. Dos registros con IDs distintos pueden representar la misma obligación o cobro. La futura observación debe conservar y tratar ese riesgo sin fusionar, escoger o cancelar registros mediante heurística no autorizada.

Los pagos de compra mantienen su cadena especializada de calendario, binding, cobertura, revisión y designación. Un pago cubierto no demuestra la completitud de otros pagos o cobros; la completitud global tampoco corrige una cuota contradictoria.

## Traducción futura a QTG

Esta autoridad permite diseñar después un registro de observación y, solo cuando exista soporte físico suficiente, el productor determinista de controles para `PROJECTION_ONLY`.

Tratamiento autorizado:

- completitud necesaria no demostrable, flujo necesario sin acreditación suficiente o contradicción crítica no resuelta: control aplicable crítico no satisfecho/no evaluable y resultado global `NO_APTO / BAJA`;
- todos los controles aplicables suficientemente satisfechos y sin limitaciones relevantes: podrá corresponder `APTO / ALTA` únicamente si el productor demuestra inventario completo y no omite controles;
- una limitación no crítica solo podrá producir advertencia cuando su no criticidad, materialidad y efecto estén justificados; esta autoridad no inventa tales casos ni umbrales.

Los errores de construcción, binding o modelos inválidos siguen siendo errores técnicos. Los estados de `CashFlow` y `ProjectionResult` no se recodifican automáticamente como estados QTG. No se invoca `evaluate_quality` mientras el productor no cubra el inventario completo exigido por este perfil.

## AUDITAR

A1: “todos los flujos” podría convertirse en una exigencia empresarial ilimitada. Se acota al `company_scope`, corte, horizonte y perímetro cuya completitud se pretende afirmar, conservando cualquier limitación del perímetro.

A2: un vencimiento ausente podría permitir omisión silenciosa. Se clasifica como potencialmente relevante hasta demostrar lo contrario.

A3: una lista completa declarada podría autoacreditarse. Se exige soporte reproducible; declaración y demostración permanecen separadas.

A4: `DEMONSTRATED` financiero podría confundirse con suficiencia QTG. Se conserva la separación de estados y autoridad.

A5: unicidad de `flow_id` podría confundirse con cómputo económico único. Se exige observación separada del riesgo de duplicación.

A6: excluir flujos fuera del horizonte podría borrar conflictos. Solo se evita su efecto bloqueante para este perfil; el material y los conflictos se conservan.

A7: cerrar `PROJECTION_ONLY` podría presentar todo Finance Basic como fiable. La afirmación queda limitada a `projection`; margen, fondo de maniobra y liquidez externa permanecen fuera.

A8: traducir incompletitud a `NO_APTO` podría modificar Finance Basic. El tratamiento pertenece exclusivamente al futuro resultado QTG y no altera cálculos ni estados analíticos.

## DEPURAR

Se incorporan A1–A8. Se distingue flujo capturado, flujo acreditado, inventario completo y proyección analítica. No se fija fuente universal, tolerancia temporal, umbral monetario, regla de deduplicación, prioridad documental ni comprobador operativo.

La ausencia explícita de completitud permite conservar material y diagnóstico, pero no autoriza una proyección fiable. Los datos sintéticos permiten probar contratos futuros, nunca acreditar un caso empresarial.

## AUDITAR 2

PASS metodológico:

- perfil y afirmación de calidad acotados;
- los cuatro criterios aprobados quedan representados sin ampliación económica;
- relevancia potencial impide excluir fechas desconocidas;
- completitud, acreditación y deduplicación permanecen separadas;
- fuente presentada, declaración humana y demostración suficiente no se colapsan;
- ausencia, incertidumbre y contradicción se preservan;
- opcionales ajenos al perfil no bloquean ni quedan certificados;
- QTG, Finance Basic y fronteras cerradas permanecen intactos.

HALLAZGO: todavía no existe un registro físico especializado que observe la completitud de cobros y otros pagos, sus exclusiones y el riesgo de duplicación económica. Por tanto, aún no es legítimo implementar un productor QTG positivo ni retirar la cuarentena.

## CERRAR → MATERIALIZAR → CI

Se cierra únicamente `QTG-PROJECTION-ONLY-01` como autoridad metodológica del primer perfil. La materialización consiste en este documento. CI exact-head y post-merge son obligatorias; su éxito demuestra ausencia de regresión, no completitud empresarial ni un resultado QTG.

Siguiente unidad legítima: diseñar el contrato del registro de completitud de flujos vinculado a la `FinanceQualityPreparation` exacta, con observaciones por flujo, perímetro consultado, exclusiones justificadas, limitaciones y duplicación económica. No aceptará `QualityCheck`, `QualityTrustResult`, booleanos de cumplimiento libres ni callbacks opacos, y no ejecutará Finance/QTG.
