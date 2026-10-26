# Guía interactiva de carga

Carga de archivos presenta cuatro paneles desplegables numerados: identificación de empresa, selección y comprobación, revisión y confirmación, consulta de la recepción. Los paneles usan azul, verde, crema y violeta suaves, títulos de 21 px y explicaciones de 16 px. Numeración y títulos acompañan al color.

El contexto compartido (empresa, naturaleza, corte y formato numérico) está visible en el primer paso. Continuar y comprobar requieren los campos de contexto y un código con formato válido; el servidor conserva todas sus validaciones. La selección de ruta alterna entre libro con 97_Guia_Carga y tabla individual/PDF. Revisar abre automáticamente el tercer panel al recibir resultados. La consulta de expedientes tiene acceso directo desde el cuarto.

Consultas, versiones, plantillas, preparación y ZIP se agrupan por separado en desplegables sobre fondo gris. Los controles originales se trasladan sin duplicar identificadores ni reemplazar sus manejadores. No cambia ningún contrato de recepción, admisión o activación. Guardar no acredita viabilidad económica.

Validación: 24 pruebas unitarias de recepción/libro/expediente; comprobación sintáctica JavaScript; recorrido HTTP y DOM con libro de diez hojas, recepción completa, repetición sin duplicados, contexto obligatorio, cambio de ruta, apertura de expedientes, identificadores únicos, invalidación al editar contexto y protección del endpoint. La empresa activa se conserva.
