# Elección en cabecera y recorrido de cinco pasos

La elección del proveedor y artículo se realiza en los selectores sin marco de la
cabecera. La antigua pantalla de selección deja de estar en la navegación.
Sus campos internos siguen siendo los adaptadores del contrato de formulario;
no se duplican los valores enviados al servidor ni se cambia la persistencia.

1. Revisar la necesidad.
2. Negociar condiciones.
3. Organizar los pagos.
4. Guardar y estudiar opciones.
5. Registrar el acuerdo.

Cambiar proveedor actualiza su catálogo y deja el artículo pendiente de elección.
La selección de artículo actualiza las referencias y cálculos existentes. Los
controles de cabecera transmiten el cambio al campo canónico antes de recalcular;
su evento nativo de entrada no puede restaurar el valor anterior desde el modelo.
La familia conserva su función de filtro del catálogo del proveedor.

Nueva propuesta y retorno al formulario abren el primer paso visible. Si faltan
proveedor o artículo al continuar, se enfoca el selector correspondiente en la
cabecera. Las consultas guardadas mantienen cabecera en solo lectura; los datos
históricos ampliados de proveedor y artículo se consultan en un desplegable del
primer paso. Consultar no altera el borrador ni el estudio guardado.

Validación: prueba de navegador de cinco pasos, numeración 1–5, nueva propuesta,
elección explícita en cabecera, bloqueo al faltar artículo, navegación de estudio
guardado, inmutabilidad de históricos, modo oscuro y límites en móvil. Regresión
de estudios de ambas propuestas y sus calendarios independientes.
