# EIOS — Configuration Center UI Contract — Depuración v0.1

**Fecha:** 2026-09-13  
**Origen:** Audit 1 sobre `7ddf1a5ccb379749ab51264dcde5507f92bd60f9`  
**Resultado:** COMPLETADA

## Reajustes incorporados

1. **Actor confiable:** `actor` deja de ser cualquier dato potencialmente suministrable por Presentation; debe provenir del contexto autorizado.
2. **Ámbito empresarial confiable:** `company_id` no puede ser libre; solo se seleccionan ámbitos entregados como autorizados.
3. **Revalidación pre-write:** después de confirmación humana y antes de aplicar se revalida contra estado vigente; los conflictos fallan cerrado.
4. **Explicación ≠ simulación:** se permite explicación semántica autorizada, pero no predicción cuantitativa ni recálculo de decisiones sin productor autorizado.

## Efecto

No cambia autoridad funcional, Catálogo, Rules, CRC, SQL ni backend de parametrización. La depuración endurece exclusivamente la frontera de UI y preserva trazabilidad, aislamiento empresarial y control humano.
