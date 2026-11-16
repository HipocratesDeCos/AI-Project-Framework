# EIOS — PRICE C1: puertas de equivalencia de bases económicas

**Unidad:** Core Engine / fase 1, subunidad 1B  
**Estado:** propuesta técnica en rama aislada, pendiente de CI y auditoría  
**Dependencia:** PR #575 (PRICE/QTG fail-closed y conversiones UNIT/CURRENCY)  
**No cambia:** PurchaseOperation, C0, autoridad decisional, reglas fiscales, porcentajes, precios de compra, portabilidad de ERP

## 1. Problema demostrado

`NormalizationBasis` declara bases objetivo de impuestos, transporte, descuentos, recargos y condiciones comerciales; antes de esta unidad, `pricing/engine.py` no comprobaba esas propiedades antes de afirmar `NORMALIZED`. De igual forma, registros `EconomicBasisEvidence(status=RESOLVED)` para esas dimensiones podían ser interpretados como resolución económica sin una comparación verificable de bases.

## 2. Contrato `PriceEconomicBasisComparison`

Cada comparación está asociada a una transacción histórica, una dimensión de:

- `QUANTITY`: cantidad y posible afectación de la proporcionalidad del precio unitario;
- `TAX`: base impositiva;
- `TRANSPORT`: presencia e imputación de portes;
- `DISCOUNT`: base bruta/neta y descuentos;
- `SURCHARGE`: recargos;
- `COMMERCIAL`: condiciones comerciales.

Contiene:

- `reference_id`, `dimension`;
- `source_basis` y `target_basis`, con valor declarado y trazable;
- `status`: `EQUIVALENT`, `NOT_APPLICABLE`, `DIFFERENT` o `INDETERMINATE`;
- `source_ref`, `evidence_refs`, `rule_reference`, `trace_reference`;
- `justification` para diferencias e incertidumbres, incluida la equivalencia de cantidades distintas.

`EQUIVALENT` para TAX, TRANSPORT, DISCOUNT, SURCHARGE y COMMERCIAL exige igualdad exacta de bases declaradas. No ejecuta ajustes aritméticos. Para `QUANTITY`, la equivalencia puede documentarse entre cantidades distintas si existe justificación explícita y evidencia validada.

Las comparaciones se admiten como entrada de `PriceIntelligenceInput.economic_basis_comparisons` con valor predeterminado vacío, conservando la compatibilidad de serialización y los expedientes sintéticos previos.

## 3. Validación de C1

Una dimensión material pasa a ser exigible si:

1. `NormalizationBasis` define su base objetivo;
2. existe `EconomicBasisEvidence` de esa dimensión;
3. se suministra una comparación para ella;
4. `PriceReference.commercial_conditions` declara condiciones comerciales (para `COMMERCIAL`).

En estas situaciones, la referencia solo alcanza `NORMALIZED` si:

- existe `PriceEconomicBasisComparison` para esa dimensión y referencia;
- su `status` indica equivalencia o no aplicabilidad cuando proceda;
- el objetivo coincide con la base objetivo declarada; para `QUANTITY`, origen/destino deben coincidir con las cantidades de referencia y operación;
- la dimensión tiene `EconomicBasisEvidence` concordante, con estado, regla, traza y evidencias comunes;
- las evidencias asociadas constan como `EvidenceValidation(status=VALID)`;
- no existen diferencias económicas sin transformación aritmética autorizada ni contradicciones.

La ausencia de la comparación requerida, del objetivo, de la evidencia, o cualquier contradicción retorna `PENDING`, `normalized_unit_price=None` y códigos `ECONOMIC_DIMENSION_*`.

## 4. Trazabilidad

Las referencias `source_ref`, `rule_reference`, `trace_reference` y `evidence_refs` de comparaciones correspondientes a precios seleccionados se incluyen en `PriceIntelligenceResult.trace_references`.

El gate no autentica externamente facturas, tipos de IVA, condiciones de transporte, descuentos ni observaciones firmadas. La confianza de origen corresponde a la capa de ingesta/admisión/QTG.

## 5. Limitaciones explícitas

**Esta unidad no cierra todavía la comparación económico-financiera integral.**

- No crea reglas de cálculo del IVA, portes, descuentos, rappels o recargos.
- No ajusta importes por diferencias de base: conserva `PENDING` hasta tener un contrato de transformación numérica autorizado.
- Los expedientes **antiguos** sin bases objetivo explícitas, sin evidencia material suministrada y sin condiciones comerciales declaradas conservan el comportamiento anterior, por compatibilidad. Por tanto, ausencia de declaración **no constituye evidencia de equivalencia**.
- La diferencia de cantidades históricas solo activa el nuevo gate cuando se declara expresamente la comparación/evidencia de QUANTITY; la cobertura obligatoria integral por perfil de empresa es una tarea posterior.
- Las bases son expresiones declaradas como texto, no códigos fiscales normalizados; las equivalencias semánticas y terminológicas entre ERPs quedan pendientes de mapeo autorizado.
- Este cambio no concede autoridad de recomendación ni habilita ejecución operacional.

## 6. Pruebas de regresión

`tests/test_price_economic_basis_gate.py` cubre:
- rechazo de bases objetivo declaradas sin comparaciones;
- aceptación de bases literalmente equivalentes con evidencia trazable;
- diferencias de IVA, portes, descuentos, recargos y condiciones comerciales;
- rechazo de objetivos inconsistentes, evidencias ausentes/no válidas, duplicados y fuentes incorrectas;
- particularidades de comparación por cantidad y justificación;
- integración de selección, agregación y trazas C1.

**Criterio de aceptación:** CI completa de GitHub en verde y validaciones SQL satisfactorias, sin cambios en los precios de las simulaciones anteriores.

## 7. Pendientes de la fase 1

- Perfiles de entrada que hagan obligatoria la declaración de todas las dimensiones materiales aplicables, sin recurrir a un supuesto de equivalencia para expedientes externos.
- Política autorizada y verificable de transformación de bases realmente diferentes (IVA, transporte, descuentos, etc.), evitando cálculos fiscales genéricos.
- Auditoría de compatibilidad entre HIS003, las reglas de precio, QTG, el invocador provenance-safe y escenarios.
- Aceptación y cierre de las PR apiladas antes de cualquier integración en `main`.
