# EIOS — F5.5 · CONTRATOS C0 COMPARTIDOS SIN DUPLICADOS

**Fecha:** 2026-11-17  
**Baseline:** `main @ 0a88692cb7a9c3ac3537a3143c9d9f2d0ae83323`; F5.4 integrada, CI postmerge #43969401213 SUCCESS.  
**Unidad:** F5.5 — empaquetado, coexistencia y ejecución real de Motor + PRICE + TCO.  
**Condición de cierre:** suite Python + SQL + todas las instalaciones F4/F5 + CI postmerge SUCCESS sobre commit exacto; hasta entonces pendiente de cierre.

## 1. DISEÑAR — CAUSA Y SOLUCIÓN

F5.3 y F5.4 distribuyeron capacidades opcionales de adquisición, pero **ambos wheels contenían `eios/core/models.py`**. La igualdad de bytes no resolvía la colisión de propiedad entre paquetes; instalar o desinstalar uno podía afectar al otro.

La solución es una única distribución de contratos de Compras:

| Distribución | Versión | Archivos Python exclusivos | Dependencias |
|---|---|---|---|
| `eios-contracts-procurement` | `0.1.0` | `eios/core/models.py` (único propietario) | Pydantic |
| `eios-tco-procurement` | `0.2.0` | `eios/tco/__init__.py`, `models.py`, `engine.py` | Pydantic + `eios-contracts-procurement==0.1.0` |
| `eios-price-procurement` | `0.2.0` | 12 módulos canónicos `eios/pricing/` + `eios/core/validation.py` | Pydantic + `eios-contracts-procurement==0.1.0` |
| `eios-kernel` | `0.1.0` | `eios/kernel/execution.py`, `eios/parameters/center.py` | Pydantic |

**No se cambia ningún archivo del código de ejecución de producción `eios/`.** El contrato `PurchaseOperation` y su ruta pública `eios.core.models` permanecen idénticos; la diferencia es que cada proyecto los obtiene de una sola distribución física.

El cambio de la dependencia de PRICE y TCO es explícito y se distingue con la **versión 0.2.0**. No se instala ni se desinstala sobre aplicaciones antiguas en uso. El empaquetado anterior 0.1.0 es incompatible con la composición completa y **no** debe mezclarse con la nueva versión ni con el monolito `eios-mvp`.

## 2. AUDITAR — ORIGEN CANÓNICO

`tools/build_eios_contracts_distribution.py` copia el archivo canónico a staging efímero y audita:

- Cero importaciones internas `eios.*` desde los contratos;
- wheel con exactamente un módulo `eios/core/models.py`, sin extras;
- metadatos y dependencia Pydantic únicos, sin código oculto;
- verificación de bytes canónicos al construir y, más tarde, en la instalación.

Los generadores de PRICE y TCO eliminan `eios/core/models.py` de su lista de archivos físicos. Ambos preservan **el import público original** al declarar el módulo C0 como dependencia externa explícita. Cada auditor comprueba sus dos dependencias y el pin exacto `eios-contracts-procurement==0.1.0`.

## 3. DEPURAR — RETROCOMPATIBILIDAD CONTROLADA

Se actualizan las pruebas F5.3 y F5.4 para la nueva disposición, **sin suprimir** las comprobaciones de cálculos y falta de evidencia. Ambas siguen siendo instalables en venvs nuevos *con* su dependencia C0 y, de manera opcional, con el Motor.

Se mantiene una prueba adversaria de ruedas antiguas con `eios/core/models.py` duplicado: la política de detección de colisiones debe seguir rechazándolas.

No se alteran `run_price_intelligence`, `calculate_tco`, sus contratos, el núcleo neutral, el adaptador estricto F5.2, QTG/O1, las pantallas, los datos empresariales ni SQL Server.

## 4. AUDITAR 2 — PRUEBA DE CUATRO WHEELS

`tools/verify_f5_5_shared_contracts.py`:

1. Audita las cuatro ruedas reales antes de instalar.
2. Inspecciona **todas** las rutas `eios/` y exige intersección nula entre distribuciones.
3. Compara **cada archivo incluido** contra los bytes de la fuente canónica en GitHub, con huellas SHA-256.
4. Crea un venv aislado fuera del repositorio, suprime `PYTHONPATH`, ejecuta `pip install` con los cuatro wheels, `pip check` y una prueba `python -I`.
5. Confirma la identidad de clase compartida `PurchaseOperation` en los contratos TCO y PRICE, sin definiciones paralelas.
6. Ejecuta el TCO canónico en un expediente sintético: 10 × 5 + 7,50 de transporte = **57,50 euros**.
7. Ejecuta PRICE C1 canónico con dos referencias sintéticas (10 y 12) y obtiene mediana **11,00 euros** bajo los supuestos metodológicos declarados.
8. Demuestra que ese PRICE no supera la puerta documental estricta de empresa sin pruebas de seis dimensiones. En la ejecución neutral, PRICE = `NOT_EVALUABLE`, TCO = `COMPLETED` y resultado global `PARTIALLY_COMPLETED`.
9. Comprueba `decision_authority=False`, `operational_path=FORBIDDEN`, `provenance_status=UNVERIFIED_ADAPTER_RESPONSIBILITY`.
10. Verifica que una identidad incompatible se rechaza **antes de llamar** a cualquiera de las capacidades.

**Los datos son exclusivamente sintéticos y no proceden de una empresa real.** Un precio `PR_AVAILABLE` de C1 es un cálculo condicionado; **no** reemplaza la evidencia documental ni habilita operaciones.

## 5. CERRAR → MATERIALIZAR → CI

La CI ejecuta secuencialmente regresión Python completa, tres controles SQL, pruebas F4 del kernel y de dos consumidores, construcción de contratos, pruebas F5.3 de TCO, F5.4 de PRICE y coinstalación real F5.5. Solo después del SUCCESS se puede fusionar la PR y volver a verificar el SHA exacto de `main`.

Comandos locales desde la raíz del repositorio:

```powershell
python -m pip install "setuptools>=64" "wheel>=0.42"
python tools/build_eios_kernel_distribution.py --output dist/kernel
python tools/build_eios_contracts_distribution.py --output dist/contracts
python tools/build_eios_tco_distribution.py --output dist/tco
python tools/build_eios_price_distribution.py --output dist/price
python tools/verify_f5_5_shared_contracts.py --contracts-dir dist/contracts --kernel-dir dist/kernel --price-dir dist/price --tco-dir dist/tco
```

**Criterio de salida F5.5:** `single_c0_owner=VERIFIED`, `four_wheel_coinstallation=VERIFIED`, `canonical_calculations=UNCHANGED`, `operational_path=FORBIDDEN`. Los contratos siguen siendo específicos de adquisiciones: **la reutilización universal para Ventas queda expresamente NO PROBADA**.

El siguiente frente, si se desea proseguir, será **F5.6: diseñar contratos de entrada neutrales para nuevas capacidades sin sacrificar los contratos sectoriales actuales**, no copiar la clase de compras a otros dominios.
