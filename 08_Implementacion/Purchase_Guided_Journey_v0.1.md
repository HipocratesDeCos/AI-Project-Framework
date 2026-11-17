# Propuesta de compra: recorrido guiado v0.2

Fecha: 06/11/2026. Cambio: **EIOS-CHG-004**.

Actualización **EIOS-CHG-005**, autorizada por el usuario: los pasos 1 a 4
también se pueden consultar en un estudio guardado. Se elimina la redirección
silenciosa al paso 5. Cada paso presenta una lectura de sus capturas históricas,
sin rellenar, clonar ni deshabilitar los controles del borrador independiente.
Se ofrecen las acciones explícitas de crear copia y volver al formulario.
Los campos no capturados se identifican como no conservados; no se completan
con el catálogo actual. El paso 6 incorpora retorno directo al comparador del 5.

## Decisión y alcance

El usuario autoriza materializar la propuesta de seis pasos presentada en la
conversación. La autorización se refiere a presentación, navegación y ayuda;
no modifica contratos comerciales, autoridad decisional ni rutas operacionales.
Se implementa en la rama de pruebas y no se integra en main en este cambio.

La página se genera desde módulos Python. El HTML exportado del navegador no
es la fuente que se mantiene. Se reutilizan los nodos y funciones existentes,
sin clonar el formulario ni introducir otro calculador o API.

## Mapa de componentes y propietarios

| Paso | Contenido conservado | Responsable funcional existente |
| --- | --- | --- |
| Elegir la compra | supplier_id, article_id, código, SKU, descripción, familia y contacto | Selección de proveedor/artículo, catálogo y filtros |
| Revisar la necesidad | quantity, order_date, ficha e historial; po-stock-assumptions | Formulario comercial; purchaseStockPlanningDraft y control de vinculación del escenario |
| Negociar condiciones | Oferta original, Mi propuesta, Respuesta; pricing_mode, unit_price, descuentos, IVA, portes y vencimientos de cada columna | company_purchase_negotiation_ui; API de cotización existente |
| Organizar los pagos | delivery_location, shipping_mode, shipping_net, shipping_vat_percent, shipping_billed_by, shipping_due_date, due_date y cuotas | Calendario y generador de cuotas; declaredPaymentRows y validación del servidor |
| Guardar y estudiar opciones | reference, documentos, save, po-study-state, síntesis, alternativas guardadas, review-panel e informe | Guardado y reviewSaved; revisiones conservadas y sus huellas |
| Registrar el acuerdo | Responsable, fecha, referencia, confirmación e historial | company_purchase_agreement; DECLARED_UNVERIFIED y retirada explícita |

Los campos comerciales internos que sincroniza la negociación conservan sus
id/name. Los contenedores summary, proposal-cost-summary, notice, available y
last-price conservan sus observadores. La fecha del pedido se mueve, no se
copia. Los vencimientos individuales de las cuotas mantienen su independencia.

## Interacción

- Un paso desarrollado; seis anclas con progreso y acceso directo al borrador.
- Continuar cambia de paso y valida los controles de ese paso. No guarda.
- El envío final conserva la validación global y la del servidor. Un campo
  inválido abre sus detalles y su paso, recibe foco y una explicación en español.
- Los estados de cumplimentación no certifican suficiencia financiera, validez
  de evidencias, aceptación del proveedor ni autorización de compra.
- El análisis ampliado del borrador y las referencias técnicas quedan plegados,
  con acceso explícito. No se eliminan sus datos ni acciones.
- El estudio guardado muestra resultados históricos en el paso 5. Editarlo
  requiere crear un borrador o volver explícitamente al formulario anterior.
- El acuerdo queda fuera del formulario de compra: sus campos obligatorios no
  participan en la validación de una propuesta. Se vincula al estudio revisado.
- Las fuentes desde la cinta abren el paso o la revisión que las contiene.

## Duplicados y procedencia

| Caso | Tratamiento |
| --- | --- |
| Navegaciones de cuatro pestañas | Se sustituyen por seis anclas de progreso. La clase interna po-nav se conserva para las llamadas existentes, sin otro formulario. |
| Borrador y estudio guardado | Se muestra una cinta según el contexto. Los resultados conservados no se reconstruyen con el borrador. |
| Estado, síntesis y alternativas | Se mueven los mismos nodos entre análisis del borrador y revisión guardada. Nunca se clonan. |
| Datos de cabecera y campos | La cabecera es una referencia persistente; el control editable tiene una única instancia. |
| Acuerdos sucesivos | Se sustituye su interfaz al abrir otra revisión. El historial persistido permanece en su registro existente. |

## Estética y límites

Se conservan Bricolage Grotesque e IBM Plex Sans locales y el modo oscuro.
El CSS nuevo queda acotado a la vista propuestas. La tabla de negociación
mantiene desplazamiento horizontal interno y sus columnas alineadas.

No se añaden decisiones empresariales, estados operacionales, llamadas API ni
dependencias. La guía no convierte un paso completado en una compra autorizada.
La declaración de acuerdo sigue sin verificar aceptación y sin generar pedidos,
movimientos de stock o pagos.

## Verificación y criterio de cierre

El prototipo se ejecuta contra empresas y bases temporales del corredor de
pruebas, antes de publicar la rama. Los recorridos automatizados cubren
navegación, conservación de campos, validación entre pasos, consulta histórica,
copia, cuotas, stock, acuerdos e informes. Se inspeccionan capturas y tamaños
de 1536, 900 y 390 px en claro y oscuro.

La aceptación funcional y visual técnica no sustituye una prueba de comprensión
con una persona nueva. No se afirma que un usuario sin experiencia complete
el recorrido sin ayuda hasta observar esa prueba.
