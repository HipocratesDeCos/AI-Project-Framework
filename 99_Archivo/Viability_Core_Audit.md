# Viability_Core_Audit

**Proyecto:** EIOS — Enterprise Intelligent Operations System  
**Objeto:** Auditoría del nuevo núcleo de propuesta de valor  
**Versión:** 0.1  
**Estado:** PROPUESTA — pendiente de aprobación

---

## 1. Alcance

Se audita la coherencia entre:

- [[Viability_Frontier]]
- [[Viability_Scenario_Engine]]
- [[Decision_Twin]]
- [[Negotiation_Ladder]]

y la arquitectura existente de EIOS:

- CAPA 0 — Gatekeeper / Quality & Trust
- CAPA 1 — Inteligencia de Precio
- CAPA 2 — TCO
- CAPA 3 — Stock y demanda
- CAPA 4 — Finanzas / liquidez
- CAPA 5 — Proveedor / riesgo
- CAPA 6 — Resolución de conflictos
- [[Motor_Escenarios]]
- Assurance Framework

## 2. Veredicto

**ARQUITECTURA COMPATIBLE — CON AJUSTES NECESARIOS**

El nuevo núcleo no sustituye la arquitectura existente. La reutiliza y añade una función nueva:

> **Transformar una evaluación estática de compra en una búsqueda controlada de condiciones que pueden hacer viable la operación y en una estrategia de negociación basada en esas condiciones.**

## 3. Compatibilidades confirmadas

### EIOS recomienda; el CEO decide

El nuevo núcleo mantiene el control humano. El Decision Twin analiza, simula y explica, pero no ejecuta automáticamente una decisión empresarial.

### CRC mantiene la autoridad sobre la decisión

Frontera de Viabilidad y Scenario Engine generan, evalúan y comparan alternativas. La CRC mantiene la decisión oficial.

### Motor de Escenarios vs Viability Scenario Engine

Son componentes distintos:

- `Motor_Escenarios`: infraestructura transversal de creación, conservación, recálculo y trazabilidad.
- `Viability_Scenario_Engine`: búsqueda y evaluación de escenarios candidatos orientados a cruzar la frontera de viabilidad.

El segundo debe utilizar al primero y no duplicarlo.

## 4. Principales puntos críticos

### 4.1 VIABLE no equivale a COMPRAR

**VIABLE** es una propiedad del escenario.

**COMPRAR / NEGOCIAR / COMPRAR CONDICIONADO / NO COMPRAR / INFORMACIÓN INSUFICIENTE** son decisiones de la CRC.

Una operación puede ser viable y aun así recibir **NEGOCIAR** porque todavía existe margen de mejora.

### 4.2 Viabilidad no puede ser un score único

La viabilidad debe mantenerse como condición multidimensional basada en:

- restricciones críticas;
- valor económico;
- situación operativa;
- situación financiera;
- riesgo;
- calidad de evidencia.

No debe existir compensación automática de una salvaguarda crítica mediante una puntuación.

### 4.3 No aceptar la primera solución viable

El Scenario Engine debe:

1. detectar causas;
2. identificar variables capaces de modificar esas causas;
3. generar candidatos relevantes;
4. descartar imposibles;
5. validar;
6. comparar;
7. conservar alternativas relevantes.

### 4.4 La mejor alternativa necesita una política propia

Aún no se define qué significa exactamente **MEJOR**.

Podrá considerar:

- valor económico;
- menor intervención;
- riesgo;
- robustez;
- facilidad de negociación;
- liquidez;
- equilibrio multidimensional.

Esta política no debe surgir accidentalmente de un score.

### 4.5 Viabilidad y negociabilidad son dimensiones distintas

Una alternativa puede ser viable pero poco negociable, o viable y altamente negociable.

Esto deberá alimentar posteriormente la Negotiation Ladder.

### 4.6 La Ladder necesita plausibilidad negociadora

Una combinación matemáticamente viable puede ser comercialmente poco realista.

La Ladder tendrá que distinguir entre:

- viabilidad económica;
- viabilidad operativa;
- plausibilidad negociadora.

### 4.7 BATNA y ZOPA deben estar respaldadas por evidencia

No deben inventarse BATNA, ZOPA ni probabilidades de aceptación.

Si son inferidas, deben aparecer como inferidas. Si no existe evidencia suficiente, debe declararse.

### 4.8 Decision Twin debe ser reproducible

Cada estado importante debe poder reconstruirse mediante:

- Decision_ID;
- Scenario_ID;
- Data_Snapshot_ID;
- Rules_Version;
- Parameters_Version;
- Forecast_Version;
- RFP_Version;
- EIOS_Version;
- timestamp;
- usuario.

### 4.9 Decision Twin debe limitarse a la operación

No debe convertirse en un gemelo digital completo de la empresa ni en un ERP paralelo.

Representa la decisión de una operación concreta y consume información empresarial externa.

### 4.10 La frontera debe degradarse de forma segura

Si falta evidencia crítica:

**NO EVALUABLE**

y no:

**VIABLE**

## 5. Arquitectura corregida

```text
                 OPERACIÓN
                     │
                     ▼
              QUALITY & TRUST
                     │
                     ▼
                   CAPA 1–5
                     │
                     ▼
              MOTOR DE ESCENARIOS
                     │
                     ▼
         VIABILITY SCENARIO ENGINE
                     │
                     ▼
            VIABILITY FRONTIER
                     │
             ┌───────┴───────┐
             ▼               ▼
        NO VIABLE          VIABLE
             │               │
             └───────┬───────┘
                     ▼
               DECISION TWIN
                     │
                     ▼
             NEGOTIATION LADDER
                     │
                     ▼
                    CRC
                     │
                     ▼
                  DECISIÓN
                     │
                     ▼
                 ASSURANCE
```

## 6. Nuevas propiedades recomendadas

### Robustez de escenario

¿Sigue siendo viable si pequeñas variables cambian?

### Margen de viabilidad

Distancia entre el escenario y la frontera de inviabilidad.

### Credibilidad de la alternativa

Combinación de viabilidad y calidad de evidencia.

Estas métricas quedan pendientes de diseño metodológico.

## 7. Veredicto Red Team

### Viability_Frontier

🟢 Arquitectónicamente sólida.

### Viability_Scenario_Engine

🟢 Compatible.

### Decision_Twin

🟢 Muy prometedor; mantener limitado a la operación.

### Negotiation_Ladder

🟢 Conceptualmente válida.

### Principales riesgos

🔴 Convertir la viabilidad en un score opaco.

🔴 Confundir VIABLE con COMPRAR.

🔴 Generar escenarios matemáticamente viables pero comercialmente poco negociables.

## 8. Decisiones fijadas

1. **VIABLE ≠ COMPRAR.**
2. `Motor_Escenarios` y `Viability_Scenario_Engine` son componentes distintos.
3. `Decision_Twin` representa una operación, no toda la empresa.
4. No habrá un score único como fundamento de la viabilidad.
5. La mejor alternativa tendrá una política de ranking propia.
6. BATNA/ZOPA solo con evidencia suficiente.
7. Robustez y margen de viabilidad quedan como propiedades futuras.
8. Todo escenario relevante debe ser reproducible mediante Assurance.

## 9. Próximo componente candidato

### Negotiation Intelligence

Resolverá:

> **¿Qué concesión conviene pedir, cuál conviene ofrecer y qué intercambio maximiza la probabilidad de llegar a una operación viable sin regalar valor?**

Podrá integrar posteriormente:

- valor de concesión;
- reciprocidad;
- BATNA;
- ZOPA;
- negociabilidad;
- robustez.

## 10. Estado

**PROPUESTA v0.1 — pendiente de aprobación.**