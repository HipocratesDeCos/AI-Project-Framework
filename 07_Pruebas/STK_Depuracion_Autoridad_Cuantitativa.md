# EIOS — DEPURACIÓN DE AUTORIDAD CUANTITATIVA STK

**Estado:** DEPURACIÓN DOCUMENTAL  
**Rama:** `design/stk-quantitative-authority`  
**Baseline de trabajo:** `main` posterior a E2E

## 1. Objetivo

Convertir los hallazgos de auditoría en un perímetro documental cerrado para decidir qué puede considerarse autoridad cuantitativa STK y qué debe permanecer pendiente. Esta fase no inventa fórmulas ni valores empresariales.

## 2. Criterio rector

La Especificación Funcional confirma que EIOS puede considerar stock, consumo, demanda, pedidos pendientes, tránsito, plazo de entrega y cantidad propuesta, pero remite la metodología concreta a su capa correspondiente.

El Catálogo de Parámetros contiene valores iniciales para STK y PYE, pero declara que requieren validación. Por tanto, ningún valor inicial se eleva a política definitiva por inferencia.

La Rule Dependency Matrix exige evidencia documental para considerar canónica una relación regla → parámetro/dato.

## 3. Matriz de depuración M01–M10

| Punto | Decisión de depuración | Estado |
|---|---|---|
| M01 Consumo | No se fija si procede de consumo real, ventas o demanda. Requiere fuente empresarial/metodológica explícita. | PENDIENTE |
| M02 Stock mínimo / seguridad / cobertura | Se mantienen como conceptos separados. No se autoriza equivalencia ni fórmula implícita. | PENDIENTE |
| M03 Base del stock de seguridad | El 15% de STK-002 es valor inicial, no autoridad cuantitativa. Falta definir base y transformación. | PENDIENTE |
| M04 Cobertura | STK-003/STK-004 fijan valores iniciales en días, pero no definen numerador, denominador, unidad temporal ni tratamiento de cero/nulo. | PENDIENTE |
| M05 Proyección | PYE-001…006 enumeran factores, pero no existe fórmula autorizada que los combine ni regla temporal completa. | PENDIENTE |
| M06 Pedidos / tránsito | Se reconoce su posible consideración, pero no está cerrada la semántica de disponibilidad futura ni la prevención de doble cómputo. | PENDIENTE |
| M07 Exceso / tolerancia | STK-005 no puede aplicarse hasta documentar su relación con STK-004 y el cálculo de exceso. | PENDIENTE |
| M08 Pedido confirmado | R-STK-004 reconoce la excepción, pero falta autoridad sobre evidencia, fecha, cantidad y mecanismo de absorción. | PENDIENTE |
| M09 Datos críticos ausentes | Se mantiene el principio general: ausencia de evidencia no es cero ni favorable. Falta catalogar inputs críticos STK individualmente. | PENDIENTE |
| M10 Contradicciones temporales | No se autoriza heurística para resolver fechas/estados incompatibles. Requiere tratamiento documental explícito. | PENDIENTE |

## 4. Cruces que NO se deben inferir

No se autoriza convertir automáticamente:

- `STK-002 = 15% del consumo` en una fórmula de stock de seguridad completa;
- `STK-003 = 30 días` o `STK-004 = 90 días` en fórmulas de cobertura;
- `PYE-005 = Sí` en una definición de demanda;
- `PYE-004 = Sí` en una fórmula de recepción;
- `PYE-002/PYE-003 = Sí` en una regla de suma de disponibilidad futura;
- `R-STK-001…004` en una implementación matemática;
- coincidencias nominales `P-STK-*`/`P-PYE-*` en dependencias canónicas.

## 5. Resultado

La depuración reduce el espacio de interpretación, pero **no resuelve todavía la autoridad cuantitativa**. Los diez puntos siguen requiriendo decisión documental/empresarial competente.

## 6. Gate siguiente

Antes de AUDITORÍA 2 del diseño deben existir fuentes autorizadas suficientes para determinar, como mínimo:

1. definición operacional de consumo;
2. definición operacional de demanda/proyección;
3. fórmula de cobertura;
4. tratamiento del stock de seguridad;
5. proyección temporal y recepción;
6. tratamiento de pedidos y tránsito sin doble conteo;
7. exceso y tolerancia;
8. evidencia de pedidos confirmados;
9. inputs críticos y estados de insuficiencia;
10. tratamiento de contradicciones.

Si las fuentes no permiten cerrar alguno de estos puntos, el resultado correcto será mantenerlo `PENDING`, no completar la metodología por inferencia.

**Conclusión:** STK queda documentalmente depurado, pero continúa bloqueado para implementación cuantitativa.
