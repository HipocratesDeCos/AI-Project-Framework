# EIOS — RENTABILIDAD / MARGEN · AUTHORIZATION GATE v0.1

**Estado:** BLOQUEO DE AUTORIDAD — CIERRE METODOLÓGICO NO AUTORIZADO  
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

## 2. Único bloqueo restante

El repositorio vigente no contiene autoridad empresarial suficiente para fijar por inferencia:

```text
margin_amount = sale_basis - cost_basis
margin_percentage = margin_amount / sale_basis * 100
```

ni para declarar que dicha segunda fórmula representa el margen porcentual oficial de EIOS y no markup u otra métrica.

La propuesta correspondiente está documentada en:

`01_Modelo/Profitability_Margin_Authority_Proposal_v0.1.md`

con estado:

`PROPUESTA — NO AUTORIZADA`.

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

## 4. Trabajo permitido mientras el gate esté abierto

Sí puede avanzarse en:

- auditoría documental adicional;
- validación de fronteras e invariantes;
- diseño de contratos abstractos que no congelen fórmula empresarial;
- identificación de dependencias y gaps;
- trabajo en unidades independientes del repositorio.

No puede avanzarse a:

```text
CERRAR → MATERIALIZAR IMPLEMENTACIÓN → CI DE IMPLEMENTACIÓN
```

para Profitability Core mientras la autoridad empresarial siga sin aprobarse.

---

## 5. Condición de desbloqueo

El gate se desbloquea únicamente mediante autorización humana explícita de `MGE-AUTH v0.1` o mediante otra autoridad empresarial equivalente que defina de forma trazable la semántica del margen.

`continuar`, `proseguir`, `actuar` o instrucciones operativas genéricas no se interpretan como aprobación de política económica.

---

## 6. Estado final

**MGE metodológico:** AUDIT 2 SUPERADA / CIERRE BLOQUEADO POR AUTORIDAD.  
**Implementación MGE:** NO AUTORIZADA.  
**Política nueva inventada:** 0.  
**Componentes cerrados reabiertos:** 0.
