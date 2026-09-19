# EIOS — QTG-PROJECTION-PRODUCER-01 — Contrato de productor y recibo v0.1

Fecha: 19/09/2026. Baseline remoto: `4d03bf7563d4c063b1b54290b7a302850f85150d`; PR #200 y CI #911/#912 SUCCESS.
Autoridad: aprobación explícita del titular de la separación `SYNTHETIC_TEST` / `OPERATIONAL`, junto con las seis funciones del manifiesto v0.2.
Estado: contrato diseñado y auditado; implementación y habilitación todavía pendientes.

## DISEÑAR — objeto y frontera

El futuro productor consumirá exclusivamente un `ProjectionMaterialEnvelope` construido y revalidado. Producirá un recibo inmutable y recomputable; no aceptará listas externas de `QualityCheck`, callbacks, estados, confianza ni `QualityTrustResult` previo.

Firma conceptual:

```text
produce_projection_quality(envelope, execution_mode) -> ProjectionQualityReceipt
```

Modos cerrados:

- `SYNTHETIC_TEST`: permite material sintético para probar el productor. El recibo queda marcado `operational_effect=false` y ningún consumidor operativo puede aceptarlo.
- `OPERATIONAL`: prohíbe cualquier naturaleza `SYNTHETIC`. Las naturalezas `PRESENTED_OPERATIONAL` continúan siendo material presentado; solo podrán sostener un resultado según las cadenas, mandatos, criterios y observaciones exigidos. El modo no presume autenticidad por etiqueta.

El productor seguirá siendo autónomo respecto al Vertical MVP. Implementarlo no retirará la cuarentena de invocación ni autorizará una decisión empresarial.

## Precondiciones técnicas

Antes de producir controles debe:

1. revalidar el envelope y todos sus vínculos/fingerprints;
2. exigir profile `PROJECTION_ONLY` y schemas compatibles exactos;
3. exigir manifiesto v0.2 con las seis funciones y coincidencia exacta de criterios;
4. recomputar el inventario estructural del envelope;
5. validar el modo;
6. rechazar `OPERATIONAL` si existe cualquier material sintético.

Un fallo de estas condiciones es error técnico. No se convierte en `NO_APTO`, porque no existe material evaluable identificado de forma segura.

## Catálogo cerrado de controles

El inventario se deriva determinísticamente del envelope y debe quedar completo antes del gate:

| Familia | Cardinalidad | Función manifiesta | Aplicabilidad/criticidad |
|---|---:|---|---|
| `PROJECTION_INITIAL_TREASURY` | exactamente 1 | `INITIAL_TREASURY_SUFFICIENCY` | aplicable y crítico para el perfil |
| `FLOW_INVENTORY_COMPLETENESS` | exactamente 1 | `HORIZON_FLOW_INVENTORY_COMPLETENESS` | aplicable y crítico |
| `FLOW_HORIZON_CLASSIFICATION:{flow_id}` | 1 por `CashFlow` capturado | inventario + preservación fuera de horizonte | aplicable y crítico para determinar participación/exclusión |
| `FLOW_AMOUNT_SUPPORT:{flow_id}` | 1 por flujo capturado | `PARTICIPATING_FLOW_ATTRIBUTE_SUPPORT` | crítico si participante/potencial; no aplicable solo tras exclusión `AFTER_HORIZON` demostrada |
| `FLOW_CURRENCY_SUPPORT:{flow_id}` | 1 por flujo capturado | igual | igual |
| `FLOW_DUE_DATE_SUPPORT:{flow_id}` | 1 por flujo capturado | igual | igual |
| `FLOW_ECONOMIC_MEMBERSHIP:{flow_id}` | 1 por flujo capturado | igual | igual |
| `FLOW_ECONOMIC_UNIQUENESS:{flow_id}` | 1 por flujo capturado | `ECONOMIC_FLOW_UNIQUENESS` | crítico si participante/potencial; no aplicable solo por exclusión demostrada |
| `PURCHASE_INSTALLMENT_COHERENCE:{installment_ref}` | 1 por cuota requerida | inventario + soporte individual + fiabilidad | aplicable y crítico |
| `PROJECTION_CONFLICTS_AND_LIMITATIONS` | exactamente 1 | `DETERMINATE_PROJECTION_RELIABILITY` + preservación | aplicable y crítico si existe incidencia necesaria o impacto no delimitable |

Los candidatos no capturados se consumen dentro de `FLOW_INVENTORY_COMPLETENESS` y `PROJECTION_CONFLICTS_AND_LIMITATIONS`; no se fabrica un `flow_id` para ellos.

El catálogo no contiene advertencias no críticas en v0.1. `APTO_CON_ADVERTENCIAS` permanece un resultado válido del gate, pero esta versión no inventará controles no críticos o materialidad sin autoridad específica.

## Traducción determinista

Cada control producido conserva:

- `control` canónico;
- `satisfied`: `True`, `False` o `None`;
- `critical`, `material` y `applicable` determinados por catálogo;
- razón canónica derivada de estados estructurados, sin interpretar notas como programa;
- referencias de evidencia/material existentes;
- función y entrada exacta del manifiesto utilizada;
- referencias a condiciones, flujos, cuotas y cadenas que lo originan.

Reglas generales:

- `True` requiere cadena completa, mandato acreditado, objetivo exacto, soporte exigido y ausencia de contradicción aplicable;
- `False` se reserva para contradicción/resultado negativo explícito;
- `None` conserva ausencia, pendiente o imposibilidad de evaluación;
- todo `False` o `None` crítico y aplicable conduce por el gate cerrado a `NO_APTO/BAJA`;
- `applicable=False` solo se permite en atributos/unicidad de un flujo con `AFTER_HORIZON` establecido y suficientemente soportado;
- fechas desconocidas, conflictivas o `NON_FUTURE` no permiten exclusión automática;
- la condición no aplicable y su motivo permanecen en el recibo aunque `QualityTrustResult.checks` la filtre;
- `material=False` se fija expresamente en v0.1 porque no se autorizan advertencias no críticas; nunca se usa para rebajar un bloqueo.

## Recibo inmutable

`ProjectionQualityReceipt` conservará como mínimo:

- schema, profile y `execution_mode`;
- `operational_effect` derivado exclusivamente del modo;
- envelope completo y fingerprint;
- productor ID/versión;
- catálogo ID/versión y fingerprint de su definición cerrada;
- manifiesto completo y fingerprint ya incluido en el envelope;
- inventario completo de controles producidos, incluidos no aplicables;
- `QualityCheck[]` exactos entregados al gate;
- `QualityTrustResult` retornado;
- referencias de procedencia por control;
- fingerprint canónico del recibo.

El builder no recibe `operational_effect`, resultado, confianza, controles ni fingerprints. Los deriva internamente.

## Ejecución y recomputación

Secuencia autorizada:

1. validar envelope y modo;
2. construir el inventario completo según catálogo;
3. verificar cardinalidad y ausencia de controles extra/duplicados/omitidos;
4. derivar `QualityCheck[]` aplicables;
5. llamar una sola vez a `evaluate_quality` sin modificarlo;
6. materializar el recibo con inventario y resultado;
7. recomputar desde envelope + modo para cualquier consumo posterior.

El validador de consumo reconstruirá todos los controles y volverá a ejecutar `evaluate_quality`. Rechazará cualquier diferencia de payload, fingerprint, catálogo, modo, checks, orden canónico, estado o confianza. No aceptará un receipt por coincidencia parcial ni un resultado desprendido.

## Frontera de consumo

- un recibo `SYNTHETIC_TEST` solo es consumible por pruebas explícitas y nunca habilita operación;
- un recibo `OPERATIONAL` informa calidad del componente `projection`, no de todo `FinanceBasicResult`, compra o decisión;
- `APTO` no autoriza ejecutar pagos, aprobar compra ni seleccionar escenario;
- la integración Vertical continúa bloqueada hasta una unidad posterior que audite invocación, consumo y cuarentena exactos;
- no se ejecuta Finance Basic dentro del productor: controla sus entradas antes del consumidor.

## AUDITAR

A1: aceptar checks suministrados permitiría obtener APTO con inventario parcial. Se construyen internamente y se verifica cardinalidad completa.

A2: el gate elimina checks no aplicables de su resultado. El recibo conserva el inventario completo previo.

A3: permitir `OPERATIONAL` con una sola pieza sintética podría presentar Mock Data como resultado real. Se rechaza antes del gate.

A4: marcar todo positivo por revisión humana elevaría declaraciones a verdad. Se exige cadena, mandato, soporte estructurado y ausencia de contradicción.

A5: usar `False` para faltantes borraría la diferencia entre contradicción e imposibilidad de evaluación. Se conserva `None`.

A6: hacer no aplicable un vencimiento desconocido permitiría excluir obligaciones. Solo `AFTER_HORIZON` demostrado habilita exclusión.

A7: un recibo con resultado guardado podría quedar obsoleto respecto del material. El consumo siempre recompone controles y gate.

A8: una identificación de productor libre permitiría cambiar política sin cambiar contrato. ID/versión y catálogo/fingerprint serán constantes de implementación cerradas.

A9: incluir candidatos sin flujo como pseudo-flujos inventaría identidad financiera. Se conservan en controles agregados.

A10: habilitar advertencias genéricas podría rebajar bloqueos necesarios. v0.1 no produce controles no críticos.

A11: ejecutar Finance dentro del productor invertiría la frontera de control de entrada. Queda prohibido.

A12: un APTO del perfil podría aparentar decisión favorable. El receipt carece de autoridad decisional y limita su afirmación a `projection`.

## DEPURAR

A1–A12 incorporados. Se separan:

```text
envelope válido → catálogo completo → checks → gate → recibo → recomputación
```

El modo forma parte de la identidad del recibo. No puede modificarse, promoverse o reutilizarse entre prueba y operación.

No se introducen umbrales, FX, tolerancias, heurísticas de deduplicación, prioridad documental, score, recomendación ni nuevos estados QTG.

## AUDITAR 2

PASS contractual:

- seis funciones autorizadas cubren el catálogo;
- inventario y cardinalidad cerrados antes del gate;
- aplicabilidad fuera de horizonte fail-closed;
- ausencia y contradicción diferenciadas;
- material sintético aislado de operación;
- resultado y receipt recomputables;
- gate, Finance y fronteras decisionales intactos;
- `APTO_CON_ADVERTENCIAS` no se fabrica sin política adicional.

DICTAMEN: **LISTO PARA IMPLEMENTAR EL PRODUCTOR AISLADO Y SU RECIBO**, pero no para habilitar su invocación en el Vertical.

Regresión documental: **1.279 pruebas satisfactorias**, seis avisos preexistentes/no bloqueantes.

## CERRAR → MATERIALIZAR → CI

Se cierra únicamente este contrato documental. Materialización: este documento. CI exact-head y post-merge obligatorias; su éxito no ejecuta ni habilita QTG.

Siguiente unidad legítima: implementar `QTG-PROJECTION-PRODUCER-01` y `ProjectionQualityReceipt` con pruebas negativas/positivas sintéticas, auditoría doble y CI, manteniendo intacta la cuarentena Vertical.
