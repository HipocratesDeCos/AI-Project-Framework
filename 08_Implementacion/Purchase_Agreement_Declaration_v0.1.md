# Acuerdo declarado de una compra · v0.1

## Alcance

Permite anotar un acuerdo sobre las condiciones y cuotas de un estudio guardado. Es una declaración local y no verificada. No modifica la propuesta, no autoriza compras, no envía pedidos y no registra pagos. La ruta operacional sigue FORBIDDEN y decision_authority/purchase_authorized son false.

Si cambia precio, cantidad, portes, IVA, vencimientos o cuotas respecto al estudio, primero debe crearse y guardarse un borrador con las condiciones revisadas. Esta declaración se liga a la propuesta base conservada, no elige silenciosamente otra columna de negociación ni una alternativa hipotética.

## Entrada y estados

En la consulta del estudio aparece «Acuerdo con el proveedor», plegado por defecto. Para declarar se requieren responsable, fecha no anterior al pedido, referencia del soporte y confirmación explícita de alcance. La referencia es declarativa: no supone que el archivo haya sido aportado ni verificado. Reutiliza `company_purchase_comparison.condition` con origen DOCUMENTED, aceptación DECLARED_ACCEPTED y evidencia DECLARED_UNVERIFIED.

Estados: NOT_DECLARED → DECLARED_UNVERIFIED → RETRACTED. Puede anotarse una declaración nueva después de dejar la anterior sin efecto. No puede sustituirse una vigente sin retirarla primero. Retirar requiere responsable, fecha, referencia, motivo y confirmación. Se conserva todo el historial.

## Persistencia y controles

POST `/api/purchases/agreement` recupera la revisión exacta guardada mediante `_saved_review`. Transacción inmediata: comprueba contexto documental actual, identidad y huella de la propuesta, revisión esperada y transición de estado. Guarda eventos anexados con huella y vínculo al evento anterior en `company_purchase_agreement_event`. La lectura comprueba continuidad e integridad.

Cada nueva revisión captura el estado y eventos de acuerdo antes de calcular su identificador. El informe imprime esa captura; un informe anterior no se actualiza retroactivamente. Una copia a nuevo borrador/propuesta no hereda acuerdos: sus nuevas condiciones necesitan una declaración propia.

La entrada de datos del acuerdo no activa el cálculo del formulario de compra ni abandona la consulta. Una respuesta tardía no vuelve a abrir el estudio si el usuario ya pasó al borrador u otro estudio.

## Uso

1. Revisar el estudio de las condiciones que se declaran acordadas.
2. Abrir «Acuerdo con el proveedor».
3. Indicar responsable, fecha y referencia; confirmar alcance y registrar.
4. Consultar «Anotado, sin verificar» y el informe.
5. Si fue un error, dejar la declaración sin efecto con motivo; el historial permanece.

## Verificación

Pruebas de servidor: declaración y retirada; conservación de propuesta, cálculo financiero e informe anterior; soporte, fecha y confirmación obligatorios; control de revisión y transición; rechazo de contexto incompatible e historial alterado; acuerdo no heredado por una nueva copia. Chromium: registro y retirada reales, permanencia en modo consulta al escribir, propuesta y saldo sin cambios, soporte en informe e historial conservado. Regresión de copia y guardado de borrador.
