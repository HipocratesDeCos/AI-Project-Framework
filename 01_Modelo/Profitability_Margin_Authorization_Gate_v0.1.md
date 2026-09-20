# EIOS — RENTABILIDAD / MARGEN · AUTHORIZATION GATE v0.1

**Estado:** GATE SATISFECHO — MGE-AUTH v0.1 AUTORIZADA  
**Fecha:** 11/09/2026  
**Rama:** `mge/profitability-methodology-v0.1`

---

## 1. Resultado del ciclo metodológico previo

Se ha completado sobre MGE:

- DISEÑAR;
- AUDITAR;
- DEPURAR;
- AUDITAR 2.

El diseño depurado separa explícitamente:

1. evidencia económica;
2. bases de venta/coste ya autorizadas externamente;
3. cálculo descriptivo de margen;
4. Rules MGE;
5. CRC y decisión humana.

No se ha identificado contradicción que obligue a reabrir C0, PRICE, TCO, Finanzas, Stock, Supplier, Rules o CRC.

---

## 2. Bloqueo de autoridad — RESUELTO

El repositorio vigente no contiene autoridad empresarial suficiente para fijar por inferencia:

```text
margin_amount = sale_basis - cost_basis
margin_percentage = margin_amount / sale_basis * 100
```

ni para declarar que dicha segunda fórmula representa el margen porcentual oficial de EIOS y no markup u otra métrica.

La propuesta correspondiente está documentada en:

`01_Modelo/Profitability_Margin_Authority_Proposal_v0.1.md`

con estado vigente:

`AUTORIZADA — MGE-AUTH v0.1`.

---

## 3. Decisiones que NO quedan autorizadas por este gate

Este documento no autoriza:

- fórmula definitiva de margen;
- denominador del porcentaje;
- selección de precio de venta;
- selección de coste;
- uso automático de TCO como coste de margen;
- transformación `TCO / quantity`;
- aplicación de descuentos o rappels;
- valores definitivos de parámetros MGE;
- ejecución de reglas R-MGE;
- recomendación o decisión empresarial.

---

## 4. Trabajo permitido tras cierre del gate

Sí puede avanzarse en:

- auditoría documental adicional;
- validación de fronteras e invariantes;
- diseño de contratos abstractos que no congelen fórmula empresarial;
- identificación de dependencias y gaps;
- trabajo en unidades independientes del repositorio.

Puede avanzarse a:

```text
CERRAR METODOLOGÍA → DISEÑAR CONTRATO TÉCNICO → AUDITAR → MATERIALIZAR → CI
```

sin ampliar el alcance autorizado de MGE-AUTH v0.1.

---

## 5. Condición de desbloqueo

El gate fue satisfecho mediante autorización humana explícita de `MGE-AUTH v0.1` el 20/09/2026.

---

## 6. Estado final

**MGE metodológico:** AUDIT 2 SUPERADA / AUTORIDAD SATISFECHA.  
**Implementación MGE:** AUTORIZADA únicamente dentro de MGE-AUTH v0.1 y su futuro contrato técnico auditado.  
**Política nueva inventada:** 0.  
**Componentes cerrados reabiertos:** 0.
