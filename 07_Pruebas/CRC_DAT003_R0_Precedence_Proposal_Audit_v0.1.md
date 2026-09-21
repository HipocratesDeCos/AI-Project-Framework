# EIOS — CRC DAT003 vs R0 Precedence Proposal Audit v0.1

**Baseline:** `main @ 7a2114e52dd4c388c0c8bdeaae338ccf4d45290c`  
**Fecha:** 21/09/2026  
**Estado:** AUDITORÍA DE PROPUESTA — NO AUTORIZA IMPLEMENTACIÓN

## 1. Hallazgo principal

La CRC materializada falla cerrada correctamente cuando dos reglas con el mismo efecto dominante R0 exigen resultados consolidados distintos.

El conflicto concreto es:

```text
R-DAT-003 TRUE → INFORMACIÓN INSUFICIENTE
otro R0 TRUE   → NO COMPRAR
```

## 2. Riesgos descartados

No es aceptable resolver el empate mediante:

- orden de ejecución;
- orden alfabético de rule_id;
- primer assessment;
- severidad, porque ambas pueden ser CRÍTICAS;
- scoring;
- prioridad implícita no documentada.

## 3. Criterio propuesto

La propuesta utiliza la naturaleza especial de DAT003:

DAT003 no afirma un riesgo empresarial sustantivo; afirma que el conjunto requerido para una evaluación fiable es insuficiente.

Por ello se propone que la insuficiencia de fiabilidad domine el resultado global mientras el otro R0 permanezca como factor crítico explícito.

## 4. Coherencia documental

Compatible con:

- cinco resultados oficiales CRC;
- finalidad de INFORMACIÓN INSUFICIENTE;
- R-DAT-003 como R0/CRÍTICA de fiabilidad;
- prohibición de inventar recomendación sin base fiable;
- conservación de trazabilidad;
- no compensación de salvaguardas críticas.

## 5. Límites

La propuesta no crea precedencia general entre R0.

No define qué ocurre entre dos R0 sustantivos con resultados diferentes distintos de DAT003.

No modifica metadata de reglas.

No crea excepción empresarial.

## 6. Audit 2

**SUPERADA — 0 bloqueadores documentales para someter la política a decisión humana.**

Implementación bloqueada hasta autorización explícita.

## 7. Estado

```text
CRC DAT003 vs R0 precedence → PROPOSED / NOT AUTHORIZED
runtime actual              → FAIL CLOSED
```
