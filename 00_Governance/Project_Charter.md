# DOC-004 - PROJECT CHARTER

Versión: 1.0
Estado: Aprobado

---

# Nombre del Proyecto

Sistema Inteligente de Decisión de Adquisiciones (SIDA)

---

# Visión

Construir un sistema inteligente que ayude al CEO y al Responsable de Compras a negociar con proveedores utilizando información financiera, operativa y comercial en tiempo real.

El sistema no tomará decisiones.

El sistema propondrá la mejor decisión posible justificándola con datos.

---

# Objetivo principal

Evitar decisiones de compra que puedan comprometer:

- Liquidez
- Fondo de Maniobra
- Márgenes
- Rotación de stock
- Rentabilidad
- Riesgo financiero

---

# Usuarios

### Fase 1

- CEO
- Responsable de Compras

### Fase 2 (Standby)

- Comerciales

---

# Arquitectura inicial

ERP

↓

Excel

↓

Power BI

↓

SQL Server

↓

Motor de Decisión

↓

Aplicación Web / Móvil

---

# Alcance

Incluye:

- Simulación de compras
- Histórico de precios
- Histórico de proveedores
- Situación financiera
- Ratios
- Márgenes
- Stock
- Recomendaciones

No incluye:

- Facturación
- Contabilidad
- Asientos
- Gestión del ERP

---

# Principios

1. Independencia del ERP.
2. Explicabilidad de todas las recomendaciones.
3. Máxima fiabilidad.
4. Simplicidad para usuarios no financieros.
5. Escalabilidad.

---

# Indicador principal de éxito

Cada recomendación deberá contribuir a mejorar la estabilidad financiera de la empresa.
