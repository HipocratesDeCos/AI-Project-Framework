# 06 — SQL

## EIOS — Enterprise Intelligent Operations System

**Estado:** CERRADO — Contrato documental del dominio SQL  
**Fase:** 8 — Implementación Técnica  
**Naturaleza:** Autoridad técnica de persistencia e implementación SQL

---

# 1. Propósito

Este documento define la autoridad, el perímetro y los criterios del dominio `06_SQL` de EIOS.

`06_SQL` proporciona la persistencia y recuperación técnica de artefactos y referencias previamente definidos por las autoridades superiores del sistema.

Su finalidad es materializar técnicamente las necesidades de persistencia de EIOS sin redefinir el significado empresarial, funcional o decisional de los elementos persistidos.

`06_SQL` no constituye un motor de decisión ni una nueva autoridad funcional.

---

# 2. Naturaleza y posición

`06_SQL` pertenece al ámbito de implementación técnica y persistencia.

La relación estructural es:

```text
Autoridades funcionales y de gobierno
            ↓
   contratos y modelos autorizados
            ↓
           SQL
            ↓
 persistencia / recuperación técnica
```

SQL no determina qué conceptos necesita EIOS ni qué significado tienen.

La existencia física de una tabla, columna, índice, relación o cualquier otro elemento del esquema no crea por sí misma una autoridad funcional.

---

# 3. Autoridad del dominio SQL

`06_SQL/06_LEEME_SQL.md` tiene autoridad sobre:

- organización del dominio SQL;
- criterios técnicos de persistencia;
- convenciones técnicas del esquema;
- integridad referencial;
- relaciones de persistencia;
- criterios de recuperación técnica;
- versionado técnico del esquema;
- criterios de trazabilidad propios de la persistencia;
- límites de la implementación SQL.

Esta autoridad es exclusivamente técnica.

No tiene autoridad sobre:

- significado empresarial;
- Modelo Empresarial de Decisión;
- reglas de negocio;
- parámetros funcionales;
- evidencia;
- dependencias funcionales;
- viabilidad;
- escenarios;
- Decision Twin;
- Decision Versioning;
- evaluación C0;
- decisión empresarial humana.

---

# 4. Principio de no redefinición

SQL implementa la persistencia de conceptos previamente autorizados.

No crea, redefine, sustituye ni modifica el significado de conceptos empresariales o funcionales definidos por otras autoridades.

En particular:

```text
Autoridad funcional
        ↓
      define
        ↓
    concepto
        ↓
       SQL
        ↓
    persiste
```

No:

```text
SQL
 ↓
determina el concepto
```

Si una necesidad de persistencia revela que falta un concepto o que existe una ambigüedad funcional, la resolución debe producirse en la autoridad documental correspondiente antes de modificar el modelo SQL.

---

# 5. Relación con las autoridades existentes

La responsabilidad de SQL es técnica y subordinada a las autoridades superiores.

| Dominio | Autoridad | Papel de SQL |
|---|---|---|
| Modelo empresarial | `05_Motor/Modelo_Empresarial_Decision.md` | Persistir sus artefactos autorizados |
| Parámetros | `02_Parametros/Catalogo_Parametros_MVP_v0.3.md` / `Centro_Parametrizacion.md` | Persistir conforme al contrato autorizado |
| Reglas | `04_Reglas/Matriz_Reglas_MVP.md` | Persistir conforme al contrato autorizado |
| Evidencia | `04_Reglas/Evidence_Contract.md` | Persistir referencias y estado conforme al contrato |
| Dependencias | `04_Reglas/Rule_Dependency_Matrix.md` | Persistir conforme a su definición |
| Viabilidad | `05_Motor/Viability_Frontier.md` | Persistir resultados y referencias autorizados |
| Escenarios | `05_Motor/Viability_Scenario_Engine.md` | Persistir resultados y referencias autorizados |
| Decision Twin | `05_Motor/Decision_Twin.md` | Persistir artefactos y referencias autorizados |
| Decision Versioning | `05_Motor/Decision_Versioning.md` | Persistir referencias y artefactos conforme a su contrato |
| C0 | contratos y artefactos C0 vigentes | Persistir salidas y referencias conforme a su autoridad |
| SQL | `06_SQL/06_LEEME_SQL.md` | Definir cómo se implementa técnicamente la persistencia |

SQL no sustituye ninguna de las autoridades anteriores.

---

# 6. Versionado técnico frente a versionado funcional y decisional

El versionado técnico del esquema SQL es independiente de cualquier versión funcional o decisional de EIOS.

```text
SQL Schema Version
        ≠
Rules Version
        ≠
Parameters Version
        ≠
Scenario Version
        ≠
Decision State Version
```

SQL puede mantener mecanismos de versionado técnico del esquema y de sus migraciones.

No puede definir, sustituir ni reinterpretar:

- `Rules_Version`;
- `Parameters_Version`;
- `Scenario_Version`;
- `Decision State Version`;
- cualquier otra versión cuya autoridad corresponda a otro dominio.

La existencia de una versión técnica del esquema no implica una nueva versión funcional o decisional.

---

# 7. Relación con Decision Versioning

`Decision Versioning` mantiene la autoridad sobre la continuidad histórica del estado decisional y las referencias necesarias para su reconstrucción. `06_SQL` únicamente proporciona persistencia y recuperación técnica para los elementos que deban almacenarse.

SQL no define:

- qué es un estado decisional;
- qué es `Decision_ID`;
- qué es una `Decision State Version`;
- qué referencias son necesarias para la reconstrucción;
- qué significa una recomendación;
- qué constituye una decisión empresarial humana.

La relación correcta es:

```text
Decision Versioning
        ↓
   define / relaciona
        ↓
 referencias y estado
        ↓
        SQL
        ↓
 persistencia / recuperación
```

La recuperación física de datos por SQL no constituye por sí misma reconstrucción semántica del estado decisional.

---

# 8. `Decision_ID`

SQL puede almacenar y utilizar `Decision_ID` como identificador técnico o referencia cuando así lo requieran los contratos autorizados.

No redefine su significado.

`Decision_ID` continúa identificando la unidad decisional EIOS conforme a `Decision Versioning` y a los contratos de C0 vigentes.

No identifica por sí mismo:

- al CEO;
- al decisor humano;
- la persona que aprueba una compra;
- la decisión empresarial final.

---

# 9. C0, `Trace` e `input_fingerprint`

SQL puede persistir artefactos producidos por C0 cuando corresponda.

No puede generar un sustituto semántico de ellos ni adquirir su autoridad.

En particular:

```text
C0
 ├── InputContract
 ├── input_fingerprint
 └── Trace
          ↓
        SQL
          ↓
      persistencia
```

SQL no:

- ejecuta C0;
- redefine `Trace`;
- genera un segundo `Trace` para sustituir al de C0;
- redefine `input_fingerprint`;
- genera un fingerprint alternativo con autoridad equivalente;
- modifica el contrato de C0.

---

# 10. `Data_Snapshot_ID`

SQL puede persistir y recuperar `Data_Snapshot_ID` y los artefactos asociados cuando una autoridad superior los haya definido y su persistencia sea necesaria.

SQL no crea un concepto paralelo de snapshot ni redefine el significado de `Data_Snapshot_ID`.

La disponibilidad física de un snapshot es una condición técnica de persistencia; no convierte a SQL en autoridad sobre su semántica.

---

# 11. Fuente de verdad

El esquema SQL no constituye una fuente de verdad empresarial independiente.

Cuando exista una discrepancia entre:

- un artefacto SQL;
- y la autoridad documental responsable del concepto;

la definición y significado del concepto corresponden a la autoridad documental competente.

SQL debe adaptarse a una resolución documental válida; no resolver unilateralmente la discrepancia mediante una modificación del significado.

---

# 12. Integridad y trazabilidad técnica

SQL podrá establecer mecanismos técnicos de integridad, consistencia, relaciones, restricciones y trazabilidad de persistencia.

Estas garantías son técnicas.

No deben confundirse con:

- autoridad funcional;
- evidencia empresarial;
- evaluación decisional;
- trazabilidad semántica de C0;
- reconstrucción decisional.

Una restricción técnica puede impedir un estado físicamente inválido, pero no determina por sí misma qué estados son empresarialmente válidos.

---

# 13. Elementos físicos y significado

La implementación futura podrá utilizar, según proceda:

- tablas;
- columnas;
- claves;
- índices;
- relaciones;
- restricciones;
- vistas;
- migraciones;
- otros mecanismos propios del SGBD seleccionado.

Ninguno de estos elementos adquiere autoridad funcional por su mera existencia.

Si un elemento físico introduce un concepto nuevo, dicho concepto deberá haber sido previamente autorizado por el dominio correspondiente.

---

# 14. SGBD objetivo y alcance físico

El SGBD objetivo del EIOS MVP es **Microsoft SQL Server**.

Esta decisión fija la plataforma física de persistencia, pero no define por sí misma:

- versión concreta de SQL Server;
- infraestructura de despliegue;
- configuración operacional;
- permisos de producción;
- driver de acceso desde Python;
- ORM;
- estrategia de migraciones.

El diseño físico debe respetar esta plataforma y continuar subordinado a los contratos funcionales y de implementación ya aprobados.

Este contrato no autoriza por sí mismo la creación de tablas, columnas, índices, triggers, procedimientos ni código de acceso.

---

# 15. Fuera de alcance de este contrato

Este contrato no determina todavía:

- el esquema físico definitivo;
- tablas concretas;
- columnas concretas;
- índices concretos;
- procedimientos almacenados concretos;
- triggers concretos;
- ORM;
- migraciones concretas;
- código de acceso a datos;
- infraestructura de despliegue;
- configuración operacional del entorno.

Esos elementos pertenecen a fases posteriores de implementación técnica y deberán respetar este contrato.

---

# 16. Regla de escalado ante conflictos

Si durante la implementación SQL aparece una necesidad que no pueda resolverse únicamente mediante criterios técnicos de persistencia, no debe resolverse creando una nueva semántica local en SQL.

El flujo correcto es:

```text
Necesidad detectada en SQL
          ↓
¿es puramente técnica?
     ┌────┴────┐
    SÍ         NO
     │           │
 implementar    escalar a
 técnicamente   autoridad competente
                  ↓
             resolver documentalmente
                  ↓
             adaptar SQL
```

Esto mantiene la separación de autoridades y evita que la implementación física se convierta accidentalmente en diseño funcional.

---

# 17. Principios de cierre

`06_SQL` queda sometido a los siguientes principios:

1. **Persistencia sin redefinición:** SQL persiste conceptos autorizados; no los define.
2. **Autoridad técnica limitada:** su autoridad se restringe a la implementación y persistencia SQL.
3. **Versionado separado:** el versionado técnico del esquema no sustituye ningún versionado funcional o decisional.
4. **C0 preservado:** SQL no redefine ni sustituye los mecanismos de C0.
5. **Decision Versioning preservado:** SQL no define el estado decisional ni su reconstrucción semántica.
6. **Snapshots preservados:** SQL no redefine `Data_Snapshot_ID` ni su semántica.
7. **Sin autoridad por existencia física:** una estructura SQL no crea autoridad funcional por sí misma.
8. **Conflictos escalados:** las ambigüedades funcionales se resuelven en la autoridad competente antes de modificar el modelo de persistencia.
9. **Sin modificación arquitectónica implícita:** SQL no puede introducir por sí mismo nuevos componentes Core ni alterar la arquitectura autorizada.
10. **Persistencia y recuperación no equivalen a reconstrucción semántica:** SQL proporciona el soporte físico; la semántica permanece en las autoridades correspondientes.