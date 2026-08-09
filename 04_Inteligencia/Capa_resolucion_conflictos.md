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
4. Responsabilidades

La CRC debe:

Recibir los resultados de las reglas.
Comprobar la fiabilidad de los datos utilizados.
Identificar reglas críticas.
Identificar bloqueos.
Evaluar excepciones.
Determinar si una situación desfavorable puede resolverse mediante una condición.
Resolver conflictos entre reglas.
Comparar escenarios cuando sea necesario.
Determinar la decisión final.
Identificar el motivo dominante.
Identificar los factores relevantes.
Generar una explicación comprensible.
Mantener trazabilidad hacia reglas, parámetros y datos.
Evitar la saturación de información al usuario.
5. Principio de no compensación automática

EIOS no debe utilizar un sistema simple de puntuación en el que factores positivos compensen automáticamente factores negativos.

Ejemplo:

Precio                    FAVORABLE
Proveedor                 FAVORABLE
Margen                    FAVORABLE
Stock                     DESFAVORABLE
Tesorería                 CRÍTICA

La existencia de tres factores favorables no permite compensar automáticamente una situación financiera crítica.

Las reglas críticas deben prevalecer según la jerarquía establecida.

6. Niveles de efecto de una regla

Cada regla deberá clasificarse según el efecto que puede producir.

Nivel	Tipo	Efecto
R0	BLOQUEO	Puede impedir la compra
R1	CONDICIONANTE	Puede convertir la operación en COMPRAR CONDICIONADO
R2	NEGOCIACIÓN	Recomienda negociar
R3	INFORMATIVA	Aporta contexto sin modificar necesariamente la decisión
7. Severidad

Cada resultado de una regla deberá incorporar un nivel de severidad.

Severidad	Significado
CRÍTICA	Puede comprometer la viabilidad de la operación
ALTA	Puede generar un perjuicio importante
MEDIA	Situación desfavorable que requiere atención
BAJA	Desviación menor
INFORMATIVA	Información contextual

La severidad y el efecto de la regla son conceptos diferentes.

Ejemplo:

Una regla puede ser de tipo NEGOCIACIÓN y tener severidad ALTA.

8. Jerarquía de resolución

La CRC utilizará una jerarquía conceptual:

Salvaguardas críticas.
Bloqueos.
Condiciones solucionables.
Reglas de negociación.
Reglas informativas.

Esta jerarquía no sustituye a los parámetros configurables.

Determina cómo debe resolverse el conflicto cuando varias reglas actúan simultáneamente.

9. Decisiones oficiales

EIOS tendrá cinco resultados posibles:

🟢 COMPRAR

La operación cumple los criterios establecidos y no existe una condición crítica que impida realizarla.

🟡 NEGOCIAR

La operación puede ser viable, pero existen condiciones comerciales que justifican intentar mejorar la operación.

🔵 COMPRAR CONDICIONADO

La operación presenta una o varias condiciones desfavorables, pero existe una modificación concreta que permitiría hacerla viable.

🔴 NO COMPRAR

La operación no resulta viable o compromete una condición crítica que no puede solucionarse mediante las alternativas disponibles.

⚪ INFORMACIÓN INSUFICIENTE

La información disponible no permite realizar una recomendación fiable.

10. Motivo dominante

Toda decisión deberá tener un único motivo dominante.

El motivo dominante es el factor que ha tenido mayor influencia en la decisión final.

Ejemplo:

NO COMPRAR

Motivo dominante: la operación compromete la capacidad prevista de atender los pagos dentro del horizonte configurado.

El motivo dominante debe ser breve, concreto y comprensible para un usuario no financiero.

11. Factores relevantes

El motivo dominante no debe ocultar información complementaria de valor.

Los factores relevantes son circunstancias adicionales que ayudan al CEO o responsable de compras a comprender la situación y disponer de argumentos para negociar.

Ejemplo:

NEGOCIAR

Motivo dominante: precio superior a la referencia configurable.

Factores relevantes:

Precio propuesto: 18,20 €.
Precio de referencia: 17,10 €.
Diferencia: +6,43 %.
Última compra comparable: 17,40 € hace 2 meses.
Stock actual: 420 unidades.
Cobertura estimada: 74 días.
Existe proveedor alternativo.
Plazo de pago propuesto: 30 días.

Los factores relevantes no deben modificar por sí mismos la decisión salvo que una regla específica así lo determine.

Su función principal es proporcionar:

contexto;
argumentos;
transparencia;
capacidad de negociación;
comprensión de la decisión.
12. Principio de información útil

EIOS debe diferenciar entre:

Información necesaria para decidir

y

Información útil para actuar.

El CEO no debe recibir toda la información disponible.

Debe recibir primero:

Decisión.
Motivo dominante.
Factores relevantes.
Condición recomendada, si existe.
Acceso al detalle cuando sea necesario.
13. Excepciones

Las excepciones permiten que una circunstancia desfavorable no produzca automáticamente una decisión negativa cuando existe una justificación empresarial válida.

Ejemplo:

Regla:
Exceso de stock

Excepción:
Existe pedido confirmado de cliente

Resultado:
La regla de exceso de stock no bloquea la operación.

Las excepciones deberán estar definidas y parametrizadas.

No se permitirá que una excepción se aplique de forma implícita o arbitraria.

14. Salvaguardas no anulables

No todas las reglas deben poder ser anuladas mediante una excepción.

Las salvaguardas destinadas a proteger la estabilidad financiera y la integridad de la decisión deberán tener un nivel de protección superior.

Ejemplos potenciales:

imposibilidad de atender obligaciones financieras;
ausencia de información crítica;
datos incompatibles o inválidos;
errores graves en los datos de entrada.

La lista definitiva de salvaguardas no anulables deberá aprobarse antes de la implementación.

15. Compra condicionada

COMPRAR CONDICIONADO debe utilizarse cuando exista una condición concreta capaz de transformar una operación desfavorable en una operación viable.

Ejemplos:

Caso 1 — Precio

Precio propuesto: 18,50 €

Precio máximo recomendado: 17,80 €

Condición:

Comprar únicamente si el proveedor acepta ≤17,80 €.

Caso 2 — Plazo de pago

Situación:

El pago a 30 días genera tensión financiera.

Condición:

Ampliar el plazo a 90 días.

Caso 3 — Cantidad

Situación:

La cantidad propuesta genera exceso de stock.

Condición:

Reducir la compra de 1.000 a 400 unidades.

16. Principio de mínima intervención

Cuando una operación presenta un problema, EIOS debe buscar la solución menos restrictiva que mantenga la seguridad económica de la empresa.

Orden conceptual:

INFORMAR
   ↓
NEGOCIAR
   ↓
CONDICIONAR
   ↓
NO COMPRAR

No se debe recomendar NO COMPRAR cuando existe una alternativa razonable que permite resolver el problema.

Sin embargo, las salvaguardas críticas prevalecen sobre este principio.

17. Riesgo financiero

El riesgo financiero tendrá especial prioridad.

Si una compra compromete la capacidad de la empresa para atender sus pagos, EIOS deberá considerar la operación no viable salvo que exista una condición concreta que permita resolver el riesgo.

Posibles alternativas a evaluar:

ampliación del plazo de pago;
reducción de la cantidad comprada;
reducción del precio;
utilización de stock existente;
recuperación de liquidez mediante productos de baja rotación;
reducción del periodo de cobro;
otras medidas empresariales configuradas.

EIOS podrá proponer alternativas, pero no ejecutará automáticamente decisiones financieras o empresariales.

18. Stock: escenario con y sin compra

La CRC deberá poder evaluar dos escenarios:

ESCENARIO A — No realizar la compra
Stock actual
+ entradas previstas
- salidas previstas
= stock proyectado
ESCENARIO B — Realizar la compra
Stock actual
+ compra propuesta
+ entradas previstas
- salidas previstas
= stock proyectado con compra

La comparación permitirá detectar, entre otras situaciones:

posible rotura de stock;
exceso de stock;
compra innecesaria;
mejora de cobertura;
impacto de la cantidad propuesta.
19. Fecha de referencia

La fecha de propuesta de compra será la fecha principal de referencia para el análisis.

EIOS deberá evitar utilizar información posterior a dicha fecha cuando se realice una evaluación histórica o una simulación de decisión.

Ejemplo:

Fecha de propuesta:
09/08/2026

Datos operativos:
referidos a la fecha de propuesta

Histórico:
información disponible hasta la fecha de propuesta

Proyección:
desde la fecha de propuesta

Fecha prevista de entrega:
25/08/2026

Este principio será especialmente importante para las pruebas retrospectivas.

20. Calidad y fiabilidad de los datos

La CRC deberá considerar la calidad de la información antes de emitir una recomendación.

Niveles:

ALTA
MEDIA
BAJA
INSUFICIENTE

La antigüedad de los datos no debe interpretarse de forma uniforme.

Debe distinguirse entre:

actualidad de datos operativos;
antigüedad de referencias históricas;
antigüedad de precios comparables;
calidad de los registros.
21. Histórico insuficiente

Como criterio inicial:

Compras comparables	Resultado
0	Información insuficiente
1	Fiabilidad baja
2 o más	Puede utilizarse como referencia

Estos valores serán configurables y deberán validarse con datos reales.

22. Precio y referencia histórica

EIOS no deberá considerar automáticamente que un precio histórico antiguo representa un precio actual fiable.

La comparación deberá considerar:

antigüedad;
número de operaciones;
fechas;
condiciones de compra;
proveedor;
cantidad;
descuentos;
rappels;
condiciones de pago;
otros factores relevantes disponibles.

El precio máximo recomendado será objeto de una metodología específica que deberá definirse antes de su implementación.

23. Resolución mediante escenarios

Cuando exista una situación conflictiva, EIOS podrá comparar escenarios.

Ejemplo:

Factor	No comprar	Comprar	Condicionado
Tesorería	🟢	🔴	🟢
Stock	🟢	🔴	🟡
Margen	—	🟢	🟢
Plazo de pago	—	🔴	🟢

Resultado:

COMPRAR CONDICIONADO

Condición:

Obtener un plazo de pago mínimo de 90 días.

Los escenarios deberán utilizarse únicamente cuando aporten valor a la decisión.

24. Trazabilidad

Toda decisión deberá poder rastrearse hasta:

DECISIÓN
   ↓
MOTIVO DOMINANTE
   ↓
REGLA
   ↓
PARÁMETRO
   ↓
INDICADOR
   ↓
DATO DE ORIGEN

Ejemplo:

NO COMPRAR
   ↓
Riesgo financiero crítico
   ↓
FIN-001
   ↓
Tesorería mínima
   ↓
Tesorería proyectada
   ↓
Datos financieros del ERP
25. Explicabilidad

La explicación para el usuario deberá responder:

¿Qué recomienda EIOS?
¿Por qué?
¿Qué factores ha considerado?
¿Existe alguna alternativa?
¿Qué condición permitiría modificar la recomendación?
¿Qué nivel de fiabilidad tienen los datos?
26. Ejemplo de salida para el CEO
🟡 NEGOCIAR
Motivo principal

Precio superior a la referencia configurable.

Factores relevantes
Precio propuesto: 18,20 €.
Precio de referencia: 17,10 €.
Diferencia: +6,43 %.
Última compra comparable: 17,40 €.
Última compra: hace 2 meses.
Stock actual: 420 unidades.
Cobertura estimada: 74 días.
Proveedor alternativo disponible.
Plazo de pago actual: 30 días.
Recomendación de negociación

Precio máximo recomendado: 17,80 €.

Objetivo

Reducir el precio manteniendo un margen operativo adecuado y evitando incrementar innecesariamente el stock.

27. Principio de comunicación ejecutiva

La pantalla principal deberá ser breve.

El sistema no debe mostrar automáticamente todos los cálculos disponibles.

Orden recomendado:

DECISIÓN
   ↓
MOTIVO DOMINANTE
   ↓
FACTORES RELEVANTES
   ↓
RECOMENDACIÓN / CONDICIÓN
   ↓
DETALLE

El detalle completo deberá estar disponible bajo demanda.

28. Registro interno de resolución

Aunque el usuario vea una respuesta resumida, EIOS deberá conservar internamente:

reglas activadas;
reglas no activadas;
parámetros utilizados;
valores utilizados;
severidad;
prioridad;
excepciones;
condiciones evaluadas;
escenarios;
calidad de datos;
motivo dominante;
factores relevantes;
decisión final.

Esto permitirá auditoría, pruebas y mejora futura.

29. Principio de no automatización de decisiones empresariales externas

EIOS puede:

analizar;
calcular;
recomendar;
comparar;
alertar;
proponer condiciones de negociación.

EIOS no debe ejecutar automáticamente:

ampliaciones de capital;
ventas de inmovilizado;
cambios de política de cobro;
ofertas comerciales;
compras;
negociaciones con proveedores;

salvo que una futura versión incorpore explícitamente esas capacidades y exista autorización empresarial.

30. Relación con otros documentos

La CRC depende conceptualmente de:

Modelo_Empresarial_Decision.md

Define qué debe decidir EIOS.

Catalogo_Parametros_MVP.md

Define los parámetros configurables.

Centro_Parametrizacion.md

Define cómo se administran los parámetros.

Matriz_Reglas_MVP.md

Define las reglas que generan resultados.

La CRC determina cómo se combinan esos resultados para producir una decisión.

31. Regla de coherencia documental

Ninguno de los documentos anteriores deberá definir una jerarquía de decisión contradictoria con esta capa.

Cuando exista una modificación en:

prioridades;
severidades;
bloqueos;
excepciones;
resultados;
condiciones;

deberá revisarse la coherencia entre todos los documentos relacionados.

32. Estado MVP

La siguiente definición queda establecida como base conceptual del MVP:

Resultados
COMPRAR
NEGOCIAR
COMPRAR CONDICIONADO
NO COMPRAR
INFORMACIÓN INSUFICIENTE
Componentes de resolución
efecto de la regla;
severidad;
prioridad;
bloqueos;
excepciones;
condiciones;
calidad de datos;
escenarios;
motivo dominante;
factores relevantes;
trazabilidad.
Principios
No compensación automática.
Salvaguarda financiera.
Mínima intervención.
No saturación informativa.
Explicabilidad.
Trazabilidad.
Configuración humana.
Adaptabilidad empresarial.
33. Elementos pendientes de definición

Quedan deliberadamente pendientes:

Fórmula definitiva del precio máximo recomendado.
Jerarquía numérica definitiva de prioridades.
Lista definitiva de salvaguardas no anulables.
Catálogo definitivo de excepciones.
Metodología de cálculo de fiabilidad.
Fórmula definitiva de proyección de stock.
Método definitivo para calcular el impacto financiero de una compra.
Reglas específicas por familia o artículo.
Diseño visual definitivo del Centro de Parametrización.
Implementación técnica de la CRC.

Estos elementos no deben inventarse prematuramente.

Deberán definirse mediante casos reales y validación empresarial.

34. Principio rector

EIOS no debe limitarse a responder "¿compro o no compro?".

Debe ayudar a responder:

"¿Qué tendría que cambiar para que esta compra fuese económicamente segura y razonable para la empresa?"

Y cuando no exista una solución viable:

"No comprar."
