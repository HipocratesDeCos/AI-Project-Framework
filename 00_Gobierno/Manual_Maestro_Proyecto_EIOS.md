# MANUAL MAESTRO DEL PROYECTO EIOS

## EIOS — Enterprise Intelligent Operations System

**Documento:** Manual Maestro del Proyecto EIOS (MMP-EIOS)  
**Versión:** 2.1  
**Estado:** APROBADO — reconciliación de continuidad vigente  
**Fecha:** 13/09/2026  
**Ubicación oficial:** `00_Gobierno/Manual_Maestro_Proyecto_EIOS.md`

---

# 1. FUNCIÓN DEL MANUAL

El Manual Maestro del Proyecto EIOS es el documento de **orientación, navegación y continuidad** del proyecto.

Debe permitir responder rápidamente:

1. qué es EIOS;
2. qué Vertical se está construyendo;
3. cómo se organiza el proyecto;
4. dónde está la fuente oficial de cada materia;
5. cuál es el estado general;
6. dónde puede continuar el trabajo sin inventar autoridad.

El Manual Maestro **no es una segunda fuente normativa** y no debe reproducir íntegramente la lógica de los documentos especializados.

Cuando exista discrepancia, prevalece la fuente definida por `00_Gobierno/Matriz_Autoridad_Documental.md`.

---

# 2. IDENTIDAD Y FRONTERA DECISIONAL

**EIOS — Enterprise Intelligent Operations System** es un sistema inteligente de apoyo a la decisión empresarial basado en datos.

La arquitectura conceptual se estructura como:

**CORE + VERTICAL**

El Vertical MVP vigente se centra en:

**Intelligent Procurement Decision & Negotiation**

EIOS puede analizar, evaluar, simular, explicar y recomendar.

La decisión empresarial final corresponde al usuario autorizado.

> **EIOS analiza, evalúa, simula, explica y recomienda. El decisor decide.**

EIOS no sustituye al ERP, a la contabilidad ni al decisor humano y no debe ejecutar unilateralmente una compra como consecuencia de una recomendación.

---

# 3. DOCUMENTOS FUNDAMENTALES DE RECUPERACIÓN

La recuperación del proyecto debe comenzar por estas fuentes:

```text
00_Gobierno/
├── Project_Charter.md
├── Project_Context.md
├── Project_Governance.md
├── Matriz_Autoridad_Documental.md
├── Manual_Maestro_Proyecto_EIOS.md
├── EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md
└── Baselines/
    └── EIOS-BL-002.md

03_Arquitectura/
├── Framework_Map.md
└── Master_Project_Map.md
```

Funciones principales:

- `Project_Charter.md` → identidad, propósito, visión, alcance y límites.
- `Project_Context.md` → estado y continuidad vigente.
- `Project_Governance.md` → gobierno y evolución controlada.
- `Matriz_Autoridad_Documental.md` → precedencia y fuente oficial por dominio.
- Salvaguarda Vertical MVP → marco congelado, restricciones y no regresión.
- `EIOS-BL-002.md` → punto formal de recuperación asociado a un SHA concreto.
- `Framework_Map.md` → dónde buscar documentación y materialización.
- `Master_Project_Map.md` → cómo se organiza EIOS como sistema/proyecto.

Un Baseline no sustituye el estado posterior de `main`; para trabajo operativo debe verificarse siempre el repositorio vivo.

---

# 4. ALCANCE ACTUAL DEL VERTICAL MVP

El núcleo actual comprende, entre otras áreas:

- decisión de compras;
- evaluación financiera y operativa;
- evaluación factual de proveedores;
- reglas y evidencia;
- viabilidad;
- escenarios;
- Decision Twin;
- negociación;
- Negotiation Ladder;
- resolución de conflictos;
- recomendación explicable;
- trazabilidad y versionado.

La funcionalidad de ventas para comerciales permanece **EN STANDBY** y cualquier ampliación futura requiere su propio gobierno documental.

---

# 5. ORGANIZACIÓN DEL FRAMEWORK

La estructura física principal es:

```text
00_Gobierno/        Gobierno, autoridad, continuidad y Baselines
01_Modelo/          Metodología y modelo funcional especializado
02_Parametros/      Parámetros y parametrización
03_Arquitectura/    Arquitectura y mapas del sistema
03_App/             Especificación de aplicación e interfaz
04_Reglas/          Reglas, evidencia, dependencias y CRC
05_Motor/           Viabilidad, escenarios, Twin, negociación y versionado
06_SQL/             Persistencia y modelos SQL
07_Pruebas/         Auditorías, pruebas, cierres y reconciliaciones
08_Implementacion/  Contratos y gobierno de implementación técnica
99_Archivo/         Histórico / obsoleto

eios/               Código ejecutable
tests/              Verificación automatizada
.github/             CI y validaciones técnicas
```

La ubicación física no concede autoridad funcional. La autoridad se resuelve mediante la Matriz de Autoridad y las fuentes especializadas.

`03_App/` gobierna representación e interacción dentro del alcance autorizado; no crea reglas ni decisiones empresariales nuevas.

---

# 6. MODELO GENERAL DE DECISIÓN

El flujo conceptual de referencia es:

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
RESOLUCIÓN DE CONFLICTOS
  ↓
RECOMENDACIÓN
  ↓
DECISOR
```

La CRC vigente reconoce cinco resultados consolidados:

- 🟢 **COMPRAR**
- 🟡 **NEGOCIAR**
- 🔵 **COMPRAR CONDICIONADO**
- 🔴 **NO COMPRAR**
- ⚪ **INFORMACIÓN INSUFICIENTE**

La autoridad funcional de estos resultados corresponde a `04_Reglas/Capa_resolucion_conflictos.md` y a las fuentes especializadas relacionadas.

Ningún resultado constituye automáticamente una orden de compra.

---

# 7. CÁLCULOS, REFERENCIAS Y EVIDENCIA

El **Reference & Calculation Framework (RCF)** se conserva como marco conceptual transversal para describir cómo EIOS transforma datos y referencias en información utilizable para la decisión.

No debe interpretarse como un único componente monolítico pendiente de implementación.

La autoridad real de cálculo se distribuye entre dominios especializados, por ejemplo:

- Price Intelligence;
- TCO Core;
- Stock / STK;
- Delivery Stockout;
- Finance Basic;
- Viability Frontier;
- otras capacidades formalmente autorizadas.

Cada componente debe conservar trazabilidad, contexto, evidencia y límites de autoridad.

Conceptos históricos o ilustrativos como PMR, CEA, RFP u otras denominaciones antiguas **no adquieren vigencia por aparecer en versiones anteriores de este Manual**. Su validez debe demostrarse en la fuente especializada actual antes de utilizarse.

---

# 8. REGLAS, DEPENDENCIAS Y CRC

La definición oficial de reglas corresponde a:

`04_Reglas/Matriz_Reglas_MVP.md`

Las dependencias canónicas corresponden a:

`04_Reglas/Rule_Dependency_Matrix.md`

El contrato general de evidencia corresponde a:

`04_Reglas/Evidence_Contract.md`

La resolución de conflictos corresponde a:

`04_Reglas/Capa_resolucion_conflictos.md`

Principios que deben preservarse:

- no compensar automáticamente salvaguardas críticas mediante señales favorables;
- no transformar ausencia de evidencia en certeza;
- no crear reglas desde el código o desde la interfaz;
- no fabricar dependencias, parámetros o excepciones no autorizados;
- mantener explícita la insuficiencia de información cuando corresponda.

---

# 9. COMPONENTES CERRADOS / MATERIALIZADOS EN SU ALCANCE AUTORIZADO

El estado integrado contiene, entre otras, las siguientes capacidades o fronteras cerradas:

- C0 / motor de reglas en su alcance cerrado;
- Assessment y fronteras de provenance asociadas;
- Price Intelligence;
- TCO Core;
- Stock / STK ejecutable en su alcance autorizado;
- Delivery Stockout Analyzer;
- Finance Basic;
- Supplier Evidence Core como núcleo factual;
- Viability Frontier;
- Scenario Engine y coordinación de escenarios en sus fronteras cerradas;
- Decision Twin y comparación;
- Negotiation Intelligence;
- Negotiation Ladder;
- CRC-MVP;
- Decision Versioning;
- E2E Execution Boundary;
- UI / Visual Frontend U1.1 en su alcance representacional;
- reconciliaciones de provenance e integración asociadas.

“Cerrado” significa únicamente cerrado dentro del alcance expresamente autorizado por su contrato o fuente especializada. No autoriza ampliaciones semánticas por inferencia.

Para el estado exacto debe consultarse `00_Gobierno/Project_Context.md` y, después, la documentación especializada correspondiente.

---

# 10. FRENTES BLOQUEADOS O NO AUTORIZADOS

Los siguientes frentes no deben cerrarse por inferencia:

### Quality & Trust Gate

No está demostrado un productor físico de `Decision Input Package` agregado, trazable y autorizado que permita declarar cerrada una frontera provenance-safe end-to-end.

### Supplier Risk cuantitativo / valorativo

`Supplier Evidence Core` está cerrado como núcleo factual, pero scoring, ranking, pesos, umbrales y política decisional no disponen de autoridad aprobada.

### Rotation

El cierre metodológico factual existente no autoriza contrato técnico mientras continúen sin resolver las dependencias/autoridades expresamente identificadas por sus documentos especializados, incluyendo `ROT-G01` y `ROT-G04-A`.

### Assurance / Shadow Mode / piloto

No puede materializarse una comparación decisional real mientras no exista una fuente gobernada de decisión humana de referencia y el modelo autorizado para su comparación/override.

### Profitability / MGE

La propuesta `MGE-AUTH v0.1` continúa **NO AUTORIZADA**. Una instrucción genérica de “continuar”, “proseguir” o equivalente no constituye aprobación empresarial de esa política.

El trabajo sobre cualquiera de estos frentes debe fallar cerrado ante ausencia de autoridad material.

---

# 11. PARAMETRIZACIÓN Y CONFIGURATION CENTER

La definición de qué parámetros existen corresponde a:

`02_Parametros/Catalogo_Parametros_MVP_v0.3.md`

La configuración y gobierno de sus valores corresponde a:

`02_Parametros/Centro_Parametrizacion.md`

Las relaciones parámetro ↔ regla deben consultarse en las matrices oficiales correspondientes.

Existe materialización técnica del alcance autorizado de parametrización, pero la interfaz definitiva del Configuration Center continúa siendo una evolución separada.

La existencia de backend, SQL o UI no permite crear silenciosamente nuevos parámetros ni valores empresariales.

---

# 12. ESCENARIOS, DECISION TWIN Y NEGOCIACIÓN

EIOS puede analizar alternativas y consecuencias mediante los componentes especializados autorizados de escenarios, Decision Twin y negociación.

Estos componentes deben mantener separadas:

- evaluación técnica;
- representación de alternativas;
- recomendación de EIOS;
- decisión empresarial humana.

Negotiation Intelligence y Negotiation Ladder no transfieren autoridad decisional al sistema y deben respetar sus fronteras de provenance.

---

# 13. INTERFAZ Y EXPERIENCIA DEL DECISOR

La interfaz debe priorizar información útil para decidir sin saturar al usuario.

Principio de representación:

> **La interfaz muestra lo autorizado; no crea autoridad nueva.**

U1.1 Visual Frontend está cerrado en su alcance exclusivamente representacional.

Los contratos de UI, registro de campos, mapping e interacción se localizan en `03_App/`.

La interfaz no puede convertir un estado técnico, escenario o recomendación en una decisión humana implícita.

---

# 14. RUTA DE DATOS Y ERP

La ruta histórica de trabajo:

```text
ERP → Excel → Power BI → SQL Server
```

representa un origen/ruta inicial de datos, no la arquitectura conceptual oficial de EIOS.

EIOS no debe quedar limitado a SAGE ni a un proveedor concreto de ERP.

La integración automática con ERP permanece como evolución futura hasta que exista diseño y materialización autorizados.

---

# 15. ASSURANCE Y SALVAGUARDAS

Assurance actúa transversalmente sobre EIOS mediante controles de:

- integridad;
- trazabilidad;
- explicabilidad;
- coherencia;
- auditabilidad;
- no regresión;
- respeto de fronteras de autoridad.

No existe una fuente especializada única que autorice inventar una capa completa de Assurance más allá de los controles formalizados.

La Salvaguarda vigente del Vertical MVP es:

`00_Gobierno/EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md`

Las restricciones congeladas por la Salvaguarda no pueden modificarse silenciosamente.

---

# 16. MÉTODO OBLIGATORIO DE TRABAJO

Para cualquier unidad técnica o documental sometida a cierre operativo se aplica:

```text
DISEÑAR
   ↓
AUDITAR
   ↓
DEPURAR
   ↓
AUDITAR 2
   ↓
CERRAR
   ↓
MATERIALIZAR
   ↓
CI
```

Reglas de continuidad:

- verificar el `main` vivo antes de actuar;
- contrastar siempre la autoridad documental aplicable;
- no inventar alcance, datos, fórmulas, parámetros, umbrales o política empresarial;
- no reabrir componentes cerrados sin contradicción objetiva;
- no convertir resultados desacoplados en provenance demostrada;
- ante falta de autoridad material, bloquear / fail closed;
- preservar siempre la autoridad decisional humana;
- verificar CI en el HEAD exacto de la PR y tras la integración cuando corresponda.

---

# 17. CÓMO RECUPERAR EL PROYECTO EN UN NUEVO CHAT O ENTORNO

Secuencia mínima:

1. leer `Project_Charter.md`;
2. leer `Project_Context.md`;
3. leer `Project_Governance.md`;
4. leer `Matriz_Autoridad_Documental.md`;
5. leer la Salvaguarda Vertical MVP;
6. consultar `Framework_Map.md` y `Master_Project_Map.md`;
7. consultar `EIOS-BL-002.md` como punto formal de recuperación;
8. verificar el SHA actual de `main`;
9. identificar la unidad realmente abierta y su autoridad especializada;
10. continuar únicamente dentro del alcance autorizado.

No debe reconstruirse el estado del proyecto exclusivamente desde conversaciones anteriores.

---

# 18. REGLA DE NO DUPLICACIÓN Y ACTUALIZACIÓN

Si una materia dispone de una fuente especializada con autoridad, este Manual debe limitarse a:

- identificarla;
- resumir su función;
- señalar dónde encontrarla;
- conservar el contexto mínimo necesario.

El Manual debe actualizarse cuando cambie de forma relevante:

- el alcance;
- la estructura del proyecto;
- la arquitectura conceptual;
- el gobierno documental;
- los componentes principales;
- el estado general;
- las rutas de navegación.

No debe actualizarse por cada cambio menor de regla, parámetro, test o implementación especializada.

GitHub conserva el historial; las versiones antiguas del Manual no deben utilizarse como autoridad sobre el estado vigente.

---

# 19. ESTADO DE CONTINUIDAD

**Framework:** EIOS  
**Vertical:** Intelligent Procurement Decision & Negotiation  
**Baseline formal más reciente:** EIOS-BL-002  
**Estado general:** En desarrollo  
**Gobierno:** Activo  
**Salvaguarda Vertical MVP:** Vigente  
**Manual:** v2.1 — reconciliado 13/09/2026

El Vertical MVP completo **no está declarado cerrado**.

Los componentes cerrados y los bloqueos vigentes deben resolverse desde `Project_Context.md` y sus fuentes especializadas, no desde estados históricos de este Manual.

---

# 20. PRINCIPIO FINAL

> **El Manual Maestro no debe contener todo EIOS.**
>
> **Debe permitir encontrar, comprender y continuar EIOS sin perderse y sin crear autoridad nueva.**
