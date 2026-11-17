# EIOS — F5.9 · TERCER DOMINIO INDEPENDIENTE Y PRUEBA DE PORTABILIDAD

**Fecha:** 17/11/2026.  
**Baseline de partida:** `main @ 8d2100c91de8d8e5ceff2cefd3519c283faf6abe`; F5.8 integrada con CI postmerge #44044989990 SUCCESS.  
**Estado:** candidato de cierre. No considerar cerrada la unidad hasta **CI PR SUCCESS, merge controlado y CI postmerge SUCCESS sobre SHA exacto**.

## 1. DISEÑAR — QUÉ ESTAMOS PROBANDO

EIOS está concebido como un **Motor técnico reutilizable**, al que proyectos diferentes añaden sus propios modelos, reglas de dominio y fuentes documentales. F5.4/F5.5 verificaron capacidades específicas de Compras; F5.6/F5.7/F5.8 demostraron contratos, versiones y gobierno independientes en **Compras y Ventas**.

F5.9 añade un tercer dominio genuinamente diferente, **mantenimiento de equipos industriales**, para no confundir la mera posibilidad de cambiar `project_id` con portabilidad física y funcional.

El consumidor `eios-maintenance-example==0.1.0` es una **distribución Python independiente**, no un módulo de `eios/` ni un nombre cambiado en los datos de Compras. Dispone de código y empaquetado propios en `tests/fixtures/f5_9_maintenance_consumer/` y se instala físicamente como paquete ajeno al Motor.

Modelo de dominio propio: `MaintenanceWorkOrder` (referencias de operación, instalación, equipo, horas desde última revisión, intervalo de mantenimiento, vibración declarada y disponibilidad de justificante de bloqueo/inspección).

Dos capacidades propias y explícitas:

| Capacidad | Productor del proyecto | Comportamiento esperado |
|---|---|---|
| `SERVICE_INTERVAL_CHECK` | Clasificación sintética de horas transcurridas frente al intervalo | `COMPLETED`; indicación técnica informativa, nunca orden de trabajo |
| `INSPECTION_EVIDENCE_CHECK` | Comprobación de presencia de soporte documental de inspección | `NOT_EVALUABLE` por ausencia de evidencia, sin autorización de reparación |

La primera ejecución conjunta debe obtener `PARTIALLY_COMPLETED`, `decision_authority=False`, `operational_path=FORBIDDEN` y procedencia `UNVERIFIED_ADAPTER_RESPONSIBILITY`.

## 2. AUDITAR — PRUEBA FÍSICA DE DESACOPLAMIENTO

El nuevo proyecto depende de **exactamente cuatro paquetes neutrales**:

1. `eios-kernel==0.1.0`
2. `eios-input-contracts==0.1.0`
3. `eios-capability-catalog==0.1.0`
4. `eios-catalog-governance==0.1.0`

Además de Pydantic, no instala ni importa `eios-mvp`, `eios-contracts-procurement`, `eios-price-procurement`, `eios-tco-procurement`, módulos de `eios.core`, `eios.pricing`, `eios.tco`, SQL o frontend.

`tools/verify_f5_9_third_domain.py`:

- Audita por AST los imports de la aplicación externa; solo admite los cuatro módulos neutrales de EIOS.
- Construye su wheel desde un staging independiente y verifica sus dependencias y sus únicos dos módulos `eios_maintenance_example/{__init__,consumer}.py`.
- Audita los cuatro wheels neutrales preexistentes, rechaza cualquier archivo EIOS duplicado o de negocio y contrasta **cada byte instalado** con el código canónico de la rama mediante SHA-256.
- Crea **un venv nuevo fuera del checkout**, instala los cuatro wheels neutrales y el paquete externo, comprueba `pip check` y ejecuta con `python -I` desde carpetas externas.
- Ejecuta **dos veces** el mismo paquete instalado en dos carpetas independientes; los resultados deben coincidir, sin reutilizar el ledger, dependencias o modelos del proyecto anterior.

Esta es evidencia de **portabilidad modular física y de ejecución en una plataforma concreta de CI**, no certificación universal de todas las plataformas y sectores.

## 3. DEPURAR — ATAQUES Y FRONTERAS REALES

Antes de dar una operación por técnicamente compatible, el proyecto simulado debe completar la misma cadena de contratos:

`KernelContext` → entrada tipada F5.6 → catálogo de release y esquema F5.7 → estado autorizado y persistido F5.8 → invocadores → Motor neutral F4.

Se comprueban estas situaciones *fail-closed*:

| Intento | Resultado requerido |
|---|---|
| Ausencia de autorización, autorización booleana o perteneciente a otro proyecto | No crear el ledger |
| Acceso al mismo ledger desde otro `project_id` | Rechazar |
| Cambiar el esquema sin actualizar el catálogo autorizado | Rechazar antes de productores |
| Deshabilitar una capacidad con permiso limitado solo a `ENABLE` | Rechazar y no cambiar el historial |
| Deshabilitación correctamente autorizada | Crear revisión 2, manteniendo hash de revisión 1 |
| Invocador creado antes de deshabilitar la capacidad | Rechazar antes de ejecutar |
| Volver a presentar una revisión obsoleta | Rechazar |
| Modificar una copia del historial sin recomputar los hashes | Detectar inconsistencia |
| Incluir código de PRICE, TCO o modelos de Compras en el wheel externo | Rechazar paquete |
| Incluir una dependencia del Motor con versión no fijada | Rechazar paquete |
| Un productor modifica su copia de entrada | No afectar a la entrada original ni al segundo productor |

Las pruebas **no** exponen credenciales ni simulan autenticación empresarial real. La función que autoriza los cambios es un *test double* expresamente identificado. No se pretende certificar que F5.8 controle un actor malicioso con acceso a todo el sistema de ficheros ni ofrecer firmas digitales o una transacción distribuida.

## 4. AUDITAR 2 — PRUEBAS ADVERSARIAS Y CI

Se añaden:

- `tests/fixtures/f5_9_maintenance_consumer/pyproject.toml` y su propio módulo Python.
- `tests/test_f5_9_third_domain_portability.py`: revisión de manifiesto, AST de imports, mal empaquetado, dependencias ajenas o no fijadas, inyección de código, identidad byte a byte, guardas de CLI y negativa a instalar ruedas de Compras.
- `tools/verify_f5_9_third_domain.py`: construcción del wheel **del consumidor externo**, venv aislado, comprobación de instalación y dos ejecuciones completas con pruebas de seguridad.

La CI realiza la comprobación F5.9 **después** de Python, SQL, F4 y F5.3–F5.8, sin desactivar ninguna prueba anterior.

No se cambia ningún módulo existente del Motor, PRICE, TCO, contratos C0, parámetros, interfaz, datos reales o gobernanza ya cerrada.

## 5. CERRAR → MATERIALIZAR → CI

Desde una rama local equivalente, y después de preparar ruedas neutrales:

```powershell
python -m pip install "setuptools>=64" "wheel>=0.42"
python tools/build_eios_kernel_distribution.py --output dist/kernel
python tools/build_eios_input_contracts_distribution.py --output dist/inputs
python tools/build_eios_capability_catalog_distribution.py --output dist/catalog
python tools/build_eios_catalog_governance_distribution.py --output dist/governance
python tools/verify_f5_9_third_domain.py --kernel-dir dist/kernel --inputs-dir dist/inputs --catalog-dir dist/catalog --governance-dir dist/governance
```

**Criterios de cierre:**

- Tercer proyecto realmente instalado desde **wheel independiente**, sin importar Compras/Ventas.
- Cuatro wheels EIOS neutrales compartidos con fuentes y versiones verificadas.
- Entrada propia, capacidades propias, catálogo propio y revisiones autorizadas del tercer dominio.
- Todos los intentos indebidos declarados rechazados sin saltarse productores.
- `decision_authority=False`, `operational_path=FORBIDDEN`.
- CI PR SUCCESS en HEAD exacto + revisión de diff + merge + CI postmerge SUCCESS en SHA exacto.

## 6. DECISIÓN QUE HABILITA Y SUS LÍMITES

Si se superan los controles, F5.9 **demuestra reutilización técnica del Motor en tres dominios sintéticos diferentes**: Compras, Ventas y Mantenimiento, sin duplicar ni reescribir el núcleo.

**No prueba** capacidad de operación real, autenticación empresarial, seguridad hostil multiusuario, firmas de auditoría, escalabilidad distribuida, calidad de datos reales ni que los algoritmos de PRICE/TCO sean transversales. Son siguientes frentes de validación distintos y no deben etiquetarse como resultados de F5.9.

**Propuesta posterior a F5.9:** revisar el punto de entrada real de un nuevo proyecto (provisión de adapters, manejo de autorizaciones y límites del ledger local) y diseñar una certificación de despliegue fuera de CI sin modificar módulos canónicos innecesariamente.
