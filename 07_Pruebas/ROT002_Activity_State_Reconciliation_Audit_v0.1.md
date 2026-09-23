# EIOS — ROT002 activity_state Reconciliation Audit v0.1

**Baseline:** `main @ 4cf1dd6d6b6152ed20f309d6a299b9804e70cb89`  
**Fecha:** 23/09/2026  
**Estado:** AUDIT 2 — SUPERADA  
**Objeto:** reconciliar nomenclatura del carrier `SalesActivityWindowEvidence`.

## 1. Contradicción detectada

La metodología especializada `01_Modelo/Rotation_Methodological_Design_v0.3.md` define el carrier conceptual:

```text
SalesActivityWindowEvidence
├── article_id
├── evaluation_date
├── window_start
├── window_end
├── window_authority_ref
├── source_ref
├── source_semantics_ref
├── completeness_ref
├── activity_state
├── evidence_refs
└── trace_refs
```

El contrato técnico integrado por PR #310 utilizó accidentalmente `state`.

## 2. Autoridad aplicable

Conforme a `00_Gobierno/Matriz_Autoridad_Documental.md`:

- la metodología especializada define la semántica del dominio;
- implementación puede concretar la materialización;
- implementación no puede redefinir unilateralmente la metodología.

Por tanto prevalece:

```text
activity_state
```

## 3. Corrección

Se sustituye exclusivamente el nombre físico del campo ROT:

```text
state → activity_state
```

No se modifica:

- `Evidence.state`;
- estados Track A;
- P-ROT-001;
- Evidence binding;
- ventana;
- Rules;
- CRC.

## 4. Estados conservados

```text
SALES_ACTIVITY_PRESENT
ZERO_VALID_SALES_DEMONSTRATED
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

## 5. Dictamen

```text
DISEÑAR       ✅
AUDITAR       ✅
DEPURAR       ✅
AUDITAR 2     ✅
CERRAR        ✅
MATERIALIZAR  ✅ documental
CI            ⏳ PR
```

**0 bloqueadores para materializar el carrier físico con `activity_state`.**
