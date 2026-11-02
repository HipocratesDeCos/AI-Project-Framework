# Comparación de compras — revisión visual y funcional v0.1

Fecha: 02/11/2026. PR #570. Base: d2e49c83155bdc35799331de32eab32849bb59ec.

## Método

Aplicación HTTP local real, Chromium sin interfaz y Playwright. Base de datos temporal derivada de las fixtures sintéticas de FinanceActivationTest/PurchaseComparisonTest; no datos empresariales reales. Inspección de capturas de la sección y comprobaciones de interacción en ventanas de 1440 × 1000 y 760 × 1000 píxeles. La revisión no acredita todos los navegadores ni todos los tamaños.

## Defectos encontrados y corregidos

1. renderSavedMinimum utilizaba m.source en lugar de minimum.source en la rama de origen del archivo. La variable no existía y podía interrumpir la revisión de propuestas. Se corrige la referencia.
2. La tabla de siete columnas quedaba recortada en una ventana estrecha por el contenedor exterior. Se añade región desplazable horizontalmente, accesible mediante teclado y con indicación visible. No se cambia la anchura global de la aplicación.
3. Las condiciones mostraban claves internas como unit_price. Se traducen a etiquetas de negocio.
4. Fecha con microsegundos y zona UTC sin formato de presentación. Se muestra fecha y hora en castellano y Europe/Madrid.
5. Casilla de cuotas centrada y separada de su texto; editor sin etiquetas visibles. Se alinean casilla y texto y se etiquetan los controles de cada cuota.
6. Un error de entrada borraba el resultado previo de la pantalla. Se conserva y se presenta el error en una zona de estado independiente.

## Comprobaciones realizadas

| Prueba | Resultado |
|---|---|
| Abrir revisión de propuesta sin mínimo configurado | Correcto, sin excepción JavaScript |
| Precio 100 → 95; dos unidades, IVA 21 % | Total 242,00 → 229,90 EUR; diferencia 12,10 EUR; comparación disponible sin déficit |
| Oferta documentada sin referencia | Rechazada; estudio previo permanece visible |
| Precio antes de descuentos 100 y descuento 3 % | Total 234,74 EUR, sin doble descuento |
| Vencimiento fuera del horizonte | Alternativa pendiente, sin presentarla favorable |
| Dos cuotas de 121 EUR, 20/10 y 01/11 | Total y calendario conservados |
| Reabrir propuesta | Recupera los estudios persistidos |
| Ventana de 760 píxeles | Tabla desplazable; sin desbordamiento horizontal exterior |
| Excepciones JavaScript durante el flujo | Ninguna |

El formulario de compra vacío genera una respuesta de validación HTTP 400 del cálculo previo existente; no se confunde con una excepción JavaScript ni con un fallo del nuevo guardado.

## Dictamen

APTO en las dimensiones y flujos comprobados tras estas correcciones. Se mantiene el alcance sintético, sin aceptación verificada ni autoridad operacional. La revisión visual no sustituye CI. Este ajuste requiere comprobar la nueva ejecución de GitHub antes de integrar.
