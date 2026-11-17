# Paso 2: negociación y análisis alineados

La negociación del borrador ocupa todo el ancho del espacio de trabajo. Las
columnas Condiciones y Oferta original tienen 180 px cada una; Mi propuesta y
Propuesta del proveedor reparten el espacio restante por igual.

Bajo la tabla, el contexto de análisis ocupa el ancho conjunto de las dos
primeras columnas. Las tarjetas de comparación se alinean con su columna de
propuesta. Se reutilizan los mismos nodos, cálculos y acciones; no se clonan
formularios ni se mezclan las dos opciones.

Al cambiar de paso, el contexto vuelve a su posición habitual. Al consultar un
estudio guardado, las opciones conservan su ubicación en el estudio. En pantallas
estrechas, los recuadros se apilan para mantener la legibilidad; la tabla conserva
su desplazamiento horizontal.

La prueba de navegador verifica anchuras, alineación, restauración al navegar,
consulta de estudio y retorno al borrador, modo oscuro y ausencia de desbordamiento
en móvil. La regresión de opciones comprueba selección, cuotas independientes y
conservación de los estudios y sus informes.

## Ajuste de ubicación

Las tarjetas de las dos propuestas comienzan a la misma altura que el recuadro
izquierdo; la explicación común se presenta debajo de las tarjetas. Comparar
alternativas ocupa ahora el recuadro izquierdo. La evaluación con gráfica pasa a
la ubicación anterior de las alternativas, dentro del detalle de análisis. El
intercambio se limita al paso de negociación del borrador y se restaura al salir;
los estudios guardados siguen utilizando sus ubicaciones históricas de consulta.
