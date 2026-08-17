# TCO_04_Transporte

**Proyecto:** EIOS — Enterprise Intelligent Operations System  
**Capa:** CAPA 2 — TCO  
**Versión:** 0.3  
**Estado:** PROPUESTA — pendiente de aprobación

---

## 1. Propósito

Definir cómo debe tratar EIOS el transporte asociado a una operación de compra dentro del **TCO directo**.

El transporte pertenece a CAPA 2 cuando constituye un coste directamente atribuible a adquirir y recibir la mercancía de la operación analizada.

---

## 2. Principio fundamental

Debe distinguirse entre:

- precio del producto;
- transporte;
- TCO directo.

Por tanto:

> **Precio ≠ TCO**

El transporte puede incrementar el coste real de adquisición aunque no modifique el precio nominal del producto.

---

## 3. Transporte directamente atribuible

Se incluye en CAPA 2 cuando el coste:

1. está relacionado con la operación analizada;
2. puede atribuirse razonablemente a ella;
3. forma parte del coste necesario para recibir la mercancía.

Ejemplos:

- transporte contratado específicamente para la compra;
- porte indicado en la oferta;
- transporte facturado por el proveedor para esa operación;
- coste de una agencia de transporte contratada para el pedido.

---

## 4. Transporte incluido en el precio

Si el proveedor ofrece:

> **18,50 €/unidad, transporte incluido**

No debe añadirse nuevamente un coste de transporte.

EIOS debe registrar la condición de transporte incluido para evitar doble contabilización.

---

## 5. Transporte facturado por separado

Ejemplo:

Precio mercancía: 18,50 €/unidad  
Transporte: 250 €  
Cantidad: 1.000 unidades

Coste de transporte unitario:

250 / 1.000 = 0,25 €/unidad

Coste antes de otros componentes directos:

18,50 + 0,25 = 18,75 €/unidad

El TCO deberá incorporar ambos componentes.

---

## 6. Coste de transporte fijo

Cuando el transporte sea un importe fijo independiente de la cantidad:

**Transporte unitario = Coste transporte / cantidad adquirida**

La distribución deberá conservar:

- coste total;
- cantidad utilizada para la distribución;
- coste unitario resultante.

---

## 7. Transporte variable

Cuando el transporte dependa de variables como:

- peso;
- volumen;
- distancia;
- número de bultos;
- tipo de mercancía;
- urgencia;
- condiciones especiales;

EIOS deberá utilizar el coste disponible para la operación concreta.

No debe inventar un coste cuando la información no exista.

---

## 8. Pedido con cantidad mínima de transporte

Si un proveedor establece:

> Transporte mínimo: 100 €

y el coste calculado del envío sería 70 €:

El coste aplicable a la operación será 100 €.

La condición contractual deberá quedar registrada.

---

## 9. Transporte gratuito condicionado

Debe diferenciarse entre:

### Transporte gratuito confirmado

La oferta actual establece que el transporte no tendrá coste.

→ No añadir coste de transporte.

### Transporte gratuito condicionado

Ejemplo:

> Transporte gratuito a partir de 1.000 €.

EIOS debe comprobar si la operación cumple actualmente la condición.

Si no la cumple:

→ no tratar el transporte gratuito como beneficio cierto.

---

## 10. Transporte y negociación

El transporte puede constituir una variable negociable.

Ejemplo:

Precio: 18,50 €  
Transporte: 300 €

Alternativa negociada:

Precio: 18,50 €  
Transporte: gratuito

El nuevo escenario deberá recalcular el TCO.

El escenario anterior se conserva.

---

## 11. Transporte asociado a varios productos

Cuando un mismo transporte corresponda a varias referencias, EIOS deberá distribuir el coste mediante un criterio definido.

Posibles bases conceptuales:

- unidades;
- peso;
- volumen;
- valor;
- bultos.

No debe elegirse arbitrariamente cuando una base más adecuada esté disponible.

El criterio utilizado debe quedar trazado.

---

## 12. Transporte no imputable de forma fiable

Si un transporte afecta a varias operaciones y no existe información suficiente para asignarlo razonablemente:

**INFORMACIÓN INSUFICIENTE**

antes que realizar una imputación ficticia.

---

## 13. Transporte y TCO

Conceptualmente:

**TCO directo = componentes directos de adquisición + transporte directamente atribuible + otros costes directos**

La fórmula completa permanecerá pendiente hasta cerrar el resto de componentes de CAPA 2.

---

## 14. Transporte y CAPA 3

El transporte directo de adquisición pertenece a:

**CAPA 2**

Los costes posteriores derivados de mantener la mercancía en stock pertenecen principalmente a:

**CAPA 3**

Ejemplo:

- transporte para recibir la mercancía → CAPA 2;
- almacenamiento posterior → CAPA 3;
- exceso de stock provocado por la cantidad → CAPA 3.

---

## 15. Transporte y CAPA 4

El transporte directo no debe confundirse con el impacto financiero de la compra.

Ejemplo:

- coste del transporte → CAPA 2;
- efecto de la operación sobre liquidez → CAPA 4;
- coste de financiación → CAPA 4.

No duplicar el mismo coste entre capas.

---

## 16. Variables mínimas

Para analizar transporte EIOS debería poder disponer, cuando proceda, de:

- transporte incluido;
- coste de transporte;
- moneda;
- cantidad;
- unidad;
- proveedor;
- transportista, si está disponible;
- condición de transporte;
- mínimo de transporte;
- fecha;
- escenario;
- criterio de reparto, si afecta a varias referencias.

---

## 17. Trazabilidad

Toda imputación de transporte deberá conservar:

- fuente del dato;
- importe;
- unidad monetaria;
- operación;
- escenario;
- criterio de reparto;
- condición aplicable.

---

## 18. Regla de seguridad

> **Un coste de transporte directamente atribuible a la compra se incorpora al TCO directo.**

> **Un transporte ya incluido en el precio no se vuelve a sumar.**

> **Un transporte condicionado solo se considera gratuito cuando la condición se cumple.**

> **Cuando la imputación no pueda justificarse, EIOS no debe inventarla.**

---

## 19. Relaciones estructurales

- [[TCO_05_Seguro]]
- [[TCO_10_Merma]]
- [[TCO_11_Fronteras]]
- [[Motor_Escenarios]]

---

## 20. Estado

**PROPUESTA v0.3 — pendiente de aprobación.**
