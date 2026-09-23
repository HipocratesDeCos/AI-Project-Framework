# EIOS — ROT002 Sales Activity Window Provenance Audit 1 v0.1

**Baseline:** `main @ d0e94c47eb8d1622c2fbb3125c7e1da63756e4fc`  
**Fecha:** 23/09/2026  
**Objeto:** `08_Implementacion/ROT002_Sales_Activity_Window_Provenance_Contract_v0.1.md`  
**Estado:** AUDIT 1 — 1 HALLAZGO BLOQUEANTE / 3 CORRECCIONES

## 1. Hallazgo A1 — company_id no existe en PurchaseOperation

El contrato diseñado pretende validar el scope empresarial de `P-ROT-001` a partir de:

```text
PurchaseOperation
DecisionContext
ResolvedConfiguration(P-ROT-001)
```

pero `PurchaseOperation` no contiene `company_id`.

Por tanto, una implementación basada solo en esos objetos no puede demostrar:

```text
ResolvedConfiguration.company_id == company_id de la decisión
```

sin introducir un argumento adicional o una identidad paralela.

### Corrección obligatoria

La frontera debe anclarse en `DecisionInputPackage`, que ya contiene de forma canónica:

```text
company_id
effective_at
purchase
context
configurations
missing_parameter_ids
evidence
```

y ya valida la identidad PurchaseOperation ↔ DecisionContext y el binding de configuración por empresa/contexto.

**Resultado:** BLOQUEANTE HASTA DEPURAR.

## 2. Hallazgo A2 — evitar ResolvedConfiguration desprendida

La autoridad exige `ResolvedConfiguration(P-ROT-001) + Evidence`.

Si la API pública acepta una `ResolvedConfiguration` separada del aggregate DIP, se reabre una ruta de provenance desprendida similar a las ya cerradas en Finance/PRICE.

### Corrección

La frontera pública debe localizar `P-ROT-001` dentro de:

```text
DecisionInputPackage.configurations
```

y comprobar que:

```text
P-ROT-001 ∈ requested_parameter_ids
P-ROT-001 ∉ missing_parameter_ids
exactamente una configuración P-ROT-001 está presente
```

No debe aceptar el valor o resolución como argumento público separado.

**Resultado:** CORRECCIÓN NECESARIA.

## 3. Hallazgo A3 — effective_at

La autoridad exige vigencia aplicable y binding a Parameters_Version.

`DecisionInputPackage.effective_at` ya es la fecha/hora canónica con la que el Centro resolvió las configuraciones capturadas.

### Corrección

No crear un segundo `effective_at` en la frontera ROT.

Debe validarse:

```text
resolution.effective_at == DIP.effective_at
resolution.parameters_version == DIP.context.parameters_version
resolution.company_id == DIP.company_id
```

**Resultado:** CORRECCIÓN NECESARIA.

## 4. Hallazgo A4 — Evidence de configuración

`ResolvedConfiguration.configuration_ref` es referencia técnica estable, no prueba empresarial por sí sola.

El contrato debe conservar la exigencia de Evidence, sin afirmar que el DIP autentica el Centro o las fuentes externas.

### Corrección

La futura frontera debe exigir una `Evidence` DEMONSTRATED aplicable a la configuración o un binding equivalente ya autorizado; no debe promover `configuration_ref` a autoridad de evidencia.

La definición exacta del criterio de correspondencia debe reutilizar el contrato C0/Evidence vigente y no inventar semántica nueva.

**Resultado:** CORRECCIÓN NECESARIA.

## 5. No hallazgos

Se consideran conformes:

- nombre `SalesActivityWindowEvidence`;
- estados Track A;
- ventana inclusiva;
- `PurchaseOperation.operation_date` como evaluation_date;
- entero positivo en días;
- no fallback;
- separación Track A / Rules / CRC;
- prohibición de convertir cero filas o net zero en cero ventas;
- revalidación provenance-safe.

## 6. Dictamen

```text
DISEÑAR   ✅
AUDITAR   ✅
DEPURAR   ⏳ obligatorio
AUDITAR 2 ⛔ todavía no
```

**Bloqueador:** la frontera debe usar `DecisionInputPackage` como raíz provenance-safe y no aceptar una configuración P-ROT-001 desprendida.
