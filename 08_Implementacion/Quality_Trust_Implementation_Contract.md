# EIOS — Quality & Trust Implementation Contract

## 1. Identidad

**Documento:** Quality & Trust Implementation Contract  
**Versión:** 0.1  
**Estado:** DISEÑO — pendiente de auditoría y cierre  
**Baseline de referencia:** EIOS-BL-001  
**Autoridad conceptual:** `03_Arquitectura/Architecture_Blueprint.md`  
**Arquitectura funcional:** `03_Arquitectura/DSS_Functional_Architecture.md`

---

## 2. Propósito

Define la frontera técnica mínima para materializar `Quality & Trust Gate` como capacidad de control previo a la evaluación analítica.

No constituye un motor de decisión ni una autoridad sobre reglas, parámetros, viabilidad, negociación, CRC o decisión empresarial.

Su función es determinar si el conjunto de entrada dispone de calidad y confianza suficientes para continuar hacia las capas posteriores, preservando las incertidumbres y contradicciones relevantes.

---

## 3. Autoridad y precedencia

La arquitectura estructural reconoce `Quality & Trust Gate` como capacidad Core.

La arquitectura funcional lo sitúa inmediatamente después del `Decision Input Package` y antes de las capas analíticas.

La definición de criterios generales de evidencia permanece bajo `04_Reglas/Evidence_Contract.md`.

Las dependencias concretas de reglas permanecen bajo `04_Reglas/Rule_Dependency_Matrix.md`.

Este contrato no sustituye ninguna de esas autoridades.

---

## 4. Entrada

La implementación recibe una representación de `Decision Input Package` ya identificada y trazable.

El contrato no crea un nuevo repositorio de datos ni redefine `InputContract`, `DecisionContext`, `Evidence` o `Trace`.

La entrada debe permitir identificar, cuando corresponda:

- datos de la propuesta;
- evidencia asociada;
- datos empresariales disponibles;
- parametrización vigente disponible;
- identidad contextual de la evaluación.

---

## 5. Controles mínimos

La implementación deberá poder evaluar, según disponibilidad y aplicabilidad:

- existencia;
- integridad;
- validez;
- consistencia interna;
- consistencia entre fuentes;
- temporalidad;
- semántica;
- trazabilidad;
- contradicciones críticas;
- modificaciones humanas relevantes.

La mera presencia de un campo no implica que el dato sea fiable.

---

## 6. Estados de salida

Los estados funcionales autorizados son exclusivamente:

```text
APTO
APTO_CON_ADVERTENCIAS
NO_APTO
```

No se introducen estados adicionales por implementación.

La salida de Quality & Trust no es una evaluación de regla y no equivale a `TRUE` o `FALSE`.

---

## 7. Confianza

La representación funcional reconoce tres niveles:

```text
ALTA
MEDIA
BAJA
```

La implementación no debe convertir un nivel de confianza en una decisión empresarial.

La fórmula o algoritmo de agregación de confianza queda fuera de este contrato mientras no exista especificación aprobada.

---

## 8. Incertidumbre y ausencia

La implementación no puede convertir silenciosamente:

```text
ausencia → 0
ausencia → FALSE
incertidumbre → certeza
contradicción → valor único arbitrario
```

Una deficiencia crítica debe conservarse como condición explícita del resultado de Quality & Trust.

La semántica `GAP ≠ FALSE` del Evidence Contract permanece intacta.

---

## 9. Contradicciones

Cuando existan fuentes contradictorias, la contradicción debe conservarse y hacerse visible.

Quality & Trust no resuelve mediante prioridad arbitraria, promedio, último valor, score u otra heurística no autorizada.

La resolución de conflictos entre resultados de reglas pertenece a `Capa_resolucion_conflictos.md` y CRC según corresponda.

---

## 10. Evidencia

Quality & Trust puede comprobar propiedades de calidad, integridad, consistencia y trazabilidad de la evidencia disponible.

No redefine los criterios generales de admisibilidad del `Evidence Contract`.

No determina qué evidencia concreta necesita una regla; esa responsabilidad permanece en la RDM y en las autoridades de reglas.

No modifica objetos `Evidence` ni genera un segundo sistema de evidencia.

---

## 11. Relación con C0

Quality & Trust precede funcionalmente al procesamiento analítico, pero no sustituye C0.

No modifica:

- `InputContract`;
- `DecisionContext`;
- `Evidence`;
- `EvidenceValidation`;
- `Rule`;
- `Assessment`;
- `Trace`.

La implementación futura deberá definir mediante pruebas la frontera exacta entre controles de calidad de entrada y validación de evidencia de C0.

---

## 12. Relación con Decision Versioning

Quality & Trust no crea ni redefine:

- `Decision_ID`;
- `Scenario_ID`;
- `Data_Snapshot_ID`;
- `Rules_Version`;
- `Parameters_Version`;
- `input_fingerprint`;
- `Trace`.

Cuando estén disponibles, estas referencias se conservan como contexto y no se convierten en nuevas autoridades.

---

## 13. No autoridad decisional

Quality & Trust no puede producir:

- `COMPRAR`;
- `NEGOCIAR`;
- `COMPRAR CONDICIONADO`;
- `NO COMPRAR`;
- recomendación CEO;
- decisión empresarial.

`NO_APTO` significa que el paquete no satisface las condiciones de calidad/confianza necesarias para continuar; no constituye una decisión de compra.

---

## 14. No duplicación

No se crearán por este contrato:

- segundo Evidence Contract;
- segundo Evidence Validation;
- segundo Trace;
- segundo mecanismo de fingerprint;
- segundo motor de reglas;
- segundo sistema de parámetros;
- segundo sistema de versionado.

---

## 15. Persistencia

Este contrato no autoriza todavía tablas SQL, ORM, API ni driver de base de datos específicos para Quality & Trust.

La persistencia física se diseñará únicamente después de cerrar las estructuras de salida y sus invariantes.

---

## 16. Tests mínimos previstos

Antes de cerrar la implementación deberán demostrarse, como mínimo:

- entrada íntegra → `APTO`;
- defecto no crítico → `APTO_CON_ADVERTENCIAS`;
- defecto crítico → `NO_APTO`;
- ausencia de dato crítico no convertida en cero/falso;
- contradicción crítica conservada;
- evidencia trazable conservada;
- no modificación de C0;
- no producción de decisión empresarial;
- determinismo sobre la misma entrada y contexto.

---

## 17. Límites

Este contrato no define:

- fórmulas de confianza;
- pesos de scoring;
- umbrales empresariales;
- reglas de negocio;
- parámetros concretos;
- selección de fuentes por regla;
- resolución de conflictos empresariales;
- viabilidad;
- escenarios;
- Decision Twin;
- negociación;
- CRC;
- decisión humana.

---

## 18. Criterio de cierre del contrato

Este contrato no podrá declararse CERRADO hasta demostrar mediante auditoría que:

1. sus entradas y salidas están respaldadas por autoridad funcional suficiente;
2. no duplica C0 ni Evidence Contract;
3. sus estados son los definidos por arquitectura;
4. las invariantes están materializadas en tests;
5. no introduce lógica empresarial no autorizada;
6. su implementación puede materializarse sin modificar componentes cerrados;
7. CI demuestra el comportamiento previsto.

**Estado actual: DISEÑO — NO CERRADO.**
