# EIOS — PRICE: ejecución trazable de conversiones (alcance acotado)

**Unidad:** Preparación del Core Engine, fase 1 / PRICE–QTG  
**Estado:** Implementación en revisión (PR #575, no integrable sin CI y auditoría)  
**Autoridad normativa:** `01_Modelo/Price_Intelligence_Methodological_Matrix.md`, `Price_Intelligence_Economic_Basis_Matrix.md` y `Price_Intelligence_Normalization_Matrix.md`.

## Motivación

El código previo podía presentar `reference.unit_price` como `normalized_unit_price` aunque se hubieran declarado diferencias de unidad o moneda. Documentar un cambio no equivale a ejecutar una conversión numérica.

## Contrato añadido

`PriceIntelligenceInput.price_conversion_instructions` es opcional (por defecto vacío). Cada `PriceConversionInstruction` identifica:

- `reference_id` y dimensión (`UNIT` o `CURRENCY`);
- `source_code`, `target_code` y factor `Decimal` finito, positivo y sin tasa implícita;
- `effective_date` de la conversión, exigida igual a la fecha de referencia histórica en este primer perfil;
- `source_ref`, `evidence_refs`, `rule_reference` y `trace_reference`.

**Semántica matemática:** precio objetivo por unidad objetivo = precio original por unidad original × factor. Para `UNIT`, el factor expresa el cociente entre el precio por unidad objetivo y el precio por unidad origen; para `CURRENCY`, unidades de moneda destino por una unidad de moneda origen. La fuente autorizada debe demostrar el valor del factor y su unidad económica.

El motor ejecuta las etapas en orden fijo `UNIT → CURRENCY` y redondea una sola vez a cuatro decimales con `ROUND_HALF_EVEN`. Se generan `NormalizationRecord` para cada transformación realizada; las referencias a reglas, trazas, fuente y evidencia aparecen en las trazas del resultado seleccionado.

## Gate de admisión de conversiones

No se ejecuta ni se publica un precio transformado salvo que:

1. la referencia sea `COMPARABLE` y exista una `NormalizationBasis` cuando hay conversiones;
2. las instrucciones cubran exactamente las dimensiones `UNIT`/`CURRENCY` que difieren de la operación;
3. el origen, el destino y la fecha coincidan con la referencia y la operación evaluada;
4. cada dimensión tenga `EconomicBasisEvidence` en estado `RESOLVED`;
5. regla, traza y evidencias de la instrucción estén vinculadas a esa dimensión;
6. todas las `EvidenceValidation` correspondientes tengan estado `VALID`;
7. los registros económicos no incluyan estados no resueltos ni duplicados.

En cualquier otro caso, `normalization_status=PENDING` y `normalized_unit_price=None`, con motivos verificables. No se reemplaza una tasa ausente ni se estima una equivalencia.

**Frontera de confianza:** `EvidenceValidation(status=VALID)` es un hecho suministrado al motor; esta unidad no autentica externamente bancos, documentos, tasas oficiales, empresas, firmas ni usuarios. Ninguna declaración habilita autoridad operacional. Los datos de pruebas son exclusivamente sintéticos.

## Restricciones expresas

- No se convierten impuestos, transporte, descuentos, rappels, recargos ni condiciones comerciales mediante reglas no definidas.
- No se admite una fecha distinta a la referencia histórica; los criterios temporales alternativos requieren un contrato autorizado aparte.
- Una tasa declarada por un usuario **sin fuente comprobable** no debe recibir un `EvidenceValidation=VALID` desde un adaptador operacional.
- Esta unidad no modifica C0, QTG, el precio de la operación ni el mecanismo de mediana.
- Los casos con bases económicas no expresadas por los contratos actuales necesitan una revisión específica de comparabilidad; no se puede declarar cobertura económica integral.

## Pruebas exigidas

- Sin instrucciones: casos de misma moneda y unidad sin regresiones.
- Instrucciones completas: unidad, moneda y composición de ambas.
- Ausencia de regla, fuente, evidencia válida, dimensión o fecha correcta: `PENDING`.
- Tasas inválidas/duplicadas o evidencia inexistente: rechazo del contrato.
- Redondeo determinista y trazas de conversiones seleccionadas.
- Suite completa GitHub Actions, incluidas validaciones SQL.

## Pendientes para el cierre integral de fase 1

- Revisión de equivalencia y ajustes en dimensiones `QUANTITY`, `TAX`, `TRANSPORT`, `DISCOUNT`, `SURCHARGE`, `COMMERCIAL`, con sus fuentes y límites.
- Auditoría de integración entre Price Intelligence, los puentes de reglas y la procedencia de evidencias.
- Revisión de consecuencias sobre la salida `PR` y casos sintéticos de referencia.
- Dictamen de auditoría posterior y autorización de integración por el responsable de EIOS.
