# EIOS — STK DECISION / GAP REGISTER

**Versión:** 0.2  
**Estado:** CIRCUITO DE DECISIÓN FORMAL — M01 ENTRADA  
**Rama:** `design/stk-quantitative-authority`  
**Baseline de `main`:** `1a4b5fadc5a89102ae71c88041e97763a2388fe1`  
**Fecha:** 03/09/2026

---

## 1. Propósito

Este registro descompone `STK-M01…STK-M10` en decisiones y gaps verificables antes de cualquier implementación cuantitativa.

No crea fórmulas, reglas, parámetros, valores empresariales ni autoridad nueva.

## 2. Clasificación de resolución

- **DOCUMENTAL:** puede resolverse con autoridad ya existente, sin nueva decisión empresarial.
- **NEGOCIO:** requiere decisión o validación empresarial explícita.
- **METODOLÓGICA:** requiere definir una metodología cuantitativa antes del contrato técnico.
- **TÉCNICA:** puede concretarse técnicamente una vez fijada la metodología, sin alterar la política empresarial.
- **BLOQUEADO:** no debe resolverse por inferencia; permanece abierto hasta disponer de autoridad suficiente.

## 3. Registro de gaps

| GAP | Concepto | Evidencia disponible | Falta | Tipo requerido | Gate | Estado |
|---|---|---|---|---|---|---|
| STK-G01 | Consumo (`STK-M01`) | El perímetro reconoce consumo/demanda histórica y la matriz exige definir `consumption`. | Magnitud canónica, unidad, período y transformación autorizada. | METODOLÓGICA / NEGOCIO | Autoridad cuantitativa | **ABIERTO — ENTRADA M01** |
| STK-G02 | Stock mínimo (`STK-M02`) | Existe `STK-001`; relación con seguridad, cobertura y demanda no demostrada. | Semántica y relación operativa. | METODOLÓGICA / NEGOCIO | Autoridad cuantitativa | ABIERTO |
| STK-G03 | Stock de seguridad (`STK-M03`) | `STK-002` figura como 15 % del consumo, pendiente de validación. | Base y carácter definitivo. | NEGOCIO / METODOLÓGICA | Validación empresarial | ABIERTO |
| STK-G04 | Cobertura (`STK-M04`) | Concepto reconocido; `STK-003/004` son valores iniciales. | Numerador, denominador, unidad temporal y nulos. | METODOLÓGICA | Autoridad cuantitativa | ABIERTO |
| STK-G05 | Proyección temporal (`STK-M05`) | MED autoriza conceptualmente stock actual + entradas previstas − salidas previstas. | Mecánica temporal, agotamiento, recepción y lead time. | METODOLÓGICA | Autoridad cuantitativa | ABIERTO — PARCIAL |
| STK-G06 | Pedidos pendientes / tránsito (`STK-M06`) | Reconocidos como entradas potenciales. | Fecha efectiva, inclusión/exclusión y doble contabilización. | METODOLÓGICA / TÉCNICA | Autoridad cuantitativa | ABIERTO |
| STK-G07 | Exceso (`STK-M07`) | `R-STK-003`, `STK-004` y `STK-005` existen. | Relación entre máximo y tolerancia. | METODOLÓGICA / NEGOCIO | Autoridad cuantitativa | ABIERTO |
| STK-G08 | Pedido confirmado (`STK-M08`) | `R-STK-004` reconoce la excepción. | Evidencia mínima y absorción cuantitativa. | NEGOCIO / METODOLÓGICA | Autoridad cuantitativa | ABIERTO |
| STK-G09 | Datos ausentes (`STK-M09`) | `INFORMACIÓN INSUFICIENTE` autorizado conceptualmente. | Conjunto exacto de entradas críticas y propagación. | DOCUMENTAL → TÉCNICA | Contrato técnico | PARCIAL |
| STK-G10 | Contradicciones (`STK-M10`) | No existe resolución automática autorizada. | Política y condición de bloqueo. | NEGOCIO / GOBIERNO | Autoridad de gobierno | ABIERTO |

## 4. Ficha de decisión — STK-M01

### Pregunta de autoridad

**¿Qué magnitud constituye `consumption` para STK y qué transformación autorizada debe aplicarse a las fuentes disponibles?**

### Debe quedar determinado

1. Magnitud canónica: consumo real, ventas, demanda u otra magnitud explícitamente autorizada.
2. Unidad de medida.
3. Período temporal de referencia.
4. Tratamiento de períodos sin observación, si aplica.
5. Transformación/agregación autorizada desde la fuente hasta `consumption`.
6. Fuente de autoridad de la decisión.
7. Vigencia o condición de aplicación, si la autoridad la establece.

### Evidencia actualmente disponible

La matriz metodológica reconoce `consumption` como variable canónica de entrada, pero declara que no define su fórmula de agregación. También mantiene abierto M01 precisamente por la necesidad de determinar si corresponde a consumo real, ventas, demanda o una transformación documentada. Por tanto, la evidencia existente **no cierra M01**.

### No inferir

No se permite cerrar M01 mediante:

- equivalencia entre ventas y consumo;
- equivalencia entre demanda y consumo;
- promedio de un período por convención;
- utilización automática de los 12 meses de `STK-006` como fórmula definitiva;
- imputación de períodos ausentes;
- cualquier transformación por práctica habitual no documentada.

### Evidencia mínima de cierre

M01 podrá pasar a AUDITAR 2 cuando exista una fuente trazable que establezca explícitamente la magnitud, unidad, período y transformación autorizada de `consumption`.

### Estado

**M01 — BLOQUEADO POR AUSENCIA DE AUTORIDAD CUANTITATIVA.**

No se modifica ningún parámetro ni regla como consecuencia de este registro.

## 5. Decisiones que no deben inferirse

1. equiparar ventas, consumo y demanda;
2. convertir el 15 % de `STK-002` en política definitiva;
3. derivar `STK-001` desde `STK-002`, cobertura o demanda;
4. imponer una fórmula de cobertura por convención;
5. asumir que pedidos pendientes o tránsito son automáticamente entradas disponibles;
6. interpretar `STK-005` como modificación del umbral de `STK-004` sin autoridad;
7. considerar un pedido confirmado como evidencia suficiente sin criterio documental;
8. convertir datos ausentes en cero;
9. resolver contradicciones mediante heurísticas no autorizadas;
10. asignar consumidores definitivos a parámetros únicamente por nombre o proximidad semántica.

## 6. Matriz de bloqueo para implementación

Mientras exista cualquier gap marcado `BLOQUEA`, STK permanece:

**NO APTO PARA IMPLEMENTACIÓN CUANTITATIVA.**

## 7. Estado de ciclo

- DISEÑAR: SUPERADO.
- AUDITAR: SUPERADO.
- DEPURAR: SUPERADO como clasificación de gaps.
- AUDITAR 2: SUPERADO como auditoría de suficiencia/límites de autoridad; no como cierre metodológico.
- CERRAR: BLOQUEADO.
- MATERIALIZAR: limitado a documentación autorizada.
- CI: no procede como sustituto de autoridad cuantitativa.

## 8. Regla de continuidad

La siguiente transición de M01 solo se produce cuando aparezca evidencia de autoridad suficiente. La ausencia de decisión no se interpreta como permiso implícito.
