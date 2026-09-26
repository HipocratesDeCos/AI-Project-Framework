# EIOS — Frontera de presentación sintética para compras v0.1

**Base auditada:** `main @ fa7654239c8c6d132d24574de06ee20c0a517daf`  
**Estado:** DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR (frontera); materialización visual pendiente de una unidad separada.

## DISEÑAR

Una futura demostración para una persona de compras puede explicar un caso
ficticio mediante resultados de referencia ya producidos. Debe ser una
proyección de lectura de un paquete sintético validado. El archivo
`reference-review.html` conserva su función de inspección técnica local; no
se presenta como pantalla de trabajo ni como resultado de una empresa real.

## AUDITAR — autoridades y material disponible

| Fuente | Aporta | Límite para esta unidad |
|---|---|---|
| `03_App/UI_Field_Registry_v0.1.md` y `UI_Field_Component_Mapping_v0.2.md` | Campos y representaciones de una futura interfaz | No autorizan poblar campos ausentes del paquete ni inventar cálculos STK. |
| `03_App/UI_Interaction_Screen_Specification_v0.1.md` | Orden de contexto, propuesta, resultados y trazabilidad | Incluye entradas y configuración; no convierte esta demostración en pantalla interactiva. |
| `03_App/UI_Architecture_Contract_v0.1.md` | Separación de presentación y autoridad de dominio | La vista consume resultados, no ejecuta reglas ni reescribe trazas. |
| `Reference_Business_Case_001_Read_Only_Review_Contract_v0.1.md` | Comparación técnica local, huellas y controles QTG | Su HTML no es una experiencia de comprador. |
| U1.5C `Designated_Synthetic_Preview_Artifact` | Vista de un `LocalSyntheticPreviewAdmission` exacto y U1.3 retenido | No acepta terminales del caso de referencia ni sus observaciones; no hay conversión autorizada. |
| Runner y capturas `reference_*_observation` | Terminales y ocho pares de observaciones de ambas variantes | Solo evidencia sintética; varias capturas declaran límites de derivación y suficiencia. |

## DEPURAR — proyección permitida

El recorrido de demostración podrá mostrar, con atribución al fixture:

1. **Contexto ficticio y alcance:** identificador de caso, variante y aviso
   visible `SYNTHETIC · SYNTHETIC_TEST_ONLY · FORBIDDEN ·
   NO_OPERATIONAL_EFFECT · decision_authority=false`.
2. **Calidad de entrada:** estado y confianza QTG junto a motivos de los
   controles, distinguiendo `NO_APTO` de `APTO`; este último no es admisión
   operacional.
3. **Análisis descriptivo:** PRICE, TCO, Supplier Risk/Value, C0/CRC,
   Decision Twin, Scenario Coordination, Negotiation Intelligence y Ladder
   únicamente cuando las dos capturas correspondientes estén presentes y
   validadas contra sus terminales. Conservar ausencias, limitaciones y
   referencias en vez de rellenarlas por inferencia.
4. **Trazabilidad:** huellas y referencias del paquete, con la aclaración de
   que una huella comprueba consistencia del archivo, no autenticidad externa.

`COMPLETED` etiqueta ejecución técnica; QTG etiqueta calidad de entrada;
`AUTHORIZED` en contenido ficticio de negociación no acredita mandato de
empresa; CRC y la secuencia Ladder no son instrucciones de compra. Los
escenarios no se ordenan por una diferencia puramente estructural ni se
declara ganador. No se muestran valores de cobertura o rotación STK sin
metodología autorizada, ni campos de empresa real que el fixture no contiene.

La vista resultante será estática, local y sin controles de acción, petición
de red, persistencia, admisión operacional o mutación de los JSON. Un aviso
de material sintético debe permanecer visible junto a cualquier resultado.

## AUDITAR 2 — condiciones verificables para materializar

- Reutilizar validadores de terminales y observaciones existentes; rechazar
  capturas parciales, variantes invertidas, huellas inválidas y discrepancias
  de binding entre observaciones relacionadas.
- Probar que el HTML escapa datos, distingue el caso negativo del elegible y
  conserva el aviso y las limitaciones aunque falten observaciones opcionales.
- Probar que ninguna etiqueta `APTO`, `COMPLETED` o `AUTHORIZED` aparece como
  permiso operacional, decisión empresarial o contacto con proveedor.
- Verificar generación y repetición del paquete por el CLI existente antes
  de añadir una opción de exportación separada para la nueva vista.

## CERRAR

Esta auditoría cierra el **límite de representación**, no una interfaz de
compras operacional. La siguiente unidad concreta será una proyección de
lectura tipada y un HTML de demostración sintética, derivados de los artefactos
validados, sin reutilizar U1.5C con un tipo de entrada incompatible ni alterar
el visor técnico existente. Su propio ciclo deberá completar
DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI.

## MATERIALIZAR / CI

La materialización de esta unidad es este registro de auditoría y frontera.
La futura vista requiere implementación, pruebas y CI propios; ningún HTML
para compradores queda aprobado por este documento.
