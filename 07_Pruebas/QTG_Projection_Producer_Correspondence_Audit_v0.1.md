# EIOS — QTG-PROJECTION-PRODUCER-CORRESPONDENCE-01 — Auditoría v0.1

Fecha: 19/09/2026. Baseline remoto: `e42b070ee5f2d0979b0d8c84c9e80e28df334b49`; PR #198 y CI #907/#908 SUCCESS.
Estado: correspondencia auditada; productor positivo todavía bloqueado por una autoridad manifiesta incompleta.

## DISEÑAR — objetivo

Contrastar `ProjectionMaterialEnvelope`, las autoridades cerradas y `QualityCheck` para determinar, antes de implementar, qué controles puede producir `PROJECTION_ONLY`, con qué criterio, aplicabilidad y criticidad.

No se implementa productor, recibo ni consumo; no se llama `evaluate_quality`; no se modifica el gate, Finance Basic, Rules, C0, PRICE, Scenario o Decision Twin.

## Frontera técnica previa

Las siguientes comprobaciones son precondiciones de construcción, no controles QTG:

- tipo e integridad del envelope;
- coincidencia completa de payloads y fingerprints;
- correspondencia exacta de preparación, manifiesto y cadenas;
- schemas, purpose scopes y modelos válidos;
- coincidencia reference/version/hash de criterios.

Su incumplimiento debe seguir siendo error técnico. Convertirlo en `NO_APTO` permitiría evaluar material que el productor ni siquiera puede identificar con seguridad.

## Matriz de correspondencia auditada

| Control productor candidato | Material determinante | Función/autoridad | Aplicabilidad | Criticidad autorizada | Estado de diseño |
|---|---|---|---|---|---|
| `PROJECTION_INITIAL_TREASURY` | soporte → contexto → mandato → revisión de tesorería; seis condiciones, comparaciones y restricciones | `FIN-PILOT-TREASURY-SUFF-01` | Siempre, porque la tesorería inicial es necesaria para afirmar una proyección determinada | Crítico cuando falta o existe contradicción no resuelta que impide acreditarla | **BLOQUEADO**: autoridad documental existente, pero ninguna función/identidad de tesorería figura en `ProjectionCriteriaManifest` |
| `FLOW_INVENTORY_COMPLETENESS` | perímetros, fuentes, declaración de cobertura, candidatos, pendientes y revisión autorizada | `HORIZON_FLOW_INVENTORY_COMPLETENESS` | Siempre para el perfil | Crítico: incompletitud necesaria impide afirmar fiabilidad | CERRABLE por contrato productor |
| `FLOW_HORIZON_CLASSIFICATION:{flow_id}` | vencimiento capturado, estado de vencimiento, `horizon_relevance`, corte/horizonte y revisión | `HORIZON_FLOW_INVENTORY_COMPLETENESS` + `OUT_OF_HORIZON_CONFLICT_PRESERVATION` | Para todo flujo capturado o candidato que pueda afectar el inventario | Crítico si no permite determinar participación o exclusión posterior al horizonte | CERRABLE; `AFTER_HORIZON` requiere soporte establecido, no etiqueta aislada |
| `FLOW_AMOUNT_SUPPORT:{flow_id}` | assessment de importe, locators y revisión `FLOW_ATTRIBUTE_SUPPORT` referida al flujo | `PARTICIPATING_FLOW_ATTRIBUTE_SUPPORT` | Solo si el flujo es participante o potencialmente relevante | Crítico para participante; no aplicable únicamente tras demostrar `AFTER_HORIZON` | CERRABLE con inventario íntegro de controles, incluidos los no aplicables y su razón |
| `FLOW_CURRENCY_SUPPORT:{flow_id}` | assessment de moneda, moneda del snapshot, soporte y revisión | `PARTICIPATING_FLOW_ATTRIBUTE_SUPPORT` | Igual que importe | Crítico para participante; FX no autorizado impide satisfacción | CERRABLE sin inventar conversión |
| `FLOW_DUE_DATE_SUPPORT:{flow_id}` | assessment de vencimiento, fecha capturada, soporte y revisión | `PARTICIPATING_FLOW_ATTRIBUTE_SUPPORT` | Igual que importe; además sostiene clasificación de horizonte | Crítico mientras el flujo no pueda excluirse de forma demostrada | CERRABLE |
| `FLOW_ECONOMIC_MEMBERSHIP:{flow_id}` | assessment de pertenencia, candidato/perímetro, identidad económica, soporte y revisión | `PARTICIPATING_FLOW_ATTRIBUTE_SUPPORT` | Igual que importe | Crítico para participante o potencialmente relevante | CERRABLE |
| `FLOW_ECONOMIC_UNIQUENESS:{flow_id}` | `economic_identity_ref`, `duplication_assessment`, candidatos relacionados y revisión | Base `PROJECTION_ONLY` de cómputo único | Para participante o potencialmente relevante | Crítico cuando la duplicación no resuelta puede alterar la proyección | **PARCIAL**: autoridad metodológica existe, pero no tiene función propia explícita en el manifiesto; no debe ocultarse bajo soporte de atributos |
| `PURCHASE_INSTALLMENT_COHERENCE:{installment_ref}` | calendario, bindings, cobertura y subhallazgo individual de revisión de flujos | Inventario + acreditación individual + FIN-AUTH-05 | Para cada cuota requerida de la compra | Crítico si su inclusión/coherencia necesaria no queda acreditada | CERRABLE, sin atribuir autoridad adicional a la revisión documental de pagos |
| `PROJECTION_CONFLICTS_AND_LIMITATIONS` | conflictos, limitaciones, pendientes, candidatos y referencias afectadas | `DETERMINATE_PROJECTION_RELIABILITY` + preservación fuera de horizonte | Cuando exista conflicto o limitación conservada | Crítico si afecta material necesario; no bloqueante solo si está demostrado que queda fuera del horizonte | **PARCIAL**: conflictos sin objetivo estructuralmente delimitado deben bloquear; no se autoriza inferir no criticidad desde una nota libre |
| `SYNTHETIC_MATERIAL_BOUNDARY` | `contains_synthetic_material` y naturalezas por origen | Fronteras cerradas de Mock Data | En ejecución que pretenda resultado empresarial | Impide emitir resultado operativo; no es un `QualityCheck` económico | **BLOQUEO DE MODO**: el futuro contrato debe separar ejecución sintética de operativa |

## Reglas de traducción seguras

1. `CONFIRMED_BY_REVIEW`, `DECLARED_CONSISTENT`, `DECLARED_COMPLETE` o `ESTABLISHED` aislados nunca generan `satisfied=True`.
2. Un control positivo exige toda su cadena aplicable, mandato acreditado, condición presente, soporte estructural requerido, ausencia de contradicción y referencias al objetivo exacto.
3. `NOT_CONFIRMED`, `NOT_ESTABLISHED`, `CONFLICTING`, pendientes o incompletitud no se convierten en un incumplimiento económico demostrado; para un requisito crítico producen `satisfied=None` o `False` según sea ausencia/no evaluabilidad o contradicción, conservando la razón original.
4. Los controles de atributos de un flujo solo pueden usar `applicable=False` cuando una clasificación `AFTER_HORIZON` suficientemente soportada lo excluya. Fecha desconocida, conflictiva o no futura no autoriza exclusión.
5. Los conflictos del flujo excluido se conservan en el inventario/recibo aunque el gate no los consuma como bloqueantes de este perfil.
6. No existe caso de advertencia no crítica autorizado para la primera versión. Por ello `APTO_CON_ADVERTENCIAS` no debe fabricarse para rellenar huecos; cualquier futura advertencia exige autoridad adicional de relevancia y materialidad.
7. El inventario del productor debe conservar también controles no aplicables y su justificación. `QualityTrustResult.checks` filtra los no aplicables, por lo que el recibo no puede limitarse al resultado del gate.

## AUDITAR

A1: usar uno de los cuatro criterios de flujos para tesorería ampliaría su función por analogía. Se declara bloqueo manifiesto.

A2: colapsar importe, moneda, vencimiento y pertenencia en un control impediría localizar el atributo no acreditado. Se exigen controles por atributo y flujo.

A3: declarar todos los controles globalmente críticos contradiría la aplicación contextual. Se fija criticidad por necesidad para el perfil y exclusión únicamente demostrada.

A4: hacer no crítico todo flujo posterior podría borrar conflictos. Se separan efecto bloqueante y conservación en recibo.

A5: `QualityTrustResult` elimina checks no aplicables. El recibo debe preservar el inventario productor completo y el resultado recomputable.

A6: material sintético podría generar `APTO/ALTA` en pruebas y aparentar operación. Se exige modo explícito; una ejecución sintética nunca es recibo empresarial.

A7: duplicación económica no es uno de los cuatro atributos y no debe esconderse dentro de ellos. Requiere función manifiesta propia o asignación explícita autorizada.

A8: las limitaciones libres no permiten deducir materialidad/no criticidad. Si afectan un requisito necesario o no puede delimitarse su impacto, bloquean el productor positivo.

A9: ejecutar el gate con solo controles construibles todavía permitiría APTO por omisión. El catálogo y la cardinalidad se cierran antes de cualquier llamada.

## DEPURAR

A1–A9 incorporados. La matriz distingue:

- errores técnicos previos;
- controles QTG críticos del perfil;
- controles no aplicables por exclusión demostrada;
- material que debe permanecer en el recibo aunque no bloquee;
- bloqueos de autoridad que impiden construir el catálogo completo.

No se define un umbral monetario, tolerancia temporal, FX, algoritmo de deduplicación, prioridad documental ni advertencia genérica.

## AUDITAR 2

PASS de correspondencias ya autorizadas: inventario, horizonte, cuatro atributos, cuotas e incompletitud necesaria pueden traducirse sin cambiar el gate ni Finance.

FAIL de completitud del productor: faltan en el manifiesto ejecutable:

1. una función/identidad autorizada para suficiencia de tesorería inicial;
2. una asignación explícita para unicidad económica, separada de los cuatro atributos;
3. el contrato de modo y recibo que impida presentar pruebas sintéticas como resultado operativo.

DICTAMEN: **NO IMPLEMENTAR AÚN EL PRODUCTOR POSITIVO**. El bloqueo no procede del gate ni del envelope, sino de la correspondencia incompleta entre autoridad documental y manifiesto ejecutable.

## CERRAR → MATERIALIZAR → CI

Se cierra únicamente esta auditoría diagnóstica. Materialización: este documento. CI exact-head y post-merge obligatorias; su éxito no habilita QTG.

## Siguiente decisión recomendada

Autorizar una extensión `QTG-PROJECTION-CRITERIA-MANIFEST-02` con dos funciones adicionales, sin cambiar los cuatro criterios ya cerrados:

- `INITIAL_TREASURY_SUFFICIENCY`, vinculada a `FIN-PILOT-TREASURY-SUFF-01`;
- `ECONOMIC_FLOW_UNIQUENESS`, vinculada a la exigencia ya cerrada de cómputo único.

Después deberá diseñarse el contrato productor/recibo con modos `SYNTHETIC_TEST` y `OPERATIONAL`, manteniendo la cuarentena hasta superar su implementación, auditorías y CI.
