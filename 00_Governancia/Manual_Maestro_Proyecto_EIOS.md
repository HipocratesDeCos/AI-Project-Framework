DOCUMENTO: MMP-EIOS
NOMBRE: Manual Maestro del Proyecto EIOS
UBICACIÓN: 00_Governancia/Manual_Maestro_Proyecto_EIOS.md
FUNCIÓN: Documento maestro de continuidad y recuperación de contexto
AUTORIDAD: Project Governance
ESTADO: Vigente

# MANUAL MAESTRO DEL PROYECTO EIOS

## EIOS — Enterprise Intelligent Operations System

**Documento:** Manual Maestro del Proyecto EIOS (MMP-EIOS)  
**Versión:** 1.0  
**Estado:** Vigente — Documento maestro de continuidad  
**Fecha:** 12/08/2026  
**Ubicación oficial:** `00_Governancia/Manual_Maestro_Proyecto_EIOS.md`

---

# 1. PROPÓSITO DEL MANUAL

Este documento constituye el **Manual Maestro del Proyecto EIOS (MMP-EIOS)**.

Su finalidad es preservar el conocimiento esencial del proyecto y permitir su recuperación y continuidad aunque se pierda el contexto de una conversación, se sustituya la IA utilizada para trabajar en el proyecto o transcurra un periodo prolongado entre sesiones.

El MMP-EIOS debe permitir que una persona o una IA pueda comprender:

- qué es EIOS;
- para qué se está construyendo;
- qué decisiones han sido tomadas;
- qué conceptos están aprobados;
- qué conceptos están pendientes;
- cómo se organiza el proyecto;
- qué documentos constituyen las fuentes oficiales;
- cuál es el estado actual;
- cuál es el siguiente trabajo que debe realizarse.

El MMP-EIOS **no sustituye** a los documentos funcionales especializados.

Actúa como documento de continuidad, contexto, coordinación y recuperación.

---

# 2. PRINCIPIO FUNDAMENTAL DEL PROYECTO

EIOS debe ayudar a la empresa a tomar mejores decisiones de compra utilizando información histórica, operativa, comercial y financiera.

EIOS no debe limitarse a responder:

> ¿Podemos comprar?

Debe intentar responder:

> ¿Tiene sentido realizar esta compra en estas condiciones y qué deberíamos negociar para mejorarla o hacerla viable?

La decisión final corresponde siempre a una persona autorizada.

EIOS es un sistema de apoyo a la decisión, no un ejecutor automático de compras.

---

# 3. IDENTIDAD DEL PROYECTO

## Nombre oficial

**EIOS — Enterprise Intelligent Operations System**

Durante las primeras fases del proyecto apareció el nombre SIDA — Sistema Inteligente de Decisión de Adquisiciones.

La decisión vigente es utilizar:

**EIOS**

como identidad principal del proyecto.

La funcionalidad de decisión de compras constituye uno de los núcleos iniciales de EIOS.

No utilizar SIDA como identidad principal salvo que exista una decisión documental posterior que modifique esta definición.

---

# 4. OBJETIVO DEL MVP

El MVP debe ayudar principalmente al CEO y al responsable de compras a valorar una propuesta de compra utilizando:

- precios actuales;
- precios históricos;
- productos comparables;
- proveedores;
- stock;
- demanda;
- rentabilidad;
- márgenes;
- liquidez;
- condiciones comerciales;
- rappels;
- descuentos;
- plazos de pago;
- fiabilidad del proveedor;
- reglas empresariales;
- excepciones;
- coste de oportunidad.

El resultado debe ser comprensible y accionable.

---

# 5. USUARIO PRINCIPAL

El usuario principal del sistema es el:

**CEO / responsable de decisión empresarial.**

El sistema debe estar diseñado pensando en situaciones reales de negociación con proveedores.

Ejemplo:

El CEO está delante de un proveedor y recibe una oferta de:

> 18,50 €/unidad

El sistema debe permitir valorar rápidamente:

- si el precio es favorable;
- cómo se compara con referencias históricas;
- qué margen genera;
- qué ocurre con descuentos;
- qué ocurre con rappels;
- qué cantidad sería conveniente comprar;
- cómo afecta al stock;
- cómo afecta a la liquidez;
- qué condiciones debería negociar;
- qué alternativas existen.

---

# 6. PRINCIPIO DE INTERFAZ

La complejidad debe permanecer principalmente en el motor interno.

La interfaz inicial del CEO debe mostrar prioritariamente:

1. decisión;
2. principales motivos;
3. riesgos;
4. condiciones de negociación;
5. margen;
6. información relevante sobre stock;
7. fiabilidad cuando sea relevante;
8. fiabilidad de las referencias cuando sea relevante.

La información secundaria deberá poder consultarse bajo demanda.

El sistema debe evitar saturar al CEO.

---

# 7. FORMA DE PRESENTAR LAS DECISIONES

EIOS debe evitar respuestas excesivamente robóticas.

La salida debe utilizar:

**Variable + valoración + breve contexto.**

Ejemplo:

**Precio:** desfavorable  
El precio está por encima de la referencia comparable de los últimos X meses.

**Margen:** aceptable  
El margen se mantiene dentro del rango establecido.

**Stock:** adecuado  
El nivel actual permite cubrir la demanda prevista.

**Liquidez:** tensionada  
La operación incrementaría la presión financiera durante el periodo previsto.

**Plazo actual:** 30 días

La explicación debe ser breve pero suficientemente contextualizada.

---

# 8. RESULTADOS OFICIALES DE DECISIÓN

La taxonomía operativa de EIOS debe contemplar inicialmente:

## COMPRAR

La operación cumple los criterios establecidos y no presenta riesgos relevantes.

## NEGOCIAR

La operación puede ser viable, pero existen condiciones que deberían mejorarse.

La negociación debe aprovechar la oportunidad de conseguir un precio igual o mejor que la referencia comparable.

Si el proveedor rechaza la negociación:

- la oferta puede quedar en standby;
- EIOS puede recomendar buscar proveedores alternativos;
- si aparece una oferta mejor, deberá utilizarse como nueva referencia.

## COMPRAR CONDICIONADO

La operación puede ser viable si se cumplen determinadas condiciones.

Ejemplos:

- obtener un precio determinado;
- conseguir un plazo de pago concreto;
- reducir la cantidad;
- obtener un descuento;
- obtener un rappel;
- disponer de un pedido confirmado;
- mantener un margen mínimo;
- resolver previamente una situación de liquidez.

## NO COMPRAR

Existe un riesgo o incumplimiento suficientemente relevante para desaconsejar la operación.

## INFORMACIÓN INSUFICIENTE

No existe información suficiente o suficientemente fiable para emitir una recomendación con el nivel de confianza requerido.

La existencia de este quinto resultado debe mantenerse alineada con la Matriz de Reglas MVP y la Capa de Resolución de Conflictos.

---

# 9. MODELO EMPRESARIAL DE DECISIÓN

El documento:

`04_Inteligencia/Modelo_Empresarial_Decision.md`

constituye el documento especializado que define el núcleo empresarial de decisión.

El MED debe analizar:

1. propuesta de compra;
2. validación de datos;
3. histórico;
4. productos comparables;
5. stock;
6. proyección temporal;
7. rentabilidad;
8. margen;
9. situación financiera;
10. condiciones comerciales;
11. reglas;
12. conflictos;
13. excepciones;
14. decisión;
15. condiciones de negociación;
16. explicación.

---

# 10. FLUJO GENERAL DE DECISIÓN

```text
PROPUESTA DE COMPRA
        ↓
VALIDACIÓN DE DATOS
        ↓
IDENTIFICACIÓN DEL PRODUCTO
        ↓
IDENTIFICACIÓN DE PRODUCTOS COMPARABLES
        ↓
ANÁLISIS HISTÓRICO
        ↓
ANÁLISIS DE STOCK
        ↓
PROYECCIÓN TEMPORAL
        ↓
ANÁLISIS DE RENTABILIDAD
        ↓
ANÁLISIS DE MARGEN
        ↓
ANÁLISIS FINANCIERO
        ↓
ANÁLISIS DE CONDICIONES COMERCIALES
        ↓
APLICACIÓN DE REGLAS
        ↓
RESOLUCIÓN DE CONFLICTOS
        ↓
APLICACIÓN DE EXCEPCIONES
        ↓
DECISIÓN
        ↓
CONDICIONES DE NEGOCIACIÓN
        ↓
EXPLICACIÓN

1. IDENTIFICACIÓN DE PRODUCTOS

Uno de los conceptos importantes incorporados al proyecto es la necesidad de distinguir entre:

producto;
denominación comercial;
referencia;
producto comparable;
categoría funcional.

Un mismo producto puede aparecer con denominaciones diferentes.

Ejemplo:

Proveedor A:

Arlita

Proveedor B:

Arcilla expandida

Si las características y funcionalidad permiten considerarlos equivalentes, EIOS debe poder relacionarlos.

12. RFP — REFERENCIA FUNCIONAL DE PRODUCTO

Se utilizará el concepto:

RFP — Referencia Funcional de Producto

como mecanismo informativo para agrupar productos que pueden cumplir una misma función o constituir referencias comparables.

Una RFP no significa necesariamente que dos productos sean idénticos.

Su finalidad es facilitar:

búsqueda;
comparación;
análisis histórico;
análisis de precios;
análisis de proveedores;
identificación de alternativas.
13. COMPARABILIDAD DE PRODUCTOS

EIOS debe poder asignar inicialmente un porcentaje de comparabilidad.

Ejemplo:

90 %;
85 %;
75 %.

La comparabilidad podrá considerar diferentes dimensiones:

funcionalidad;
características técnicas;
presentación;
calidad;
cantidad;
marca;
estética;
condiciones comerciales;
utilización empresarial.

Dos productos pueden cumplir la misma función y presentar pequeñas diferencias.

Ejemplo:

Producto A:

90 % comparable con Producto B.

La diferencia estética puede ser relevante comercialmente aunque la funcionalidad sea prácticamente idéntica.

14. VALIDACIÓN HUMANA DE PRODUCTOS COMPARABLES

Inicialmente:

EIOS propone automáticamente la relación.

Una persona podrá:

validar;
rechazar;
modificar la valoración de comparabilidad.

La decisión humana debe quedar registrada.

No se debe obligar a que un producto pertenezca a más de una RFP.

Ante una duda sobre pertenencia a una RFP:

NO.

La simplicidad y fiabilidad prevalecen sobre la creación de relaciones dudosas.

15. BÚSQUEDA ENRIQUECIDA DE PRODUCTOS

Cuando el CEO solicite información sobre un artículo relacionado con una referencia, EIOS podrá mostrar:

Producto solicitado

Precio actual:

18,50 €

Y como información secundaria:

Productos comparables
Producto	Comparabilidad	Precio	Proveedor	Otros datos
Producto A	90 %	X €	Proveedor A	...
Producto B	82 %	X €	Proveedor B	...
Producto C	76 %	X €	Proveedor C	...

Cada referencia debe mantener sus propios cálculos.

La información comparable debe enriquecer la búsqueda sin saturar la pantalla principal.

16. COMPARABILIDAD COMO HERRAMIENTA DE CÁLCULO

La relación entre productos no debe utilizarse únicamente como dato informativo.

Puede utilizarse para:

construir referencias de precio;
ampliar el histórico disponible;
identificar alternativas;
analizar proveedores;
calcular rangos de precio;
detectar oportunidades de negociación.

Sin embargo, EIOS debe conservar siempre la trazabilidad de qué producto originó cada referencia.

17. CÓDIGO DE REFERENCIA ANEXO

Como evolución del modelo, podrá utilizarse un código de referencia adicional para relacionar productos.

Este código tendrá carácter auxiliar.

Debe permitir:

identificar relaciones;
facilitar consultas;
mantener trazabilidad;
evitar depender exclusivamente de la descripción textual.

No debe utilizarse para ocultar las diferencias reales entre productos.

18. HISTÓRICO DE PRECIOS

Los precios históricos deben analizarse teniendo en cuenta:

fecha;
antigüedad;
cantidad;
proveedor;
condiciones;
descuentos;
rappels;
comparabilidad;
contexto temporal.

No debe utilizarse automáticamente el precio medio de todo el histórico.

19. VENTANAS TEMPORALES

EIOS debe poder trabajar con diferentes ventanas:

últimos 3 meses;
últimos 6 meses;
últimos 12 meses;
últimos 24 meses.

Los periodos deben ser configurables.

20. ANTIGÜEDAD DE LA REFERENCIA

La antigüedad de una compra debe afectar a su fiabilidad como referencia.

Ejemplo:

Última compra: 17,20 €
Fecha: 14/07/2026
Antigüedad: 25 días

Una referencia de hace cuatro años puede tener una utilidad considerablemente inferior.

21. FIABILIDAD DE LAS REFERENCIAS

Las referencias pueden clasificarse como:

Alta

Datos recientes, suficientes y comparables.

Media

Datos limitados o con diferencias relevantes.

Baja

Datos antiguos, escasos o poco comparables.

EIOS debe evitar transmitir una falsa precisión.

22. PRECIO MÁXIMO RECOMENDADO

EIOS podrá calcular un:

Precio Máximo Recomendado (PMR).

Su metodología debe definirse y parametrizarse.

Puede utilizar:

compras recientes;
histórico;
referencias comparables;
precio ponderado;
proveedores alternativos;
margen;
precio de venta;
descuentos;
rappels;
condiciones de pago;
estrategia empresarial.
23. CEA — COSTE EFECTIVO DE ADQUISICIÓN

El sistema debe diferenciar entre:

Precio nominal

y

Coste Efectivo de Adquisición (CEA).

El CEA permite valorar el coste real de una operación considerando ventajas económicas asociadas.

Ejemplo:

Precio:

18,50 €

Descuento:

3 %

Rappel:

2 %

El descuento puede afectar inmediatamente al coste efectivo.

El rappel, cuando se liquida posteriormente, debe conservar su naturaleza temporal y registrarse como beneficio económico diferido.

EIOS debe poder recalcular el CEA en el mismo momento de la negociación cuando cambien:

precio;
cantidad;
descuento;
rappel;
condiciones de pago;
otras variables económicas relevantes.
24. NEGOCIACIÓN DINÁMICA

Durante una reunión con el proveedor el CEO puede modificar condiciones.

Ejemplo:

Precio inicial: 18,50 €

Nueva propuesta:
18,50 €
+ 3 % descuento
+ 2 % rappel
+ 90 días de pago

EIOS debe poder recalcular inmediatamente:

CEA;
margen;
comparación histórica;
PMR;
impacto financiero;
recomendación.

Esto convierte el sistema en una herramienta de negociación dinámica.

25. MARGEN

El margen debe ser una variable especialmente visible.

El CEO trabaja habitualmente con porcentajes de margen.

Por ello EIOS debe mostrar de forma visual:

margen actual;
margen mínimo;
diferencia respecto al mínimo;
efecto del precio de compra;
efecto de descuentos;
efecto de rappels.

El margen no debe quedar oculto dentro de un análisis financiero secundario.

26. CANTIDAD DE COMPRA

La cantidad debe analizarse siempre en relación con el periodo temporal correspondiente.

Cuando EIOS indique una cantidad recomendada debe poder explicar:

demanda histórica;
demanda prevista;
stock actual;
pedidos pendientes;
compras en tránsito;
plazo de entrega;
tiempo estimado de venta;
riesgo de exceso de stock.

No debe utilizarse el concepto "cantidad comprada" sin indicar el contexto temporal.

27. PROYECCIÓN DE STOCK

EIOS debe estimar la evolución futura del stock.

Debe considerar:

stock actual;
entradas previstas;
salidas previstas;
pedidos pendientes;
compras en tránsito;
ventas históricas;
demanda prevista;
fecha de recepción.

Debe detectar:

rotura de stock;
exceso de stock;
compra innecesaria;
baja rotación.
28. PEDIDOS CONFIRMADOS

Los pedidos confirmados pueden modificar significativamente una decisión.

Ejemplo:

Stock previsto:

600 unidades

Pedido confirmado:

600 unidades

EIOS no debe considerar automáticamente esas 600 unidades como disponibles para satisfacer demanda ordinaria.

Debe calcular qué cantidad adicional sería prudente comprar para evitar rotura de stock.

El histórico deberá analizarse, cuando proceda, excluyendo el efecto extraordinario del cliente que originó el pedido.

29. TIEMPO DE PERMANENCIA EN ALMACÉN

EIOS debe permitir parametrizar el tiempo máximo recomendado de permanencia de un producto en almacén.

Ejemplo:

Compra:

01/09/2025

Periodo máximo:

12 meses

Fecha límite:

01/09/2026

El sistema debe valorar esta condición al analizar una nueva compra.

Debe poder detectar si una compra podría provocar que determinadas unidades permanezcan en stock más tiempo del permitido.

30. NOTIFICACIONES SOBRE PERMANENCIA

EIOS podrá utilizar acontecimientos históricos para mejorar la negociación.

Ejemplo:

En compras anteriores, este producto permaneció en stock durante 14 meses.

El parámetro actual establece un máximo de 12 meses.

Se recomienda reducir la cantidad o negociar condiciones antes de comprar.

Esto aporta información histórica contextualizada.

31. VELOCIDAD DE VENTA

EIOS debe poder responder:

¿Según el histórico, cuántos días tardaría en vender estas 2.000 unidades?

Debe considerar:

periodo seleccionado;
unidades vendidas;
frecuencia de venta;
estacionalidad cuando exista;
pedidos extraordinarios;
clientes extraordinarios;
comportamiento histórico comparable.
32. COSTE DE OPORTUNIDAD

El coste de oportunidad debe formar parte del análisis.

EIOS debe poder considerar:

capital inmovilizado;
espacio de almacén;
posibilidad de comprar otro producto;
capacidad financiera;
alternativas de proveedor;
oportunidad de utilizar el dinero en otra operación.

No debe analizar únicamente si la compra es rentable de forma aislada.

33. PRODUCTOS CON MARCA COMO RECLAMO

Existen casos en los que una marca tiene un valor comercial específico.

En estos casos una alternativa aparentemente equivalente puede no ser realmente sustituible.

Ejemplo:

Una marca concreta genera demanda por sí misma.

EIOS debe reconocer que:

Comparabilidad funcional ≠ sustituibilidad comercial.

Este factor debe poder reducir el valor práctico de una alternativa.

34. COMPARACIÓN DE PRODUCTOS A Y B

Cuando existan productos alternativos, EIOS podrá estudiar:

unidades vendidas;
periodo concreto;
porcentaje de ventas de A frente a B;
precio de venta;
margen;
rotación;
aceptación comercial.

Si ambos productos tienen el mismo precio de venta y el cliente no distingue comercialmente entre ellos, la marca o estética pueden tener menor importancia como elemento de decisión.

35. FIABILIDAD DEL PROVEEDOR

La fiabilidad del proveedor constituye una variable relevante.

Una oferta económicamente favorable puede perder atractivo si el proveedor presenta antecedentes negativos.

EIOS debe poder considerar:

retrasos;
mercancía deteriorada;
incumplimientos;
incidencias;
calidad;
cumplimiento de plazos;
comportamiento histórico.
36. RESPUESTA ANTE PROVEEDOR DE BAJA FIABILIDAD

Cuando un proveedor tenga fiabilidad baja, EIOS podrá proponer condiciones de mitigación.

1. Contrato con garantías

Posibles cláusulas:

penalización del 1–2 % por día de retraso hasta un máximo;
sustitución de mercancía deteriorada sin coste;
plazo máximo de sustitución;
cancelación unilateral por incumplimiento.
2. Garantías financieras
retención total o parcial de pagos;
avales.
3. Condiciones financieras
pago diferido;
condiciones comerciales específicas;
Incoterms cuando sean aplicables.
4. División de entregas

Reducir el riesgo mediante entregas parciales.

5. Inspecciones

Inspección de seguridad o calidad en origen cuando proceda.

Estas medidas dependen de que el proveedor acepte las condiciones.

37. SITUACIÓN FINANCIERA

La liquidez es una variable crítica.

Una compra puede ser excelente desde el punto de vista del precio y, aun así, no ser conveniente por falta de liquidez.

EIOS debe analizar:

tesorería;
pagos próximos;
cobros previstos;
liquidez;
fondo de maniobra;
capacidad de atender obligaciones;
impacto temporal de la compra.
38. ALTERNATIVAS ANTE TENSIÓN DE LIQUIDEZ

Cuando una compra sea necesaria pero la liquidez sea insuficiente, EIOS puede presentar alternativas para valoración humana:

standby del pedido;
ampliación de capital;
venta de inmovilizado innecesario;
negociación de plazos de cobro con clientes;
descuento por pronto pago cuando mantenga el margen;
promoción de existencias de poca rotación;
negociación de plazo de pago con proveedor;
reducción de cantidad.

Una vez conseguida la liquidez necesaria, la compra puede volver a evaluarse.

39. COSTE FINANCIERO DEL PLAZO DE PAGO

Un plazo de pago más largo puede modificar sustancialmente la decisión.

Ejemplo:

Precio: 18,50 €
Plazo actual: 30 días
Nueva propuesta: 120 días

EIOS debe valorar:

efecto sobre liquidez;
coste efectivo;
margen;
coste de oportunidad;
riesgo;
comparación con operaciones históricas.
40. REGLAS

Las reglas del sistema están documentadas principalmente en:

04_Inteligencia/Matriz_Reglas_MVP.md

Las reglas deben poder distinguir entre:

bloqueo;
recomendación;
excepción.

No se debe utilizar una simple suma de reglas positivas y negativas.

Una regla financiera crítica no debe quedar anulada por varias condiciones favorables de menor importancia.

41. CRC — CAPA DE RESOLUCIÓN DE CONFLICTOS

El documento:

04_Inteligencia/Capa_resolucion_conflictos.md

define la resolución de conflictos entre reglas.

Debe determinar:

prioridad;
severidad;
efecto;
bloqueo;
excepcionabilidad;
motivo dominante;
factores relevantes;
resultado final.

La CRC debe ser coherente con la Matriz de Reglas y el MED.

42. PRINCIPIO DE RESOLUCIÓN DE CONFLICTOS

Ejemplo:

Precio: favorable
Margen: favorable
Stock: elevado
Pedido confirmado: existente
Liquidez: suficiente

EIOS no debe decidir mediante una votación simple.

Debe determinar qué regla tiene mayor relevancia empresarial.

43. EXCEPCIONES

Las excepciones deben estar explícitamente definidas.

Ejemplo:

Regla:
No comprar si existe exceso de stock.

Excepción:
Existe pedido confirmado que absorberá el stock.

Resultado:
La regla de exceso de stock queda mitigada.

Toda excepción debe ser:

trazable;
explicable;
registrada;
justificable.
44. SALVAGUARDAS

Las reglas críticas deben identificar si son:

no anulables;
condicionables;
excepcionables.

Debe existir una lista explícita de salvaguardas no anulables.

La resolución definitiva debe mantenerse alineada con la CRC.

45. CENTRO DE PARAMETRIZACIÓN

Documento:

04_Inteligencia/Centro_Parametrizacion.md

Debe permitir configurar:

periodos de referencia;
antigüedad máxima;
tolerancias;
niveles de stock;
márgenes;
reglas;
prioridades;
excepciones;
criterios financieros;
permanencia máxima en almacén;
otros parámetros empresariales.
46. VALORES ESTÁNDAR

EIOS debe partir de valores estándar editables.

La empresa podrá modificarlos según:

actividad;
tamaño;
estrategia;
situación financiera;
política empresarial;
nivel de riesgo aceptado.
47. VIGENCIA E HISTORIAL DE PARÁMETROS

Aunque no se considera necesario utilizar una fecha de vigencia como criterio funcional de relación entre productos, sí debe conservarse el historial de configuración de parámetros cuando estos cambien.

Debe registrarse:

valor;
fecha;
usuario;
motivo;
configuración resultante.

Ejemplo:

Margen mínimo

01/01/2026 → 20 %
01/07/2026 → 22 %
01/01/2027 → 25 %
48. SIMULACIÓN DE CAMBIOS

Como evolución del sistema, el Centro de Parametrización podrá permitir simular cambios antes de aplicarlos.

Ejemplo:

Margen mínimo actual: 20 %
Nuevo valor: 25 %

Resultado simulado:

14 operaciones históricas que anteriormente eran aceptables
pasarían a clasificarse como NEGOCIAR.

Esta funcionalidad queda pendiente de diseño y validación.

49. TRAZABILIDAD

Cada decisión debe poder reconstruirse.

EIOS debe identificar:

datos utilizados;
fecha de los datos;
productos comparables;
referencias utilizadas;
parámetros utilizados;
reglas activadas;
excepciones aplicadas;
resultado final;
explicación.

El sistema debe poder responder:

¿Por qué ha llegado EIOS a esta recomendación?

50. EXPLICABILIDAD

La explicación debe ser comprensible para el CEO.

Ejemplo:

DECISIÓN: NEGOCIAR

Precio: desfavorable
El precio ofertado está por encima de la referencia comparable.

Margen: aceptable
El margen permanece dentro del rango establecido.

Stock: adecuado
La cantidad prevista se ajusta a la demanda histórica.

Liquidez: tensionada
El pago en las condiciones actuales incrementaría la presión financiera.

Proveedor: fiabilidad baja
Existen antecedentes de retrasos.

RECOMENDACIÓN:
Negociar precio y ampliar el plazo de pago.

ALTERNATIVA:
Si el proveedor no acepta, mantener la oferta en standby y consultar proveedores alternativos.
51. INFORMACIÓN SECUNDARIA

La información detallada no debe desaparecer.

Debe estar disponible mediante niveles de consulta.

Nivel 1

Información necesaria para decidir rápidamente.

Nivel 2

Información de contexto.

Nivel 3

Información técnica, histórica y de cálculo.

El CEO debe poder profundizar cuando lo necesite sin saturar la pantalla principal.

52. NOMENCLATURA

Debe mantenerse un glosario común.

Conceptos actualmente relevantes:

EIOS — Enterprise Intelligent Operations System
MED — Modelo Empresarial de Decisión
CRC — Capa de Resolución de Conflictos
RFP — Referencia Funcional de Producto
CEA — Coste Efectivo de Adquisición
PMR — Precio Máximo Recomendado
MVP — Minimum Viable Product
EVM — Earned Value Management / Gestión del Valor Ganado

Los acrónimos deberán aparecer acompañados de su nombre completo durante las primeras iteraciones documentales cuando sea necesario facilitar el aprendizaje y la comprensión.

53. ARQUITECTURA DOCUMENTAL

La estructura principal del repositorio es:

00_Governancia
01_Negocio
03_Arquitectura
04_Inteligencia
05_Aplicacion
06_Operaciones
07_Desarrollo
08_Pruebas
09_Recursos
54. DOCUMENTOS PRINCIPALES
Gobernancia
00_Governancia/Project_Charter.md
00_Governancia/Project_Context.md
00_Governancia/Project_Governance.md
00_Governancia/Matriz_Autoridad_Documental.md
00_Governancia/Manual_Maestro_Proyecto_EIOS.md
Negocio
01_Negocio/Especificacion_funcional.md
Arquitectura
03_Arquitectura/Architecture_Blueprint.md
03_Arquitectura/Framework_Map.md
03_Arquitectura/Master_Project_Map.md
Inteligencia
04_Inteligencia/Modelo_Empresarial_Decision.md
04_Inteligencia/Matriz_Reglas_MVP.md
04_Inteligencia/Capa_resolucion_conflictos.md
04_Inteligencia/Catalogo_Parametros_MVP.md
04_Inteligencia/Centro_Parametrizacion.md
55. FUENTES OFICIALES POR CONCEPTO
Concepto	Fuente oficial
Identidad, visión, alcance	Project_Charter.md
Contexto y continuidad	Project_Context.md
Gobierno documental	Project_Governance.md
Autoridad documental	Matriz_Autoridad_Documental.md
Flujo y comportamiento del usuario	Especificacion_funcional.md
Arquitectura	Architecture_Blueprint.md
Modelo empresarial	Modelo_Empresarial_Decision.md
Parámetros	Catalogo_Parametros_MVP.md
Configuración	Centro_Parametrizacion.md
Reglas	Matriz_Reglas_MVP.md
Conflictos	Capa_resolucion_conflictos.md
Índice físico	mapa maestro consolidado
56. REGLA DE AUTORIDAD DOCUMENTAL

Cuando dos documentos entren en contradicción:

No asumir automáticamente cuál es correcto.
Identificar el concepto en conflicto.
Consultar la autoridad documental establecida.
Registrar la contradicción.
Resolverla mediante decisión explícita.
Actualizar los documentos afectados.
Registrar el cambio en el historial del proyecto.

El MMP-EIOS no debe convertirse en una segunda fuente contradictoria.

Su función es mantener la continuidad y señalar cuál es la fuente especializada.

57. CONTROL DE CAMBIOS

Las modificaciones estructurales deben documentarse.

Cada cambio relevante debe registrar:

fecha;
documento afectado;
decisión;
motivo;
impacto;
responsable.

No se deben realizar cambios estructurales importantes sin comprobar sus dependencias.

58. EVM — GESTIÓN DEL VALOR GANADO

El proyecto utiliza EVM (Earned Value Management) aplicado exclusivamente a:

horas;
esfuerzo;
avance físico;
hitos temporales.

No se utilizarán valores monetarios para evaluar el avance del proyecto mediante EVM.

Indicadores principales:

PV — Valor Planificado

Horas de trabajo que deberían haberse completado según el calendario.

EV — Valor Ganado

Horas presupuestadas equivalentes al trabajo realmente completado.

AC — Coste Real / Horas Reales

Horas efectivamente trabajadas.

SPI — Schedule Performance Index

Mide el ritmo de avance respecto al plan.

SPI = EV / PV
CPI — Cost Performance Index aplicado a horas

Mide la eficiencia del trabajo realizado respecto a las horas reales invertidas.

CPI = EV / AC
SV — Schedule Variance
SV = EV - PV

Interpretación:

SPI > 1 → adelanto;
SPI = 1 → según planificación;
SPI < 1 → retraso.
CPI > 1 → eficiencia superior a la prevista;
CPI = 1 → eficiencia prevista;
CPI < 1 → menor eficiencia.
59. ESTADO DEL PROYECTO

El proyecto se encuentra en una fase avanzada de definición conceptual y empresarial.

El trabajo actual se centra principalmente en:

consolidación del MED;
productos comparables;
RFP;
comparabilidad;
histórico;
CEA;
margen;
negociación;
stock;
permanencia en almacén;
liquidez;
fiabilidad de proveedores;
resolución de conflictos;
reglas;
parametrización.

Todavía no debe considerarse cerrado el diseño funcional.

60. PRINCIPALES DECISIONES YA TOMADAS
Producto

EIOS debe poder relacionar productos con denominaciones diferentes.

Comparabilidad

La comparabilidad debe ser porcentual y multidimensional.

Validación

EIOS propone inicialmente y una persona puede validar o modificar.

RFP

Un producto no debe pertenecer automáticamente a múltiples RFP.

Ante duda:

No.

Búsqueda

La búsqueda de un producto debe poder enriquecerse con productos comparables.

Información secundaria

Los comparables deben aportar valor sin saturar al CEO.

Margen

Debe ser visual y prioritario.

CEA

Debe recalcularse dinámicamente durante la negociación.

Rappel

Debe distinguirse del descuento inmediato cuando su liquidación sea posterior.

Negociación

Una oferta desfavorable no debe cerrarse inmediatamente si existe margen de negociación.

Proveedores

Una fiabilidad baja debe activar medidas de mitigación.

Stock

Debe proyectarse temporalmente.

Permanencia

Debe poder parametrizarse el tiempo máximo de permanencia de un producto en almacén.

Liquidez

Es una variable crítica y puede condicionar la compra aunque el precio sea excelente.

Coste de oportunidad

Debe incorporarse al análisis.

61. PRINCIPIOS QUE NO DEBEN PERDERSE
1. No comprar únicamente por precio.
2. No utilizar el precio medio histórico de forma automática.
3. No tratar productos diferentes como idénticos.
4. No confundir comparabilidad funcional con sustituibilidad comercial.
5. No ocultar el margen.
6. No ignorar la liquidez.
7. No ignorar el tiempo.
8. No ignorar el stock futuro.
9. No ignorar el coste de oportunidad.
10. No resolver conflictos mediante una simple suma de reglas.
11. No presentar falsa precisión cuando los datos sean insuficientes.
12. No saturar al CEO con información innecesaria.
13. Toda decisión importante debe ser explicable.
62. ÁREAS PENDIENTES

Quedan pendientes, entre otras:

jerarquía definitiva de reglas;
prioridad entre reglas;
modelo definitivo de excepciones;
salvaguardas no anulables;
metodología exacta del PMR;
metodología definitiva del CEA;
ponderación temporal;
metodología de comparabilidad;
definición formal de RFP;
cálculo de rotación;
cálculo de cobertura;
proyección de stock;
cálculo de permanencia;
impacto financiero proyectado;
niveles de fiabilidad;
parámetros iniciales;
diseño definitivo del Centro de Parametrización;
arquitectura técnica definitiva;
modelo de datos;
implementación;
pruebas.
63. ORDEN DE TRABAJO RECOMENDADO

El proyecto debe avanzar siguiendo una lógica de dependencia.

MODELO EMPRESARIAL
        ↓
PRODUCTOS / RFP / COMPARABILIDAD
        ↓
REGLAS
        ↓
CONFLICTOS
        ↓
PARAMETRIZACIÓN
        ↓
MODELO DE DATOS
        ↓
ARQUITECTURA
        ↓
APLICACIÓN
        ↓
DESARROLLO
        ↓
PRUEBAS
        ↓
VALIDACIÓN EMPRESARIAL

No debe adelantarse el desarrollo técnico si todavía existen contradicciones estructurales en el modelo empresarial.

64. ESTADO DE TRABAJO ACTUAL
Fase actual

Modelo Empresarial de Decisión.

Trabajo inmediato

Consolidar y cerrar las reglas empresariales derivadas de los casos reales trabajados durante las iteraciones.

Especial atención a:

conflicto entre precio y margen;
conflicto entre precio y liquidez;
exceso de stock;
pedidos confirmados;
coste de oportunidad;
productos comparables;
permanencia máxima en almacén;
fiabilidad del proveedor;
condiciones de negociación;
recalculo del CEA.
65. SIGUIENTE PASO

Antes de pasar a la siguiente fase se debe comprobar:

coherencia entre MED y Matriz de Reglas;
coherencia entre MED y CRC;
coherencia entre Catálogo y Centro de Parametrización;
coherencia de los resultados;
coherencia de los identificadores;
coherencia de RFP y comparabilidad;
coherencia de CEA;
coherencia de margen;
coherencia de stock;
coherencia de liquidez;
coherencia de fiabilidad;
ausencia de contradicciones documentales relevantes.

Una vez completado este control podrá declararse cerrado el bloque empresarial correspondiente.

66. PROTOCOLO DE CONTINUIDAD PARA LA IA

Cuando una nueva IA o una nueva sesión continúe el proyecto:

Leer este MMP-EIOS.
Leer Project_Charter.md.
Leer Project_Context.md.
Leer Project_Governance.md.
Leer Matriz_Autoridad_Documental.md.
Identificar la fase actual.
Leer los documentos especializados relacionados con dicha fase.
No inventar decisiones que no estén documentadas.
Diferenciar claramente:
aprobado;
en desarrollo;
pendiente;
descartado.
Continuar desde el último estado documentado.

La IA debe utilizar el MMP-EIOS como documento de recuperación de contexto, pero debe consultar siempre las fuentes especializadas antes de modificar una decisión empresarial.

67. REGLA FUNDAMENTAL DE CONTINUIDAD

Si existe discrepancia entre la memoria de una conversación y los documentos versionados del repositorio:

Los documentos versionados constituyen la fuente de verdad del proyecto.

La conversación sirve para descubrir, discutir y validar decisiones.

La decisión consolidada debe terminar registrada en los documentos oficiales.

68. PRINCIPIO FINAL

EIOS debe evolucionar desde:

una idea de aplicación para decidir compras

hacia:

un sistema empresarial de apoyo a la decisión capaz de interpretar datos, contexto, riesgos, alternativas y consecuencias para ayudar al CEO a tomar mejores decisiones.

La calidad de EIOS dependerá menos de la cantidad de datos que de su capacidad para:

relacionarlos;
contextualizarlos;
compararlos;
ponderarlos;
detectar conflictos;
explicar sus consecuencias;
proponer alternativas;
y mantener trazabilidad.
