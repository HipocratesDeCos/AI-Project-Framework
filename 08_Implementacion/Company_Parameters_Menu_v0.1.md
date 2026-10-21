# Menú Parámetros por empresa v0.1

## Alcance
Añade Parámetros al lateral, antes de Carga de archivos. Organiza el catálogo aprobado en categorías desplegables con búsqueda, nombre, unidad, valor inicial documental, valor empresarial y frase sobre las consecuencias del cambio. El valor inicial no se aplica automáticamente ni se etiqueta como recomendación sectorial.

## Estado funcional y fronteras
Esta primera pantalla conserva solicitudes de configuración empresarial, pendientes de activación en el motor. No escribe en el Centro canónico ni redefine sus operaciones, vigencias, permisos o histórico. El estado PENDING_ENGINE_ACTIVATION se refiere a la solicitud local, no es una nueva taxonomía del Centro. Guardar no cambia reglas, no ejecuta una compra y no resuelve la integración financiera pendiente. El mensaje es visible junto al formulario y al guardado.

Los valores financieros requieren revisión expresa, responsable y motivo, pero esta confirmación no constituye autorización operacional ni autenticación corporativa. Las salvaguardas y controles sin autoridad de edición permanecen protegidos. Stock mínimo se remite a su gestión por artículo/unidad en Stock. Ningún valor sin consumidor vinculado adquiere aplicación por estar guardado.

La adaptación a empresas reales seguirá necesitando el flujo de autorización/vigencia del Centro; no se afirma que la pantalla local sustituya la persistencia SQL Server aprobada.

## Persistencia
company_parameter_request conserva solicitudes inmutables por company_id y revisión, dataset de origen, valores anteriores/nuevos, responsable, instante y motivo. Control optimista por revisión y transacción de escritura. Distintas versiones documentales de la misma empresa consultan su historial común; otras empresas permanecen aisladas. Vacío conserva ausencia, no cero/default.

## Actividad y bandas sectoriales
Permite identificar actividad, epígrafe IAE, CNAE y versión, tamaño y país, sin inferir equivalencia IAE/CNAE. La consulta oficial RSE compara empresas por actividad/tamaño/país: https://www.bde.es/wbe/es/areas-actuacion/central-balances/bases-de-datos-y-aplicaciones/bbdd-datos-publicas-informacion-sectores/ . Clasificaciones INE: https://www.ine.es/Ayudacod/ .

No hay rangos numéricos automáticos: la pantalla indica Sin rango sectorial contrastado. Permite registrar una banda de referencia con límites, unidad, fuente, periodo y definición, ligada al perfil declarado, con estado USER_DECLARED_NOT_VERIFIED. No se trata como recomendación, validación o límite de compra y no modifica valores seleccionados. Cambiar el perfil en pantalla limpia las bandas para que vuelvan a documentarse. Un saldo mínimo en euros no se deduce de una ratio sectorial sin metodología y datos de escala.

## Verificación
Pruebas de persistencia, separación de empresas, histórico, conflicto de revisión, valores inválidos, confirmación financiera, controles protegidos, metadatos sectoriales y ausencia de defaults/activación. Pruebas HTTP y sintaxis JavaScript existentes ampliadas para el menú. CI completa Python/SQL; entorno local desconectado y comprobación visual pendiente.
