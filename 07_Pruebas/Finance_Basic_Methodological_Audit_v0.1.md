# EIOS — FINANCE BASIC · METHODOLOGICAL AUDIT v0.1

**Estado:** AUDIT 1 COMPLETADA — REQUIERE DEPURACIÓN  
**Fecha:** 11/09/2026  
**Objeto auditado:** `01_Modelo/Finance_Basic_Methodological_Design_v0.1.md`  
**Commit de diseño inicial:** `5e12d74d70167be153b9ce7ae1235ffd117f5192`

---

## 1. Propósito

Auditar el diseño metodológico inicial de Capa 4 — Finanzas Básica contra las fuentes de autoridad existentes, buscando contradicciones, inferencias no autorizadas, duplicación de responsabilidades, falsa evaluabilidad y pérdidas de trazabilidad.

Fuentes principales contrastadas:

- Gobierno y Matriz de Autoridad Documental;
- `01_Modelo/Especificacion_funcional.md`;
- `03_Arquitectura/Architecture_Blueprint.md`;
- `05_Motor/Modelo_Empresarial_Decision.md`;
- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md`;
- `02_Parametros/Matriz_Parametros_Reglas_MVP.md`;
- `04_Reglas/Matriz_Reglas_MVP.md`;
- `04_Reglas/Evidence_Contract.md`;
- `04_Reglas/Rule_Dependency_Matrix.md`;
- `08_Implementacion/TCO_Core_Implementation_Contract.md`;
- fronteras de C0 / Assessment / CRC ya cerradas.

---

## 2. Dictamen ejecutivo

El diseño v0.1 es direccionalmente compatible con la arquitectura, pero **NO está limpio para cierre metodológico**.

Se identifican **9 hallazgos**:

- 4 bloqueadores estructurales depurables sin nueva política empresarial;
- 3 precisiones de frontera/temporalidad;
- 2 gaps de autoridad que no pueden resolverse por inferencia documental.

No se autoriza contrato técnico ni implementación.

---

## 3. Hallazgos

### FIN-A1-01 — Liquidez insuficientemente representada

**Severidad:** BLOQUEADOR DE DISEÑO  
**Tipo:** Omisión funcional

El MED, la Especificación Funcional, Architecture Blueprint y TCO reconocen `liquidez` como responsabilidad de Finanzas. El diseño v0.1 trata tesorería, fondo de maniobra y margen de seguridad, pero no separa liquidez como concepto propio.

**Riesgo:** que una futura implementación equipare implícitamente liquidez con tesorería o fondo de maniobra.

**Corrección:** incorporar un módulo/concepto explícito de liquidez que no prescriba fórmula mientras no exista autoridad especializada.

---

### FIN-A1-02 — Riesgo de doble cómputo en projected_treasury

**Severidad:** BLOQUEADOR DE DISEÑO  
**Tipo:** Integridad cuantitativa

La propuesta:

```text
current treasury
+ inflows
- outflows
- purchase outflows
```

es ambigua si `outflows` ya contiene el pago de la compra.

**Riesgo:** descontar dos veces el mismo flujo.

**Corrección:** exigir conjuntos disjuntos o una única colección de flujos con identidad estable y deduplicación; si se mantiene separación, `non_purchase_outflows` debe excluir expresamente `purchase_outflows`.

---

### FIN-A1-03 — Frontera monetaria/FX ausente

**Severidad:** BLOQUEADOR DE DISEÑO  
**Tipo:** Comparabilidad monetaria

TCO ya establece que no se mezclan monedas ni se inventa FX. Finance Basic agregaría saldos y flujos monetarios, por lo que debe preservar la misma frontera.

**Riesgo:** sumar EUR con otra moneda o aplicar conversión implícita.

**Corrección:** una proyección cuantitativa solo agrega importes monetariamente comparables o previamente normalizados por una política FX autorizada. Finance Basic no crea tipos de cambio.

---

### FIN-A1-04 — TCO/coste económico ≠ flujo de caja

**Severidad:** BLOQUEADOR DE DISEÑO  
**Tipo:** Frontera interdominio

TCO declara expresamente que no sustituye Finanzas y excluye financiación/coste temporal. Un valor TCO no puede convertirse automáticamente en desembolso financiero de la propuesta.

**Riesgo:** utilizar el coste económico como pago, ignorando temporalidad, impuestos recuperables, condiciones o calendario.

**Corrección:** el flujo de pago de la compra requiere evidencia/autorización propia. `TCO value ≠ purchase cash outflow` salvo transformación expresamente autorizada.

---

### FIN-A1-05 — P-FIN-005/006 no son controles globales por inferencia

**Severidad:** ALTA  
**Tipo:** Autoridad parámetro→uso

La relación demostrada es:

```text
P-FIN-005 → R-FIN-001 (compuesta)
P-FIN-006 → R-FIN-001 (compuesta)
```

No está demostrado que esos parámetros gobiernen universalmente cualquier proyección financiera de Capa 4.

**Corrección:** limitar su uso reconocido al contexto autorizado de R-FIN-001 / capacidad financiera prevista hasta que una metodología competente determine un uso más amplio.

---

### FIN-A1-06 — Horizonte operativo todavía no autorizado

**Severidad:** ALTA  
**Tipo:** Temporalidad / parametrización

`P-FIN-001` existe como “Horizonte de pagos”, pero permanece pendiente de identificación documental individual en la matriz parámetro↔regla.

El diseño no puede utilizarlo silenciosamente como horizonte universal de toda proyección.

**Corrección:** mantener el horizonte como requisito explícito cuya autoridad debe resolverse antes de materializar una proyección cuantitativa general.

---

### FIN-A1-07 — Estado de los flujos futuros insuficientemente acotado

**Severidad:** MEDIA  
**Tipo:** Evidencia

Una fecha e importe no bastan para demostrar que un pago/cobro futuro sigue vigente. Debe poder acreditarse que el flujo es aplicable al snapshot/horizonte y no está cancelado, liquidado, sustituido o duplicado.

**Corrección:** exigir evidencia de vigencia/aplicabilidad sin inventar una nueva taxonomía global de estados.

---

### FIN-A1-08 — Coherencia temporal del snapshot

**Severidad:** MEDIA  
**Tipo:** Reproducibilidad

El diseño debe impedir mezclar una posición de tesorería de una fecha con flujos cuya condición de pendiente se conoce en otra fecha sin reconciliación temporal.

**Corrección:** todo flujo debe evaluarse respecto de `as_of_date`; la condición de pendiente/aplicable debe ser válida para ese corte.

---

### FIN-A1-09 — Gaps cuantitativos de autoridad siguen abiertos

**Severidad:** BLOQUEADOR DE CIERRE METODOLÓGICO  
**Tipo:** Autoridad funcional

No existe todavía metodología especializada suficiente para cerrar:

- fórmula/composición de fondo de maniobra en EIOS y su impacto post-compra;
- definición cuantitativa de margen de seguridad financiera;
- identidad cuantitativa de `capacidad financiera prevista`;
- dependencias DATA/EVIDENCE críticas por regla financiera;
- `Criticality` / `Evaluability_Impact` de esas dependencias.

Estos puntos no pueden resolverse por conveniencia técnica.

---

## 4. Hallazgo sobre reglas — fuera de Finance Basic

`R-FIN-002` y `R-FIN-003` incluyen ramas/escaladas (`R1 ↔ R0`, `NO COMPRAR ↔ COMPRAR CONDICIONADO`) cuya selección efectiva no queda determinada por Finance Basic.

Este diseño no debe resolverlas. Permanecen como gap de Rules/autoridad funcional antes de implementar predicados deterministas.

---

## 5. Aspectos conformes

Se consideran correctos y deben preservarse:

- ausencia ≠ cero;
- evidencia antes de cálculo;
- temporalidad explícita;
- hecho ≠ política;
- análisis ≠ regla;
- no decisión;
- no compensación implícita;
- separación respecto de CRC;
- `P-FIN-001` no recibe consumidor inventado;
- working capital, safety margin y financial capacity no reciben fórmulas inventadas;
- reglas PAG permanecen separadas;
- no se crean dependencias RDM por similitud semántica.

---

## 6. Acción autorizada siguiente

**DEPURAR** el diseño v0.1 para resolver FIN-A1-01…08 sin introducir política empresarial nueva.

Después ejecutar **AUDITAR 2**.

FIN-A1-09 no se considera resoluble mediante simple redacción: Audit 2 deberá determinar con precisión qué definiciones pueden derivarse de autoridad existente y cuáles requieren una decisión empresarial/metodológica expresa.

---

## 7. Dictamen

**AUDIT 1: NO SUPERADA PARA CIERRE.**

El diseño puede avanzar a **DEPURAR**, pero no a cerrar, contrato técnico ni implementación.