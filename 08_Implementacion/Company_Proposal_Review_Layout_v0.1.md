# Revisión visual de propuestas

La revisión mantiene el encabezado ámbar de evaluación completa pendiente y el motivo. El contenido se divide en tarjetas: importes, comparación de precio, stock/cobertura, mínimo al guardar y tesorería pendiente. Las tarjetas se distribuyen en dos columnas o una en pantalla estrecha.

Los importes de mercancía neta, IVA, total y vencimiento se muestran con etiquetas y cifras independientes; se añade descuento y desglose de portes cuando consta. El total de operación tiene un bloque destacado. Si no está disponible, se identifica PENDIENTE y se explica que faltan portes; no se presenta el total de mercancía como total completo. Fechas de vencimiento e inventario en DD/MM/AAAA.

La comparación muestra última compra, precio propuesto, diferencia por unidad y variación porcentual por separado. Ninguna variación recibe un color que implique aprobación. Los avisos de ausencia se distinguen mediante fondo ámbar, texto y borde. La tesorería conserva su mensaje de evaluación no realizada. Mínimos antiguos ausentes no se reconstruyen. La referencia del mínimo guardado permanece congelada.

Comprobaciones pendientes y trazabilidad siguen siendo desplegables. La huella de revisión permite saltos para evitar desbordamiento. No se cambia ningún cálculo, regla, estado, persistencia o autoridad del sistema.

Verificación: pruebas existentes de revisión y propuestas; recorrido DOM/HTTP sobre copia desechable con importes de mercancía y portes, vencimiento independiente, cinco tarjetas, cambio de mínimos conservando referencia antigua, y presentación de propuesta anterior sin portes ni mínimo conservado.
