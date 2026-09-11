# EIOS — R-ENT-001 · Vertical Integration Depuration v0.1

**Estado:** DEPURADO — PENDIENTE DE AUDIT 2 FINAL  
**Fecha:** 11/09/2026

## 1. Aclaraciones incorporadas

La unidad se define como **prueba de composición contractual aislada**, no como ejecución completa del Vertical.

Se fijan dos límites:

```text
adapt_c0((assessment,), (trace,))
→ demuestra compatibilidad contractual de R-ENT-001 con el adapter C0
→ NO demuestra que ese único Assessment represente todo C0
```

```text
resolve_crc([assessment], metadata, base_result explícito)
→ demuestra la contribución normativa aislada de R-ENT-001
→ NO constituye la decisión completa del Vertical
```

## 2. Alcance físico

Permanece exclusivamente:

```text
tests/test_r_ent_001_vertical_integration.py
```

Código productivo nuevo: **0**.

## 3. Invariantes

- metadata R2/ALTA solo como fixture autorizado;
- `base_result` siempre explícito;
- Trace construido con `build_trace()` existente;
- C0 adapter existente, sin adapter ENT adicional;
- CRC existente, sin registry global;
- ninguna recomendación ejecutable ni decisión humana automatizada.

## 4. Estado

**DEPURACIÓN COMPLETADA.**  
Procede AUDIT 2 FINAL.
