# EIOS — STK-M10 · Autoridad metodológica de contradicciones

**Versión:** 1.0
**Estado:** APROBADO — STK-M10 CERRADO
**Fecha de decisión:** 11/09/2026
**Autoridad:** decisión humana expresa incorporada al gobierno metodológico STK

## 1. Decisión autorizada

STK-M10 representa la existencia de dos o más datos o evidencias suficientemente identificados que, referidos al mismo artículo, variable, ámbito y momento temporal comparable, ofrecen valores o estados materialmente incompatibles y no pueden considerarse simultáneamente ciertos.

Una diferencia entre fuentes no constituye automáticamente una contradicción.

## 2. Comprobación de comparabilidad

Antes de declarar una contradicción, EIOS comprueba:

- identidad del artículo;
- variable representada;
- unidad de medida;
- normalización aplicada;
- fecha de referencia y comparabilidad temporal;
- ámbito operativo;
- versión del dato;
- contexto y estado de cada fuente.

No son contradicción los valores que puedan explicarse legítimamente por diferencias temporales, unidades convertibles mediante una conversión autorizada, ámbitos distintos o versiones sucesivas correctamente trazadas. Esos valores permanecen separados conforme a su contexto.

## 3. Detección y preservación

Cuando exista una contradicción real, EIOS:

- conserva todas las evidencias implicadas sin sobrescribir ninguna;
- identifica fuentes, valores o estados, fechas, versiones y alcance de la discrepancia;
- identifica el artículo, variable, ámbito y momento comparable;
- registra los módulos y evaluaciones afectados;
- clasifica el resultado como `CONFLICTING_DATA / UNRESOLVED_CONTRADICTION` mientras no pueda determinarse legítimamente un valor autorizado.

La contradicción detectada forma parte de la trazabilidad incluso cuando posteriormente sea resuelta.

## 4. Prohibición de resolución implícita

EIOS no selecciona automáticamente el valor más reciente, mayor, menor o aparentemente más probable. Tampoco resuelve contradicciones mediante promedio, score, prioridad arbitraria ni otra heurística implícita.

Una regla de precedencia solo puede aplicarse cuando exista una política de autoridad documental previamente autorizada, aplicable al concepto y contexto evaluados.

STK-M10 no corrige silenciosamente los datos ni decide qué fuente tiene razón por inferencia.

## 5. Propagación

Si la contradicción afecta materialmente al resultado de STK-M01–STK-M08 o a cualquier evaluación posterior, EIOS propaga la incertidumbre y bloquea la conclusión que dependa de ese dato, evitando producir una certeza artificial.

Una conclusión independiente que no dependa del dato contradictorio puede conservarse, pero no resuelve ni oculta la contradicción.

## 6. Resolución autorizada

Cuando exista una regla de autoridad suficiente, EIOS puede utilizar el valor autorizado para el cálculo correspondiente. Debe conservar:

- la contradicción detectada;
- todas las evidencias implicadas;
- la evidencia no utilizada para ese cálculo;
- la regla o política de autoridad aplicada;
- la justificación de la resolución;
- la versión y fecha efectiva;
- la evaluación resultante.

La resolución queda trazable, versionada y vinculada a la evidencia y autoridad que la sustenta. Si requiere interpretación empresarial no contemplada por una regla vigente, se escala a autoridad humana.

Una resolución posterior genera una nueva versión y no reescribe retroactivamente la contradicción ni la evaluación anterior.

## 7. Fronteras de autoridad

STK-M10 gobierna contradicciones entre datos y evidencias de stock y demanda.

Los conflictos entre resultados de reglas, evaluaciones, bloqueos, excepciones o condiciones pertenecen exclusivamente a la Capa de Resolución de Conflictos.

Las contradicciones entre documentos se resuelven conforme a la Matriz de Autoridad Documental. STK-M10 no crea una autoridad documental paralela.

## 8. Relación con STK-M09

`contradiction ≠ missing_data`.

En STK-M09 falta evidencia suficiente para determinar el dato. En STK-M10 existen dos o más datos o evidencias suficientemente identificados, pero son materialmente incompatibles dentro de un contexto comparable.

La presencia de una contradicción no autoriza a reclasificar silenciosamente las evidencias como ausentes ni a escoger una de ellas sin autoridad.

## 9. Autoridad decisional

STK-M10 detecta, caracteriza, preserva y, cuando existe autoridad suficiente, permite resolver trazablemente contradicciones.

Puede generar alertas de contradicción o calidad, pero no constituye una decisión de compra, reposición, exceso, rotura de stock ni otra acción empresarial automática. La autoridad decisional final permanece en la persona autorizada.

## 10. Continuidad

`STK-M01…M10` quedan metodológicamente cerrados. Este cierre no constituye por sí mismo un contrato técnico ni autoriza la implementación cuantitativa: la entrada a esas fases requiere una auditoría separada de todos los criterios establecidos en la matriz.
