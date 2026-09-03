# EIOS — AUDITORÍA DE AUTORIDAD METODOLÓGICA · VIABILITY FRONTIER

**Baseline:** `d82cf899ccc0a133e9a6d9a7be3084ca3f5dbc40`  
**Rama:** `design/viability-frontier-authority`  
**Estado:** AUDITORÍA DOCUMENTAL — PENDIENTE DE DEPURACIÓN

## 1. Alcance

Se audita si las fuentes actualmente materializadas autorizan una metodología cuantitativa/operacional suficiente para implementar Viability Frontier. No se implementa código ni se crean reglas, parámetros, umbrales o fórmulas.

## 2. Fuentes contrastadas

- `01_Modelo/Viability_Frontier_Methodological_Matrix.md` v0.1.
- `03_Arquitectura/Architecture_Blueprint.md` v2.0.
- `00_Gobierno/Matriz_Autoridad_Documental.md` v2.4.
- `04_Reglas/Rule_Dependency_Matrix.md` v1.3.
- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md`.

## 3. Hallazgos

### VF-A01 — Catálogo de restricciones

La matriz metodológica exige un catálogo de restricciones críticas y no críticas, pero no se identifica todavía una fuente especializada que lo cierre por operación/dominio.

**Estado: ABIERTO.**

### VF-A02 — Valor

“Valor aceptable” está definido como dimensión conceptual, no como criterio operativo autorizado.

**Estado: ABIERTO.**

### VF-A03 — Riesgo

La arquitectura identifica proveedor/riesgo como capa de entrada, pero no queda demostrado un criterio de criticidad específico de Viability.

**Estado: ABIERTO.**

### VF-A04 — Sostenibilidad

Existe como dimensión arquitectónica, pero no se localiza metodología específica que determine qué evidencia y condiciones son exigibles.

**Estado: ABIERTO.**

### VF-A05 — Condiciones

El estado `VIABLE_CON_CONDICIONES` está bien delimitado semánticamente, pero falta catálogo autorizado de condiciones y su efecto.

**Estado: ABIERTO.**

### VF-A06 — Consolidación

No existe todavía una regla autorizada que determine cómo consolidar múltiples restricciones sin compensación indebida.

**Estado: ABIERTO.**

### VF-A07 — Dependencias con capas 1–5

La arquitectura enumera PRICE, TCO, STK, FIN y Supplier/Risk como posibles entradas, pero no demuestra para cada restricción cuáles son obligatorias, opcionales o irrelevantes.

**Estado: ABIERTO.**

### VF-A08 — Umbrales

No se identifica autoridad específica para convertir conceptos de viabilidad en umbrales empresariales.

**Estado: ABIERTO.**

### VF-A09 — Contradicciones

La metodología exige tratamiento explícito, pero no existe todavía precedencia específica para contradicciones materiales entre capas/fuentes dentro de Viability.

**Estado: ABIERTO.**

### VF-A10 — Evidencia insuficiente

`NO_EVALUABLE` está correctamente separado de `NO_VIABLE`, pero falta cerrar el catálogo de ausencia que impide evaluar frente al que permite continuar con advertencia.

**Estado: ABIERTO.**

## 4. Hallazgo transversal

La arquitectura y la matriz metodológica sí autorizan el **perímetro y los estados** de Viability, pero no autorizan todavía la lógica cuantitativa/operacional necesaria para producirlos de forma implementable.

No debe inferirse que una salida de PRICE, TCO, STK, FIN o Supplier/Risk sea automáticamente una restricción de Viability.

## 5. Salvaguardas

No se autoriza:

- scoring agregado;
- pesos compensatorios;
- umbrales inventados;
- fórmulas de viabilidad por inferencia;
- creación de parámetros para rellenar huecos;
- conversión de `NO_EVALUABLE` en estado negativo o positivo;
- segundo CRC;
- recomendación automática;
- integración técnica con O1.

## 6. Decisión de auditoría

**VIABILITY FRONTIER — NO APTO PARA CONTRATO TÉCNICO.**

La siguiente fase autorizada es **DEPURAR**, contrastando VF-M01…VF-M10 con fuentes documentales adicionales antes de decidir si existe autoridad suficiente o si es necesaria una decisión empresarial explícita.
