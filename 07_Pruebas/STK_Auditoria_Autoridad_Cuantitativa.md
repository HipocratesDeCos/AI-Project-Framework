# EIOS — AUDITORÍA DE AUTORIDAD CUANTITATIVA STK

**Área:** Stock & Demand Intelligence  
**Baseline:** EIOS Vertical MVP  
**Estado:** AUDITORÍA DOCUMENTAL — PENDIENTE DE DEPURACIÓN

## 1. Alcance

Se audita exclusivamente si la documentación vigente permite transformar STK en una metodología cuantitativa implementable. No se crea código, regla, parámetro ni política empresarial.

## 2. Evidencia contrastada

- `01_Modelo/Especificacion_funcional.md` v2.0: exige evaluación temporal y de stock y enumera stock, consumo, demanda, pedidos pendientes, tránsito, plazo, recepción y cantidad propuesta, pero deja la metodología cuantitativa fuera de esta capa.
- `01_Modelo/Stock_Demand_Methodological_Matrix.md` v0.1: declara expresamente pendiente la autoridad cuantitativa y enumera STK-M01…M10.
- `04_Reglas/Matriz_Reglas_MVP.md` v2.1: define R-STK-001…004 y sus resultados funcionales, pero no cierra las fórmulas necesarias.
- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md` y `02_Parametros/Matriz_Parametros_Reglas_MVP.md`: contienen P-STK-001…006 y P-PYE-001…006, pero la matriz marca su cruce individual con reglas como pendiente.

## 3. Resultado por requisito

| Requisito | Estado | Evidencia |
|---|---|---|
| Perímetro funcional | ✅ | Especificación funcional |
| Reglas STK identificadas | ✅ | Matriz de Reglas |
| Parámetros identificados | ✅ | Catálogo |
| Regla ↔ parámetro individual | ❌ | Cruce pendiente |
| Definición canónica de consumo | ❌ | STK-M01 |
| Definición de demanda/proyección | ❌ | STK-M05 |
| Fórmula de cobertura | ❌ | STK-M04 |
| Stock de seguridad | ❌ | STK-M03 |
| Recepción futura | ❌ | STK-M05/M06 |
| Exceso/tolerancia | ❌ | STK-M07 |
| Pedido confirmado | ❌ | STK-M08 |
| Ausencia de datos | ❌ | STK-M09 |
| Contradicciones | ❌ | STK-M10 |

## 4. Hallazgo principal

La arquitectura funcional demuestra que STK pertenece al MVP, pero la autoridad cuantitativa necesaria para implementar su cálculo no está cerrada.

Los valores iniciales del catálogo no pueden elevarse a política empresarial por inferencia. La propia matriz metodológica los clasifica como pendientes de validación.

## 5. Decisión de auditoría

**NO APTO PARA CONTRATO TÉCNICO.**

Antes de diseñar una implementación deberán resolverse documentalmente STK-M01…M10 y demostrarse las relaciones parámetro ↔ regla.

## 6. Salvaguarda

No se autoriza durante esta fase:

- implementación cuantitativa;
- creación de parámetros adicionales;
- creación de reglas adicionales;
- asignación inferida de consumidores;
- conversión de valores iniciales en política definitiva;
- integración STK → O1.

**Conclusión:** STK permanece bloqueado por autoridad cuantitativa. La siguiente actividad autorizada es la depuración documental de los diez puntos metodológicos.
