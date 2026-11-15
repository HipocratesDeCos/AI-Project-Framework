# EIOS — PRICE: admisión económica estricta por empresa (v0.1)

**Fase:** preparación del Core Engine, fase 1 / unidad 1C  
**Estado:** cambio experimental en rama aislada, sin autoridad operacional  
**Depende de:** PR #575 (PRICE/QTG) y PR #576 (bases económicas)  
**No modifica:** C0, contratos existentes, invocadores previos, base de datos, UI ni resultados históricos

## 1. Problema real

Los casos de referencia sintética anteriores pueden funcionar sin declarar una base económica completa. La compatibilidad es deliberada; **no constituye una garantía para nuevas empresas**. Es necesario un acceso distinto que exija evidencia de las bases de precio antes de calcular el Precio de Referencia.

## 2. API nueva y explícita

`eios.pricing.company_coverage` contiene:

- `PriceCompanyCoverageProfile`: perfil documental con `company_id`, `profile_id`, identidad de decisión/escenario, versión de parámetros, snapshot, fuente, evidencia, regla y traza;
- `assess_price_company_coverage(payload, profile, expected_company_id=...)`: retorna un `PriceCoverageReport` sin efectos laterales;
- `run_price_intelligence_for_company(payload, context, profile, expected_company_id=...)`: permite ejecutar C1 **solo** con perfil `COMPLETE`, y adjunta trazas del perfil al resultado. En otro caso lanza `PriceCoverageError` con motivos tipados de falta de cobertura.

El argumento `expected_company_id` debe venir del contexto de empresa autenticado por la aplicación/adaptador. **No** equivale a autenticación: un invocador puede mentir si le permite al usuario rellenarlo libremente. No hemos incorporado identidad de empresa a `DecisionContext`, respetando C0.

## 3. Completitud económica exigida

Para cada referencia histórica, el acceso estricto exige las **seis dimensiones que el contrato económico C1 soporta en este nivel**:

`QUANTITY, TAX, TRANSPORT, DISCOUNT, SURCHARGE, COMMERCIAL`.

Además:
- `NormalizationBasis` con base objetivo definida para TAX, TRANSPORT, DISCOUNT, SURCHARGE y COMMERCIAL, más unidad objetivo;
- comparación explícita `PriceEconomicBasisComparison(status=EQUIVALENT)` por referencia y dimensión;
- `EconomicBasisEvidence(status=RESOLVED)` única, con regla/traza y evidencias concordantes y `EvidenceValidation=VALID`;
- para `QUANTITY`, bases de cantidad iguales a la referencia y a la operación, respectivamente; si son diferentes, exige una justificación válida en la comparación;
- si se declara `commercial_conditions`, su texto debe concordar con la base origen evaluada;
- si se necesita convertir moneda o unidad, el motor C1 debe poder completar la conversión documentada. No se inventa ningún factor;
- para dimensiones realmente no aplicables, el perfil v0.1 requiere declarar una **misma base documentada** (por ejemplo, un código empresarial `NO_APLICA`) con evidencia positiva; no se convierte una ausencia de datos en equivalencia.

Se admiten duplicados documentales idénticos por transacción (deduplicación C1), pero no referencias con el mismo ID y contenido contradictorio.

Si alguna dimensión está ausente, no es comparable, o está sin pruebas, el acceso estricto **no invoca C1** y devuelve los motivos de admisión en un error de cobertura. No devuelve `APTO` ni una recomendación.

## 4. Compatibilidad

`run_price_intelligence(...)` existente conserva sus contratos y el comportamiento de las simulaciones antiguas. No se reescriben ni se invalidan las pruebas históricas.

**Importante:** las aplicaciones de empresa nuevas deberán ser configuradas para llamar a `run_price_intelligence_for_company`. Hasta que se conecte ese adaptador, no hay un cierre efectivo de la admisión empresarial ni una obligación universal en el motor heredado.

## 5. Reconciliación de autoridades — PRICE / HIS003 / QTG

Los controles existentes cumplen tareas **diferentes**:

| Frontera | Qué comprueba | Qué no autoriza |
|---|---|---|
| Admisión económica estricta C1 | Cobertura declarada y congruencia de seis dimensiones de precio por referencia y contexto de empresa | No autentica empresa, documentos ni decisiones |
| PRICE | Comparabilidad C1, normalización, temporalidad, representatividad, selección y suficiencia del precio histórico | No decide comprar ni concede validez operacional |
| HIS003 | Siete dimensiones de comparabilidad comercial histórica (cantidad, proveedor, condiciones, descuentos, rappels, plazo de pago, características del artículo) | Su dictamen no sustituye ni acredita normalización C1 |
| QTG | Calidad/confiabilidad de controles del expediente según su catálogo y productor | `APTO` no significa que un precio esté normalizado o sea comercialmente representativo |

**Regla de integridad:** ningún `COMPLETE` del nuevo perfil debe convertirse en `COMPARABLE` de HIS003 ni en `APTO` de QTG. Tampoco se aceptan como sustituto resultados HIS003/QTG desprendidos de su procedencia: deben revalidarse mediante su productor e identidad original antes de vincularse al flujo de empresa.

En este cambio se mantiene la separación de autoridades; **todavía no se materializa un orquestador que vuelva a ejecutar los tres productores y vincule sus recibos completos**. Esa coordinación es una unidad posterior y no puede darse por implementada.

## 6. Limitaciones concretas

- El Core **no autentica** `company_id`, `expected_company_id` ni `EvidenceValidation=VALID`: estas afirmaciones son responsabilidad del adaptador autorizado.
- Los campos de base son declaraciones textuales. La verdad de un IVA, porte, descuento o condición contractual no se comprueba leyendo únicamente esos textos.
- `RAPPELS` y `PAYMENT_TERM` no están modelados como dimensiones independientes en esta puerta de PRICE. HIS003 los evalúa en su propia frontera, sin conceder autoridad económica automáticamente.
- El perfil estricto v0.1 exige equivalencia demostrada de seis dimensiones; **no ejecuta ajustes monetarios** de fiscalidad, transporte o descuentos entre bases distintas.
- No se sustituye un defecto crítico por una confianza o un score alto; no hay autoridad operacional nueva ni habilitación de transacciones reales.
- La comprobación de cobertura es local y determinista; sigue pendiente una prueba independiente de su inclusión obligatoria en el adaptador para nuevas empresas.

## 7. Criterios de cierre

1. Todas las pruebas previas y nuevas superadas en CI.
2. Negativas de empresa distinta, parámetros/snapshot distintos, una dimensión faltante, evidencia ausente/incorrecta y referencias documentales incompatibles.
3. Sin cambios en PR de las dos demostraciones sintéticas históricas.
4. Revisión final del diff, CI verde y PR borrador aislada y apilada sobre #576.
5. Integración no autorizada hasta revisión explícita de las unidades previas y actual.

**Siguiente unidad:** integrador con vinculación de identidades de QTG/HIS003 y obligatoriedad efectiva del perfil estricto en los adaptadores empresariales, no en datos sintéticos heredados.
