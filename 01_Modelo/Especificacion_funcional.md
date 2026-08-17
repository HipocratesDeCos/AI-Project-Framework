# DOC-005 - FUNCTIONAL SPECIFICATION

Versión: 1.0
Estado: En desarrollo

---

# Objetivo

Definir el funcionamiento funcional del Sistema Inteligente de Decisión de Adquisiciones.

Este documento describe QUÉ hace el sistema.

No describe CÓMO se implementa.

---

# Actor principal

CEO

---

# Actor secundario

Responsable de Compras

---

# Objetivo del usuario

Conocer si una compra debe:

- Aceptarse
- Negociarse
- Rechazarse

antes de comprometer recursos financieros.

---

# Flujo principal

1. Seleccionar artículo.

2. Introducir:

    • Precio ofertado

    • Cantidad

3. Ejecutar simulación.

4. Analizar resultados.

5. Tomar decisión.

---

# Información utilizada

El sistema consultará:

- Balance de situación
- Histórico de compras
- Histórico de ventas
- Stock disponible
- Rotación
- Márgenes
- Proveedores
- Plazos de pago
- Liquidez
- Fondo de Maniobra
- Ratios financieros

---

# Resultado esperado

El sistema emitirá una recomendación razonada.

Nunca decidirá por el usuario.
