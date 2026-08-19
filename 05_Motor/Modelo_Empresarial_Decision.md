# MODELO EMPRESARIAL DE DECISIÓN

## EIOS — Enterprise Intelligent Operations System

**Versión:** 2.0  
**Estado:** APROBADO — Baseline EIOS Vertical MVP  
**Baseline:** EIOS Vertical MVP  
**Última actualización:** 19/08/2026

---

# 1. PROPÓSITO

El Modelo Empresarial de Decisión (MED) define cómo EIOS analiza una propuesta de compra, combina información histórica, operativa y financiera, aplica los criterios y reglas establecidos por la empresa y genera una recomendación comprensible para el usuario.

El MED constituye el núcleo lógico empresarial de decisión de EIOS.

No ejecuta automáticamente la compra.

Su función es proporcionar información, análisis, riesgos, alternativas y una recomendación que facilite la decisión humana.

---

# 2. OBJETIVO

Determinar si una compra propuesta:

- debe realizarse;
- debe negociarse;
- puede realizarse condicionadamente;
- no debe realizarse;
- o no puede evaluarse con fiabilidad suficiente.

Los resultados oficiales son:

1. **COMPRAR**
2. **NEGOCIAR**
3. **COMPRAR CONDICIONADO**
4. **NO COMPRAR**
5. **INFORMACIÓN INSUFICIENTE**

La decisión debe considerar tanto la operación concreta como su impacto sobre la situación económica, financiera y operativa de la empresa.

---

# 3. PRINCIPIO FUNDAMENTAL

EIOS no debe limitarse a responder:

> ¿Podemos comprar?

Debe intentar responder:

> ¿Tiene sentido realizar esta compra en estas condiciones y qué deberíamos negociar para mejorarla o hacerla viable?

El MED debe favorecer una decisión empresarial explicable, trazable y sustentada por evidencia.

---

# 4. RESPONSABILIDAD DEL MED

El MED es el componente que coordina el proceso empresarial de evaluación de una propuesta de compra.

Debe:

- recibir la propuesta;
- identificar los datos necesarios;
- coordinar los análisis;
- evaluar las reglas aplicables;
- recoger sus resultados;
- incorporar las excepciones permitidas;
- remitir los resultados a la Capa de Resolución de Conflictos (CRC);
- recibir la resolución consolidada;
- construir la recomendación explicable para el usuario.

El MED no constituye una segunda autoridad de resolución de conflictos.

---

# 5. LÍMITES DEL MED

El MED:

- no redefine la autoridad documental de EIOS;
- no sustituye a la CRC;
- no establece una jerarquía propia de reglas;
- no modifica parámetros por iniciativa propia;
- no ejecuta compras;
- no anula salvaguardas no anulables;
- no inventa evidencia;
- no convierte ausencia de datos en una conclusión favorable o desfavorable sin fundamento;
- no sustituye al decisor humano.

---

# 6. ENTRADA DEL MODELO

La entrada principal es una:

## PROPUESTA DE COMPRA

Cuando estén disponibles, deberá incorporar:

- artículo;
- proveedor;
- cantidad;
- precio unitario;
- importe total;
- fecha de propuesta;
- fecha prevista de entrega;
- plazo de entrega;
- plazo de pago;
- condiciones de pago;
- descuentos;
- rappels;
- incidencias;
- otras condiciones relevantes.

La **fecha de propuesta de compra** es especialmente importante porque permite realizar análisis temporales y proyectar el impacto de la operación.

---

# 7. INFORMACIÓN UTILIZADA

El modelo puede utilizar información procedente de diferentes áreas.

## 7.1 Compras

- últimas compras;
- fechas;
- precios;
- cantidades;
- proveedores;
- condiciones;
- descuentos;
- rappels;
- incidencias.

## 7.2 Proveedores

- proveedor actual;
- proveedores alternativos;
- histórico;
- precios;
- condiciones;
- incidencias.

## 7.3 Stock

- stock actual;
- stock comprometido;
- pedidos pendientes;
- compras en tránsito;
- rotación;
- cobertura;
- demanda histórica;
- demanda prevista.

## 7.4 Rentabilidad

- precio de venta;
- margen en euros;
- margen porcentual;
- margen mínimo establecido;
- impacto de descuentos;
- impacto de rappels.

## 7.5 Situación financiera

- tesorería;
- pagos previstos;
- liquidez;
- fondo de maniobra;
- necesidades financieras;
- impacto de la compra sobre la capacidad de pago.

---

# 8. CALIDAD Y SUFICIENCIA DE LOS DATOS

Antes de emitir una recomendación, EIOS debe determinar si la información disponible permite realizar una evaluación suficientemente fiable.

Debe considerar, cuando corresponda:

- actualidad;
- completitud;
- comparabilidad;
- número de referencias;
- consistencia;
- evidencia disponible.

Cuando una evaluación crítica no pueda realizarse por falta de información suficiente, el resultado podrá ser:

**INFORMACIÓN INSUFICIENTE**

EIOS no debe confundir:

> No disponemos de evidencia suficiente.

con:

> La operación no es viable.

---

# 9. ANÁLISIS TEMPORAL

El MED debe analizar la compra teniendo en cuenta el tiempo.

No debe limitarse al estado actual de la empresa.

Cuando existan datos suficientes podrá considerar:

- stock actual;
- ventas históricas;
- demanda;
- pedidos pendientes;
- compras en tránsito;
- fecha prevista de recepción;
- plazo de entrega;
- cantidad propuesta.

El análisis temporal permitirá estudiar la evolución prevista de la situación después de realizar la compra.

---

# 10. PROYECCIÓN DE STOCK

EIOS debe poder estimar la evolución futura del stock.

Conceptualmente:

```text
Stock proyectado =
Stock actual
+ entradas previstas
- salidas previstas
```

La proyección podrá utilizar:

- ventas históricas;
- demanda prevista;
- pedidos pendientes;
- compras en tránsito;
- fecha de recepción;
- plazo de entrega.

Una de sus aplicaciones principales será anticipar:

- posibles roturas de stock;
- exceso de stock;
- compras innecesarias;
- compras de productos de baja rotación.

---

# 11. ROTURA DE STOCK

El MED debe poder evaluar si una compra puede:

- evitar una futura rotura de stock;
- llegar demasiado tarde para evitarla;
- generar exceso de stock;
- ser innecesaria.

La evaluación deberá tener en cuenta especialmente:

- stock actual;
- consumo histórico;
- demanda;
- pedidos pendientes;
- plazo de entrega;
- fecha prevista de recepción;
- cantidad propuesta.

No debe limitarse a mostrar el stock actual.

---

# 12. REFERENCIAS TEMPORALES DEL PRECIO

El precio de compra propuesto no debe compararse automáticamente con un único valor histórico.

El modelo deberá poder trabajar con diferentes ventanas temporales, configurables por la empresa.

Ejemplos:

- últimos 3 meses;
- últimos 6 meses;
- últimos 12 meses;
- últimos 24 meses.

La elección del periodo deberá responder a criterios empresariales y podrá variar según artículo, sector o política de la empresa.

---

# 13. ANTIGÜEDAD DE LAS REFERENCIAS

La antigüedad de un dato debe formar parte de la evaluación.

El modelo deberá considerar:

- fecha;
- antigüedad;
- número de operaciones;
- comparabilidad;
- condiciones de compra.

Una referencia histórica antigua no deberá recibir automáticamente el mismo peso que una referencia reciente y comparable.

---

# 14. COMPARABILIDAD DE LAS COMPRAS

No todos los precios históricos deben considerarse automáticamente comparables.

Cuando los datos estén disponibles, deberán considerarse:

- artículo;
- proveedor;
- cantidad;
- fecha;
- descuentos;
- rappels;
- condiciones de pago;
- otras condiciones comerciales.

Una compra de 10 unidades no necesariamente constituye una referencia adecuada para una compra de 1.000 unidades.

---

# 15. PRECIO MEDIO HISTÓRICO

El precio medio histórico no deberá considerarse automáticamente una referencia válida.

Cuando el histórico abarque muchos años pueden existir factores que reduzcan su utilidad:

- inflación;
- evolución del mercado;
- cambios de proveedor;
- cambios en las cantidades;
- descuentos;
- rappels;
- cambios de condiciones;
- cambios en la política de compras.

Por ello, el MED deberá priorizar referencias que sean suficientemente recientes y comparables.

---

# 16. PRECIO MÁXIMO RECOMENDADO

El MED podrá generar un:

## PRECIO MÁXIMO RECOMENDADO

Este valor no debe ser arbitrario.

Su metodología deberá definirse mediante criterios configurables.

Podrá considerar:

- compras recientes;
- histórico de compras;
- precio ponderado;
- operaciones comparables;
- proveedor;
- proveedores alternativos;
- margen mínimo;
- precio de venta;
- condiciones de pago;
- descuentos;
- rappels;
- estrategia empresarial.

La metodología definitiva deberá mantenerse parametrizable y documentada.

El MED no deberá inventar un precio máximo cuando no exista evidencia suficiente para calcularlo.

---

# 17. EXPLICACIÓN DEL PRECIO

EIOS deberá evitar mensajes genéricos.

### No deseable:

> Precio superior al histórico reciente.

### Preferible:

> Precio ofertado: 18,50 €

> +7,6 % respecto a la última compra de 17,20 €, realizada hace 25 días.

> +3,4 % respecto al precio medio ponderado de los últimos 3 meses.

> +6,6 % respecto al precio medio ponderado de los últimos 12 meses.

La información detallada deberá estar disponible sin saturar la pantalla principal.

---

# 18. FIABILIDAD DE LAS REFERENCIAS

Cuando sea posible, EIOS deberá valorar la calidad de la referencia.

### Alta

Datos recientes, suficientes y comparables.

### Media

Datos limitados o con diferencias relevantes.

### Baja

Datos antiguos, escasos o poco comparables.

EIOS no debe transmitir una falsa sensación de precisión cuando los datos disponibles sean insuficientes.

La valoración de fiabilidad debe quedar explicada y trazable.

---

# 19. MOTOR DE REGLAS

El MED utilizará las reglas definidas en la **Matriz de Reglas MVP**.

Las reglas podrán adaptarse mediante parámetros configurables a:

- empresa;
- sector;
- política empresarial;
- situación económica;
- estrategia de compras;
- estrategia financiera;
- nivel de riesgo aceptado.

El MED no redefine las reglas de negocio ni su autoridad documental.

---

# 20. EFECTO Y SEVERIDAD DE LAS REGLAS

La Matriz de Reglas v2.0 separa:

- **Efecto de la regla:** capacidad de intervenir en la decisión.
- **Severidad:** importancia o gravedad del resultado.

Los efectos son:

| Código | Efecto |
|---|---|
| R0 | BLOQUEO |
| R1 | CONDICIONANTE |
| R2 | NEGOCIACIÓN |
| R3 | INFORMATIVA |

El MED recibe estos resultados.

No los sustituye por una puntuación agregada ni por una suma de reglas favorables y desfavorables.

---

# 21. RESULTADOS INDIVIDUALES Y CONSOLIDACIÓN

Las reglas pueden producir resultados individuales.

Ejemplo:

```text
PRE-001 → R2 / ALTA → NEGOCIAR
STK-001 → R1 / ALTA → COMPRAR CONDICIONADO
FIN-001 → R0 / CRÍTICA → NO COMPRAR
```

Estos resultados no se compensan automáticamente.

Cuando existan varias reglas activadas, la consolidación corresponde a la:

**Capa de Resolución de Conflictos (CRC).**

El MED deberá proporcionar a la CRC la información necesaria y utilizar posteriormente el resultado consolidado.

---

# 22. FLUJO DE REGLAS Y CRC

El flujo lógico será:

```text
DATOS
  ↓
ANÁLISIS
  ↓
REGLAS
  ↓
RESULTADOS INDIVIDUALES
  ↓
EXCEPCIONES PERMITIDAS
  ↓
CRC
  ↓
RESULTADO CONSOLIDADO
```

La CRC aplica la autoridad de resolución definida para EIOS.

El MED no deberá establecer una segunda jerarquía de resolución.

---

# 23. EXCEPCIONES

Las excepciones deberán estar expresamente definidas y ser trazables.

Ejemplo:

Regla:

> No comprar si existe exceso de stock.

Excepción:

> Existe un pedido confirmado que absorberá el stock.

Resultado:

> La regla de exceso de stock queda mitigada.

Las excepciones no podrán anular salvaguardas clasificadas como no anulables.

El MED deberá registrar la excepción aplicada y trasladar la información correspondiente a la CRC.

---

# 24. RESULTADOS OFICIALES DE LA DECISIÓN

El MED trabajará exclusivamente con los cinco resultados oficiales:

## 🟢 COMPRAR

La operación cumple los criterios establecidos y no presenta bloqueos incompatibles con la compra.

## 🟡 NEGOCIAR

La operación puede ser viable, pero existen condiciones que deberían mejorarse.

## 🔵 COMPRAR CONDICIONADO

La operación puede ser viable si se cumplen determinadas condiciones.

## 🔴 NO COMPRAR

Existe un bloqueo o la operación no resulta viable conforme a las reglas aplicables.

## ⚪ INFORMACIÓN INSUFICIENTE

La evidencia disponible no permite emitir una recomendación suficientemente fiable.

---

# 25. NEGOCIACIÓN

Cuando una operación pueda mejorar mediante negociación, EIOS deberá identificar, cuando sea posible:

- precio objetivo;
- precio máximo recomendado;
- plazo de pago objetivo;
- cantidad recomendada;
- descuento necesario;
- rappel necesario;
- condiciones necesarias.

Ejemplo:

> NEGOCIAR

> Precio ofertado: 18,50 €

> Precio máximo recomendado: 17,80 €

> Alternativa:

> Mantener 18,50 € si el plazo de pago aumenta de 30 a 90 días.

Las acciones de negociación son acciones secundarias y no sustituyen a los cinco resultados oficiales.

---

# 26. COMPRA CONDICIONADA

Esta categoría permite transformar determinadas situaciones problemáticas en condiciones concretas.

Ejemplos:

- comprar si se obtiene un plazo de pago determinado;
- comprar si se reduce el precio;
- comprar si se reduce la cantidad;
- comprar si existe un pedido confirmado;
- comprar si se mantiene un margen mínimo.

La condición deberá quedar explícitamente documentada y ser verificable.

---

# 27. SITUACIÓN FINANCIERA

La compra no debe evaluarse únicamente desde la perspectiva de compras.

Debe analizarse su impacto sobre:

- tesorería;
- pagos próximos;
- liquidez;
- fondo de maniobra;
- capacidad de atender obligaciones;
- rentabilidad.

Una compra que comprometa la capacidad de hacer frente a los pagos puede ser desaconsejada aunque el precio de compra sea excelente.

---

# 28. ALTERNATIVAS ANTE RIESGO FINANCIERO

Cuando una compra comprometa la situación financiera, EIOS podrá mostrar alternativas para valoración humana.

Ejemplos:

- solicitar ampliación de capital;
- vender inmovilizado no utilizado;
- promocionar productos de baja rotación;
- acelerar cobros de clientes;
- negociar condiciones de pago;
- reducir la cantidad comprada.

EIOS no ejecutará estas acciones automáticamente.

Las alternativas deberán presentarse como opciones para valoración humana y no como órdenes operativas.

---

# 29. EXCESO DE STOCK

No se recomendará automáticamente una compra cuando exista un nivel elevado de stock.

Sin embargo, deberán contemplarse excepciones.

Ejemplo:

```text
Stock elevado
     ↓
Riesgo

Pedido confirmado
     ↓
Excepción

CRC
     ↓
Resultado consolidado
```

El MED deberá proporcionar la información necesaria para que la interacción pueda ser evaluada conforme a las reglas y a la CRC.

---

# 30. PARAMETRIZACIÓN

Los criterios utilizados por el MED deberán poder configurarse mediante el sistema de parametrización de EIOS.

Entre otros, podrán configurarse:

- periodos de referencia;
- antigüedad máxima;
- límites;
- tolerancias;
- niveles de stock;
- márgenes;
- reglas;
- excepciones;
- criterios financieros.

El MED utiliza estos parámetros; no constituye la autoridad para administrarlos.

Los parámetros deberán mantener su propia versión y vigencia.

---

# 31. VALORES ESTÁNDAR

EIOS deberá partir de valores estándar editables.

Estos valores servirán como configuración inicial.

La empresa podrá modificarlos según:

- actividad;
- tamaño;
- política;
- situación financiera;
- estrategia;
- nivel de riesgo aceptado.

No se deberán presentar valores estándar como si fueran decisiones empresariales definitivas.

---

# 32. VIGENCIA E HISTORIAL DE CONFIGURACIÓN

Las modificaciones importantes deberán conservar:

- valor;
- fecha de inicio;
- fecha de finalización, cuando corresponda;
- usuario que realizó el cambio;
- motivo del cambio;
- versión del parámetro.

EIOS debe poder determinar qué configuración estaba vigente cuando se tomó una decisión.

Ejemplo:

```text
Margen mínimo:

01/01/2026 → 20 %
01/07/2026 → 22 %
01/01/2027 → 25 %
```

No se deberá sobrescribir una configuración anterior sin conservar su historial.

---

# 33. SIMULACIÓN DE CAMBIOS

Como evolución del sistema, el Centro de Parametrización podrá permitir simular el efecto de modificar un parámetro antes de aplicarlo.

Ejemplo:

```text
Margen mínimo actual:
20 %

Nuevo valor:
25 %

Impacto simulado:
14 operaciones históricas que anteriormente eran aceptables
pasarían a clasificarse como "NEGOCIAR".
```

Esta funcionalidad queda sujeta a validación y diseño específico.

El MED podrá consumir sus resultados, pero no deberá confundir simulación con configuración vigente.

---

# 34. TRAZABILIDAD

Cada decisión importante deberá poder reconstruirse.

EIOS deberá poder identificar:

- datos utilizados;
- fecha de los datos;
- referencias utilizadas;
- parámetros vigentes;
- versión de parámetros;
- reglas activadas;
- efecto y severidad de cada regla;
- excepciones aplicadas;
- resolución de la CRC;
- resultado final;
- versión del MED y de las reglas.

El sistema debe poder explicar:

> POR QUÉ HA LLEGADO A ESTA RECOMENDACIÓN.

---

# 35. IDENTIDAD DE LA DECISIÓN

Cuando el sistema lo soporte, la trazabilidad deberá permitir identificar:

```text
Decision_ID
Scenario_ID
Data_Snapshot_ID
Parameter_Version
Rules_Version
MED_Version
EIOS_Version
```

Esto permite reconstruir el contexto exacto en el que se produjo una recomendación.

---

# 36. FLUJO GENERAL DEL MED

```text
PROPUESTA DE COMPRA
        ↓
VALIDACIÓN DE DATOS
        ↓
EVALUACIÓN DE SUFICIENCIA Y CALIDAD
        ↓
ANÁLISIS HISTÓRICO
        ↓
ANÁLISIS DE STOCK
        ↓
PROYECCIÓN TEMPORAL
        ↓
ANÁLISIS DE RENTABILIDAD
        ↓
ANÁLISIS FINANCIERO
        ↓
COMPARACIÓN CON REFERENCIAS
        ↓
APLICACIÓN / EVALUACIÓN DE REGLAS
        ↓
EVALUACIÓN DE EXCEPCIONES
        ↓
RESOLUCIÓN CRC
        ↓
RESULTADO CONSOLIDADO
        ↓
CONDICIONES / ACCIONES DE NEGOCIACIÓN
        ↓
EXPLICACIÓN
        ↓
DECISOR HUMANO
```

Si la información crítica es insuficiente, el flujo deberá poder finalizar en:

```text
INFORMACIÓN INSUFICIENTE
```

sin fabricar una recomendación.

---

# 37. EXPLICACIÓN DE LA DECISIÓN

La explicación deberá permitir identificar:

1. qué se ha evaluado;
2. qué reglas se activaron;
3. qué evidencia las sustentó;
4. qué excepciones se aplicaron;
5. cómo intervino la CRC;
6. cuál fue el resultado;
7. qué condiciones o alternativas se proponen.

Ejemplo:

```text
Resultado:
NEGOCIAR

Motivo principal:
El precio ofertado supera la referencia comparable configurada.

Evidencia:
Última compra comparable: 17,20 €
Precio ofertado: 18,50 €

Regla:
PRE-001

Efecto:
R2 — NEGOCIACIÓN

Acción sugerida:
Solicitar reducción del precio.
```

La explicación no deberá introducir información que no proceda de la evidencia disponible.

---

# 38. PRINCIPIO DE SIMPLICIDAD

La complejidad debe permanecer principalmente en el motor interno.

La interfaz destinada al CEO deberá mostrar inicialmente:

1. decisión;
2. principales motivos;
3. riesgos;
4. condiciones de negociación;
5. fiabilidad de los datos cuando sea relevante.

La información detallada deberá estar disponible bajo demanda.

El sistema debe evitar la saturación de información.

---

# 39. CONTROL HUMANO

Las reglas proporcionan evaluaciones.

La CRC consolida resultados.

EIOS genera una recomendación.

El decisor autorizado toma la decisión empresarial final.

```text
REGLAS
   ↓
EVALUACIÓN
   ↓
CRC
   ↓
RECOMENDACIÓN
   ↓
DECISOR
```

El MED no sustituye al criterio empresarial autorizado.

---

# 40. PRINCIPIOS RECTORES DEL MED

El Modelo Empresarial de Decisión deberá respetar:

1. **Trazabilidad**
2. **Explicabilidad**
3. **No compensación automática**
4. **Separación entre regla y resolución de conflictos**
5. **Separación entre parámetro y lógica empresarial**
6. **Configurabilidad**
7. **Evidencia suficiente**
8. **Control humano**
9. **No automatización silenciosa**
10. **Coherencia con la arquitectura EIOS**
11. **No invención de datos o evidencia**
12. **Reproducibilidad de la recomendación**

---

# 41. EVOLUCIÓN DEL MODELO

El Modelo Empresarial de Decisión no se considera cerrado.

Debe evolucionar a medida que se validen:

- nuevos casos reales;
- nuevas reglas;
- nuevos datos;
- nuevas necesidades empresariales;
- nuevas pruebas del sistema.

Toda modificación estructural deberá quedar documentada y mantener trazabilidad de versión.

La evolución no deberá alterar silenciosamente las decisiones ya tomadas.

---

# 42. ASPECTOS PENDIENTES DE DEFINICIÓN

Tras la consolidación de la arquitectura v2.0, permanecen como áreas de diseño o validación:

- metodología exacta para calcular el precio máximo recomendado;
- definición definitiva de operaciones comparables;
- metodología de cálculo de rotación;
- metodología de cálculo de cobertura;
- metodología de proyección de stock;
- metodología de impacto financiero proyectado;
- definición definitiva de niveles de fiabilidad;
- parámetros iniciales empresariales;
- diseño definitivo de la simulación de cambios;
- casos reales para validar interacciones complejas.

Estos puntos no deben interpretarse como una ausencia de arquitectura, sino como elementos de diseño, parametrización o validación pendientes.

---

# 43. ESTADO DEL DOCUMENTO

**Versión:** 2.0  
**Estado:** APROBADO — Baseline EIOS Vertical MVP  
**Baseline:** EIOS Vertical MVP  
**Autoridad:** Modelo Empresarial de Decisión  
**Reglas:** `04_Reglas/Matriz_Reglas_MVP.md`  
**Resolución de conflictos:** `04_Reglas/Capa_resolucion_conflictos.md`  
**Control documental:** `Matriz_Autoridad_Documental.md`

Este documento no modifica ni sustituye la autoridad de los documentos anteriores.

---

# 44. RELACIÓN DOCUMENTAL

El MED deberá mantenerse coherente con:

- `Matriz_Autoridad_Documental.md` — autoridad documental.
- `04_Reglas/Matriz_Reglas_MVP.md` — definición de reglas.
- `04_Reglas/Capa_resolucion_conflictos.md` — resolución de conflictos.
- catálogo de parámetros / Configuration Center — parametrización.
- contratos de evidencia EIOS — requisitos de evidencia.
- componentes de análisis y escenarios que sean aprobados posteriormente.

No deberán crearse dependencias documentales hacia archivos inexistentes.

Toda nueva relación documental deberá ser aprobada y registrada conforme a la autoridad documental de EIOS.
