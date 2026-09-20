# EIOS — QTG-PROJECTION-SYNTHETIC-E2E-01 — Contrato de ensayo v0.1

**Baseline:** `main @ e259ddf04aa5114923cff418441da08805d4031e`

**Estado:** DISEÑADO → AUDITADO → DEPURADO — MATERIALIZACIÓN DE PRUEBA PENDIENTE

## DISEÑAR

Validar de extremo a extremo, sin introducir nueva frontera de producción:

```text
ProjectionMockDataset SYNTHETIC
→ ProjectionOnlySyntheticMaterialBundle
→ ProjectionMaterialEnvelope
→ produce_projection_quality(..., SYNTHETIC_TEST)
→ ProjectionQualityReceipt
→ consume_projection_quality(..., TEST_ONLY)
→ ProjectionQualityConsumption
```

El ensayo usa exclusivamente APIs públicas ya cerradas. No crea wrapper, invoker, adaptador QTG adicional ni vínculo con O1/Vertical.

Se ensayan dos casos:

1. fixture semántica física actual: material construible pero con limitaciones/soporte de revisión insuficiente para una afirmación positiva;
2. variante Mock Data explícita sin esas limitaciones y con findings por flujo completos: resultado sintético positivo, siempre sin efecto operacional.

## AUDITAR

**A1 — confundir completitud del bundle con calidad.** Prohibido. S7 acredita construcción y pertenencia; el productor QTG decide el resultado desde su catálogo.

**A2 — convertir un APTO sintético en autorización.** Prohibido. `SYNTHETIC_TEST` y `TEST_ONLY` conservan `operational_effect=false` y `decision_authority=false`.

**A3 — crear un nuevo orquestador.** Innecesario y peligroso. El ensayo llama secuencialmente a las APIs existentes y no añade código de producción.

**A4 — ocultar un resultado negativo de la fixture física.** Se conserva. La fixture incluye una limitación declarada y no aporta binding por flujo en tres findings especializados; el productor debe reflejarlo.

**A5 — fabricar positivo mediante cambio de etiqueta.** Prohibido. La variante positiva continúa declarando `SYNTHETIC`; solo completa material permitido dentro del mismo contrato.

**A6 — usar modo OPERATIONAL.** Debe fallar porque el envelope recompone naturaleza sintética.

**A7 — receipt desprendido.** Se valida por recomputación contra el envelope exacto.

**A8 — consumo desprendido.** Se valida por recomputación contra receipt, envelope, modo y scope exactos.

**A9 — ejecutar Finance.** Prohibido. El ensayo puede ejecutar el gate QTG porque ese es precisamente el objeto de esta unidad, pero intercepta cualquier llamada a Finance Basic/provenance.

## DEPURAR

Queda fuera:

- cambios en productor, consumidor, gate, adapter S7 o envelope;
- integración O1/Vertical;
- `OPERATIONAL`;
- material empresarial real;
- autoridad decisional;
- nuevos criterios, controles, umbrales o heurísticas;
- persistencia del receipt/consumption.

## AUDITAR 2 — criterio de cierre

El ensayo será válido solo si demuestra simultáneamente:

- fixture física → receipt sintético reproducible y consumo validado;
- resultado negativo no impide consumo técnico;
- variante sintética suficientemente soportada → `APTO/ALTA`;
- ambos casos tienen efecto operacional falso;
- el consumidor mantiene `decision_authority=false`;
- modo operacional rechaza el mismo material sintético;
- fingerprints de bundle/envelope/receipt/consumption permanecen encadenados;
- Finance no se ejecuta.

## CERRAR → MATERIALIZAR → CI

La materialización autorizada es únicamente una prueba E2E y su auditoría. No se añade código de producción.

Tras CI satisfactoria, quedará demostrada la cadena sintética completa hasta consumo QTG. La ruta operacional seguirá bloqueada por ausencia de material `PRESENTED_OPERATIONAL` autorizado y por el binding O1 diseñado pero no implementable con Mock Data.
