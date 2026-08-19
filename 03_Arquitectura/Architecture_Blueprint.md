# EIOS — ARCHITECTURE BLUEPRINT

## Arquitectura de Referencia EIOS Vertical MVP

**Versión:** 2.0  
**Estado:** APROBADO  
**Función:** Definir la arquitectura estructural de EIOS y su Vertical MVP  
**Ubicación:** `03_Arquitectura/Architecture_Blueprint.md`

---

# 1. PROPÓSITO

Este documento define la arquitectura estructural de EIOS y su aplicación al:

**EIOS Vertical MVP — Decision & Negotiation Intelligence para compras.**

Su función es establecer:

- los componentes principales;
- sus relaciones;
- la separación entre EIOS Core y Vertical MVP;
- los flujos principales;
- los límites arquitectónicos.

No sustituye la Salvaguarda Oficial EIOS Vertical MVP ni la Matriz de Autoridad Documental.

---

# 2. PRINCIPIO ARQUITECTÓNICO

EIOS se estructura como:

```text
EIOS CORE
      │
      ▼
EIOS VERTICAL
      │
      ▼
DOMINIO EMPRESARIAL ESPECÍFICO
```

El Core contiene capacidades reutilizables.

El Vertical contiene la inteligencia específica del dominio de compras.

---

# 3. EIOS CORE

El Core reutilizable está compuesto por:

```text
EIOS CORE
│
├── Gobernanza
├── Quality & Trust Gate
├── Data Lineage & Provenance
├── Evidence Contract
├── Rule Dependency Matrix
├── Motor de Escenarios
├── Motor de Reglas
├── Centro de Parametrización
├── CRC
├── Assurance
├── Decision Versioning
└── Auditoría / Trazabilidad
```

Estas capacidades constituyen la base común sobre la que pueden construirse futuros verticales.

---

# 4. EIOS VERTICAL MVP

El Vertical MVP corresponde a:

**Decision & Negotiation Intelligence para compras.**

Su arquitectura funcional es:

```text
PROPUESTA DE COMPRA
        │
        ▼
CAPA 0 — QUALITY & TRUST
        │
        ▼
CAPA 1 — INTELIGENCIA DE PRECIO
        │
        ▼
CAPA 2 — TCO
        │
        ▼
CAPA 3 — STOCK / DEMANDA
        │
        ▼
CAPA 4 — FINANZAS BÁSICA
        │
        ▼
CAPA 5 — PROVEEDOR / RIESGO
        │
        ▼
VIABILITY FRONTIER
        │
        ▼
VIABILITY SCENARIO ENGINE
        │
        ▼
DECISION TWIN
        │
        ▼
NEGOTIATION INTELLIGENCE
        │
        ▼
NEGOTIATION LADDER
        │
        ▼
CRC
        │
        ▼
DECISIÓN CEO
```

**Assurance atraviesa todo el flujo.**

---

# 5. CAPA 0 — QUALITY & TRUST

## Función

Determinar si los datos son suficientemente fiables para que EIOS pueda pronunciarse.

## Controles

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

## Estados

```text
APTO
APTO CON ADVERTENCIAS
NO APTO
```

## Confianza

```text
ALTA
MEDIA
BAJA
```

## Regla arquitectónica

> La ausencia, contradicción o incertidumbre de un dato crítico no debe convertirse silenciosamente en cero, falso o valor por defecto.

---

# 6. CAPA 1 — INTELIGENCIA DE PRECIO

La capa de precio incorpora:

- Precio de Referencia (PR);
- Precio Objetivo (PO);
- Precio Máximo Recomendado (PMR);
- PPV como señal.

Debe preservar:

- comparabilidad real;
- unidad y cantidad;
- fecha;
- condiciones;
- trazabilidad;
- exclusiones justificadas.

El PMR permanece sin fórmula definitiva mientras no exista especificación aprobada.

---

# 7. CAPA 2 — TCO

El TCO se estructura en:

## TCO directo

- precio;
- transporte;
- seguro;
- aranceles;
- impuestos no recuperables;
- manipulación directa;
- inspecciones necesarias;
- merma directamente atribuible;
- otros costes directos.

## Costes derivados

- almacenamiento;
- exceso;
- obsolescencia;
- devoluciones;
- incidencias.

## Finanzas / oportunidad

- financiación;
- coste de capital;
- liquidez;
- coste de oportunidad.

### Regla

Cada coste debe tener una capa principal y no duplicarse como coste decisorio entre capas.

---

# 8. CAPA 3 — STOCK Y DEMANDA

La capa se estructura en:

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
- demanda extraordinaria etiquetada;
- forecasting multimétodo;
- cobertura ≠ rotación;
- exceso ≠ stock elevado;
- compra comparada contra escenario base sin compra.

---

# 9. CAPA 4 — FINANZAS BÁSICA

El MVP contempla:

- liquidez;
- pagos;
- impacto de la compra;
- situación proyectada;
- sobreinmovilización;
- crédito comercial;
- conceptos esenciales de CCC cuando proceda.

Flujo:

```text
SITUACIÓN ACTUAL
      ↓
IMPACTO DE LA COMPRA
      ↓
SITUACIÓN PROYECTADA
      ↓
RECOMENDACIÓN
```

Los umbrales son parametrizables.

---

# 10. CAPA 5 — PROVEEDOR / RIESGO

La capa contempla:

- fiabilidad;
- cumplimiento;
- riesgo;
- alternativas;
- concentración cuando sea relevante;
- comportamiento histórico;
- señales críticas.

No constituye un SRM completo.

---

# 11. MOTOR DE REGLAS

El Motor de Reglas transforma:

```text
EVIDENCIA
+
PARÁMETROS
+
REGLAS
      ↓
EVALUACIÓN
```

Las reglas no deben pronunciarse cuando carecen de la evidencia mínima necesaria.

Una regla no evaluable no equivale a una regla falsa.

---

# 12. EVIDENCE CONTRACT

Cada regla debe declarar qué evidencia necesita para poder pronunciarse.

Estados:

```text
LEGÍTIMA
LEGÍTIMA CON ADVERTENCIA
NO LEGÍTIMA PARA EVALUACIÓN
```

La evidencia debe conservar trazabilidad suficiente para reconstruir la evaluación.

---

# 13. RULE DEPENDENCY MATRIX

Cada regla deberá declarar:

- datos necesarios;
- evidencias requeridas;
- calidad mínima;
- criticidad;
- temporalidad;
- fuentes admisibles;
- capas afectadas;
- resultado si falta evidencia.

Esta matriz permite conocer las dependencias de cada decisión.

---

# 14. CENTRO DE PARAMETRIZACIÓN

El Centro de Parametrización controla los elementos configurables de EIOS.

Su función es separar:

```text
LÓGICA DEL SISTEMA
        ≠
CONFIGURACIÓN
```

Los cambios de parámetros deben ser identificables y versionables.

---

# 15. MOTOR DE ESCENARIOS

El Motor de Escenarios:

- crea escenarios;
- conserva escenarios;
- versiona;
- recalcula;
- traza.

Regla:

> Todo cambio relevante genera un nuevo escenario y nunca sobrescribe el anterior.

---

# 16. VIABILITY FRONTIER

La Viability Frontier define las condiciones bajo las cuales una operación puede considerarse viable.

No significa:

- menor precio;
- mayor margen;
- mayor descuento;
- mayor score.

Significa:

> Satisfacer restricciones críticas y mantener valor, riesgo y sostenibilidad aceptables.

Estados:

```text
VIABLE
VIABLE CON CONDICIONES
NO VIABLE
NO EVALUABLE
```

**VIABLE ≠ COMPRAR.**

La decisión corresponde a la CRC.

---

# 17. VIABILITY SCENARIO ENGINE

Proceso:

```text
ESCENARIO ACTUAL
      ↓
CAUSAS DE INVIABILIDAD
      ↓
VARIABLES RELEVANTES
      ↓
ESCENARIOS CANDIDATOS
      ↓
QUALITY & TRUST
      ↓
CAPAS 1–5
      ↓
VIABILITY FRONTIER
      ↓
COMPARACIÓN
```

No debe:

- generar escenarios al azar;
- cruzar restricciones críticas;
- aceptar escenarios sin evidencia;
- detenerse en la primera solución viable.

---

# 18. DECISION TWIN

El Decision Twin representa dinámicamente una operación concreta.

Permite:

> ¿Qué pasa si cambio esto?

Puede simular:

- precio;
- cantidad;
- plazo;
- descuentos;
- rappels;
- transporte;
- entrega;
- otras variables negociables.

No representa un gemelo digital de toda la empresa.

No constituye un segundo motor de decisión.

---

# 19. NEGOTIATION INTELLIGENCE

Determina la estrategia negociadora a partir de los escenarios viables.

Analiza:

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

> No negociar variables aisladas; negociar intercambios de valor.

No forma parte del MVP:

- negociación autónoma;
- ZOPA probabilística;
- predicción avanzada de aceptación;
- ejecución automática.

---

# 20. NEGOTIATION LADDER

Secuencia:

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

Cada escalón corresponde a un escenario evaluado.

No puede cruzar salvaguardas.

---

# 21. CRC

La CRC mantiene la decisión oficial:

```text
COMPRAR
NEGOCIAR
COMPRAR CONDICIONADO
NO COMPRAR
INFORMACIÓN INSUFICIENTE
```

No se permite compensar automáticamente bloqueos críticos mediante puntuación.

La decisión final permanece bajo control humano.

---

# 22. ASSURANCE

Assurance constituye una capacidad transversal.

Incluye conceptualmente:

```text
Quality & Trust Gate
Data Lineage & Provenance
Golden Dataset
Adversarial Testing
Backtesting
Shadow Mode
Override Governance
Decision Monitoring
Drift Management
Fail-Safe & Recovery
Decision Versioning
```

Principio:

> EIOS debe poder demostrar que, en el momento de decidir, disponía de información válida, metodología controlada, configuración conocida y trazabilidad reproducible.

Assurance atraviesa todo el flujo del Vertical MVP.

---

# 23. DECISION VERSIONING

Toda decisión relevante debe poder reconstruirse mediante:

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

Ningún cambio relevante debe destruir la capacidad de reconstruir una decisión anterior.

---

# 24. AUDITORÍA Y TRAZABILIDAD

La arquitectura debe permitir reconstruir:

```text
QUÉ
+
CON QUÉ DATOS
+
CON QUÉ REGLAS
+
CON QUÉ PARÁMETROS
+
EN QUÉ VERSIÓN
+
CUÁNDO
+
POR QUIÉN
```

La trazabilidad forma parte del diseño, no de una función posterior.

---

# 25. PRINCIPIO DE SEPARACIÓN

EIOS separa:

```text
DATOS
   ↓
EVIDENCIA
   ↓
REGLAS
   ↓
EVALUACIÓN
   ↓
ESCENARIOS
   ↓
VIABILIDAD
   ↓
NEGOCIACIÓN
   ↓
DECISIÓN
```

Esta separación evita que una capa absorba indebidamente responsabilidades de otra.

---

# 26. INDEPENDENCIA DEL ERP

EIOS no constituye un ERP.

La arquitectura debe permanecer desacoplada del sistema transaccional que proporcione los datos.

El ERP puede actuar como fuente de datos, pero no determina:

- la autoridad de EIOS;
- las reglas decisionales;
- la arquitectura;
- la lógica de negociación.

---

# 27. CONTROL HUMANO

Principio fundamental:

> **EIOS analiza, simula, explica y recomienda; el CEO decide.**

El MVP no ejecutará automáticamente decisiones empresariales.

---

# 28. COMPONENTES FUERA DEL MVP

Quedan fuera del Vertical MVP:

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

# 29. RELACIÓN CON LA SALVAGUARDA

La arquitectura definida aquí está subordinada a:

`00_Gobierno/EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md`

La Salvaguarda establece el punto de congelación arquitectónica vigente.

Este Blueprint desarrolla la estructura arquitectónica sin sustituir dicha Salvaguarda.

---

# 30. RELACIÓN CON OTROS MAPAS

| Documento | Función |
|---|---|
| `Framework_Map.md` | Índice documental |
| `Master_Project_Map.md` | Mapa global del sistema/proyecto |
| `Architecture_Blueprint.md` | Arquitectura estructural de referencia |
| `Matriz_Autoridad_Documental.md` | Autoridad documental |

---

# 31. PRINCIPIO FINAL

> EIOS debe mantener separadas la evidencia, la lógica, la simulación, la negociación y la decisión, garantizando trazabilidad y control humano.

---

# 32. ESTADO

**Versión:** 2.0  
**Estado:** APROBADO  
**Baseline:** EIOS Vertical MVP  
**Arquitectura:** Vertical MVP congelada por Salvaguarda Oficial  
**Gobierno:** Activo
