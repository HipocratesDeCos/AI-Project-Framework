# EIOS — Examen Supplier Risk/Value de la empresa ficticia 002 v0.1

**Conclusión:** el fixture 002 identifica una compra y un proveedor, pero no
contiene hechos históricos, métricas externas, señales, candidatos ni una
evaluación de riesgo. Su precio de referencia PRICE tampoco demuestra
fiabilidad del proveedor. No hay base para declarar `FAVORABLE` o una ventaja
comparativa en la empresa 002.

## DISEÑAR → AUDITAR

Se revisaron `SupplierEvidenceInput`, `evaluate_supplier_evidence`,
`produce_supplier_risk_value`, el constructor observado y la observación del
caso 001. Son dos capas distintas:

| Capa | Qué conoce del 002 | Qué falta |
|---|---|---|
| Evidencia factual | Identidad de compra, artículo y proveedor del bundle 002. | Observaciones, historial, métricas, señales, candidatos y comparaciones propios. |
| Risk/Value externo | Puede ligar evaluaciones declaradas al proveedor actual y exigir evidencia de autoridad y de la declaración. | Assessment 002, metodología, evidencia y trazas propias; tampoco hay un segundo proveedor para comparar valor. |

El ejemplo 001 usa entradas factuales vacías y **añade por separado** una
declaración sintética `RELIABILITY=FAVORABLE`, con autoridad y referencias 001.
Su observación identifica ese origen como
`DECLARED_SYNTHETIC_EXTERNAL_ASSESSMENT`. Esa declaración no se traslada al
proveedor 002.

## DEPURAR → AUDITAR 2

| Entrada a Risk/Value | Salida del contrato actual | Interpretación correcta |
|---|---|---|
| Sin assessments | Sin dimensiones ni conclusiones; `COMPLETED` si `unresolved_items` está vacío. | Terminó la invocación; **no** significa riesgo favorable ni suficiencia de datos. |
| Assessment `NOT_DETERMINABLE` declarado con autoridad, evidencia y traza sintéticas | Dimensión explícita pendiente; `PARTIALLY_COMPLETED`. | Informa al lector de que no se ha determinado el riesgo, pero sigue siendo una declaración externa de prueba. |
| Assessment `FAVORABLE` como en 001 | Dimensión favorable si su autoridad y evidencia son válidas. | Solo sería una hipótesis ficticia explícita; el fixture 002 no la justifica por sí mismo. |

La capa externa valida identidad, autoridad demostrada y referencias de
evidencia, pero **no infiere** la calidad del proveedor a partir de un
inventario vacío. `result_available=true` en la adaptación indica que existe
un objeto resultado, no que exista dictamen favorable.

## CERRAR → MATERIALIZAR → CI

Se cierra el examen sin cambiar motor, contratos ni fixture. Para una
demostración 002 legible, la próxima unidad puede aportar una evaluación
**sintética y explícita** `RELIABILITY=NOT_DETERMINABLE`, ligada a
`COMPANY-MOCK-002` y a su proveedor, con autoridad y traza propias; dejar
`value_assessments=()` mientras no haya candidato comparable. Una prueba
deberá verificar la salida parcial y el rechazo de una compra ajena.

Hasta entonces, no se registra conclusión sobre riesgo/valor del proveedor
002 ni se afirma un segundo E2E. La ruta conserva
`SYNTHETIC · SYNTHETIC_TEST_ONLY · FORBIDDEN · NO_OPERATIONAL_EFFECT · decision_authority=false`.
Esta unidad es una auditoría estática y no requiere una prueba nueva.
