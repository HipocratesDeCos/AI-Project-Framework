# EIOS — STK DECISION / GAP REGISTER

**Versión:** 0.1  
**Estado:** DEPURACIÓN FORMAL DEL DISEÑO  
**Rama:** `design/stk-quantitative-authority`  
**Baseline de `main`:** `1a4b5fadc5a89102ae71c88041e97763a2388fe1`  
**Fecha:** 03/09/2026

---

## 1. Propósito

Este registro descompone los puntos `STK-M01…STK-M10` de la matriz metodológica en decisiones y gaps verificables antes de cualquier implementación cuantitativa.

No crea fórmulas, reglas, parámetros, valores empresariales ni autoridad nueva.

## 2. Clasificación de resolución

- **DOCUMENTAL:** puede resolverse con autoridad ya existente, sin nueva decisión empresarial.
- **NEGOCIO:** requiere decisión o validación empresarial explícita.
- **METODOLÓGICA:** requiere definir una metodología cuantitativa antes del contrato técnico.
- **TÉCNICA:** puede concretarse técnicamente una vez fijada la metodología, sin alterar la política empresarial.
- **BLOQUEADO:** no debe resolverse por inferencia; permanece abierto hasta disponer de autoridad suficiente.

## 3. Registro

| GAP | Concepto | Evidencia disponible | Falta | Tipo requerido | ¿Resoluble sin decisión empresarial? | Gate | Estado |
|---|---|---|---|---|---|---|---|
| STK-G01 | Consumo (`STK-M01`) | El perímetro reconoce consumo/demanda histórica y la matriz exige definir `consumption`. | Determinar magnitud canónica y transformación autorizada. | METODOLÓGICA / NEGOCIO | No | Autoridad cuantitativa | ABIERTO |
| STK-G02 | Stock mínimo (`STK-M02`) | Existe `STK-001`; su relación con seguridad, cobertura y demanda no está demostrada. | Definir semántica y relación operativa. | METODOLÓGICA / NEGOCIO | No | Autoridad cuantitativa | ABIERTO |
| STK-G03 | Stock de seguridad (`STK-M03`) | `STK-002` figura como 15 % del consumo, pendiente de validación. | Validar base y carácter definitivo del parámetro. | NEGOCIO / METODOLÓGICA | No | Validación empresarial | ABIERTO |
| STK-G04 | Cobertura (`STK-M04`) | El concepto de cobertura está funcionalmente reconocido; `STK-003/004` existen como valores iniciales. | Numerador, denominador, unidad temporal y tratamiento de nulos. | METODOLÓGICA | No | Autoridad cuantitativa | ABIERTO |
| STK-G05 | Proyección temporal (`STK-M05`) | MED autoriza conceptualmente stock proyectado como stock actual + entradas previstas − salidas previstas. | Mecánica temporal exacta, agotamiento, recepción y lead time. | METODOLÓGICA | Parcial | Autoridad cuantitativa | ABIERTO — PARCIALMENTE RESUELTO |
| STK-G06 | Pedidos pendientes / tránsito (`STK-M06`) | Ambos están reconocidos como entradas potenciales del análisis. | Fecha efectiva, inclusión/exclusión y prevención de doble contabilización. | METODOLÓGICA / TÉCNICA | No | Autoridad cuantitativa | ABIERTO |
| STK-G07 | Exceso (`STK-M07`) | `R-STK-003`, `STK-004` y `STK-005` existen; su relación no está definida. | Determinar cómo interactúan máximo y tolerancia. | METODOLÓGICA / NEGOCIO | No | Autoridad cuantitativa | ABIERTO |
| STK-G08 | Pedido confirmado (`STK-M08`) | `R-STK-004` reconoce la excepción por pedido confirmado. | Evidencia mínima y mecánica cuantitativa de absorción. | NEGOCIO / METODOLÓGICA | No | Autoridad cuantitativa | ABIERTO |
| STK-G09 | Datos ausentes (`STK-M09`) | Especificación funcional y MED permiten `INFORMACIÓN INSUFICIENTE`; no debe sustituirse ausencia por cero sin autoridad. | Identificar conjunto exacto de entradas críticas y propagación técnica. | DOCUMENTAL → TÉCNICA | Sí, en principio | Contrato técnico | PARCIALMENTE RESUELTO |
| STK-G10 | Contradicciones (`STK-M10`) | No existe regla autorizada para resolver automáticamente contradicciones temporales. | Política de tratamiento y condición de bloqueo. | NEGOCIO / GOBIERNO | No | Autoridad de gobierno | ABIERTO |

## 4. Decisiones que no deben inferirse

Las siguientes decisiones quedan explícitamente fuera de la inferencia automática:

1. equiparar ventas, consumo y demanda;
2. convertir el 15 % de `STK-002` en política definitiva;
3. derivar `STK-001` desde `STK-002`, cobertura o demanda;
4. imponer una fórmula de cobertura por convención;
5. asumir que pedidos pendientes o tránsito son automáticamente entradas disponibles;
6. interpretar `STK-005` como modificación del umbral de `STK-004` sin autoridad;
7. considerar un pedido confirmado como evidencia suficiente sin criterio documental de confirmación;
8. convertir datos ausentes en cero;
9. resolver contradicciones mediante heurísticas no autorizadas;
10. asignar consumidores definitivos a parámetros únicamente por nombre o proximidad semántica.

## 5. Matriz de bloqueo para implementación

| Condición | Impacto | Estado |
|---|---|---|
| Fórmula de consumo/demanda no autorizada | Impide cobertura y proyección cuantitativas | BLOQUEA |
| Relación stock mínimo / seguridad / cobertura no autorizada | Impide clasificación completa STK | BLOQUEA |
| Cobertura sin fórmula y unidad temporal | Impide `R-STK-002` y parte de `R-STK-003` | BLOQUEA |
| Proyección sin mecánica temporal completa | Impide `R-STK-001` y `R-ENT-001` cuantitativos | BLOQUEA |
| Entradas futuras sin regla temporal/doble conteo | Riesgo de resultado materialmente incorrecto | BLOQUEA |
| Exceso/tolerancia sin semántica definida | Impide aplicación cuantitativa segura de `R-STK-003` | BLOQUEA |
| Pedido confirmado sin prueba de absorción | Impide aplicación cuantitativa segura de `R-STK-004` | BLOQUEA |
| Ausencia sin conjunto de campos críticos definido | Impide contrato completo de evaluabilidad | BLOQUEA PARCIALMENTE |
| Contradicciones sin política | Impide resolución determinista segura | BLOQUEA |

## 6. Estado de depuración

### Resuelto conceptualmente

- Existencia del perímetro funcional STK.
- Existencia de variables canónicas de entrada.
- Existencia conceptual de proyección.
- Principio de `INFORMACIÓN INSUFICIENTE` ante ausencia crítica.
- Prohibición de convertir valores iniciales en política definitiva.

### No resuelto

- Metodología cuantitativa M01–M04.
- Mecánica temporal completa M05.
- Integración temporal de M06.
- Semántica de exceso M07.
- Evidencia y absorción cuantitativa M08.
- Política de contradicciones M10.

## 7. Gate de salida de DEPURACIÓN

**Resultado:** DEPURACIÓN FORMAL SUPERADA COMO CLASIFICACIÓN DE GAPS.

Esto **no equivale** a autorización de implementación.

La siguiente condición de entrada a `AUDITAR 2` es disponer de decisiones/autoridad suficiente para cerrar los gaps bloqueantes, manteniendo sin cambios las cuestiones que no tengan autoridad.

## 8. Regla de continuidad

Mientras exista cualquier gap marcado `BLOQUEA`, STK permanece:

**NO APTO PARA IMPLEMENTACIÓN CUANTITATIVA.**

La ausencia de decisión no se interpreta como permiso implícito.
