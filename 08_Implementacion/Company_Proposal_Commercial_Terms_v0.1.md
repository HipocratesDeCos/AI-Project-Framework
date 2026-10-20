# Portes y descuentos de propuestas

El formulario principal Propuestas admite precio neto ya negociado o precio antes de descuentos. El precio neto no admite un segundo descuento. En el segundo modo, el descuento puede ser un porcentaje o euros del total de la línea, nunca euros por unidad. Se conservan el precio introducido, modalidad y valor del descuento, importe antes de descuento y descuento aplicado.

Los portes pueden quedar pendientes, ser a cargo de la empresa compradora, del proveedor, estar incluidos en precio o declararse sin portes. Solo el comprador introduce importe neto, tipo de IVA expresamente declarado, quién factura (proveedor o transportista) y vencimiento propio. No se infiere ningún tratamiento fiscal. Los portes incluidos no se suman de nuevo. Pendiente significa desconocido, no cero: el total completo queda nulo.

`unit_price` es el precio efectivo neto del artículo después de descuentos, sin portes, para comparar con compras históricas. `net`, `tax`, `total` conservan su significado anterior de mercancía. Los campos `operation_net`, `operation_tax`, `operation_total` añaden exclusivamente los portes declarados. Otros gastos y la evaluación financiera permanecen pendientes. Los vencimientos de mercancía y portes son independientes y quedan conservados.

Los cálculos utilizan Decimal y ROUND_HALF_EVEN a céntimos por línea e impuesto. El precio unitario derivado no se redondea prematuramente; una futura adaptación al contrato canónico deberá resolver explícitamente su precisión máxima sin modificarla silenciosamente. El descuento fijo y el neto de portes admiten dos decimales. Se rechazan valores negativos, no finitos, descuentos excesivos y cargos de portes contradictorios con el modo elegido.

POST `/api/purchases/quote` calcula sin guardar y exige el token local. Guardar conserva las condiciones y los importes. La revisión incluye la propuesta congelada; no convierte la declaración en factura o evidencia financiera. Las propuestas antiguas no se reescriben: sin datos de portes, su total completo permanece pendiente en pantalla.

No se ejecutan compras, reglas ni decisiones. La propuesta sigue pendiente de evaluación, sin autoridad decisoria. La prueba de interfaz utiliza una copia desechable de la base de datos.
