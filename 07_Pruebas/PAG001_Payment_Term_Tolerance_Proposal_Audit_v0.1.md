# EIOS — PAG001 Payment-Term Tolerance Proposal Audit v0.1

**Baseline:** `main @ 4fd2c51c32400c7e986c4b9947dbe3e191667d03`  
**Fecha:** 22/09/2026  
**Estado:** AUDIT 2 DE PROPUESTA — SUPERADA / NO AUTORIZA IMPLEMENTACIÓN

## 1. Evidencia documental disponible

La fuente especializada vigente establece:

- P-PAG-003 = margen permitido respecto al objetivo;
- modula la evaluación alrededor de P-PAG-002;
- no sustituye P-PAG-001;
- su relación con R-PAG-001 es derivada.

No establece fórmula exacta.

## 2. Fórmulas descartadas

No existe autoridad para:

- `target + tolerance`;
- porcentaje sobre target;
- ratio;
- tolerancia simétrica;
- valor absoluto;
- clamp silencioso;
- selección de bandas múltiples.

## 3. Fórmula propuesta

```text
threshold = target - tolerance
TRUE  iff offered < threshold
FALSE iff offered >= threshold
```

Es la transformación mínima coherente con “desviación desfavorable permitida respecto del objetivo”.

## 4. Hallazgo de seguridad

Si `tolerance > target`, el umbral sería negativo.

No debe convertirse esa configuración en una regla que nunca active silenciosamente.

Se propone:

```text
tolerance > target → NOT_EVALUABLE
```

## 5. Igualdad

La igualdad con `target - tolerance` queda dentro de la tolerancia:

```text
offered == threshold → FALSE
```

Esto evita activar la regla en el límite aceptado.

## 6. Separación de responsabilidades

La propuesta no resuelve:

- control P-PAG-004;
- descuento P-PAG-005;
- multicuota;
- contrafactual R-PAG-002;
- valores empresariales concretos.

## 7. Dictamen

```text
DISEÑAR   → SUPERADA
AUDITAR   → SUPERADA
DEPURAR   → SUPERADA
AUDIT 2   → SUPERADA
CERRAR    → BLOQUEADO POR AUTORIZACIÓN HUMANA
IMPLEMENT → BLOQUEADO
```

**0 bloqueadores documentales para someter PAG001 Payment-Term Tolerance Authority v0.1 a autorización humana.**
