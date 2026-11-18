# EIOS — F7.1 · PUBLIC API BASELINE & COMPATIBILITY MANIFEST

**Fecha:** 18/11/2026  
**Base:** `main @ f4f5add8aba2ad9ddcb041e6b1db6d6a50c58a34`

## 1. PROPÓSITO

F7.1 inicia la Fase 7 fijando, por primera vez, la **superficie pública estable del Motor neutral**.

El objetivo no es cambiar el Motor ni ampliar capacidades. El objetivo es poder detectar de forma automática cuándo una modificación futura rompe la interfaz que consumen proyectos externos.

## 2. SUPERFICIE PÚBLICA DECLARADA

Se consideran públicos, en esta baseline, únicamente estos cuatro paquetes neutrales:

- `eios-kernel==0.1.0`
- `eios-input-contracts==0.1.0`
- `eios-capability-catalog==0.1.0`
- `eios-catalog-governance==0.1.0`

Módulos públicos:

- `eios.kernel.execution`
- `eios.input_contracts`
- `eios.capability_catalog`
- `eios.catalog_governance`

F7.1 registra exactamente sus exports públicos, funciones, forma de parámetros, campos de modelos Pydantic/dataclasses, enums, constantes API y versión de distribución.

## 3. LO QUE NO ES API PÚBLICA DEL MOTOR

Quedan fuera de esta baseline:

- módulos privados o con prefijo `_`;
- `tools/`;
- fixtures de pruebas;
- aplicaciones UI;
- `eios.core` de contratos específicos;
- `eios.pricing`;
- `eios.tco`;
- `eios.company_app`;
- cualquier implementación empresarial externa.

Esto es deliberado: no debe convertirse toda la base de código en una obligación de compatibilidad perpetua.

## 4. REGLA DE COMPATIBILIDAD

La numeración SemVer **no implica por sí sola compatibilidad**.

Una modificación futura que altere cualquiera de los elementos públicos fijados por este manifiesto debe:

1. ser detectada por CI;
2. declarar una nueva baseline o una política de compatibilidad explícita;
3. aportar evidencia de migración/compatibilidad antes de aceptarse.

Un simple cambio de número de versión no puede silenciar el gate.

## 5. IMPORTACIONES EXISTENTES

F7.1 conserva las rutas realmente consumidas hoy.

En particular, el kernel se importa desde:

`eios.kernel.execution`

No se crea ahora un nuevo `eios.kernel.__init__` solo para uniformar estética, porque eso sería modificar la superficie en la misma unidad cuyo objetivo es medirla.

## 6. GATE EJECUTABLE

`tools/verify_f7_1_public_api_baseline.py` compara el código actual con:

`08_Implementacion/phase7_public_api_baseline_v0.1.json`

Bloquea, entre otros:

- export eliminado o añadido sin actualizar evidencia;
- firma de función modificada;
- campo público añadido/eliminado/reordenado;
- enum cambiado;
- constante API cambiada;
- versión de distribución divergente;
- promoción accidental de módulos de negocio al baseline neutral.

## 7. LÍMITES

F7.1 no define aún:

- compatibilidad entre dos releases diferentes;
- ventanas de deprecación;
- migraciones automáticas;
- rollback de paquete;
- política de soporte temporal;
- release estable 1.0.

Esos son frentes posteriores de F7.

F7.1 tampoco concede ninguna autoridad operacional:

- `production_authorized=false`
- `decision_authority=false`
- `operational_path=FORBIDDEN`

## 8. CRITERIO DE CIERRE

F7.1 queda cerrada si:

- el baseline refleja exactamente la API pública actual;
- pruebas positivas y adversarias pasan;
- CI Python/SQL y regresiones F4–F6 siguen verdes;
- no se modifica comportamiento del Motor;
- no se altera código bajo `eios/`;
- PR y CI post-merge son verdes sobre SHA exactos.
