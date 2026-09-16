# EIOS — Finance Horizon Provenance · RDM Reconciliation Design v0.1

**Estado:** DISEÑAR — PROPUESTA DOCUMENTAL ACOTADA  
**Baseline:** `main @ eae980a979eeaedac53a9e85d7d5d5c88e889723`  
**Objeto:** reconciliar el estado de `FIN-PROV-HORIZON-01` en `04_Reglas/Rule_Dependency_Matrix.md` después de la integración física de PR #150.

## 1. Hallazgo

La RDM v1.5.3 conserva formulaciones que declaran `FIN-PROV-HORIZON-01` abierto. Esa afirmación era correcta cuando se canonizó la arista `P-FIN-001 → R-FIN-001`, pero ha quedado obsoleta tras la implementación provenance-safe integrada por PR #150.

Evidencia posterior:

- contrato técnico: `08_Implementacion/Finance_Horizon_Provenance_Contract_v0.1.md`;
- implementación: `eios/finance/provenance.py` y consumidores FIN migrados;
- PR #150 integrado;
- CI pre-merge #808 — SUCCESS;
- merge `eae980a979eeaedac53a9e85d7d5d5c88e889723`;
- CI post-merge #809 — SUCCESS.

## 2. Cambio autorizado

Actualizar exclusivamente la RDM vigente para:

1. conservar `P-FIN-001 → R-FIN-001` como `DERIVED / CONFIRMED`;
2. sustituir las notas que presentan `FIN-PROV-HORIZON-01` como abierto por su estado físico cerrado;
3. referenciar la frontera `ProvenancedFinanceBasicExecution` como evidencia técnica posterior de binding provenance-safe;
4. preservar `Criticality = PENDING`, `Evaluability_Impact = PENDING`, `Fallback = NONE` y `Affected_Component = NONE`;
5. incrementar versión documental `1.5.3 → 1.5.4`.

## 3. No cambia

Esta reconciliación no:

- crea una nueva dependencia RDM;
- convierte `P-FIN-001` en parámetro directo de `R-FIN-001`;
- crea `P-FIN-001 → R-FIN-003`;
- valida 30 días como política empresarial;
- asigna criticidad ni impacto de evaluabilidad;
- cambia Finance Basic, Rules, CRC, C0, parámetros, fórmulas o código;
- reabre documentos históricos de PR #149/#150.

## 4. Criterio de cierre

La unidad podrá cerrarse si Audit 1 y Audit 2 confirman que el único efecto es eliminar una contradicción temporal de estado en la fuente canónica vigente y que la RDM conserva todas sus fronteras semánticas.
