"""Portable read-only export of a saved received dossier, not an import/admission package."""
from html import escape
from io import BytesIO
from pathlib import PurePosixPath
import re
import sqlite3
from urllib.parse import quote
from zipfile import ZipFile, ZIP_DEFLATED

from eios.company_dossier_versions import version
from eios.company_reception import CompanyReception, canonical

MAX_EXPORT_BYTES = 100 * 1024 * 1024


def safe_name(filename):
    basename = PurePosixPath(filename.replace('\\', '/')).name
    return re.sub(r'[<>:"/\\|?*\x00-\x1f\x7f]', '_', basename).strip(' .')[:120] or 'documento'


def export_version(db, dossier_id):
    saved = version(db, dossier_id)
    manifest, check = saved['manifest'], saved['check']
    ids = manifest['batch_ids']
    with sqlite3.connect(db) as c:
        source_size = c.execute('SELECT SUM(length(content)) FROM received_company_batch WHERE batch_id IN (' + ','.join('?' for _ in ids) + ')', ids).fetchone()[0]
    check_bytes = canonical(check).encode()
    if source_size + len(check_bytes) > MAX_EXPORT_BYTES:
        raise ValueError('La versión supera el límite de exportación de 100 MiB. Exporta los originales por separado.')
    package_files = []
    for index, source in enumerate(manifest['files'], 1):
        package_files.append(dict(source, path='originales/' + str(index).zfill(3) + '_' + safe_name(source['filename'])))
    exported = dict(schema='EIOS-RECEIVED-DOSSIER-EXPORT-01/v0.1', dossier_id=dossier_id,
        name=saved['name'], created_at=saved['created_at'], manifest=manifest, files=package_files,
        admission_status='PENDING', operational_path='FORBIDDEN', decision_authority=False,
        scope='Copia documental de la versión guardada. No es un paquete de importación de empresa activa ni una copia completa de la base de datos.')
    def e(value):
        return escape(str(value), quote=True)
    labels = dict(sale_price='Tarifa de venta sin IVA',supplier='Proveedores',customer='Clientes',article='Artículos',inventory='Inventario',stock_policy='Parámetros de stock',purchase_line='Líneas de compra',sales_line='Líneas de venta',sales_installment='Vencimientos de venta',cash_flow='Cobros y pagos',balance='Saldos contables',document='PDF de soporte')
    rows = ''.join('<tr><td>'+str(i)+'</td><td><a href="'+quote(item['path'], safe='/')+'">'+e(item['filename'])+'</a></td><td>'+e(labels[item['kind']])+'</td><td>'+e(item['sheet'] or '—')+'</td><td class="hash">'+e(item['source_sha256'])+'</td></tr>' for i,item in enumerate(package_files,1))
    issues = ''.join('<li>'+e(issue['message'])+' — '+e(issue['source']['filename'])+' · hoja '+e(issue['source'].get('sheet') or '—')+' · fila '+e(issue['source'].get('row') if issue['source'].get('row') is not None else '—')+'</li>' for issue in check['issues'])
    html = '''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>EIOS · Índice de expediente</title><style>body{font:16px system-ui,sans-serif;background:#eef3fa;color:#17243b;margin:0;padding:32px}main{max-width:1100px;margin:auto;background:white;padding:28px;border-radius:12px}h1,h2{color:#0a2246}.status{background:#fff1cf;border-left:5px solid #b57b00;padding:16px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;padding:10px;border-bottom:1px solid #dce4ef;vertical-align:top}.hash{font:12px monospace;overflow-wrap:anywhere}a{color:#0a369d}.scroll{overflow:auto}li{margin:8px 0}</style><main><h1>EIOS · ÍNDICE DEL EXPEDIENTE</h1>'''
    html += '<p><strong>'+e(manifest['legal_name'])+'</strong> · Corte: '+e(manifest['as_of_date'])+'</p><p>Versión: '+e(saved['name'])+' · Guardada: '+e(saved['created_at'])+'</p><p>Datos: '+('reales' if manifest['material_nature']=='REAL' else 'sintéticos')+'</p><p class="status"><strong>PENDIENTE DE ADMISIÓN</strong><br>Esta copia conserva la documentación seleccionada y su comprobación de referencias. No acredita integridad del expediente, conciliación financiera ni autorización para tomar decisiones.</p>'
    html += '<h2>Archivos originales</h2><p>'+str(len(package_files))+' archivos. Descomprime el ZIP completo antes de abrir este índice.</p><div class="scroll"><table><thead><tr><th>N.º</th><th>Documento</th><th>Tipo</th><th>Hoja</th><th>SHA-256</th></tr></thead><tbody>'+rows+'</tbody></table></div>'
    html += '<h2>Comprobación conservada</h2><p>'+str(check['issue_count'])+' incidencias o avisos. '+e(check['scope'])+'</p><ul>'+issues+'</ul><p>Detalle técnico: <a href="comprobacion_referencias.json">comprobacion_referencias.json</a> · <a href="expediente_manifest.json">expediente_manifest.json</a></p><p>Identificador de versión: <span class="hash">'+e(dossier_id)+'</span></p></main></html>'
    manifest_bytes = canonical(exported).encode()
    index_bytes = html.encode()
    if source_size + len(check_bytes) + len(manifest_bytes) + len(index_bytes) > MAX_EXPORT_BYTES:
        raise ValueError('La versión supera el límite de exportación de 100 MiB. Exporta los originales por separado.')
    target = BytesIO()
    reception = CompanyReception(db)
    with ZipFile(target, 'w', compression=ZIP_DEFLATED) as archive:
        archive.writestr('expediente_manifest.json', manifest_bytes)
        archive.writestr('comprobacion_referencias.json', check_bytes)
        archive.writestr('indice.html', index_bytes)
        for item in package_files:
            original = reception.original(manifest['company_id'], item['batch_id'])
            if original['source_sha256'] != item['source_sha256']:
                raise ValueError('El original no coincide con la versión guardada. Exportación cancelada.')
            archive.writestr(item['path'], original['content'])
    return dict(filename='EIOS_Expediente_'+dossier_id[:12]+'.zip', content=target.getvalue())
