# Desglose de stock junto a la negociación

La cabecera de negociación conserva dos columnas de referencia de 180 px.
Del ancho restante, cada propuesta recibe el 40 % y el desglose recibe el 20 %.
Esto reduce aproximadamente un 20 % cada propuesta respecto del reparto previo
por mitades, conservando los márgenes y bordes de los controles existentes.

El panel de consulta reproduce el primer cuadro de De dónde salen los números
del paso Revisar la necesidad. Mantiene cuatro fases, letras A–L, fórmulas,
unidades, fechas y el resultado calculado. Los textos se centran y sus cifras
aparecen debajo; los títulos largos se abrevian manteniendo el título completo
como descripción accesible y ayuda al pasar el cursor.

No solicita otra simulación ni implementa fórmulas paralelas. Observa la salida
existente, incluida su invalidación cuando faltan datos o confirmación. Excluye
los controles de edición, el botón de adoptar cantidad y la tabla comparativa
inferior. Los estudios guardados siguen ocultando el formulario de edición.

En pantallas de 1200 px o menos se presenta bajo el bloque principal para evitar
un panel ilegible. La tabla conserva su desplazamiento horizontal. Las pruebas
verifican proporción, posición derecha, fases, letras, ausencia de controles e
identificadores duplicados, valor del escenario, invalidación y modo oscuro móvil.
