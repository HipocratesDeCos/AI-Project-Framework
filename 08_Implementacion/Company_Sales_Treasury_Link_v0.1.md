# Fuentes financieras de ventas: selección automática y excepción manual

## Regla por defecto

Sin intervención del comercial, EIOS resuelve las referencias financieras de la empresa sintética por:

1. Mayor fecha de corte entre archivos recibidos de saldos y flujos de esa razón social.
2. Dentro de ese corte, última recepción de cada contenido: saldos y calendario.
3. A igualdad de instante de recepción, orden de inserción conservado en la recepción. El nombre del archivo no determina su prioridad.
4. Cuentas de bancos 572. Caja 570 solo mediante una excepción manual. Para cada rama contable se utiliza el nivel superior documentado, sin sumar sus descendientes.

Un archivo de corte antiguo subido después no desplaza al corte más reciente. Una recepción duplicada sin cambios tampoco crea una nueva versión. No se mezclan cortes; si el último corte está incompleto o el último origen no es utilizable, se informa de ello y no se recuperan silenciosamente cifras antiguas. La regla identifica fuentes, no acredita conciliación, completitud ni solvencia.

## Identidad y fecha

Solo naturaleza sintética y la misma razón social normalizada (mayúsculas, acentos, espacios y puntuación). Las diferencias de código interno se conservan en la procedencia; el uso automático responde a la política autorizada, no a una confirmación humana ficticia. Razones sociales diferentes permanecen excluidas.

El corte financiero puede ser más reciente que el de la versión documental base. Se identifica expresamente en el contexto financiero y en el panel; no se reescribe el manifiesto original. No se reutilizan magnitudes de fondo de maniobra ni referencias externas de liquidez de otro corte. Una propuesta anterior al corte financiero utilizado se rechaza para impedir uso retrospectivo de datos posteriores.

## Panel y excepciones

El panel se carga al preparar el formulario y muestra fuentes, corte, recepción y cuentas utilizadas. En Automática no hay que guardar un vínculo ni rellenar responsable. Los controles de edición están deshabilitados.

Para elegir otro archivo, versión o caja: cambiar a Manual, seleccionar fuentes y cuentas, revisar el total, indicar responsable y motivo, confirmar el alcance y guardar. Una diferencia de identidad interna exige confirmación expresa en este modo. La selección manual queda fijada hasta volver a Automática; nuevas recepciones no la sustituyen. El control de retorno al modo automático conserva una revisión en el historial.

Las cuentas aparecen como tarjetas y el total se destaca separadamente. Las fuentes completas se muestran fuera del selector, que incluye fecha de corte y número de recepción. La suma del panel es orientativa hasta la validación del servidor.

## Contrato y controles

- EUR y códigos numéricos 570/572 o subcuentas; se rechazan cuentas repetidas, saldos negativos, monedas distintas y mezcla de padres e hijos. Cero explícito es válido.
- El calendario recibido sustituye la lista base, nunca se añade a ella. Sus movimientos conservan identidad, archivo, fila y evidencia `NOT_EVIDENCED`.
- No se asigna una cuenta bancaria concreta a cada movimiento cuando el archivo no la identifica. La política 572/570 elige los saldos de tesorería, no inventa una imputación contable histórica.
- No se deduce crédito disponible ni se añaden cobros futuros al saldo inicial.
- La selección alimenta la evaluación comercial y el plan financiero existente de la venta. Un calendario nuevo se distingue de las cuotas nuevas de la oferta; los movimientos ya documentados se reutilizan sin duplicar.
- La huella documental incluye las fuentes resueltas y la política o excepción. Una nueva versión pertinente invalida la evaluación anterior. Una fuente alterada provoca fallo cerrado.
- Ofertas y planes guardados conservan sus fuentes originales; los cambios posteriores no reescriben su resultado ni permiten editarlo con otro contexto.
- Seleccionar fuentes automáticamente no demuestra disponibilidad, conciliación, calidad, cobertura de crédito ni viabilidad. `decision_authority=false`, ruta operacional prohibida.

## Verificación

`tests/test_company_sales_treasury.py` comprueba regla automática, prioridad de corte sobre fecha de carga, revisión más reciente, 572 sin duplicar subcuentas, excepción 570, corte incompleto, fuente alterada, fechas de propuesta anteriores al corte, conservación de ofertas, retirada del modo manual y ejecución del motor con fuentes seleccionadas.

`python tests/browser/run_sales_treasury.py` prueba HTTP/DOM, valores por defecto, modo manual, confirmación de identidad y evaluación. `run_sales_proposal_workspace.py` cubre el recorrido de propuesta y guardado. Requieren Node y jsdom (`EIOS_JSDOM_MODULE` admite la ruta al paquete).
