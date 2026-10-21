# Propuestas: entrega, contacto y presentación española v0.1

## Datos comerciales conservados
Lugar de entrega editable en Propuestas, precargado desde delivery_location (o delivery_address) de la ficha del proveedor. Un vacío explícito en la propuesta conserva ausencia; si falta el campo de entrada se toma el valor configurado. No se infiere lugar de entrega de localidad, domicilio fiscal ni dirección genérica del proveedor. Campo limitado a 500 caracteres.

Cada propuesta nueva conserva supplier_commercial_at_save con código, razón social, contacto y lugar predeterminado, además del lugar específico de la propuesta. El saludo del borrador usa contact_name (o contact_person) y, si está ausente, legal_name. Las propuestas antiguas sin captura no se enriquecen retrospectivamente; mantienen saludo genérico si no se conservó nombre.

La recepción asistida de proveedores incorpora contact_name y delivery_location opcionales. La cartera muestra esos campos de las fichas existentes; cargar archivos recibidos no activa automáticamente una nueva versión.

## Presentación
Números visibles con punto de miles y coma decimal, incluso con cuatro cifras. Correos e informes comparten helpers Decimal sin modificar valores originales. Fechas visibles DD/MM/YYYY, conservando hora y desplazamiento cuando procede. Inputs de fecha de la pantalla aceptan DD/MM/YYYY y convierten a ISO para el contrato HTTP. No se alteran IDs, documentos fuente ni JSON canónicos, y los campos numéricos editables mantienen su valor numérico para cálculo.

## Verificación
Defaults, modificación/vacío explícito, contacto/razón social, ausencia de localidad como sustituto de entrega, validación de texto, formato de cantidades/importes/fechas e identidad canónica preservada. Pruebas Node sobre formato visible y conversión de fechas válidas e inválidas, además de sintaxis global y HTTP existentes. CI Python/SQL antes/después de integrar; entorno local desconectado y comprobación visual pendiente.
