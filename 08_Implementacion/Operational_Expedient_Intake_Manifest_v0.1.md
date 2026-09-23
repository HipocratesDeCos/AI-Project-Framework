# EIOS — Operational Expedient Intake Manifest v0.1

**Baseline:** `main @ 013dfd4a5c6e90f2b6f6f97e944447cbb1412a9e`  
**Fecha:** 23/09/2026  
**Estado:** IMPLEMENTACIÓN DERIVADA — SIN NUEVA AUTORIDAD

## Propósito

Crear una capa de entrada previa al preflight que responda únicamente:

> ¿Están referenciados todos los bloques documentales obligatorios para empezar a construir el expediente?

No responde:

- si los documentos son auténticos;
- si los datos son correctos;
- si el mandato es válido;
- si la revisión humana es suficiente;
- si el expediente es estructuralmente admisible;
- si QTG será APTO.

## Estados

```text
REQUIRED_SET_COMPLETE
REQUIRED_SET_INCOMPLETE
```

`REQUIRED_SET_COMPLETE` significa solo que todos los ítems marcados REQUIRED tienen al menos una referencia no vacía.

## Ítems CONDITIONAL

Se conservan separados:

- parameter_p_fin_002;
- treasury_additional_material.

Su ausencia no se considera error en intake. La necesidad real se resolverá después por los contratos de dominio correspondientes.

## Flujo

```text
Intake Manifest
→ construcción de objetos de dominio
→ ProjectionMaterialEnvelope
→ OperationalAdmissionPreflight
→ QTG OPERATIONAL
```

## Salvaguarda

El manifest no almacena contenido, no fabrica documentos y no permite transformar una referencia en evidencia demostrada.
