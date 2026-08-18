# DOC-004 — PROJECT CHARTER

**Proyecto:** EIOS — Enterprise Intelligent Operations System  
**Versión:** 2.0  
**Estado:** Aprobado  
**Documento:** Project Charter  
**Autoridad:** Identidad, propósito, visión, alcance y límites del proyecto

---

# 1. Identidad del Proyecto

**Nombre oficial:**

EIOS — Enterprise Intelligent Operations System

**Vertical MVP:**

EIOS Vertical — Intelligent Procurement Decision & Negotiation

---

# 2. Visión

Construir un sistema inteligente de apoyo a la decisión empresarial que ayude al CEO y al Responsable de Compras a evaluar, simular y negociar adquisiciones utilizando información financiera, operativa, comercial e histórica.

EIOS debe transformar datos empresariales en decisiones explicables, trazables y accionables.

**EIOS no sustituye al decisor.**

EIOS analiza, evalúa, simula, explica y recomienda.

La decisión empresarial final corresponde al usuario autorizado.

---

# 3. Objetivo Principal

Mejorar la calidad y seguridad de las decisiones de compra y negociación, evitando operaciones que puedan deteriorar injustificadamente:

- Liquidez
- Fondo de Maniobra
- Márgenes
- Rentabilidad
- Rotación de stock
- Capacidad financiera
- Riesgo empresarial

El sistema debe identificar también condiciones bajo las cuales una operación inicialmente desfavorable pueda convertirse en una alternativa viable mediante negociación o modificación de sus condiciones.

---

# 4. Usuarios

## Fase MVP

- CEO
- Responsable de Compras

## Evolución futura

- Comerciales
- Otros usuarios autorizados de la organización

---

# 5. Alcance del EIOS Vertical MVP

El Vertical MVP comprende la inteligencia aplicada a decisiones de adquisición y negociación.

Incluye:

- Evaluación de compras
- Histórico de precios
- Histórico de proveedores
- Situación financiera
- Ratios financieros
- Márgenes
- Stock
- Condiciones de compra
- Viabilidad
- Reglas de decisión
- Evidencia
- Escenarios
- Decision Twin
- Análisis de negociación
- Negotiation Ladder
- Resolución de conflictos
- Recomendaciones explicables
- Trazabilidad de decisiones

---

# 6. Fuera de Alcance

EIOS no sustituye:

- ERP
- Contabilidad
- Facturación
- Gestión contable
- Gestión operativa del ERP
- Registro automático de asientos
- Decisión empresarial del CEO

El sistema tampoco debe ejecutar unilateralmente una compra como consecuencia de una recomendación.

---

# 7. Principio de Decisión

La responsabilidad de decisión mantiene la siguiente relación:

```text
DATOS
  ↓
EVIDENCIA
  ↓
REGLAS
  ↓
EVALUACIÓN
  ↓
VIABILIDAD
  ↓
ESCENARIOS
  ↓
DECISION TWIN
  ↓
NEGOCIACIÓN
  ↓
RECOMENDACIÓN
  ↓
DECISOR
```

El resultado de EIOS es una recomendación fundamentada, no una orden automática.

---

# 8. Arquitectura Conceptual

EIOS se organiza mediante una arquitectura **Core + Vertical**.

```text
                 EIOS
                  │
        ┌─────────┴─────────┐
        │                   │
       CORE              VERTICAL
        │                   │
 Gobierno / Assurance   Procurement
 Modelo / Datos         Decision
 Arquitectura           & Negotiation
        │                   │
        └─────────┬─────────┘
                  │
             DECISIÓN EIOS
```

La arquitectura técnica concreta y sus tecnologías no forman parte de la autoridad de este Charter.

---

# 9. Principios Fundamentales

1. **El decisor mantiene el control.**
2. **Toda recomendación debe ser explicable.**
3. **Toda decisión relevante debe ser trazable.**
4. **La evidencia debe ser suficiente para evaluar.**
5. **Las reglas deben ser identificables y reproducibles.**
6. **Los escenarios deben poder compararse y versionarse.**
7. **EIOS debe preservar las restricciones financieras y empresariales definidas.**
8. **La configuración debe estar gobernada.**
9. **El sistema debe detectar y gestionar conflictos entre resultados.**
10. **Las salvaguardas de EIOS son obligatorias cuando estén definidas como tales.**

---

# 10. Independencia del ERP

EIOS debe poder utilizar información procedente del ERP u otras fuentes empresariales sin quedar conceptualmente limitado a un ERP concreto.

La fuente de datos y la implementación tecnológica podrán evolucionar sin modificar la identidad ni el propósito fundamental de EIOS.

---

# 11. Explicabilidad

Toda recomendación relevante debe poder explicar:

- qué se ha evaluado;
- qué datos y evidencias se han utilizado;
- qué reglas han intervenido;
- qué restricciones se han detectado;
- qué escenarios se han considerado;
- por qué se obtiene el resultado;
- qué condiciones podrían modificarlo.

---

# 12. Indicador Principal de Éxito

El EIOS Vertical MVP será considerado exitoso si permite al decisor:

> **tomar decisiones de compra y negociación mejor fundamentadas, reduciendo el riesgo de deterioro financiero u operativo y comprendiendo claramente el motivo de la recomendación.**

---

# 13. Límites de Responsabilidad

EIOS:

- no garantiza el resultado económico futuro;
- no sustituye el juicio empresarial;
- no convierte automáticamente una evaluación en una decisión;
- no debe ocultar incertidumbre o falta de evidencia;
- no debe presentar como certeza aquello que sea una estimación o escenario.

---

# 14. Evolución del Proyecto

La evolución de EIOS deberá respetar:

- la autoridad documental;
- la Salvaguarda Oficial del EIOS Vertical MVP;
- el Assurance Framework;
- la trazabilidad de decisiones;
- la separación entre definición conceptual, configuración e implementación.

Los cambios que afecten a identidad, propósito, alcance o límites requieren modificación formal de este Project Charter.

---

# 15. Estado

**Versión:** 2.0  
**Estado:** Aprobado

Esta versión sustituye al Charter v1.0 y establece oficialmente:

- EIOS como identidad del proyecto;
- EIOS Vertical como MVP actual;
- la separación Core + Vertical;
- el carácter de sistema de apoyo a la decisión;
- la inteligencia de negociación como parte del alcance;
- la responsabilidad final del decisor;
- los límites funcionales del sistema.
