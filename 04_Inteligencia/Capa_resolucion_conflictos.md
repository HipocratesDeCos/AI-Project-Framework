# CAPA DE RESOLUCIÓN DE CONFLICTOS — MVP

## EIOS — Enterprise Intelligent Operations System

**Versión:** 1.0  
**Estado:** MVP — Diseño conceptual aprobado  
**Ubicación:** `04_Inteligencia/Capa_Resolucion_Conflictos_MVP.md`

---

# 1. Propósito

La Capa de Resolución de Conflictos (CRC) es el componente de EIOS encargado de transformar los resultados de múltiples reglas en una única decisión empresarial coherente, explicable y trazable.

Su función es resolver situaciones en las que diferentes reglas pueden producir recomendaciones distintas o incluso contradictorias.

La CRC no sustituye al motor de reglas.

El motor de reglas determina qué condiciones se cumplen.

La CRC determina qué importancia tiene cada condición y cómo debe influir en la decisión final.

---

# 2. Objetivo empresarial

EIOS no debe limitarse a detectar problemas.

Debe ayudar a encontrar la alternativa económicamente más viable para realizar una operación cuando sea posible.

Principio fundamental:

> **EIOS no pretende impedir comprar. Pretende evitar comprar mal.**

Por tanto, ante una situación desfavorable, el sistema debe intentar determinar si existe una condición que permita realizar la operación sin comprometer la situación económico-financiera de la empresa.

---

# 3. Posición dentro de la arquitectura

La Capa de Resolución de Conflictos se sitúa entre el motor de reglas y la decisión final.

```text
DATOS
  ↓
VALIDACIÓN Y CALIDAD DE DATOS
  ↓
CÁLCULOS E INDICADORES
  ↓
PARÁMETROS
  ↓
MOTOR DE REGLAS
  ↓
CAPA DE RESOLUCIÓN DE CONFLICTOS
  ↓
DECISIÓN
  ↓
EXPLICACIÓN PARA EL USUARIO
