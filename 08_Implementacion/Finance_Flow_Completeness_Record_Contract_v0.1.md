# EIOS — FIN-FLOW-COMP-01 — Contrato del registro de completitud de flujos v0.1

Fecha: 19/09/2026. Base de trabajo local: `57b8fa2` sobre `main @ 480f213fdf9cb9bc5dd68bcbdc0ae4e6f23a0e94`.
Dependencia: `QTG-PROJECTION-ONLY-01`, pendiente de integración remota por indisponibilidad de credenciales de escritura en esta sesión.
Estado: diseño técnico auditado; no implementa el registro, productor QTG ni ejecución financiera.

## DISEÑAR — propósito y frontera

Materializar en una unidad posterior un registro inmutable que conserve qué perímetro de cobros y pagos fue examinado, qué fuentes se presentaron, cómo se relacionan sus candidatos con los `CashFlow` capturados y qué limitaciones, exclusiones o posibles duplicaciones fueron declaradas.

El registro se vincula a una `FinanceQualityPreparation` construida y exacta. No modifica su captura, no incorpora flujos nuevos a `FinanceBasicInput`, no calcula la proyección y no acredita que las declaraciones sean verdaderas. Su única garantía será conservación y coherencia técnica del material presentado.

Fuentes: QTG-PROJECTION-ONLY-01; FIN-AUTH-01/05; QTG v0.4; Evidence Contract; FIN-DIP-01; QTG-FIN-PREP-01; DOC-PAY-CAP/COVER-01 y contratos Finance Basic v0.3/v0.3.1.

No recibe ni produce `QualityCheck`, `QualityTrustResult`, `FinanceBasicResult`, `ProjectionResult`, `Assessment` o decisión empresarial. No acepta callbacks, verificadores opacos ni booleanos libres `complete`, `valid`, `authorized`, `critical`, `material` o `satisfied`.

## Entrada obligatoria

| Elemento | Obligación |
|---|---|
| Preparación financiera | `FinanceQualityPreparation` construida; payload y fingerprint completos |
| Referencia del registro | No vacía y sin espacios periféricos; identifica el registro presentado, no una entidad empresarial |
| Perímetros examinados | Tupla explícita no vacía de `FlowInventoryPerimeter` |
| Material documental | Tupla explícita de documentos con bytes íntegros, referencia única y hash calculado |
| Candidatos observados | Tupla explícita de `FlowInventoryCandidate`; puede ser vacía únicamente como declaración conservada, nunca como prueba automática de ausencia |
| Valoraciones de flujos capturados | Tupla explícita de `CapturedFlowAssessment`; parcialidad visible |
| Naturaleza | `SYNTHETIC` o `PRESENTED_OPERATIONAL`; no implica autenticidad ni suficiencia |
| Autor/momento presentados | Ambos o ninguno; referencia no vacía y fecha-hora con zona, sin inferir competencia o mandato |

El registro reconstruirá y revalidará todos los modelos recibidos. Las colecciones deben ser tuplas explícitas para distinguir material presentado de defaults accidentales.
La naturaleza propia del registro no reemplaza ni eleva las naturalezas ya conservadas dentro de la preparación. Si cualquiera de sus materiales dependientes es sintético, una etiqueta posterior `PRESENTED_OPERATIONAL` no convierte la cadena en acreditación operativa.

## Perímetro de inventario

`FlowInventoryPerimeter` conserva:

- `perimeter_ref` único;
- `description` no vacía;
- `company_scope`, `as_of_date`, `horizon_end` y `currency`, que deben coincidir exactamente con la preparación;
- `source_refs` no vacías y sin duplicados, referidas a documentos conservados;
- `coverage_declaration`: `DECLARED_COMPLETE`, `DECLARED_INCOMPLETE` o `NOT_ESTABLISHED`;
- `coverage_reason` no vacía;
- `limitations` explícitas, sin convertir tupla vacía en certeza universal.

Todos los perímetros del registro pertenecen al mismo contexto y horizonte derivados de la preparación. Varios perímetros no se agregan automáticamente como completos: el registro conserva cada declaración y sus límites, pero no decide si su unión cubre toda la empresa.

`DECLARED_COMPLETE` expresa una afirmación presentada sobre ese perímetro. No autoriza `APTO`, no demuestra ausencia de fuentes laterales y no puede derivarse del mero número de documentos o candidatos.

## Candidatos observados

`FlowInventoryCandidate` representa una obligación o derecho de cobro localizado en el material, exista o no un `CashFlow` capturado equivalente. Conserva:

- `candidate_ref` único;
- `perimeter_ref` existente;
- `declared_flow_type`: `PAYMENT`, `COLLECTION` o `NOT_ESTABLISHED`;
- `captured_flow_id` opcional, que si existe debe referir un flujo de la preparación;
- `amount_assessment`, `currency_assessment`, `due_date_assessment` y `economic_membership_assessment`: cada uno `ESTABLISHED`, `NOT_ESTABLISHED` o `CONFLICTING`;
- `horizon_relevance`: `WITHIN_HORIZON`, `AFTER_HORIZON`, `NON_FUTURE`, `NOT_ESTABLISHED` o `CONFLICTING`;
- `economic_identity_ref` opcional, como referencia declarada para estudiar duplicación, nunca como clave verdadera generada por EIOS;
- `locators` no vacíos hacia documentos conservados;
- `note` no vacía.

Reglas de coherencia:

1. `AFTER_HORIZON` exige valoración de vencimiento `ESTABLISHED` y localizador; la implementación contrasta que el `due_date` capturado, cuando exista, sea posterior al horizonte. No interpreta texto documental.
2. `NON_FUTURE` exige vencimiento establecido y, cuando exista fecha capturada, contrasta `due_date <= as_of_date`; no inventa política para vencidos.
3. Vencimiento `NOT_ESTABLISHED` o `CONFLICTING` obliga a relevancia `NOT_ESTABLISHED` o `CONFLICTING`, nunca `AFTER_HORIZON`.
4. Un vínculo a `captured_flow_id` conserva correspondencia declarada; no prueba que el candidato y el flujo sean económicamente idénticos.
5. Un candidato sin flujo capturado permanece visible. El builder no crea, modifica ni completa un `CashFlow`.
6. Varios candidatos pueden referir el mismo flujo y varios flujos pueden compartir `economic_identity_ref`; se conserva la posible duplicación y no se fusionan registros.

## Valoración de cada flujo capturado

`CapturedFlowAssessment` conserva como máximo una entrada por `flow_id` de la preparación:

- `flow_id` existente;
- `candidate_refs` relacionadas, sin duplicados;
- estados de importe, moneda, vencimiento y pertenencia económica con el mismo vocabulario local;
- `duplication_assessment`: `DECLARED_UNIQUE`, `POSSIBLE_DUPLICATE`, `CONFLICTING` o `NOT_ESTABLISHED`;
- `horizon_relevance` con el inventario anterior;
- referencias/versiones de criterios ya conservados en la preparación;
- justificación y localizadores no vacíos.

`DECLARED_UNIQUE` no se admite sin al menos un candidato vinculado y soporte localizado. Aun así continúa siendo una declaración presentada, no una deduplicación certificada. Un mismo `economic_identity_ref` asociado a más de un flujo impide declarar todos ellos únicos dentro del propio registro; se conserva como posible duplicación o conflicto.

Los `flow_id` omitidos se publican como `pending_flow_ids`. Los candidatos sin correspondencia se publican como `unmatched_candidate_refs`. Registro completo significa solamente que todos los flujos capturados tienen valoración; no demuestra que estén capturados todos los flujos empresariales.

## Material, identidad y validación

El futuro objeto será `dataclass(frozen=True, init=False)`, creado únicamente por builder. Conservará JSON canónico UTF-8, payload íntegro de preparación, fingerprints calculados, documentos en Base64 con SHA-256 calculado, colecciones en orden y exportaciones independientes.

Cambiar preparación, criterio, perímetro, documento, candidato, valoración, naturaleza, autor, momento, nota o locator produce identidad distinta. Un validador exigirá igualdad completa de payload y fingerprint con la preparación exacta; no aceptará coincidencia parcial de IDs, empresa, fecha o hash suministrado.

Referencias y secciones no vacías y sin espacios periféricos; páginas positivas; referencias únicas por categoría y sin colisiones documentales. Los locators solo pueden apuntar a documentos conservados en este registro o, con origen tipado, a documentos ya conservados en la captura contenida en la preparación.

Errores de modelo, vínculo, fecha o referencia son errores técnicos. No se traducen a `NO_APTO`.

## Frontera de autoridad y consumo futuro

`assurance_scope = BOUND_PRESENTED_FLOW_INVENTORY_DECLARATIONS_ONLY`.

El registro no autentica fuentes, no prueba completitud, no acredita pertenencia, no determina criticidad/materialidad y no comprueba mandato humano. `PRESENTED_OPERATIONAL` solo describe naturaleza aportada. Si posteriormente se necesita una comprobación humana autorizada, deberá existir mandato especializado para inventario de flujos; no se reutilizan automáticamente los mandatos cerrados de pagos o tesorería.

Un futuro productor podrá examinar este registro únicamente junto con la preparación y los demás soportes especializados requeridos. Antes de traducir declaraciones a controles deberá:

1. comprobar pertenencia exacta del material;
2. verificar que el inventario de perímetros y flujos requerido está cubierto;
3. resolver mediante autoridad admisible —no por el builder— la suficiencia de fuentes y observaciones;
4. conservar candidatos no capturados, fechas desconocidas, conflictos y duplicaciones;
5. recomputar los controles aplicables sin aceptar estados QTG suministrados.

La ausencia de una valoración o una declaración `NOT_ESTABLISHED` permanece pendiente. Este objeto no invoca `evaluate_quality`, aunque todas las declaraciones sean positivas.

## AUDITAR

A1: limitarse a valorar `cash_flows` capturados impediría detectar omisiones. Se introducen candidatos observados independientes y `unmatched_candidate_refs`.

A2: una declaración global de completitud podría ocultar perímetros parciales. Se conserva por perímetro, con fuentes y limitaciones, sin agregación automática.

A3: representar solo `WITHIN/OUTSIDE` permitiría excluir vencidos o fechas dudosas. Se añaden `NON_FUTURE`, `NOT_ESTABLISHED` y `CONFLICTING`, coherentes con el motor cerrado.

A4: igualdad de `flow_id` o `economic_identity_ref` podría presentarse como deduplicación. Ambos son vínculos declarados; el registro conserva multiplicidades y prohíbe positivos internamente incompatibles.

A5: exigir que todo candidato tenga flujo capturado borraría el principal hallazgo de incompletitud. Se permiten candidatos no vinculados sin modificar FinanceBasicInput.

A6: un registro con todos los flujos valorados podría confundirse con inventario empresarial completo. `pending_flow_ids` y cobertura del perímetro permanecen garantías distintas.

A7: autor y fecha podrían aparentar mandato. Se conservan como metadatos presentados y se pospone cualquier revisión autorizada a un contrato especializado.

A8: locators podrían apuntar fuera del material. Se tipa su origen y se valida pertenencia exacta.

A9: una colección vacía podría fabricar ausencia de actividad. Se permite conservarla, pero nunca produce completitud ni resultado positivo por construcción.

A10: una naturaleza operativa declarada en el registro podría ocultar Mock Data previo. Se conservan todas las naturalezas por separado y se prohíbe su promoción por envoltura.

## DEPURAR

Se incorporan A1–A10. El contrato separa cinco planos: material presentado, perímetro declarado, candidatos observados, flujos capturados y futura evaluación QTG. No crea OCR, búsqueda ERP, conciliación, identidad económica automática, prioridad documental, regla de vencidos, autenticación o mandato.

Las comprobaciones del builder son únicamente estructurales y reproducibles. Los estados locales usan `DECLARED`, `ASSESSMENT` o `NOT_ESTABLISHED` y no reutilizan semántica de Evidence, CashFlow, ProjectionResult o QTG.

## AUDITAR 2

PASS de diseño:

- vínculo íntegro a la preparación exacta;
- omisiones representables mediante candidatos sin flujo;
- todos los flujos capturados inventariables sin presumir completitud empresarial;
- horizonte, vencidos y fechas inciertas diferenciados;
- importe, moneda, vencimiento y pertenencia evaluados por separado;
- posible doble cómputo visible sin heurística de fusión;
- declaraciones, soporte, mandato y verdad empresarial no colapsados;
- parcialidad y colecciones vacías no producen éxito;
- Finance, QTG, C0 y componentes cerrados permanecen aislados.

HALLAZGO NO BLOQUEANTE PARA EL DISEÑO: aún faltará definir e implementar el procedimiento o revisión autorizada que pueda sustentar las declaraciones operativas. Este registro por sí solo no resuelve G03 ni autoriza un productor positivo.

## CERRAR → MATERIALIZAR → CI

Se cierra únicamente el diseño `FIN-FLOW-COMP-01`. Materialización: este contrato documental. Su implementación requerirá nuevo ciclo, pruebas sintéticas y CI completa. No debe implementarse ni integrarse antes de que `QTG-PROJECTION-ONLY-01` esté disponible en `main`.

Siguiente unidad tras integrar la autoridad previa: implementar el registro y validadores con Mock Data, cubriendo preparación ajena, perímetros parciales, candidato sin flujo, flujo sin valoración, fechas desconocidas, exclusión posterior válida/inválida, vencidos, duplicaciones, locators ajenos, modelos construidos por bypass, mutabilidad y aislamiento de Finance/QTG.
