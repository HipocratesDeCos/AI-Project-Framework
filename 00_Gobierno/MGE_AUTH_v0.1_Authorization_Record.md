# EIOS — MGE-AUTH v0.1 Authorization Record

**Fecha:** 20/09/2026  
**Baseline:** `main @ e93c609d1f3ffab72a3774f04d5db4fe7b3b012c`  
**Estado:** AUTORIZACIÓN HUMANA EXPLÍCITA REGISTRADA

## Alcance autorizado

Se autoriza expresamente `MGE-AUTH v0.1` según:

`01_Modelo/Profitability_Margin_Authority_Proposal_v0.1.md`.

La autorización cubre exclusivamente:

- `AuthorizedSaleBasis`;
- `AuthorizedCostBasis`;
- compatibilidad de bases;
- `margin_amount = sale - cost`;
- `margin_percentage = margin_amount / sale × 100`;
- `sale = 0 → margin_percentage NOT_DETERMINABLE`;
- tratamiento fail-closed de ausencia/contradicción;
- exclusión de FX/conversión implícita;
- exclusión de selección automática de PRICE/TCO;
- exclusión de descuentos/rappels implícitos;
- separación entre cálculo MGE y Rules/CRC.

## No autorizado por esta decisión

- selección automática de precio de venta;
- selección automática de coste;
- TCO como coste por defecto;
- `TCO / quantity` implícito;
- parámetros MGE definitivos;
- P-MGE-004/005/006 como consumidores;
- ejecución R-MGE;
- recomendación o decisión empresarial.

## Consecuencia

El gate de autoridad MGE queda satisfecho y se permite abrir el contrato técnico de Profitability Core dentro de este alcance.
