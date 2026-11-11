# Cinta Datos de la compra: referencia visual

Fecha: 06/11/2026. Cambio: EIOS-CHG-007.

El usuario solicita adaptar la cinta a `cinta_datos_compra.png`. Se reorganiza
el componente compartido por borrador y estudio guardado, sin cambiar sus
fuentes ni cálculos.

- Cabecera con icono, título, empresa, archivo y corte documental.
- Identidad con proveedor y artículo, incluyendo el SKU como distintivo.
- Seis métricas conservadas: cantidad, disponible, reservadas, referencia de
  precio, descuento del libro y cobertura estimada. El precio se destaca en un
  panel azul con símbolo EUR y la indicación Neto sin IVA.
- Pie con estado neutral, fechas y explicación del disponible; mantiene el
  botón de acceso a stock, demanda y fuentes.
- Los marcadores FICTICIA/FICTICIO/ARTÍCULO FICTICIO proceden exclusivamente de
  los sufijos explícitos de los nombres. Su presentación como distintivos no
  cambia el registro ni acredita su procedencia. El nombre original permanece
  como etiqueta accesible.
- Se mantiene la condición existente para mostrar cobertura finita: cálculo
  disponible, fecha y unidad compatibles con el inventario. No se deduce demanda
  de existencias ni se sustituyen datos ausentes por cero.
- Los datos históricos se toman del estudio guardado; no se completan con los
  nombres, precios o fuentes actuales de la empresa.

El aviso empresarial que repetía los mismos datos se conserva en el DOM para
sus actualizaciones, pero se oculta visualmente porque la cabecera de la cinta
ya muestra empresa, archivo y corte. Las fuentes ampliadas siguen accesibles.

La cinta permanece fija al desplazarse. En pantallas de 900 px o menos sus
métricas se despliegan mediante un control de teclado y ratón para dejar espacio
al formulario. Se ajusta la separación de las secciones a la altura real de la
cinta. El observador se retira de la cinta histórica al reemplazarla.

El CSS nuevo se limita a Propuestas de compra. Se conservan las fuentes locales,
el modo oscuro, los importes y los estados del proceso. No se alteran APIs,
reglas, documentos guardados ni autoridad decisional.

Verificación: `purchase_ribbon.cjs` comprueba composición, seis métricas,
distintivos explícitos, valor cero, cobertura finita, claro/oscuro, despliegue
adaptable y aislamiento de los datos guardados frente a cambios del catálogo.
También pasan los recorridos de guía, consulta histórica y copia a borrador.
Se inspeccionan capturas reales del componente en ambos temas.
