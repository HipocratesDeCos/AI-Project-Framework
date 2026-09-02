# EIOS — O4 · CIERRE

**Estado:** 🔒 CERRADO — DISEÑO AUTORIZADO PARA MATERIALIZACIÓN
**Baseline:** `ad7961935cc19ca4ab0a19dbef0ac9d4721c8374`
**Diseño depurado:** `e74afaa457046faa375f6ac07c6f98e5b0a03261`
**Auditoría 1:** `93f19d961abb45f8800cc8cf377ff88c9989f3fc`
**Auditoría 2:** `259c7b534b78615ffc5e756aab5b53409a027c71`

## Dictamen

O4 queda cerrado como alcance de diseño para generación y exploración controlada de escenarios.

El diseño no modifica `main`, contratos cerrados, modelos, reglas, parámetros, evidencia, RDM, Viability Frontier, Decision Twin, Negotiation ni CRC.

## Alcance cerrado

- espacio de variables explícitamente autorizado;
- dominios finitos;
- cardinalidad previa a expansión;
- límites duros con precedencia definida;
- generación determinista;
- enumeración y producto cartesiano finito para MVP;
- deduplicación canónica;
- poda exclusivamente estructural y declarada;
- estados técnicos de generación;
- trazabilidad reproducible;
- subordinación de representación/versionado a O2;
- evaluación separada mediante O3.

## Exclusiones

No quedan autorizados en este cierre:

- optimización;
- ranking;
- selección automática;
- recomendación;
- negociación automática;
- aprendizaje adaptativo;
- búsqueda ilimitada;
- persistencia;
- API;
- SQL;
- nuevo modelo de datos.

## Condición de materialización

La implementación técnica solo podrá comenzar en esta rama mediante un cambio posterior que materialice exactamente el contrato cerrado y sus pruebas de frontera.

Deberán comprobarse como mínimo:

1. cardinalidad cero, uno y múltiple;
2. dominio vacío;
3. límite exacto;
4. límite excedido;
5. profundidad excedida;
6. deduplicación;
7. invariancia al orden de entrada;
8. poda estructural;
9. `NOT_EVALUABLE` por espacio indeterminable;
10. ausencia de mutación del padre y operación real.

Cualquier expansión de autoridad o semántica constituye nuevo alcance y requiere reapertura formal.

**CIERRE O4 — SUPERADO.**