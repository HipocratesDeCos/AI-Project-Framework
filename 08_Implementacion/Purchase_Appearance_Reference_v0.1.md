# Apariencia y comparación según referencia · v0.1

## Cambios solicitados

- La diferencia de Respuesta del proveedor usa Oferta original como base, igual que Mi propuesta. No depende del importe o activación de Mi propuesta. Sin una referencia original calculable queda pendiente.
- Modo claro/oscuro mediante botón de la barra superior. La preferencia se conserva localmente en el navegador; si no hay elección, sigue la preferencia del sistema. No depende de empresa o base de datos ni modifica estudios.
- Comparación con cabecera, banda oscura de referencia, tarjetas identificadas, bloque de total, diferencia, liquidez del escenario y prueba sin el mayor cobro. Mantiene detalle y fuentes desplegables. Cantidades distintas se identifican como desembolso no comparable a un ahorro sobre el mismo volumen.
- Bricolage Grotesque para títulos e importes grandes; IBM Plex Sans para texto y controles. Cifras tabulares. Se aplica también a la negociación y a los informes HTML.

## Fuentes locales

`eios/company_font_assets.py` incluye las fuentes y sus licencias OFL, con las huellas de los originales descargados de `google/fonts`:

- https://github.com/google/fonts/tree/main/ofl/bricolagegrotesque
- https://github.com/google/fonts/tree/main/ofl/ibmplexsans

Bricolage se incorpora como WOFF latino con ancho 100 y tamaño óptico 14; conserva peso variable. IBM Plex Sans se incorpora como TTF variable original sin modificar (Reserved Font Name Plex). Se incluyen caracteres españoles y euro. Los datos de fuentes y licencias se insertan en CSS autocontenido, por lo que la aplicación y los informes no consultan servidores de fuentes ni requieren instalación por parte del usuario. FontTools se utilizó en preparación; no es una dependencia nueva de EIOS.

La elección anterior de Segoe UI queda sustituida por la especificación explícita de estas dos familias. Segoe UI/system-ui permanecen como alternativas de respaldo.

## Diseño y alcance

Las tarjetas se adaptan al ancho: tres columnas cuando caben y menos en pantallas pequeñas. Los importes y diferencias siguen procediendo del estudio calculado. La prueba de tensión se muestra como hipótesis, sin convertirla en predicción de impago ni modificar movimientos. Se conservan criterios de comparación parcial a igual cantidad y límites de búsqueda.

El tema oscuro adapta fondos, textos, bordes, controles, estados, tablas, cintas, matriz y gráfico. Mantiene etiquetas además del color. Los informes imprimibles conservan un fondo claro y tipografía local para legibilidad al imprimir. No hay cambios de persistencia, pagos, acuerdos ni autoridad.

## Comprobaciones

Chromium: fuentes reales cargadas sin peticiones externas; familias efectivas de títulos/importes/texto; contenido y riesgo de las tres tarjetas; tema oscuro y persistencia tras recargar; propuestas intactas. Diferencias positivas, negativas y neutras frente a la original, independencia de Mi propuesta y falta de IVA original. Rejilla de negociación alineada, porcentajes editables y tamaños reducidos. Regresión de copia a borrador, aplicación y guardado. Pruebas Python de importes, negociación e informes.
