"""CSV of all current reception errors and warnings; no corrected data or admission."""
import base64
import csv
from io import StringIO
import re

from eios.company_presentation import date_text


def export_issues(report,errors,warnings):
    def safe(value):
        text='' if value is None else str(value)
        return "'"+text if text.lstrip().startswith(('=','+','-','@')) else text
    stream=StringIO(newline='');writer=csv.writer(stream,delimiter=';')
    writer.writerow(['Tipo','Archivo','Hoja','Fila','Codigo_empresa','Empresa','Naturaleza','Fecha_corte','Contenido','Formato_numerico','Mensaje','SHA256_origen'])
    entries=[('ERROR',e['row'],'\n'.join(e['messages'])) for e in errors]
    for warning in warnings:
        match=re.match(r'^Fila ([0-9]+):',warning)
        entries.append(('AVISO',int(match.group(1)) if match else None,warning))
    for severity,row,message in entries:
        writer.writerow([safe(v) for v in [severity,report['filename'],report['sheet'],row,report['company_id'],report['legal_name'],report['material_nature'],date_text(report['as_of_date']),report['kind'],report['number_format'],message,report['source_sha256']]])
    return dict(filename='EIOS_Incidencias_Carga.csv',content_base64=base64.b64encode(stream.getvalue().encode('utf-8-sig')).decode(),error_row_count=len(errors),warning_count=len(warnings),incident_count=len(entries),scope='RECEPTION_FORMAT_REVIEW_ONLY',decision_authority=False,operational_path='FORBIDDEN')
