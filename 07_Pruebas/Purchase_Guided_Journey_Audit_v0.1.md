# Auditoría del recorrido guiado de compra

Fecha: 06/11/2026. Cambio: EIOS-CHG-004.

## Comprobaciones ejecutadas

71 casos unittest pasan en los módulos de pantalla de compra, síntesis,
revisión de stock, escenario de stock, separación de empresas, copia a borrador,
acuerdos, previsión financiera, negociación, cuotas e informe de propuesta.

Los recorridos de Chromium se ejecutan con bases de datos temporales y datos
ficticios. La nueva guía no se prueba sobre la base de trabajo del usuario.

| Recorrido | Evidencia comprobada |
| --- | --- |
| purchase_guide.cjs | Seis pasos; volver conserva campos y valores; error global abre el paso y enfoca; resultados guardados separados; acuerdo fuera del formulario; 1536/900/390 px y ambos temas sin desbordamiento de página; otras vistas sin cambios de contenido |
| purchase_study_to_draft.cjs | Copia real, nueva confirmación de stock, alternativa aplicada, recálculo, cuotas, guardado con procedencia y original intacto |
| purchase_agreement.cjs | Declaración y retirada, historial imprimible, sin modificar compra ni previsión |
| purchase_visual_clarity.cjs | Estado y síntesis guardados juntos en el paso 5, detalles plegables, invalidación al volver a editar |
| purchase_appearance.cjs | Fuentes locales cargadas sin peticiones externas; tarjetas y riesgos; tema persistido |
| purchase_typography.cjs | Filas comerciales e impuestos alineados; importes exactos y precisión del precio unitario |
| purchase_installments.cjs | Reparto por número/importe, redondeo final, suma por concepto y conservación del calendario ante entradas inválidas |
| purchase_stock_scenario.cjs | Captura y aplicación de hipótesis; conservación al guardar; invalidación al cambiar fecha |
| purchase_combinations.cjs | Combinación que resuelve el caso, sensibilidad conservada, informe y recálculo al aplicar |
| purchase_context_audit.cjs | Respuestas tardías y ambas pausas de hidratación no sustituyen otro contexto |

## Correcciones surgidas durante la revisión

- Se cambia la navegación interna hacia la guía conservando los enlaces que usan
  las acciones existentes; no se borra una dependencia sin sustituirla.
- Se ocultan los campos editables de guardado al consultar resultados históricos.
- Los acuerdos quedan fuera del formulario y se elimina su interfaz anterior al
  cambiar de estudio, conservando el historial persistido.
- Las etiquetas auxiliares de accesibilidad de la tabla tenían posicionamiento
  absoluto fuera de su contenedor. Se establece el contenedor de posicionamiento
  en la caja de desplazamiento; desaparece el desbordamiento móvil sin eliminar
  etiquetas ni columnas.
- Los errores se explican en español y se retiran cuando el dato ya es válido,
  también cuando lo rellena una copia a borrador.
- Los enlaces a fuentes abren el paso que ahora contiene sus datos. Las acciones
  de cambios desde un estudio dirigen a la creación explícita de borrador.

## Límites de esta auditoría

Las pruebas automatizadas y las capturas verifican comportamientos concretos.
No certifican por sí solas toda la accesibilidad ni la comprensión de un usuario
nuevo. Sigue pendiente observar a una persona sin experiencia preparando una
compra e interpretando sus resultados sin ayuda.

La CI completa se consulta en GitHub para el commit publicado; su resultado no
se presupone a partir de estas pruebas locales. Main permanece sin cambios.
