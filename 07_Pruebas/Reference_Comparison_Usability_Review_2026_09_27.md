# EIOS — Revisión de lectura del paquete comparativo · 27/09/2026

**Base:** `main @ c9aecd850b91d7f8e19ac34129cc2f80203798b4`. Revisión estructural y textual de dos empresas ficticias; no es una prueba con lectores ni una validación operacional.

## DISEÑAR

El recorrido esperado comienza en `comparison.html`, continúa en la vista para comprador del caso 001 o en la revisión del caso 002, y permite distinguir calidad de entrada, ejecución técnica, fiabilidad del proveedor y autoridad de compra. Las afirmaciones visibles deben corresponder a los JSON verificados.

## AUDITAR

Se generó el paquete con `create_comparison_bundle` en una carpeta nueva y se ejecutó `verify_comparison_bundle`. Se examinaron los cuatro HTML con un analizador, los enlaces relativos de la comparación y los terminales y observaciones JSON.

| Comprobación | Resultado observado |
|---|---|
| Inventario y repetición | 31 archivos: 20 del caso 001, 10 del caso 002 y `comparison.html`. La repetición exacta terminó correctamente. |
| Recorrido | Los dos enlaces de la comparación apuntan a archivos presentes dentro del paquete; no se encontraron enlaces externos. |
| Estructura HTML | Cada página tiene un título principal; el analizador no notificó errores. No hay `script`, formularios ni `iframe`. |
| Variante negativa del caso 001 | QTG `NO_APTO`; está disponible en la vista detallada, aunque la comparación inicial se centra en la variante apta. |
| Variante apta del caso 001 | QTG `APTO` y ejecución `COMPLETED`; su fiabilidad favorable pertenece al material ficticio de ese caso. |
| Caso 002 | QTG `APTO`, ejecución `PARTIALLY_COMPLETED` y fiabilidad `NOT_DETERMINABLE`; la página explica que faltan hechos sobre el proveedor. |
| Límite de ambos casos | Material `SYNTHETIC`, política `SYNTHETIC_TEST_ONLY`, ruta `FORBIDDEN`, efecto `NO_OPERATIONAL_EFFECT` y autoridad decisional `false` en los terminales. |

La comparación contiene unas 330 palabras y conduce a vistas con distinta profundidad: unas 1.800 palabras en el HTML del caso 001, incluidas 21 secciones desplegables, y unas 430 en el caso 002. La primera lectura queda en la comparación; los detalles técnicos se consultan después. Estas cifras incluyen texto inicialmente plegado y no miden el tiempo real de lectura.

## DEPURAR → AUDITAR 2

No apareció una contradicción entre los estados principales, los enlaces y los artefactos verificados. Tampoco hay motivo objetivo para cambiar el runner, QTG, C0, la admisión o los contratos de procedencia. La asimetría de extensión responde a que el caso 001 muestra dos variantes y ocho observaciones por variante; no se interpreta como prueba de que una página resulte más fácil de leer.

**Límite de esta auditoría:** no se observó una sesión de lectura humana ni se comprobó el diseño en un navegador Windows a distintos tamaños de pantalla. Por tanto, la comprensión íntegra y la comodidad visual siguen pendientes de una revisión de uso, no se declaran aprobadas por las comprobaciones automáticas.

Para esa revisión, abrir el paquete generado según `08_Implementacion/Reference_Comparison_Bundle_Operator_Guide_v0.1.md` y responder, sin consultar primero los JSON:

1. ¿Por qué el caso 002 queda completado parcialmente aunque su entrada sea apta para la prueba?
2. ¿Dónde se explica que la fiabilidad favorable del caso 001 no autoriza una compra?
3. ¿Se distingue con facilidad el resumen de las trazas técnicas y se puede terminar la lectura en pantalla estrecha?

Una respuesta incorrecta o una dificultad localizada debe registrarse con página, sección y frase concreta antes de modificar el HTML. No se presupone una corrección sin ese hallazgo.

## CERRAR → MATERIALIZAR → CI

Se cierra la **revisión estructural y textual del paquete comparativo** con resultado conforme a su alcance. La aceptación de uso visual queda abierta para una lectura humana. Este documento registra evidencia y criterios; no modifica código, JSON, fixtures ni límites operacionales. Integrar tras CI satisfactoria.
