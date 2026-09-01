# EIOS — Salvaguarda Oficial EIOS Vertical MVP

**Fecha:** 16/08/2026  
**Estado:** VIGENTE — punto de congelación arquitectónica  
**Ámbito:** EIOS Vertical MVP — Decision & Negotiation Intelligence para compras

---

## 1. Propósito

Esta salvaguarda congela el estado conceptual alcanzado por EIOS y sirve de referencia antes de reorganizar GitHub, archivos locales, Obsidian y el futuro Proyecto de ChatGPT.

**No sustituye los documentos oficiales de GitHub hasta su incorporación y aprobación allí.**

---

## 2. Identidad del Vertical MVP

### Nombre de trabajo

**EIOS Vertical MVP — Decision & Negotiation Intelligence**

### Propuesta de valor

> **“Tengo esta compra delante: ¿es viable, qué tendría que cambiar para hacerla viable, qué alternativas tengo, qué debo negociar y hasta dónde puedo llegar?”**

### Principio

> **EIOS analiza, simula, explica y recomienda; el CEO decide.**

El MVP no ejecutará automáticamente decisiones empresariales.

---

## 3. EIOS Core reutilizable

La nueva arquitectura separa una base común, reutilizable por futuros verticales:

```text
EIOS CORE
├── Gobernanza
├── Quality & Trust Gate
├── Data Lineage & Provenance
├── Evidence Contract
├── Rule Dependency Matrix
├── Motor de Escenarios
├── Motor de Reglas
├── Centro de Parametrización
├── CRC
├── Assurance Framework
├── Decision Versioning
└── Auditoría / Trazabilidad
```

---

## 4. EIOS Vertical MVP

```text
PROPUESTA DE COMPRA
        ↓
CAPA 0 — QUALITY & TRUST
        ↓
CAPA 1 — INTELIGENCIA DE PRECIO
        ↓
CAPA 2 — TCO
        ↓
CAPA 3 — STOCK / DEMANDA
        ↓
CAPA 4 — FINANZAS BÁSICA
        ↓
CAPA 5 — PROVEEDOR / RIESGO
        ↓
VIABILITY FRONTIER
        ↓
VIABILITY SCENARIO ENGINE
        ↓
DECISION TWIN
        ↓
NEGOTIATION INTELLIGENCE
        ↓
NEGOTIATION LADDER
        ↓
CRC
        ↓
DECISIÓN CEO
```

**Assurance atraviesa todo el flujo.**

---

## 5. CAPA 0 — Quality & Trust

### Función

Determinar si los datos son suficientemente fiables para que las capas puedan pronunciarse.

### Controles

- existencia;
- integridad;
- validez;
- consistencia interna;
- consistencia entre fuentes;
- temporalidad;
- semántica;
- trazabilidad;
- contradicciones críticas;
- modificaciones humanas.

### Estados

```text
APTO
APTO CON ADVERTENCIAS
NO APTO
```

Confianza:

```text
ALTA / MEDIA / BAJA
```

### Regla crítica

> La ausencia, contradicción o incertidumbre de un dato crítico no debe convertirse silenciosamente en cero, falso o valor por defecto.

---

## 6. CAPA 1 — Inteligencia de Precio

Conceptos:

- PR — Precio de Referencia;
- PO — Precio Objetivo;
- PMR — Precio Máximo Recomendado;
- PPV como señal.

Principios:

- comparabilidad real;
- unidad y cantidad;
- fecha y condiciones;
- trazabilidad de exclusiones;
- PMR aún sin fórmula definitiva.

---

## 7. CAPA 2 — TCO

### TCO directo

- precio;
- transporte;
- seguro;
- aranceles;
- impuestos no recuperables;
- manipulación directa;
- inspecciones necesarias;
- merma directamente atribuible;
- otros costes directos.

### Costes derivados

- almacenamiento;
- exceso;
- obsolescencia;
- devoluciones;
- incidencias.

### Finanzas / oportunidad

- financiación;
- coste de capital;
- liquidez;
- coste de oportunidad.

**Regla:** cada coste debe tener una capa principal y no duplicarse como coste decisorio entre capas.

---

## 8. CAPA 3 — Stock y Demanda

Arquitectura fijada:

```text
3.1 Estado de stock
3.2 Demanda
3.3 Cobertura y rotación
3.4 Exceso y permanencia
3.5 Impacto de la compra
3.6 Resolución de stock
```

Principios:

- stock físico ≠ stock disponible;
- stock comprometido separado;
- compras en tránsito separadas;
- stock proyectado temporal;
- demanda histórica ≠ proyectada;
- demanda extraordinaria etiquetada, no eliminada;
- forecasting multimétodo;
- cobertura ≠ rotación;
- exceso ≠ stock elevado;
- compra comparada contra escenario base sin compra.

---

## 9. CAPA 4 — Finanzas

### MVP

- liquidez;
- pagos;
- impacto de la compra;
- situación proyectada;
- sobreinmovilización;
- crédito comercial;
- conceptos esenciales de CCC cuando proceda.

Principio:

> **Situación actual → impacto de la compra → situación proyectada → recomendación.**

Los umbrales son parametrizables.

---

## 10. CAPA 5 — Proveedor / Riesgo

MVP:

- fiabilidad;
- cumplimiento;
- riesgo;
- alternativas;
- concentración cuando sea relevante;
- comportamiento histórico;
- señales críticas.

No se construye un SRM completo.

---

## 11. Motor de Escenarios

El motor transversal:

- crea escenarios;
- conserva escenarios;
- versiona;
- recalcula;
- traza.

Regla:

> Todo cambio relevante genera un nuevo escenario y nunca sobrescribe el anterior.

---

## 12. Viability Frontier

Define las condiciones bajo las cuales una operación puede considerarse viable.

No significa:

- menor precio;
- mayor margen;
- mayor descuento;
- mayor score.

Sí significa:

> **Satisfacer restricciones críticas y mantener valor, riesgo y sostenibilidad aceptables.**

Estados:

```text
VIABLE
VIABLE CON CONDICIONES
NO VIABLE
NO EVALUABLE
```

**VIABLE ≠ COMPRAR.** La decisión pertenece a la CRC.

---

## 13. Viability Scenario Engine

Proceso:

```text
Escenario actual
 ↓
causas de inviabilidad
 ↓
variables relevantes
 ↓
escenarios candidatos
 ↓
QTG
 ↓
CAPA 1–5
 ↓
Viability Frontier
 ↓
comparación
```

No debe:

- generar escenarios al azar;
- cruzar restricciones críticas;
- aceptar escenarios sin evidencia;
- detenerse en la primera solución viable.

---

## 14. Decision Twin

Representa dinámicamente **una operación concreta**.

Permite:

> **“¿Qué pasa si cambio esto?”**

Puede simular:

- precio;
- cantidad;
- plazo;
- descuentos;
- rappels;
- transporte;
- entrega;
- otras variables negociables.

No es un gemelo digital de toda la empresa ni un segundo motor de decisión.

---

## 15. Negotiation Intelligence

Determina y justifica **contenido negociador** a partir de información y resultados autorizados.

Puede analizar:

- primera petición;
- concesiones;
- reciprocidad;
- negociabilidad;
- BATNA cuando exista evidencia;
- ZOPA cuando exista evidencia suficiente;
- robustez;
- coste de concesión;
- intercambios de valor.

Principio:

> **No negociar variables aisladas; negociar intercambios de valor.**

NI no crea, gobierna ni activa Strategy, y no decide, aprueba ni ejecuta.

No entra en MVP:

- negociación autónoma;
- ZOPA probabilística;
- predicción avanzada de aceptación;
- ejecución automática.

---

## 16. Negotiation Ladder

Secuencia representacional:

```text
OBJETIVO
 ↓
PRIMERA PETICIÓN
 ↓
CONCESIÓN 1
 ↓
CONCESIÓN 2
 ↓
FALLBACK
 ↓
WALK-AWAY
```

Cada escalón representa contenido negociador previamente determinado y justificado y conserva referencia a su fuente autorizada. Un `Scenario_ID` se utiliza cuando el contenido esté efectivamente vinculado a un escenario formal; no se impone un escenario por cada escalón.

No debe cruzar salvaguardas.

---

## 17. Tradeoff Intelligence

**Estado: BORRADOR EXPLORATORIO — NO componente independiente del MVP.**

El concepto se conserva dentro de Negotiation Intelligence.

Su función conceptual:

> **qué podemos dar a cambio de qué y cuál de esos intercambios crea más valor empresarial.**

---

## 18. Robustez y margen de viabilidad

Quedan como propiedades de evolución del MVP:

**Robustez:** cuánto puede deteriorarse una variable antes de perder viabilidad.

**Margen de viabilidad:** distancia entre el escenario y la frontera de inviabilidad.

Cuando las alternativas sean comparables, se favorecerán soluciones más robustas.

---

## 19. Assurance Framework

Componentes:

```text
A01 Quality & Trust Gate
A02 Data Lineage & Provenance
A03 Golden Dataset
A04 Adversarial Testing
A05 Backtesting
A06 Shadow Mode
A07 Override Governance
A08 Decision Monitoring
A09 Drift Management
A10 Fail-Safe & Recovery
A11 Decision Versioning
```

Principio:

> **EIOS debe poder demostrar que, en el momento de decidir, disponía de información válida, metodología controlada, configuración conocida y trazabilidad reproducible.**

---

## 20. Evidence Contract

Cada regla debe declarar qué evidencia necesita para poder pronunciarse.

Estados conceptuales:

```text
LEGÍTIMA
LEGÍTIMA CON ADVERTENCIA
NO LEGÍTIMA PARA EVALUACIÓN
```

**Regla no evaluable ≠ regla falsa.**

---

## 21. Rule Dependency Matrix

Cada regla deberá declarar:

- datos necesarios;
- evidencias requeridas;
- calidad mínima;
- criticidad;
- temporalidad;
- fuentes admisibles;
- capas afectadas;
- resultado si falta evidencia.

---

## 22. CRC

La CRC mantiene la decisión oficial:

```text
COMPRAR
NEGOCIAR
COMPRAR CONDICIONADO
NO COMPRAR
INFORMACIÓN INSUFICIENTE
```

No se permite compensar automáticamente bloqueos críticos mediante puntuación.

---

## 23. Assurance y trazabilidad

Todo escenario relevante deberá poder reconstruirse mediante:

```text
Decision_ID
Scenario_ID
Data_Snapshot_ID
Rules_Version
Parameters_Version
Forecast_Version
RFP_Version
EIOS_Version
Timestamp
User
```

---

## 24. Fuera del Vertical MVP

Se pospone:

- ZOPA probabilística;
- BATNA probabilística;
- predicción avanzada de aceptación;
- agente autónomo;
- ejecución automática;
- optimización matemática compleja;
- Decision Twin de toda la empresa;
- forecasting excesivamente sofisticado;
- Tradeoff Engine independiente;
- SRM completo;
- ERP propio.

---

## 25. Gobierno documental

### GitHub

**Fuente oficial y versionada.**

### Obsidian

**Grafo de conocimiento, navegación y trabajo conceptual.**

### Local

**Zona temporal de producción.**

### Proyecto ChatGPT

**Capa de contexto de trabajo; no fuente maestra.**

---

## 26. Promoción documental

```text
BORRADOR
 ↓
PROPUESTA
 ↓
VALIDADO
 ↓
APROBADO
 ↓
OFICIAL
```

La existencia de un `.md` local o de una nota en Obsidian no la convierte en oficial.

---

## 27. Principios de continuidad

1. No eliminar material histórico antes de clasificarlo.
2. No sobrescribir documentación oficial sin aprobación.
3. No crear duplicados para resolver discrepancias.
4. No introducir nuevas capas sin auditoría arquitectónica.
5. No programar funciones críticas sin definir previamente sus evidencias y dependencias.
6. Mantener trazabilidad.
7. Mantener `Tradeoff_Intelligence` como borrador.
8. No usar la memoria del chat como fuente documental primaria.
9. No confundir propuesta conceptual con funcionalidad implementada.

---

## 28. Prioridad de construcción

```text
FASE 1 → Core + datos + QTG
FASE 2 → Precio + TCO
FASE 3 → Stock + finanzas básica
FASE 4 → Viability Frontier
FASE 5 → Scenario Engine + Decision Twin
FASE 6 → Negotiation Intelligence + Ladder
FASE 7 → CRC + Assurance
FASE 8 → Shadow Mode + piloto
```

---

## 29. Criterio de éxito

El Vertical MVP será exitoso si demuestra con operaciones reales que:

> **EIOS ayuda a identificar mejores condiciones de compra y negociación que el proceso humano de referencia, manteniendo trazabilidad y control humano.**

No se medirá por número de módulos ni sofisticación técnica.

---

## 30. Principal riesgo

> **Construir decisiones sofisticadas sobre datos semánticamente incorrectos, insuficientes o mal gobernados.**

Por eso Quality & Trust, Evidence y Assurance forman parte del núcleo.

---

## 31. Decisión estratégica

EIOS pasa de:

> **DSS integral de compras**

a:

> **Vertical de Decision & Negotiation Intelligence sobre un EIOS Core común.**

Se conserva la mayor parte del conocimiento y arquitectura desarrollados y se reduce deliberadamente el alcance técnico para priorizar una demostración vertical de valor.

---

## 32. Estado final

**SALVAGUARDA OFICIAL DEL DISEÑO ACTUAL — VIGENTE**

Esta salvaguarda es la referencia previa a la reorganización de:

- GitHub;
- archivos `.md` locales;
- Obsidian;
- futuro Proyecto de ChatGPT.

**No autoriza por sí misma ninguna modificación automática de esos entornos.**

### Próxima acción

> **Inventariar y clasificar el material existente antes de reorganizarlo.**
