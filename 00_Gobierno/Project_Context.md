# EIOS — Project Context

> **Documento de recuperación y continuidad del proyecto**
>
> **Versión:** 3.0
> **Estado:** APROBADO — reconciliación de continuidad EIOS-BL-007
> **Última actualización:** 21/09/2026
> **Proyecto:** EIOS — Enterprise Intelligent Operations System

---

## 1. PROPÓSITO DE ESTE DOCUMENTO

Este archivo contiene el contexto esencial y estable de EIOS.

Su función principal es permitir recuperar rápidamente el contexto del proyecto si se pierde continuidad en una conversación, se inicia un nuevo chat o se incorpora una nueva IA al proyecto.

Este documento NO sustituye al resto de documentación del proyecto.

Debe utilizarse como mapa de navegación hacia los documentos específicos.

La autoridad sobre identidad, propósito, visión, alcance y límites corresponde al:

`00_Gobierno/Project_Charter.md`

La autoridad sobre precedencia documental corresponde a:

`00_Gobierno/Matriz_Autoridad_Documental.md`

El marco congelado del EIOS Vertical MVP está definido por:

`00_Gobierno/EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md`

El mapa estructural y de navegación vigente corresponde a:

`03_Arquitectura/Framework_Map.md`

El punto formal de recuperación más reciente es:

`00_Gobierno/Baselines/EIOS-BL-007.md` — `6de45ba0e069074d126cf98cf0a6723e64da61e7`

Un Baseline es un punto formal de recuperación asociado a un SHA concreto; no sustituye el estado posterior de `main` ni las fuentes especializadas vigentes.

---

# 2. IDENTIDAD DEL PROYECTO

EIOS — Enterprise Intelligent Operations System es un sistema inteligente de apoyo a la decisión empresarial basado en datos.

El proyecto se estructura mediante una arquitectura conceptual:

**CORE + VERTICAL**

El **EIOS Vertical MVP** se centra actualmente en:

**Intelligent Procurement Decision & Negotiation**

Su objetivo es ayudar al CEO y al Responsable de Compras a evaluar, simular, negociar y tomar mejores decisiones de adquisición mediante el análisis conjunto de información financiera, operativa, comercial e histórica.

EIOS no sustituye al ERP ni los procesos contables.

EIOS tampoco sustituye al decisor.

EIOS:

- analiza;
- evalúa;
- simula;
- explica;
- recomienda.

La decisión empresarial final corresponde al usuario autorizado.

---

# 3. OBJETIVO PRINCIPAL

EIOS debe ayudar a determinar si una compra propuesta:

- debe realizarse;
- debe negociarse;
- puede realizarse condicionadamente;
- no debe realizarse;
- o debe declararse como información insuficiente cuando no exista base fiable para recomendar.

La decisión debe considerar tanto la operación individual como su impacto sobre la situación económica, financiera y operativa de la empresa.

Cuando una operación inicialmente desfavorable pueda convertirse en viable mediante modificación de sus condiciones, negociación o aplicación de una alternativa, EIOS debe poder identificar y explicar dichas posibilidades.

---

# 4. ALCANCE ACTUAL

## Prioridad actual

### EIOS VERTICAL — DECISIÓN DE COMPRAS Y NEGOCIACIÓN

Es el núcleo actual del proyecto.

La funcionalidad relacionada con ventas para comerciales queda actualmente:

**EN STANDBY**

Podrá incorporarse posteriormente como otro Vertical o como ampliación futura.

El alcance actual comprende:

- decisión de compras;
- evaluación financiera;
- evaluación operativa;
- evaluación de proveedores;
- reglas;
- evidencia;
- viabilidad;
- escenarios;
- Decision Twin;
- negociación;
- Negotiation Ladder;
- resolución de conflictos;
- recomendación explicable;
- trazabilidad de decisiones.

---

# 5. PRINCIPIOS FUNDAMENTALES

EIOS debe ser:

- intuitivo;
- rápido;
- fiable;
- escalable;
- visualmente atractivo;
- comprensible para usuarios no financieros;
- configurable;
- adaptable a diferentes empresas;
- parametrizable sin necesidad de modificar el código;
- orientado a la toma de decisiones;
- explicable;
- trazable;
- gobernado.

### Principio de simplicidad

EIOS no debe saturar al CEO con información.

Debe mostrar primero la información necesaria para tomar una decisión y permitir profundizar cuando sea necesario.

---

# 6. LÍMITES DEL SISTEMA

EIOS:

- NO sustituye al ERP.
- NO genera facturas.
- NO sustituye la contabilidad.
- NO sustituye la decisión empresarial.
- NO debe ejecutar unilateralmente una compra como consecuencia de una recomendación.
- NO debe presentar información como actual si los datos superan el límite de antigüedad establecido por la configuración.
- NO debe ocultar incertidumbres o referencias de baja calidad.
- NO debe convertir automáticamente una hipótesis debatida en una regla definitiva.
- NO debe presentar como certeza aquello que sea una estimación o escenario.

---

# 7. ORIGEN Y RUTA DE LOS DATOS

La ruta:

`ERP → Excel → Power BI → SQL Server`

corresponde a una **ruta inicial de trabajo y origen de datos**, no a la arquitectura conceptual oficial de EIOS.

Actualmente se trabaja habitualmente con SAGE, pero EIOS NO debe quedar limitado exclusivamente a SAGE.

La conexión automática con ERP queda contemplada como evolución futura.

Las decisiones sobre arquitectura técnica corresponden a la documentación de Arquitectura y no a este Project Context.

---

# 8. MODELO GENERAL DE DECISIÓN

La lógica conceptual actual es:

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

Los cinco resultados oficiales consolidados por la CRC son:

- 🟢 COMPRAR
- 🟡 NEGOCIAR
- 🔵 COMPRAR CONDICIONADO
- 🔴 NO COMPRAR
- ⚪ INFORMACIÓN INSUFICIENTE

La recomendación de EIOS no constituye automáticamente una orden de compra.

---

# 9. VARIABLES PRINCIPALES DE LA DECISIÓN DE COMPRA

Entre las variables consideradas están:

## Compra

- artículo;
- proveedor;
- cantidad;
- precio;
- importe;
- fecha de propuesta;
- fecha prevista de entrega;
- plazo de pago;
- condiciones de pago;
- descuentos;
- rappels;
- incidencias.

## Histórico

- últimas compras;
- fechas de compra;
- precios;
- cantidades;
- proveedor;
- condiciones;
- operaciones comparables.

## Stock

- stock actual;
- stock comprometido;
- stock en tránsito;
- pedidos pendientes;
- rotación;
- demanda;
- cobertura;
- stock proyectado.

## Rentabilidad

- precio de venta;
- margen;
- margen porcentual;
- margen mínimo objetivo.

La presencia de estas variables en el contexto no autoriza por sí sola fórmulas, denominadores, transformaciones ni umbrales. La semántica cuantitativa debe provenir de su autoridad especializada.

## Finanzas

- tesorería;
- fondo de maniobra;
- liquidez;
- pagos previstos;
- impacto financiero de la compra.

## Proveedores

- proveedor actual;
- proveedores alternativos;
- histórico;
- precios;
- condiciones;
- incidencias.

---

# 10. SIMULACIÓN TEMPORAL

La fecha de propuesta de compra es un elemento fundamental.

EIOS no debe limitarse a analizar el estado actual.

Debe poder proyectar la evolución futura teniendo en cuenta, cuando existan datos suficientes:

- stock actual;
- ventas históricas;
- demanda prevista;
- pedidos pendientes;
- compras en tránsito;
- fecha prevista de entrega;
- plazo de entrega;
- cantidad comprada.

Conceptualmente:

```text
Stock proyectado =
Stock actual
+ entradas previstas
- salidas previstas
```

Una aplicación importante es detectar posibles roturas de stock antes de que ocurran.

---

# 11. REFERENCE & CALCULATION FRAMEWORK

El **Reference & Calculation Framework (RCF)** se conserva como marco conceptual transversal para explicar cómo EIOS transforma datos en información utilizable para la decisión.

No debe interpretarse como un único componente monolítico pendiente de implementación.

Su función se materializa mediante autoridades y componentes especializados que definen, según el dominio:

- periodo de referencia;
- fecha;
- antigüedad;
- operaciones comparables;
- método de cálculo;
- ponderación;
- límites;
- excepciones;
- calidad o fiabilidad de la referencia.

Price Intelligence, TCO, Stock/STK, Delivery Stockout, Finance Basic y las demás capacidades especializadas conservan su propia autoridad; este Project Context no redefine sus cálculos.

No debe utilizarse automáticamente un precio medio histórico de muchos años si puede resultar poco representativo por inflación, evolución del mercado u otros factores.

---

# 12. REFERENCIAS TEMPORALES

Los criterios deberán poder utilizar ventanas temporales configurables cuando la autoridad especializada lo contemple.

Ejemplos:

- últimos 3 meses;
- últimos 6 meses;
- últimos 12 meses;
- últimos 24 meses.

La antigüedad de una referencia debe tenerse en cuenta.

Ejemplo:

Una última compra realizada hace 20 días puede ser una referencia relevante.

Una última compra realizada hace 4 años puede no serlo.

---

# 13. INFORMACIÓN EXPLICABLE

EIOS no debe mostrar únicamente:

> "Precio superior al histórico."

Debe explicar la referencia utilizada.

Ejemplo conceptual:

```text
Precio ofertado: 18,50 €

+7,6 % respecto a la última compra:
17,20 € — realizada hace 25 días.

+3,4 % respecto al precio medio ponderado:
últimos 3 meses.

+6,6 % respecto al precio medio ponderado:
últimos 12 meses.
```

La información detallada debe estar disponible sin saturar la pantalla principal.

Los ejemplos de este documento son ilustrativos y no sustituyen las metodologías vigentes de Price Intelligence ni las autoridades especializadas.

---

# 14. FIABILIDAD DE LAS REFERENCIAS

Cuando sea relevante, EIOS deberá poder valorar la calidad de la referencia.

Ejemplo:

🟢 Alta  
Existen varias operaciones recientes y comparables.

🟠 Media  
Existen pocas operaciones o presentan diferencias relevantes.

🔴 Baja  
Los datos son escasos, antiguos o poco comparables.

EIOS debe evitar transmitir una falsa sensación de precisión.

La suficiencia y calidad de la evidencia deberán alinearse con el `Evidence_Contract.md` y con las fuentes especializadas aplicables.

---

# 15. MOTOR DE REGLAS

EIOS dispone de un alcance materializado del motor de reglas y de sus fronteras de ejecución/provenance.

Las reglas deben poder adaptarse, dentro de la autoridad y parametrización aprobadas, a:

- empresa;
- momento;
- política empresarial;
- condiciones económicas;
- criterios de riesgo;
- estrategia de compras.

No deben quedar rígidamente codificadas ni redefinidas fuera de sus fuentes oficiales.

La definición oficial de las reglas corresponde a:

`04_Reglas/Matriz_Reglas_MVP.md`

Las dependencias canónicas corresponden a:

`04_Reglas/Rule_Dependency_Matrix.md`

La existencia de código no autoriza por sí sola nuevas reglas, parámetros o política empresarial.

---

# 16. TIPOS DE REGLAS

Se han identificado inicialmente tres categorías conceptuales:

### Reglas de bloqueo

Pueden impedir una recomendación de compra.

Ejemplo:

Liquidez insuficiente para atender pagos.

### Reglas de recomendación

Modifican o condicionan la decisión.

Ejemplo:

Precio superior al objetivo → recomendar negociación.

### Reglas de excepción

Pueden modificar el efecto de otra regla cuando las condiciones definidas lo permitan.

Ejemplo:

Stock elevado + pedido de cliente confirmado → reducir riesgo de sobrestock.

La clasificación definitiva y el comportamiento de cada regla corresponden a la documentación oficial de reglas y no a estos ejemplos conceptuales.

---

# 17. PRIORIDAD Y CONFLICTO ENTRE REGLAS

La prioridad y resolución de conflictos entre reglas está formalizada en el alcance autorizado de la **CRC-MVP**.

No debe utilizarse una simple suma de reglas verdes y rojas.

Una regla financiera crítica, por ejemplo, no debe quedar anulada simplemente porque existan varias condiciones favorables.

La resolución formal contempla, conforme a su autoridad especializada:

- prioridad;
- severidad;
- bloqueos;
- excepciones;
- dependencias;
- condiciones;
- conflictos;
- resultado consolidado.

La autoridad funcional de resolución de conflictos corresponde a:

`04_Reglas/Capa_resolucion_conflictos.md`

La materialización técnica del alcance CRC-MVP se encuentra en `08_Implementacion/` y `eios/core/crc_mvp.py`.

Cualquier ampliación de la CRC requiere autoridad y ciclo documental propios; el cierre actual no autoriza semántica nueva por inferencia.

---

# 18. COMPRA CONDICIONADA

Entre los cinco resultados oficiales se incluye:

### COMPRAR CONDICIONADO

Ejemplos:

- comprar si se consigue un plazo de pago de 90 días;
- comprar si se reduce el precio;
- comprar si se reduce la cantidad;
- comprar si existe un pedido confirmado;
- comprar si se consigue determinada condición comercial.

EIOS no debe limitarse a diagnosticar un problema.

Cuando sea posible y exista autoridad suficiente, debe ayudar a identificar condiciones que hagan viable la operación.

La condición debe quedar explícita y ser trazable.

---

# 19. PLAN DE ACCIÓN FINANCIERO

Cuando una compra comprometa la situación financiera, EIOS puede mostrar alternativas que permitan estudiar la viabilidad.

Ejemplos considerados:

- ampliación de capital;
- venta de inmovilizado no utilizado;
- promoción de productos de baja rotación;
- reducción del periodo de cobro de clientes;
- negociación de plazos con proveedores;
- reducción de la cantidad comprada.

Estas alternativas no deben ejecutarse automáticamente.

EIOS debe presentarlas como posibles vías de actuación para valoración humana.

---

# 20. CONFIGURATION CENTER

El **EIOS Configuration Center** es un componente transversal del sistema.

La parametrización dispone de fuentes oficiales y materialización técnica para su alcance autorizado. El Configuration Center dispone además de contrato UI cerrado y de un subconjunto ejecutable **selected-context** materializado y validado mediante Slices 1–4 y conformidad E2E. Este estado no equivale a una interfaz completa ni autoriza por inferencia autenticación/resolución de identidad, enumeración de empresas autorizadas o descubrimiento global de parámetros sin productor físico autorizado.

Debe permitir gobernar, dentro del alcance autorizado, elementos como:

- valores de referencia;
- periodos;
- fechas;
- límites;
- tolerancias;
- criterios;
- reglas;
- prioridades;
- excepciones;
- políticas de empresa.

Debe partir de valores estándar editables. La existencia y los valores concretos de esos estándares corresponden a las fuentes de parametrización; este documento no los crea.

La definición de qué parámetros existen corresponde al:

`02_Parametros/Catalogo_Parametros_MVP_v0.3.md`

La configuración y gobierno de sus valores corresponde al:

`02_Parametros/Centro_Parametrizacion.md`

Las relaciones parámetro ↔ regla y las dependencias transversales deben consultarse en sus matrices oficiales.

---

# 21. EXPLICACIÓN DE LOS PARÁMETROS

Cada parámetro configurable debería incluir una explicación breve y comprensible.

Ejemplo:

**Antigüedad máxima de referencia: 12 meses**

ⓘ Determina hasta qué antigüedad EIOS considera válida una compra histórica para comparar el precio actual. Reducir este valor prioriza referencias más recientes, pero puede reducir el número de operaciones comparables.

El usuario debe comprender qué efecto produce modificar un parámetro.

Los ejemplos no crean parámetros ni valores autorizados; la autoridad corresponde al Catálogo y al Centro de Parametrización.

---

# 22. CONFIGURACIÓN POR EMPRESA

La configuración debe poder adaptarse a diferentes empresas.

El motor puede ser común, mientras que cada empresa puede tener:

- diferentes límites;
- diferentes políticas;
- diferentes márgenes;
- diferentes criterios de stock;
- diferentes criterios financieros;
- diferentes prioridades;
- diferentes reglas.

Toda diferencia empresarial debe respetar el gobierno de parámetros, reglas y autoridad documental vigente.

---

# 23. VERSIONADO DE CONFIGURACIÓN

Los cambios importantes deben conservar historial.

Ejemplo:

```text
Margen mínimo:

01/01/2026 → 20 %

01/07/2026 → 22 %

01/01/2027 → 25 %
```

EIOS debe poder conocer qué configuración estaba vigente cuando se produjo una determinada decisión.

La trazabilidad temporal de las decisiones deberá alinearse con:

`05_Motor/Decision_Versioning.md`

Los valores del ejemplo son ilustrativos y no constituyen configuración vigente.

---

# 24. SIMULACIÓN DE CAMBIOS

Se considera interesante que el Configuration Center pueda permitir:

**Simular una modificación antes de aplicarla.**

Ejemplo:

```text
Margen mínimo actual: 20 %

Nuevo margen mínimo: 25 %

Resultado simulado:

14 operaciones históricas que anteriormente eran aceptables
pasarían a clasificarse como negociar.
```

Esta funcionalidad queda como propuesta de evolución hasta su formalización.

---

# 25. PRINCIPIO DE TRAZABILIDAD

Las decisiones importantes deben poder explicar:

- qué datos se utilizaron;
- qué evidencias se utilizaron;
- qué referencias se utilizaron;
- qué parámetros estaban vigentes;
- qué reglas se activaron;
- qué excepciones se aplicaron;
- qué escenarios se evaluaron;
- qué resultado produjo el motor;
- qué recomendación se generó.

El objetivo es que EIOS pueda explicar:

> "He llegado a esta recomendación por estas razones."

La trazabilidad no convierte una recomendación de EIOS en una decisión humana ni autoriza reconstrucciones de provenance no demostradas.

---

# 26. ASSURANCE Y SALVAGUARDAS

Assurance actúa transversalmente sobre EIOS.

Las decisiones deberán respetar:

- evidencia suficiente;
- trazabilidad;
- explicabilidad;
- integridad;
- coherencia;
- auditabilidad;
- control de regresiones.

Assurance permanece como principio transversal. No existe actualmente un documento independiente único que autorice por sí solo toda la capa de Assurance; la autoridad aplicable se determina mediante la Salvaguarda, la Matriz de Autoridad Documental y la fuente especializada vigente de cada control.

El marco congelado del EIOS Vertical MVP corresponde a:

`00_Gobierno/EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md`

Ningún componente especializado puede contradecir una restricción expresamente congelada por la Salvaguarda.

**Shadow Mode / piloto no está autorizado para materialización decisional completa** mientras no exista una fuente gobernada de decisión humana de referencia y su correspondiente modelo de comparación/override.

---

# 27. ESTADO ACTUAL DEL PROYECTO

## Estado de continuidad reconciliado — 20/09/2026

Este apartado resume el estado para recuperación rápida. No sustituye a los documentos especializados de diseño, auditoría, cierre, implementación y reconciliación.

### 🔒 Cerrado / materializado en su alcance autorizado

El estado integrado y documentado contiene, entre otras, las siguientes capacidades o fronteras cerradas:

- C0 / motor de reglas en su alcance cerrado y sus fronteras de provenance;
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
- `DIP-AGG-01` como Decision Input Package seleccionado, inmutable y trazable por contenido;
- `PROJECTION_ONLY` Quality material: criterios v0.2, material envelope, productor y consumidor QTG especializados;
- adapter semántico sintético `PROJECTION_ONLY` S1–S7 y fixture física de 13 componentes;
- conformidad E2E `SYNTHETIC_TEST → TEST_ONLY`, incluyendo resultados sintéticos `NO_APTO/BAJA` y `APTO/ALTA` sin efecto operacional;
- E2E Execution Boundary;
- UI / Visual Frontend U1.1 en su alcance exclusivamente representacional;
- U1.2 Vertical MVP Visual Read-Only Composition + conformidad E2E, sin ejecución de motores;
- U1.3 Read-Only Visual Artifact con bytes HTML reproducibles y `content_sha256` de transporte, sin I/O;
- U1.4 Controlled Visual Delivery Boundary, puro y sin I/O;
- U1.5A Synthetic Visual Admission con fixture registrada y binding atómico;
- U1.5C Designated Synthetic Preview Artifact con designación persistente `SYNTHETIC / TEST_ONLY / NO OPERATIONAL EFFECT`;
- U1.5B Local Loopback Preview Adapter sobre `127.0.0.1`, puerto efímero y GET/HEAD;
- Configuration Center UI: contrato cerrado y Slices 1–4 + conformidad selected-context E2E en el alcance ejecutable demostrado;
- migración documental de identificadores `P-*` / `R-*` y reconciliaciones postintegración asociadas.

“Cerrado” significa cerrado únicamente en el alcance expresamente autorizado por su fuente especializada. No autoriza ampliar semántica, reglas, scoring, política empresarial ni ejecución automática.

### ⛔ Bloqueado por autoridad, evidencia o dependencia no demostrada

- **Quality & Trust Gate — ruta operacional:** la cadena especializada `PROJECTION_ONLY / SYNTHETIC_TEST → TEST_ONLY` está materializada y validada E2E. Permanece bloqueada la rama `OPERATIONAL → O1` hasta disponer de un expediente operacional concreto, autorizado y trazable; el contrato de admisión y el diseño de binding causal no sustituyen ese expediente ni habilitan QTG en el Vertical genérico.
- **Scenario Stage 2 ↔ Viability Frontier:** la finalización pública permanece en cuarentena mientras no exista un productor VF provenance-safe de consecuencias H/K/U/S procedentes de una autoridad físicamente identificada. El core VF permanece cerrado.
- **Decision Twin — wrapper dependiente de Stage 2:** continúa en cuarentena por esa dependencia; Decision Twin core/comparator no se consideran bloqueados por ello.
- **Negotiation Intelligence / Negotiation Ladder provenance:** los contratos de resultado están cerrados y el Vertical usa invocadores explícitos, pero la mera presencia del invocador no prueba provenance y no existe productor determinista NI/Ladder autorizado desde la compra completa.
- **Supplier Risk cuantitativo/valorativo:** `Supplier Evidence Core` está cerrado como núcleo factual; scoring, ranking, pesos, umbrales y política decisional continúan sin autoridad aprobada.
- **Rotation:** Track A conserva su cierre metodológico factual, pero el contrato técnico sigue bloqueado mientras falten `ROT-G01` y `ROT-G04-A`; cualquier Track B mantiene además sus propias dependencias de fórmula/umbral y reglas.
- **Payment / PAG:** `R-PAG-001` y `R-PAG-002` disponen de relaciones parámetro → regla documentadas. Supplier Evidence Core ya preserva hechos `PAYMENT_TERM` del proveedor actual y la cadena documental de pagos/cuotas conserva vencimientos y asociaciones, por lo que el carrier factual genérico ya no está totalmente ausente. El cierre ejecutable sigue bloqueado porque no existe un binding EVIDENCE/DATA canónico que transforme ese material en el escalar autorizado “plazo ofrecido” para Rules, no está definida la normalización de estructuras multicuota, sigue sin resolverse la transformación exacta de `P-PAG-003`, `P-PAG-005` mantiene contradicción entre control booleano y factor económico, y `R-PAG-002` carece de productor autorizado de viabilidad contrafactual.
- **Historical / HIS:** `R-HIS-001` y `R-HIS-002` están materializadas en su alcance autorizado. `R-HIS-001` consume `HistoricalReferenceTemporalObservation + Evidence` vinculadas a la `PurchaseOperation` exacta y `ResolvedConfiguration(P-DAT-002) + Evidence`, con meses calendario, clipping y fail-closed. `R-HIS-003` permanece bloqueada porque no dispone de una cadena completa autorizada para determinar comparabilidad comercial material.
- **Data Quality / DAT:** `R-DAT-001` y `R-DAT-002` están materializadas sobre una única cadena factual de frescura. `R-DAT-003` también está materializada en su alcance autorizado mediante `DecisionEvidenceRequirementSet → RequirementEvidenceBinding → DecisionEvidenceSufficiencyObservation + Evidence → evaluate_r_dat_003`. DAT003 no consume `P-DAT-003` ni `P-DAT-007`, no reutiliza QTG y distingue `FAILED` de `UNDETERMINED` (`GAP → UNDETERMINED`). `R-DAT-003 TRUE` conserva su resultado explícito `INFORMACIÓN INSUFICIENTE`. La precedencia CRC DAT003↔R0 está cerrada: solo `R-DAT-003 EVALUABLE/TRUE` domina como `INFORMACIÓN INSUFICIENTE` frente a un R0 concurrente `NO COMPRAR`; el otro R0 se preserva como factor/conflicto trazable. DAT003 `FALSE` o `NOT_EVALUABLE` no activa esta precedencia.
- **Supplier Alternatives / PROV:** `R-PROV-001` y `R-PROV-002` existen en la Matriz de Reglas, pero la RDM no contiene dependencias `R-PROV-*` confirmadas y no existe un productor autorizado que transforme hechos de proveedor en alternativa, comparabilidad o mejora potencial/significativa; `Supplier Evidence Core` conserva únicamente autoridad factual.
- **Discounts & Rappels / COM:** `R-COM-001` y `R-COM-002` existen en la Matriz de Reglas, pero la RDM no contiene dependencias `R-COM-*` confirmadas ni el Catálogo define parámetros `P-COM-*`; la presencia conceptual de descuentos/rappels o de hechos `COMMERCIAL_CONDITION` no autoriza por sí sola su transformación en semántica de regla o coste efectivo.
- **Assurance / Shadow Mode / piloto:** bloqueado para comparación decisional real mientras no exista una fuente autorizada de decisión humana de referencia y su gobierno.
- **Profitability / MGE:** `MGE-AUTH v0.1`, `Profitability Core v0.1`, `ProvenancedProfitabilityExecution` y `R-MGE-001/002/003` están materializados y validados. `MGE-RULES-AUTH v0.1` fija: `R-MGE-001: m < minimum`; `R-MGE-002: m >= minimum AND m >= target - tolerance AND m < target`; `R-MGE-003: m >= target`. Las tres reglas consumen un único bundle coherente de `P-MGE-001/002/003` mediante `ResolvedConfiguration + Evidence`, sin hardcodear 20/30/3; `minimum > target`, `tolerance < 0`, parámetros ausentes o Profitability no determinada producen `NOT_EVALUABLE`, no `FALSE`. Metadata cerrada: R1/ALTA, R2/MEDIA y R3/INFORMATIVA; no existe escalada R0. Integración física: PR #244, CI #1007 — 1686 tests passed + SQL SUCCESS. P-MGE-004/005/006 continúan fuera de consumo.

### 🟡 En evolución del sistema, sin declarar cerrado el Vertical MVP completo

- integración automática con ERP;
- ampliación del Configuration Center más allá del selected-context demostrado, especialmente identidad/autenticación, enumeración de empresas y descubrimiento global de parámetros;
- evolución del modelo de datos empresarial más allá de los modelos físicos ya materializados;
- ampliaciones de dominios y capacidades que requieran nueva autoridad;
- cierre integral del Vertical MVP una vez resueltos sus frentes bloqueados y gates pendientes.

### Gate operativo post-BL-007

La auditoría `Post_BL_007_Frontier_Readiness_Audit_v0.1.md` determina que no existe actualmente una nueva implementación funcional positiva que pueda abrirse sin cerrar previamente al menos un gate de autoridad/evidencia.

El contrato `00_Gobierno/Post_BL_007_Gate_Intake_Contract_v0.1.md` define los requisitos mínimos de intake para HIS-001, DAT-001, PAG-001, QTG operacional, MGE y Stage 2/VF.

Regla de continuidad:

```text
BLOCKED
  ↓
intake verificable
  ↓
autoridad + productor + identity/provenance + fail-closed
  ↓
READY_FOR_DESIGN
```

Una instrucción genérica de continuar no sustituye el intake específico cuando el propio gate exige autorización o evidencia material.

### Readiness funcional post-MGE

La auditoría `07_Pruebas/Post_MGE_Next_Frontier_Readiness_Audit_v0.1.md` identificó inicialmente FIN002/STK002/PRE como los frentes técnicos más próximos.

Tras autorización humana explícita de `FIN002 Post-Operation Working Capital Authority v0.1`, `R-FIN-002` quedó materializada e integrada mediante PR #249:

```text
main @ b77b16d5af5d9c1035a01ecb827ebcb4c47d9551
CI #1017 → 1723 passed / 8 warnings / SQL SUCCESS
```

Estado actualizado:

```text
R-FIN-002 → CLOSED / MATERIALIZED / CI VALIDATED

R-STK-002 → CLOSED / MATERIALIZED / CI VALIDATED

R-PRE-003 → CLOSED / MATERIALIZED / CI VALIDATED

R-PRE-001 → CLOSED / MATERIALIZED / CI VALIDATED

R-PRE-002 → CLOSED / MATERIALIZED / CI VALIDATED

R-HIS-001 → CLOSED / MATERIALIZED / CI VALIDATED

R-DAT-001 → CLOSED / MATERIALIZED / CI VALIDATED
R-DAT-002 → CLOSED / MATERIALIZED / CI VALIDATED
R-DAT-003 → CLOSED / MATERIALIZED / CI VALIDATED (scope v0.1)
```

FIN002 usa un carrier post-operación separado de Finance Basic, vinculado a la `PurchaseOperation` exacta y a `P-FIN-003` mediante `ResolvedConfiguration + Evidence`.

STK002 quedó cerrado mediante `ProjectedCoverageAfterPurchase` + `JustifiedNeedState`, ambos vinculados a la `PurchaseOperation` exacta, más `ResolvedConfiguration(P-STK-004) + Evidence`. PR #252: `main @ be13aad7d1dde788ef6e79cf262c1a7e91ed7374`; CI #1023: 1767 passed / 8 warnings / SQL SUCCESS.

PRE003 quedó cerrado mediante `RecommendedPriceCeiling + RecommendedPriceCeilingEvidence`, ligado a la `PurchaseOperation` exacta y físicamente separado de Price Intelligence. PR #255: `main @ a16a6343a43dd72a5676f351ecb28bcfa1b94250`; CI #1029: 1789 passed / 8 warnings / SQL SUCCESS.

PRE001 quedó cerrado mediante `ComparablePriceReference + ComparablePriceReferenceEvidence`, ligado a la `PurchaseOperation` exacta, más `ResolvedConfiguration(P-PRE-001) + Evidence` y `ResolvedConfiguration(P-PRE-004) + Evidence`. La regla utiliza una referencia individual ya seleccionada upstream, meses calendario con clipping y uplift porcentual sin defaults. PR #258: `main @ 433007bf59d1a1fdb94df9dbfcd262e14878df85`; CI #1037: 1829 passed / 8 warnings / SQL SUCCESS.

PRE002 quedó cerrado mediante `CriticalPriceBaseline + CriticalPriceBaselineEvidence`, ligado a la `PurchaseOperation` exacta, más `ResolvedConfiguration(P-PRE-005) + Evidence`. La regla calcula el límite crítico sin default y aplica frontera estricta `purchase.unit_price > critical_limit`. PR #262: `main @ 3621424a45ee1c01ecb9327a5fa187f3bd07504f`; CI #1044: 1865 passed / 8 warnings / SQL SUCCESS.

El frente PRE (R-PRE-001/002/003) queda cerrado física y documentalmente.

HIS001 quedó cerrado mediante `HistoricalReferenceTemporalObservation + HistoricalReferenceTemporalEvidence`, ligado a la `PurchaseOperation` exacta, más `ResolvedConfiguration(P-DAT-002) + Evidence`. La regla usa `PurchaseOperation.operation_date` como fecha base, meses calendario con clipping y frontera estricta `reference_operation_date < cutoff_date`; igualdad con el corte → `FALSE`, fecha futura/ausente/contradictoria → `NOT_EVALUABLE`. PR #265: `main @ 56c5d58478bef64922629e1f584ce7d02dc4cd1f`; CI #1052: Python tests + SQL SUCCESS.

DAT001 quedó cerrado mediante un productor factual separado del evaluador normativo. `DataSnapshotFreshnessProducer` conserva metadata temporal explícita del snapshot y no deriva fechas desde IDs, Evidence, DIP ni reloj del sistema. `R-DAT-001` consume `P-DAT-001` sin hardcodear 6 semanas; cutoff inclusivo, semana = 7 días; fecha futura/ausente/contradictoria → `NOT_EVALUABLE`. PR #268: `main @ ff0d648a0594c3d495d5d348e6eaabdbe6d615ff`; CI #1059: Python tests + SQL SUCCESS.

DAT002 quedó cerrado reutilizando exactamente el mismo carrier/Evidence y la misma resolución de `P-DAT-001`; `updated < cutoff → TRUE`, igualdad → `FALSE`, futuro/ausencia/contradicción → `NOT_EVALUABLE`. No existe inferencia cruzada cuando alguna regla no es evaluable. PR #271: `main @ 24e246161106512d1bb1b69475145ad6c687ae66`; CI #1066 SUCCESS.

No debe reinterpretarse `FinanceBasicResult.working_capital` como valor post-operación, `CoverageResult` como cobertura proyectada post-compra, `R-STK-004 FALSE` como ausencia de necesidad justificada, ni `PriceIntelligenceResult.pr_value` como precio máximo recomendado o como referencia individual de R-PRE-001. PRE003 preserva explícitamente `PR ≠ PMR`; PRE001 no selecciona referencias automáticamente.

### Regla de interpretación

No debe inferirse que una capacidad está abierta solo porque un documento histórico diga “pendiente”, ni que está cerrada solo porque exista código.

Para resolver el estado real:

```text
Matriz de Autoridad Documental
        ↓
fuente especializada vigente
        ↓
auditoría / cierre
        ↓
implementación
        ↓
reconciliación / CI
```

El Baseline `EIOS-BL-007 @ 6de45ba0e069074d126cf98cf0a6723e64da61e7` es el punto formal de recuperación más reciente, pero el repositorio puede haber avanzado después de su SHA. Para trabajo operativo debe verificarse siempre el `main` vivo antes de actuar.

---

# 28. AUTORIDAD Y NAVEGACIÓN DOCUMENTAL

Este documento es la fuente oficial de contexto y continuidad conforme a `00_Gobierno/Matriz_Autoridad_Documental.md`.

No redefine conceptos cuya autoridad corresponda a documentos especializados.

Cuando exista una discrepancia documental, debe consultarse:

```text
Matriz_Autoridad_Documental.md
          ↓
determina la fuente oficial
          ↓
documento especializado
          ↓
implementación / pruebas / CI
```

Documentos fundamentales de referencia:

```text
00_Gobierno/
├── Project_Charter.md
├── Project_Context.md
├── Project_Governance.md
├── Matriz_Autoridad_Documental.md
├── EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md
└── Baselines/EIOS-BL-007.md

03_Arquitectura/
└── Framework_Map.md
```

`Framework_Map.md` indica dónde buscar; la Matriz de Autoridad determina qué fuente manda; los documentos especializados definen el contenido.

Las copias o subárboles auxiliares no adquieren autoridad por similitud de nombre.

---

# 29. REGLA DE TRABAJO DEL PROYECTO

El trabajo conceptual continúa siguiendo el principio de definir, cuestionar, contrastar, mejorar, simplificar, validar, documentar e implementar.

Para cualquier unidad técnica o documental sometida a cierre operativo se aplica el ciclo obligatorio:

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

- verificar el estado físico del repositorio antes de actuar;
- no inventar alcance, autoridad, fórmulas, parámetros, umbrales o datos;
- no reabrir componentes cerrados sin contradicción objetiva;
- no convertir resultados opacos o desacoplados en provenance demostrada;
- si falta autoridad material, bloquear/fail closed en lugar de fabricar una decisión;
- preservar la autoridad decisional humana;
- verificar CI y reconciliación postintegración sobre los SHAs exactos cuando corresponda.

No se debe programar una pieza importante antes de haber definido suficientemente su lógica de negocio y su autoridad.

Las decisiones congeladas por la Salvaguarda no deben modificarse silenciosamente.

---

# 30. PRINCIPIO FUNDAMENTAL

> EIOS no debe limitarse a decir qué está ocurriendo.
>
> Debe ayudar a comprender por qué ocurre, qué riesgo implica y qué alternativas existen para tomar una mejor decisión.

Y debe hacerlo manteniendo siempre una premisa fundamental:

> **EIOS analiza, evalúa, simula, explica y recomienda. El decisor decide.**