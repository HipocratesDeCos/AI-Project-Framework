# EIOS — GAP-ID-01 Identifier Migration Contract v0.1

## Estado

**CERRADO PARA MATERIALIZACIÓN DOCUMENTAL**

Baseline: `main @ ed289c98f7ca763b01a15392424eb712d57d00c8`.

## 1. Autoridad

`02_Parametros/Decision_Log_Parametros_MVP.md` mantiene `GAP-ID-01` como **ABIERTO — MIGRACIÓN** y establece la convención:

- `P-*` para parámetros;
- `R-*` para reglas.

La numeración funcional se conserva. La migración no crea parámetros ni reglas nuevos.

## 2. Hallazgo

En el baseline:

- `02_Parametros/Matriz_Parametros_Reglas_MVP.md` ya utiliza identificadores `P-*`;
- `04_Reglas/Matriz_Reglas_MVP.md` ya utiliza identificadores `R-*`;
- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md` conserva identificadores legacy sin `P-`.

Por tanto, el gap físico restante está concentrado en el Catálogo y en el estado del Decision Log.

## 3. Migración autorizada

En `Catalogo_Parametros_MVP_v0.3.md` se normalizan únicamente los identificadores de la columna `ID`:

`XXX-NNN` → `P-XXX-NNN`.

Familias afectadas:

- `PRE-001..006` → `P-PRE-001..006`
- `STK-001..006` → `P-STK-001..006`
- `PYE-001..006` → `P-PYE-001..006`
- `MGE-001..006` → `P-MGE-001..006`
- `FIN-001..006` → `P-FIN-001..006`
- `PAG-001..005` → `P-PAG-001..005`
- `RGL-001..007` → `P-RGL-001..007`
- `DAT-001..007` → `P-DAT-001..007`

La numeración, nombres, valores iniciales, unidades, estados, severidades y editabilidad permanecen idénticos.

## 4. Reconciliación del Decision Log

Tras materializar y auditar la migración, `Decision_Log_Parametros_MVP.md` debe:

- cambiar `GAP-ID-01` a **CERRADO — MIGRACIÓN DOCUMENTAL**;
- declarar que Catálogo, Matriz P→R y Matriz de Reglas convergen en la convención `P-*` / `R-*`;
- no reabrir C-07, GAP-HIS-01, GAP-HIS-02 ni EVID-HIS-004;
- no alterar relaciones funcionales ni estados de parámetros/reglas.

## 5. Prohibiciones

No se autoriza:

- renumerar IDs;
- crear, eliminar o fusionar parámetros;
- inferir nuevas relaciones parámetro→regla;
- cambiar valores empresariales;
- modificar `05_Motor`, `06_SQL`, código o tests funcionales;
- reescribir documentos históricos solo para homogeneizar referencias;
- modificar IDs usados como ejemplos cuando no representan la identidad oficial de un parámetro.

## 6. Criterios de aceptación

1. Los 49 IDs oficiales del Catálogo llevan prefijo `P-`.
2. Cada ID coincide con la identidad correspondiente en `Matriz_Parametros_Reglas_MVP.md`.
3. Ningún valor o significado funcional cambia.
4. `GAP-ID-01` queda cerrado documentalmente.
5. El diff se limita a este contrato, Catálogo y Decision Log.
6. CI de PR y CI post-merge terminan en `SUCCESS` sobre los SHA exactos.

## 7. Dictamen de diseño

**DISEÑAR ✅ · AUDITAR ✅ · DEPURAR ✅ · AUDITAR 2 DE DISEÑO ✅ · CERRAR ✅**

Se autoriza MATERIALIZAR exclusivamente dentro de este alcance.
