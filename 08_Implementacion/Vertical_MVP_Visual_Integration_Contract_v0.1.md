# Vertical MVP Visual Integration — Implementation Contract v0.1

Estado: **CERRADO PARA IMPLEMENTACIÓN**

## 1. Propósito

Materializar una frontera de presentación adicional para resultados ya producidos por `VerticalMVPSupportResult`, sin reabrir ni ampliar el contrato cerrado de U1.1.

La unidad consume exclusivamente el `Mapping` generado por `eios.frontend.application_boundary.present_vertical_mvp_result` y produce un view-model de presentación.

## 2. Entradas autorizadas

El adaptador recibe un `Mapping` con:

- `execution`: estado, versión de política, limitaciones y capacidades ya producidas;
- `rules`: `null` cuando no existe resultado de Rules/CRC, o el bloque ya producido con reglas ejecutadas/omitidas, resultado consolidado, Assessments y trazas.

No recibe modelos de dominio para evaluarlos y no ejecuta capacidades EIOS.

## 3. Salida

El view-model puede exponer únicamente:

- estado de ejecución y versión de política;
- fallo/limitaciones y elementos no resueltos;
- capacidades y sus estados ya producidos;
- disponibilidad del bloque Rules/CRC;
- cobertura de reglas: ejecutadas y omitidas, como categorías separadas;
- resultado consolidado de soporte, razón dominante, factores relevantes y conflictos;
- Assessments tal como fueron producidos;
- referencias de traza ya existentes.

## 4. Invariantes obligatorios

1. **Presentación solamente.** No calcular, evaluar reglas, ejecutar CRC, ordenar alternativas ni llamar motores.
2. **Ausencia ≠ falso.** `rules = null` se conserva como indisponibilidad del bloque Rules/CRC; no se materializa como resultados negativos.
3. **Omitida ≠ falsa.** Una regla omitida nunca genera un Assessment sintético.
4. **NOT_EVALUABLE ≠ FALSE.** El estado y outcome de cada Assessment se copian sin reinterpretación.
5. **CRC ≠ decisión humana.** `consolidated_result` se presenta como resultado de soporte; no implica aprobación, rechazo, recomendación ni autoridad decisional.
6. **Sin autoridad nueva.** Prohibidos `score`, `ranking`, `recommendation`, `approval`, `best_scenario` o equivalentes inferidos por esta capa.
7. **Sin mutación.** El view-model es una copia de presentación; modificarlo no puede modificar el payload de entrada.
8. **Orden preservado.** No se reordenan capacidades, reglas, Assessments ni trazas.
9. **Fallo cerrado de forma.** La entrada debe ser un `Mapping`, `execution` debe ser un `Mapping` y `rules`, si existe, debe ser un `Mapping`.

## 5. Fuera de alcance

- modificar `eios/frontend/visual/view_model.py` de U1.1;
- modificar la semántica o cierre de U1.1;
- cablear `index.html` a ejecución real;
- ejecutar Vertical MVP, Rules Engine o CRC;
- persistencia, networking o APIs;
- nuevas reglas, parámetros o semántica de negocio;
- decisión humana o automatización de aprobación/rechazo.

## 6. Pruebas mínimas

La implementación debe demostrar:

- mapeo fiel de un payload con Rules/CRC;
- conservación de `rules = null` como no disponible;
- conservación de reglas omitidas sin Assessment sintético;
- conservación literal de `NOT_EVALUABLE`;
- copia independiente del payload fuente;
- ausencia de campos de autoridad no autorizados.

## 7. Dictamen de auditoría previa

**APTO PARA IMPLEMENTACIÓN.**

El contrato añade una frontera puramente presentacional sobre el adaptador ya integrado por PR #94. No modifica U1.1, no traslada lógica analítica al frontend y no crea autoridad decisional.
