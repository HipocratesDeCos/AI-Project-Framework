# EIOS — Evidence Contract

**Versión:** 1.0  
**Estado:** MATERIALIZADO — Baseline EIOS Vertical MVP  
**Ubicación:** `04_Reglas/Evidence_Contract.md`  
**Ámbito:** EIOS Core / EIOS Vertical MVP

---

## 1. Propósito

`Evidence Contract` define el contrato mediante el cual EIOS determina si una evidencia es admisible para sustentar la evaluación de una regla.

Su responsabilidad se limita a establecer las propiedades y criterios generales de admisibilidad, suficiencia y trazabilidad mínima de la evidencia.

No define:

- la lógica de las reglas;
- los parámetros;
- las dependencias concretas de cada regla;
- la resolución de conflictos;
- escenarios;
- viabilidad;
- negociación;
- recomendación;
- decisión empresarial.

El flujo canónico es:

```text
DATO
  ↓
EVIDENCIA
  ↓
EVIDENCE VALIDATION
  ↓
RULE
  ↓
ASSESSMENT
```

---

## 2. Autoridad y fronteras

La Matriz de Autoridad Documental reserva `Evidence_Contract.md` como autoridad especializada sobre evidencia y criterios de suficiencia.

La autoridad se distribuye de la siguiente forma:

```text
Evidence Contract
    ↓
criterios generales de admisibilidad y suficiencia
    ↓
Rule Dependency Matrix
    ↓
evidencias requeridas por cada regla
    ↓
Rule
    ↓
condición y lógica de evaluación
    ↓
Assessment
    ↓
resultado individual
```

`Evidence Contract` **no determina qué evidencias necesita una regla concreta**. Esa responsabilidad corresponde a `Rule Dependency Matrix` y, cuando proceda, a la definición especializada de la regla.

---

## 3. Definición de evidencia

Una evidencia es una representación identificable, trazable y verificable de información que puede utilizarse para sustentar una evaluación de regla.

La mera existencia de un dato no convierte automáticamente ese dato en evidencia suficiente.

Como mínimo, la evidencia debe permitir identificar:

- qué información representa;
- su origen;
- una referencia reproducible;
- el momento de captura cuando corresponda;
- su estado de demostración.

---

## 4. Contrato físico C0

El contrato debe permanecer compatible con el objeto `Evidence` implementado en C0:

```text
Evidence
├── evidence_id
├── source_type
├── source_ref
├── captured_at
├── state
└── demonstration_ref
```

Los estados operativos de C0 son exclusivamente:

```text
DEMONSTRATED
GAP
```

Este documento no introduce estados físicos adicionales.

---

## 5. DEMONSTRATED

`DEMONSTRATED` indica que la evidencia está disponible y dispone de una referencia de demostración.

Una evidencia en estado `DEMONSTRATED` debe contener `demonstration_ref`.

La validación física de C0 transforma este estado en:

```text
DEMONSTRATED → VALID
```

`VALID` es un estado de `EvidenceValidation`, no un estado adicional de `Evidence`.

---

## 6. GAP

`GAP` representa evidencia requerida que no está disponible o que no permite demostrar el requisito correspondiente.

`GAP` no constituye evidencia demostrada.

Por tanto:

```text
GAP ≠ TRUE
GAP ≠ FALSE
GAP ≠ NO COMPRAR
```

En C0:

```text
GAP → INVALID
```

La consecuencia `NOT_EVALUABLE` se determina en la evaluación de la regla y se representa en `Assessment`; `Evidence Contract` no produce directamente ese resultado.

---

## 7. Suficiencia

La suficiencia es una propiedad de la evidencia respecto del requisito para el que se pretende utilizar.

Debe distinguirse entre:

```text
EXISTENCIA DE EVIDENCIA
        ≠
SUFICIENCIA PARA UNA REGLA
```

`Evidence Contract` define los criterios generales que debe satisfacer una evidencia.

La determinación de la evidencia concreta necesaria para una regla, incluyendo cantidad, tipo, dependencia, temporalidad específica o condiciones particulares, corresponde a `Rule Dependency Matrix` y a la definición de la regla cuando proceda.

---

## 8. Trazabilidad mínima

Una evidencia utilizable debe conservar, conforme al contrato físico C0:

- `evidence_id`;
- `source_type`;
- `source_ref`;
- `captured_at`;
- `state`;
- `demonstration_ref` cuando `state = DEMONSTRATED`.

La trazabilidad completa de una ejecución pertenece al contrato de `Trace` y no se duplica aquí.

---

## 9. Fuente y referencia

`source_type` identifica el tipo de origen de la evidencia.

`source_ref` identifica la referencia concreta que permite localizar o reconstruir su origen.

El contrato no establece un catálogo universal de tipos de fuente ni decide qué fuentes son admisibles para una regla concreta.

---

## 10. Temporalidad

La temporalidad puede ser relevante para determinar la suficiencia de una evidencia.

Este contrato exige conservar `captured_at` cuando forme parte del contexto de evidencia.

Las ventanas temporales concretas son requisitos de cada regla y no se definen universalmente aquí.

Por tanto:

```text
Evidence Contract
→ conserva y hace verificable la temporalidad

Rule / Dependency Matrix
→ determina qué ventana temporal exige una regla
```

---

## 11. Evidencia múltiple

Una regla puede requerir varias evidencias.

La existencia de varias evidencias no implica automáticamente que el requisito esté demostrado.

La evaluación deberá considerar el conjunto de evidencias conforme a los requisitos declarados por la regla y sus dependencias.

`Evidence Contract` no define la combinación lógica concreta de esas evidencias.

---

## 12. Evidencia indirecta y contextual

La evidencia puede formar parte de una cadena reproducible de demostración.

Sin embargo:

- una evidencia indirecta no demuestra automáticamente una conclusión superior;
- una evidencia contextual no demuestra por sí sola una condición de negocio;
- las relaciones necesarias deben poder justificarse y reproducirse.

La semántica concreta de la relación corresponde a la regla y a las dependencias que la sustentan.

---

## 13. Evidencia contradictoria

Cuando existan evidencias contradictorias, la contradicción debe conservarse explícitamente.

`Evidence Contract` no resuelve el conflicto mediante:

- promedio;
- prioridad arbitraria;
- último valor recibido;
- mayor o menor valor;
- score;
- otra regla implícita.

La resolución de conflictos pertenece a la autoridad correspondiente.

Una contradicción crítica no resuelta no puede utilizarse silenciosamente como si constituyera evidencia inequívoca.

---

## 14. Ausencia de evidencia

Cuando una evidencia requerida no existe:

```text
Evidence requerida
       ↓
     ausencia
       ↓
no puede demostrarse el requisito
       ↓
Rule puede resultar NOT_EVALUABLE
```

La ausencia de evidencia no se convierte en `FALSE` por defecto.

Por tanto:

```text
ausencia de evidencia ≠ FALSE
```

---

## 15. Calidad y confianza

`Quality & Trust Gate` mantiene la autoridad sobre la calidad y confianza de los datos.

`Evidence Contract` no constituye un segundo Quality & Trust Gate.

La relación es:

```text
QUALITY & TRUST
    ↓
calidad / confianza / integridad
    ↓
EVIDENCE CONTRACT
    ↓
admisibilidad para evaluación
```

---

## 16. Relación con F3

`Data Lineage & Provenance` y la especificación F3 mantienen la autoridad sobre demostrabilidad y trazabilidad de relaciones documentales y técnicas.

`Evidence Contract` utiliza esos principios para establecer los requisitos mínimos de una evidencia utilizable, pero no sustituye F3 ni crea una segunda capa de lineage.

---

## 17. Relación con Rule Dependency Matrix

La separación de responsabilidades es obligatoria:

### Evidence Contract

Define:

> qué características generales debe cumplir una evidencia para ser admisible y suficiente en principio.

### Rule Dependency Matrix

Define:

> qué evidencias necesita cada regla y qué dependencias concretas deben cumplirse.

### Rule

Define:

> qué condición se evalúa y cómo se obtiene su resultado.

---

## 18. Relación con Assessment

`Assessment` representa exclusivamente el resultado de evaluar una regla individual.

El flujo es:

```text
Evidence
    ↓
EvidenceValidation
    ↓
Rule
    ↓
Assessment
```

`Evidence Contract` no redefine `Assessment` ni añade campos al objeto `Assessment`.

La semántica de `Assessment` permanece:

```text
EVALUABLE → TRUE | FALSE
NOT_EVALUABLE → outcome = None
```

Por tanto:

```text
NOT_EVALUABLE ≠ FALSE
```

---

## 19. Relación con Trace

`Trace` conserva la información necesaria para reproducibilidad de la ejecución, incluyendo los `evidence_ids` utilizados.

`Trace` y `Evidence` son responsabilidades distintas:

```text
Evidence
→ objeto de evidencia

Trace
→ contexto reproducible de la ejecución
```

No se fusionan ambos contratos.

---

## 20. Relación con CRC

`Evidence Contract` no consolida evaluaciones ni resuelve conflictos entre reglas.

No produce:

- `COMPRAR`;
- `NEGOCIAR`;
- `COMPRAR CONDICIONADO`;
- `NO COMPRAR`;
- una decisión empresarial final.

Una evidencia válida solo permite que las capas posteriores dispongan de soporte para evaluar la regla correspondiente.

---

## 21. Estados conceptuales no operativos de C0

La Salvaguarda utiliza conceptualmente categorías como:

```text
LEGÍTIMA
LEGÍTIMA CON ADVERTENCIA
NO LEGÍTIMA PARA EVALUACIÓN
```

Estas categorías no constituyen estados físicos adicionales de `Evidence` en C0.

En particular, `LEGÍTIMA CON ADVERTENCIA` no se introduce como estado operativo en esta versión del contrato.

El contrato físico permanece limitado a:

```text
DEMONSTRATED
GAP
```

---

## 22. Invariantes

Deben preservarse como invariantes del MVP:

```text
DEMONSTRATED requiere demonstration_ref

GAP ≠ TRUE
GAP ≠ FALSE

ausencia de evidencia ≠ FALSE

NOT_EVALUABLE ≠ FALSE

NOT_EVALUABLE → outcome = None

EVALUABLE → outcome = TRUE | FALSE
```

Ninguna ampliación documental puede convertir estos invariantes en comportamiento opcional.

---

## 23. Prohibiciones

Este contrato no podrá:

1. crear reglas;
2. modificar reglas;
3. crear parámetros;
4. modificar parámetros;
5. determinar qué evidencia concreta necesita una regla;
6. introducir umbrales de negocio;
7. resolver conflictos entre reglas;
8. producir recomendaciones;
9. producir decisiones;
10. introducir estados físicos no implementados en C0;
11. transformar ausencia o GAP en `FALSE`;
12. sustituir Quality & Trust;
13. sustituir F3;
14. sustituir Trace;
15. convertirse en un segundo motor de decisión.

---

## 24. Compatibilidad con C0

Este contrato documental describe y formaliza la responsabilidad de evidencia ya presente en C0.

No modifica el modelo físico, la validación ni el flujo de ejecución.

En particular, no requiere cambios en:

- `models.py`;
- `validation.py`;
- tests;
- reglas;
- parámetros;
- C0;
- CRC.

La validación física actual conserva:

```text
DEMONSTRATED → VALID
GAP          → INVALID
```

---

## 25. Regla de no regresión

Cualquier modificación futura de este contrato deberá preservar:

```text
Evidence ≠ Rule
Evidence ≠ Assessment
Evidence ≠ Trace
Evidence ≠ CRC

GAP ≠ FALSE
NOT_EVALUABLE ≠ FALSE
```

Cualquier cambio que altere estas fronteras requiere una revisión formal de autoridad y alcance.

---

## 26. Criterio de cierre

El contrato se considera correctamente materializado cuando:

- coincide con el contrato físico de `Evidence` existente;
- no introduce estados físicos nuevos;
- no redefine reglas;
- no duplica `Rule Dependency Matrix`;
- no redefine `Assessment`;
- no absorbe `Trace`;
- no sustituye F3 ni Quality & Trust;
- conserva `GAP ≠ FALSE`;
- no requiere modificaciones técnicas para su cumplimiento.

---

## 27. Estado de materialización

**DICTAMEN:** MATERIALIZADO

**Tipo de cambio:** DOCUMENTACIÓN ÚNICAMENTE

**Cambios técnicos derivados:** NINGUNO

**Baseline C0:** NO ALTERADO

**Método aplicado:** DISEÑAR → AUDITAR → DEPURAR → AUDITAR CIERRE → MATERIALIZAR
