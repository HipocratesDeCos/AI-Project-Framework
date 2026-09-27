# EIOS — Reconciliación de preparación del piloto real · 27/09/2026

## DISEÑAR → AUDITAR

La auditoría consolidada del 23/09/2026 identificó
`ProjectionQualityO1Binding` como software pendiente. Después se materializó
`eios/core/projection_quality_o1_binding.py` y se auditó en
`Projection_Quality_O1_Binding_Materialization_Audit_v0.1.md`. Esa frase de
la auditoría anterior describe su fecha de corte; **ya no es un pendiente
actual**. No se reescribe el documento histórico.

| Tramo | Estado comprobado | Límite que conserva |
|---|---|---|
| Intake documental | Existe inventario canónico y detección de referencias obligatorias. | Presencia de una referencia no autentica documentos ni admite el expediente. |
| Admisión operacional y QTG | Existen contratos, productor, recibo y consumidor operacionales. | El material sintético es rechazado para QTG operacional. |
| Vínculo QTG↔O1 | Implementado con validación de recibo, consumo, envelope y compra/contexto exactos; la fachada posee la ejecución O1 y el cierre terminal. | QTG queda fuera del catálogo de capacidades O1 y no concede autoridad decisional. |
| Casos 001 y 002 | Paquetes sintéticos completos y comparación de solo lectura, verificados por repetición exacta. | `SYNTHETIC / SYNTHETIC_TEST_ONLY / FORBIDDEN / NO_OPERATIONAL_EFFECT / false`. |
| Piloto empresarial positivo | No existe expediente real aportado y admitido. | No hay E2E `PRESENTED_OPERATIONAL → QTG OPERATIONAL → O1` ejecutado. |

## DEPURAR → AUDITAR 2

El cambio de estado es **de preparación técnica**, no de admisión de un
caso real. Ni el intake completo, ni un hash, ni las dos empresas ficticias
demuestran autenticidad, mandato o revisión humana. Tampoco se puede pasar
un bundle sintético por la fachada operacional cambiando su etiqueta.

La implementación del binding ya dispone de pruebas de rechazo del consumo
sintético y de paridad con O1. Un ensayo E2E operacional positivo exige
material empresarial presentado, soporte y actos humanos que el repositorio
no puede fabricar. Las declaraciones auxiliares de PRICE, proveedor, C0,
escenarios y negociación de los casos 001/002 son hipótesis de prueba y no
se transfieren a una empresa futura.

## CERRAR → MATERIALIZAR → CI

**Dictamen:** no queda abierto el código del binding QTG↔O1. La validación
operacional positiva continúa condicionada al primer expediente real
admisible y a sus actos de revisión. Mientras no exista ese material, la
línea ejecutable de referencia sigue siendo estrictamente sintética. Esta
reconciliación actualiza la lectura del estado, sin modificar contratos,
productores, admisión, reglas ni resultados.
