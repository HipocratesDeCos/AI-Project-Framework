# EIOS — VIABILITY FRONTIER METHODOLOGICAL MATRIX

**Versión:** 0.1  
**Estado:** DISEÑO — PENDIENTE DE AUTORIDAD METODOLÓGICA ESPECÍFICA  
**Baseline:** EIOS Vertical MVP  
**Fecha:** 01/09/2026

---

## 1. Propósito

Esta matriz formaliza el perímetro metodológico de la **Viability Frontier** sin convertir la arquitectura funcional en reglas, fórmulas, umbrales o decisiones empresariales no autorizadas.

Su finalidad es preparar la posterior implementación mediante la secuencia:

`metodología → regla → evidencia → evaluación → contrato → implementación → tests`

La matriz no crea criterios cuantitativos nuevos ni atribuye a Viability la decisión final de compra.

---

## 2. Autoridad utilizada

Fuentes demostradas:

- `01_Modelo/Especificacion_funcional.md` v2.0 — finalidad funcional, suficiencia de información, análisis multidimensional y recomendación humana.
- `03_Arquitectura/Architecture_Blueprint.md` v2.0 — definición arquitectónica de Viability Frontier, estados y separación respecto de CRC.
- `04_Reglas/Rule_Dependency_Matrix.md` v1.3 — gobierno de dependencias, evidencia y resultado ante ausencia de evidencia.
- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md` — catálogo vigente de parámetros, cuando una futura metodología autorice su consumo.

Ninguna fuente actualmente localizada autoriza por sí sola una fórmula completa de viabilidad ni un sistema de scoring compensatorio.

---

## 3. Perímetro funcional demostrado

La Viability Frontier debe determinar si una operación, bajo un escenario concreto y con la evidencia disponible, satisface las restricciones críticas y mantiene condiciones aceptables de valor, riesgo y sostenibilidad.

La evaluación puede recibir información procedente de:

- precio y TCO;
- stock y demanda;
- finanzas básicas;
- proveedor/riesgo;
- condiciones comerciales;
- impacto temporal;
- evidencia y calidad de datos;
- escenario concreto evaluado.

La Viability Frontier **no decide comprar**.

---

## 4. Estados canónicos

| Estado | Semántica | Consecuencia |
|---|---|---|
| `VIABLE` | Las restricciones críticas aplicables están satisfechas y existe evidencia suficiente para sostener la evaluación | El escenario puede pasar a las capas posteriores |
| `VIABLE_CON_CONDICIONES` | El escenario puede resultar aceptable si se cumplen condiciones explícitas, verificables y trazables | Puede pasar a negociación/CRC sujeto a las condiciones declaradas |
| `NO_VIABLE` | Existe al menos una condición o restricción crítica incumplida de forma demostrada | El escenario no puede tratarse como viable |
| `NO_EVALUABLE` | No existe evidencia suficiente o válida para determinar la viabilidad | No permite inferir viabilidad ni no viabilidad |

### Invariante VF-01

`NO_EVALUABLE` no equivale a `NO_VIABLE`.

### Invariante VF-02

`NO_VIABLE` requiere evidencia suficiente para demostrar el incumplimiento relevante.

### Invariante VF-03

`VIABLE_CON_CONDICIONES` debe declarar las condiciones que permiten sostener la viabilidad; no puede utilizarse como estado genérico de incertidumbre.

### Invariante VF-04

`VIABLE` no constituye una orden de compra ni una recomendación automática de comprar.

---

## 5. Separación Viability ↔ CRC

La Viability Frontier responde exclusivamente:

> **¿Este escenario satisface las condiciones de viabilidad definidas para la operación?**

La CRC responde posteriormente:

> **¿Qué decisión empresarial corresponde adoptar?**

Por tanto:

```text
VIABILITY
   ↓
ESTADO DE VIABILIDAD
   ↓
CRC
   ↓
DECISIÓN OFICIAL
```

Viability no puede emitir por sí misma:

- `COMPRAR`;
- `NEGOCIAR`;
- `COMPRAR CONDICIONADO`;
- `NO COMPRAR`;
- `INFORMACIÓN INSUFICIENTE` como decisión oficial de CRC.

Puede aportar evidencia y estado para que CRC adopte la decisión conforme a sus propias reglas.

---

## 6. Restricciones críticas

Una futura metodología autorizada deberá identificar explícitamente qué restricciones son críticas para cada operación o dominio evaluado.

Como mínimo, el diseño deberá permitir distinguir:

- restricción satisfecha;
- restricción incumplida;
- restricción no evaluable;
- condición pendiente de cumplimiento;
- evidencia contradictoria.

No se presupone que precio, margen, descuento o cualquier score sean por sí mismos una restricción crítica.

---

## 7. Evidencia mínima

Cada evaluación de viabilidad deberá poder identificar:

- escenario evaluado;
- datos utilizados;
- evidencias relevantes;
- reglas/metodología aplicadas;
- parámetros consumidos, si procede;
- restricciones evaluadas;
- resultado de cada restricción;
- razones del estado final;
- advertencias o condiciones pendientes.

La ausencia de evidencia crítica debe impedir una afirmación de viabilidad cuando la metodología así lo requiera.

---

## 8. Contradicciones

Las contradicciones relevantes no deben resolverse mediante heurística silenciosa.

Antes de implementar deberá quedar definido:

- qué contradicciones son materiales;
- qué fuente tiene autoridad cuando exista precedencia documental;
- cuándo una contradicción impide evaluar;
- cuándo puede continuar la evaluación con advertencia;
- cómo queda registrada la contradicción.

Hasta entonces, una contradicción crítica no resuelta deberá impedir una conclusión de viabilidad positiva.

---

## 9. Valor, riesgo y sostenibilidad

La arquitectura establece que la viabilidad debe mantener condiciones aceptables de:

- valor;
- riesgo;
- sostenibilidad.

Estos conceptos son dimensiones metodológicas, no fórmulas.

No se autoriza introducir un score agregado para compensar un incumplimiento crítico de otra dimensión.

---

## 10. Viabilidad condicional

`VIABLE_CON_CONDICIONES` solo podrá utilizarse cuando:

1. la condición esté explícitamente identificada;
2. sea verificable;
3. sea trazable;
4. no contradiga una restricción crítica ya incumplida;
5. pueda ser representada en el escenario o trasladada de forma inequívoca a la fase posterior.

No podrá utilizarse para ocultar datos ausentes, contradicciones críticas o metodología no definida.

---

## 11. Ausencia de información

Cuando falte información necesaria para evaluar una restricción crítica:

- no se sustituirá por cero;
- no se sustituirá por `False`;
- no se asumirá cumplimiento;
- no se asumirá incumplimiento;
- no se inventará un valor por defecto sin autoridad explícita.

El resultado será `NO_EVALUABLE` cuando esa ausencia impida pronunciarse.

---

## 12. Dependencia temporal

La evaluación debe quedar vinculada al escenario y a la fecha de evaluación.

Cambios relevantes en:

- precio;
- cantidad;
- plazo;
- recepción;
- stock;
- demanda;
- pagos;
- riesgo;
- cualquier otra variable material

generan un escenario distinto cuando así lo determine el gobierno de escenarios.

No debe sobrescribirse silenciosamente una evaluación anterior.

---

## 13. Resultado explicable

La salida metodológica deberá poder explicar:

```text
ESTADO
+
RESTRICCIONES EVALUADAS
+
RESTRICCIONES INCUMPLIDAS
+
CONDICIONES
+
EVIDENCIA
+
ADVERTENCIAS
```

La explicación debe ser reconstructible mediante la trazabilidad de EIOS.

---

## 14. Prohibiciones explícitas

La futura implementación de Viability no podrá:

- convertir `NO_EVALUABLE` en `NO_VIABLE`;
- convertir `NO_EVALUABLE` en `VIABLE`;
- convertir `VIABLE` en `COMPRAR`;
- compensar una restricción crítica incumplida mediante scoring;
- aceptar una conclusión positiva sin evidencia suficiente;
- crear umbrales empresariales no autorizados;
- inventar reglas o parámetros;
- asumir que una condición es cumplida sin evidencia;
- actuar como segundo CRC.

---

## 15. Puntos metodológicos pendientes

### VF-M01 — Catálogo de restricciones

Debe existir una autoridad que determine las restricciones críticas y no críticas aplicables a cada operación.

### VF-M02 — Criterio de valor

Debe definirse cómo se determina que el valor de un escenario es aceptable.

### VF-M03 — Criterio de riesgo

Debe definirse qué señales de riesgo son críticas y cómo afectan al estado.

### VF-M04 — Criterio de sostenibilidad

Debe definirse qué condiciones de sostenibilidad son evaluables en el MVP y con qué evidencia.

### VF-M05 — Viabilidad condicional

Debe definirse el catálogo de condiciones admisibles y su efecto exacto.

### VF-M06 — Resolución de conflictos

Debe definirse cómo se consolida el resultado de múltiples restricciones sin permitir compensaciones indebidas.

### VF-M07 — Dependencia con capas 1–5

Debe demostrarse qué salidas de PRICE, TCO, STK, FIN y Supplier/Risk son inputs obligatorios, opcionales o irrelevantes para cada evaluación.

### VF-M08 — Umbrales

No se implementarán umbrales de viabilidad mientras no exista autoridad documental específica.

### VF-M09 — Contradicciones

Debe quedar formalizado el tratamiento de contradicciones materiales entre capas y fuentes.

### VF-M10 — Resultado ante evidencia insuficiente

Debe concretarse qué ausencia conduce a `NO_EVALUABLE` y qué ausencia permite continuar con advertencia.

---

## 16. Criterio de entrada a implementación

Viability podrá pasar a contrato técnico únicamente cuando exista autoridad suficiente para determinar, como mínimo:

- catálogo de restricciones;
- criticidad;
- condiciones de evaluación;
- evidencia requerida;
- tratamiento de ausencia;
- tratamiento de contradicción;
- tratamiento de condiciones;
- relación demostrada con las capas 1–5;
- reglas de consolidación;
- trazabilidad del resultado.

**Estado actual:** NO APTO PARA IMPLEMENTACIÓN TÉCNICA.

---

## 17. Estado

**Viability Frontier Methodological Matrix v0.1**  
**Estado:** DISEÑO — PENDIENTE DE AUTORIDAD METODOLÓGICA ESPECÍFICA  
**No constituye contrato de implementación ni decisión empresarial.**
