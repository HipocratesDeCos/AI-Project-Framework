# TCO Core — Implementation Contract v0.1

**Estado:** CERRADO PARA IMPLEMENTACIÓN DEL CORE
**Fase:** 8 — Implementación Técnica
**Dominio:** Price Intelligence / Total Cost of Ownership
**Autoridad:** MED / arquitectura EIOS vigente
**Extensiones:** Fuera de alcance — GAP-TCO-01

---

## 1. Propósito

Este contrato define el comportamiento mínimo implementable del **TCO Core v0.1** para calcular el coste total atribuible a una propuesta de compra cuando los datos requeridos son suficientes, consistentes y comparables.

El contrato materializa únicamente el núcleo determinista suficientemente definido. No crea nuevas reglas empresariales, parámetros ni autoridad decisional.

## 2. Objeto de evaluación

El contexto funcional de evaluación es una **propuesta de compra**, conforme a la especificación funcional existente.

La propuesta puede contener, entre otros, artículo, proveedor, cantidad, precio unitario, importe total, fechas y condiciones comerciales.

La granularidad física interna de la propuesta no se redefine aquí: TCO consume el objeto de entrada conforme al modelo canónico existente.

## 3. Autoridad y fronteras

TCO:

- calcula un resultado económico analítico;
- no decide la acción de compra;
- no modifica la propuesta de compra;
- no modifica C0;
- no modifica C1 ni recalcula su inteligencia de precios;
- no modifica parámetros del sistema;
- no sustituye Finanzas;
- no sustituye Stock;
- entrega su resultado al flujo coordinador del MED.

## 4. Entrada

La entrada debe proporcionar la información económica necesaria para los componentes TCO aplicables.

Como mínimo conceptual:

- identificación del artículo/referencia;
- cantidad cuando sea necesaria para el cálculo;
- precio de adquisición o resultado de precio que corresponda consumir;
- moneda;
- costes directamente atribuibles disponibles;
- contexto temporal disponible cuando una regla aplicable lo requiera.

Los nombres físicos de clases, campos o interfaces deberán seguir el modelo canónico del repositorio y no se crean mediante este contrato.

## 5. Componentes del TCO Core

El núcleo admite conceptualmente componentes directamente atribuibles a la adquisición, entre ellos:

- precio de adquisición;
- transporte atribuible;
- seguro atribuible;
- arancel atribuible;
- impuestos no recuperables;
- manipulación atribuible;
- inspección atribuible;
- merma directamente atribuible.

La inclusión efectiva de un componente exige que sea aplicable y que exista información suficiente y válida para calcular su contribución.

## 6. Atribución

Un coste solo puede contribuir al TCO Core si existe una relación trazable entre el coste y la propuesta de compra evaluada.

No se incorporarán costes generales de empresa por mera disponibilidad.

La ausencia de una regla de atribución no autoriza a estimar o imputar el coste.

## 7. Aplicabilidad, disponibilidad y determinabilidad

Estas tres dimensiones son independientes:

1. **Aplicabilidad:** determina si el componente corresponde a la propuesta.
2. **Disponibilidad:** determina si están disponibles los datos necesarios.
3. **Determinabilidad:** determina si, con los datos disponibles y las reglas aplicables, puede obtenerse un valor válido.

No se colapsarán estas dimensiones en un único estado semántico inventado por TCO.

## 8. Ausencia e insuficiencia

Una entrada ausente no equivale a cero.

Si un componente aplicable requiere un dato que no está disponible, TCO no debe sustituirlo silenciosamente por cero ni inventar un valor.

La insuficiencia debe conservarse en el resultado para que la capa decisional pueda valorar su impacto.

## 9. Contradicciones

Cuando existan datos incompatibles o contradictorios, TCO no corregirá silenciosamente uno de ellos.

Ejemplo conceptual:

`cantidad × precio unitario != importe total`

La discrepancia debe conservarse como condición que afecta a la determinabilidad del cálculo, conforme a la semántica canónica que se materialice en la implementación.

**Limitación v0.1:** el modelo físico canónico `PurchaseOperation` actualmente no contiene un `importe_total` independiente. Por tanto, esta comprobación no es ejecutable con la entrada C0 actual y queda registrada como `GAP-TCO-02`; TCO no introduce un campo paralelo ni modifica C0 para resolverla.

## 10. Moneda

Los componentes agregados deben ser monetariamente comparables.

TCO Core no inventa tipos de cambio, fechas de conversión ni fuentes de FX.

Si los componentes están expresados en monedas incompatibles y no existe una normalización autorizada disponible, no se realizará una agregación monetaria silenciosa.

La política completa de FX queda fuera de este contrato hasta que exista autoridad documental suficiente.

## 11. Temporalidad

Las fechas y condiciones temporales de la propuesta son datos de entrada y no adquieren automáticamente significado de valoración TCO.

TCO no asume una fecha universal de valoración ni transforma automáticamente un plazo de pago en coste financiero.

Las extensiones que requieran una política temporal específica permanecen fuera del Core.

## 12. Cálculo

El TCO Core se define conceptualmente como la suma de las contribuciones válidas de los componentes aplicables y determinables:

`TCO = suma de contribuciones válidas`

La fórmula anterior no autoriza la incorporación de componentes para los que falte una regla de atribución o cálculo.

No se aplicarán estimaciones implícitas.

## 13. Resultado

El resultado debe conservar, como mínimo semántico:

- valor TCO cuando sea determinable;
- desglose de componentes contribuyentes;
- componentes aplicables no determinables;
- causas de insuficiencia o contradicción cuando existan;
- información necesaria para mantener la trazabilidad del cálculo.

Los nombres físicos de campos de salida se adaptarán al modelo canónico del repositorio durante la implementación.

Un resultado con componentes aplicables no determinables conserva `value = None` y registra esos componentes como no resueltos; no se presenta como un TCO completo.

## 14. Trazabilidad

Cada contribución deberá poder relacionarse con:

- el dato de entrada utilizado;
- la regla aplicable;
- el componente TCO correspondiente;
- cualquier transformación necesaria y autorizada.

TCO no genera una autoridad documental nueva mediante la trazabilidad.

## 15. No duplicación

TCO puede consumir resultados o datos pertenecientes a otros dominios, pero no asume su propiedad funcional.

En particular:

- precio/inteligencia de precios → C1;
- liquidez, tesorería y capacidad financiera → Finanzas;
- stock y proyección de stock → Stock;
- coordinación e integración decisional → MED.

Consumir un resultado no transfiere su autoridad.

## 16. Invariantes ejecutables

**I-TCO-01 — No autoridad decisional**

TCO no puede producir directamente una decisión COMPRAR, NEGOCIAR, COMPRAR CONDICIONADO o NO COMPRAR.

**I-TCO-02 — No modificación de fuentes**

El cálculo TCO no modifica C0, C1, parámetros ni datos fuente.

**I-TCO-03 — Ausencia ≠ cero**

Un dato ausente nunca se convierte implícitamente en cero.

**I-TCO-04 — No mezcla monetaria silenciosa**

Importes incompatibles por moneda no pueden agregarse sin normalización autorizada.

**I-TCO-05 — Atribución obligatoria**

Un coste sin relación trazable con la propuesta no contribuye al TCO Core.

**I-TCO-06 — No corrección silenciosa**

Una contradicción entre datos de entrada no se resuelve seleccionando arbitrariamente un valor. La comparación contra `importe_total` queda bloqueada mientras C0 no proporcione ese dato independiente (`GAP-TCO-02`).

**I-TCO-07 — No estimación implícita**

La ausencia de una regla o dato no autoriza una estimación automática.

**I-TCO-08 — No extensión implícita**

Las materias incluidas en GAP-TCO-01 no pueden implementarse como parte del Core por interpretación del desarrollador.

## 17. Errores y condiciones no determinables

La implementación distingue entre:

- entrada estructuralmente inválida;
- componente no aplicable;
- dato requerido ausente;
- dato incompatible o contradictorio;
- cálculo no determinable;
- moneda no comparable.

Los códigos y nombres concretos de error siguen las convenciones físicas de la implementación TCO; este contrato no crea una taxonomía global de errores.

## 18. Exclusiones

Quedan fuera de TCO Core v0.1:

- financiación;
- coste de capital;
- coste de oportunidad;
- almacenamiento;
- obsolescencia;
- exceso de stock;
- devoluciones cuando requieran una política económica adicional;
- cualquier coste derivado sin regla de atribución y cálculo autorizada;
- motor propio de FX;
- política propia de valoración temporal.

## 19. GAP-TCO-01

**Definición:** falta de especificación normativa suficiente para determinar qué costes derivados o financieros deben incorporarse al TCO y bajo qué reglas de atribución, temporalidad y cálculo.

Este GAP no constituye autorización de implementación.

Cualquier ampliación futura deberá diseñarse, auditarse y cerrarse como extensión normativa antes de su materialización.

## 20. GAP-TCO-02

**Definición:** el modelo canónico C0 `PurchaseOperation` no contiene un `importe_total` independiente que permita comprobar la contradicción `cantidad × precio_unitario != importe_total`.

Este GAP no autoriza a duplicar el campo dentro de TCO ni a modificar C0 sin una decisión específica de gobierno del modelo canónico.

## 21. Relación con el MED

TCO entrega un resultado analítico al MED.

El MED conserva la autoridad para integrar TCO con los demás resultados y determinar si la evidencia disponible permite continuar hacia una recomendación o si corresponde `INFORMACIÓN INSUFICIENTE`.

## 22. Estado de implementación

**Contrato:** cerrado para implementación del Core v0.1.

**Implementación física:** materializada.

**Tests físicos:** materializados y alineados con la semántica de ausencia/incompletitud.

**CI:** verificada satisfactoriamente en los runs `#270` y `#271`.

**Extensiones:** bloqueadas por GAP-TCO-01.

**GAP de modelo:** GAP-TCO-02 permanece abierto y no se implementa mediante modificación de C0.

---

## Historial

### v0.1

Primera materialización del contrato TCO Core tras auditoría conceptual y Auditoría 2 global.

Principio rector: materializar únicamente comportamiento suficientemente definido y mantener explícitamente fuera del Core toda decisión económica no autorizada por el baseline.

### v0.1.1

Alineación post-implementación: se documenta GAP-TCO-02 y se formaliza el tratamiento de componentes aplicables con importe ausente como resultado no determinable, sin convertir la ausencia en cero.
