"""Bounded preview/commit for the existing synthetic documentary ZIP contract."""
from io import BytesIO
from pathlib import Path
import secrets
from tempfile import TemporaryDirectory
from time import monotonic
import zipfile
import zlib

from eios.company_data import read_dataset

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_EXPANDED_BYTES = 100 * 1024 * 1024
MAX_MEMBERS = 512
PREVIEW_TTL_SECONDS = 600


class PreparedCompanyImport:
    def __init__(self, store, clock=monotonic):
        self.store = store
        self.clock = clock
        self.pending = None

    def preview(self, content):
        self.pending = None
        if not isinstance(content, bytes) or not 0 < len(content) <= MAX_UPLOAD_BYTES:
            raise ValueError('El paquete debe tener entre 1 byte y 25 MiB.')
        try:
            with zipfile.ZipFile(BytesIO(content)) as archive:
                members = archive.infolist()
                if len(members) > MAX_MEMBERS or sum(m.file_size for m in members) > MAX_EXPANDED_BYTES:
                    raise ValueError('El ZIP supera 512 archivos o 100 MiB descomprimidos.')
                if 'company_manifest.json' not in archive.namelist():
                    raise ValueError('Falta company_manifest.json. Selecciona el ZIP documental, no el paquete de instalación ni archivos PDF/Excel sueltos.')
                if any(m.flag_bits & 1 for m in members):
                    raise ValueError('No se admiten archivos ZIP cifrados.')
                if any(m.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED) for m in members):
                    raise ValueError('El ZIP debe usar almacenamiento sin compresión o DEFLATE.')
            with TemporaryDirectory() as temp:
                path = Path(temp) / 'company.zip'
                path.write_bytes(content)
                manifest, records, documents, identity = read_dataset(path)
            # The generic intake also accepts partial catalogues; this screen needs
            # identifiers and display fields before it can safely switch datasets.
            fields = {'supplier': ('supplier_id','legal_name'),
                      'customer': ('customer_id','legal_name'),
                      'article': ('article_id','supplier_id','description','unit_as_documented')}
            for record in records:
                required = fields.get(record['kind'])
                if required:
                    data = record['data']
                    if any(not isinstance(data.get(key),str) or not data[key].strip() for key in required):
                        raise ValueError('Faltan identificadores o campos de catálogo para mostrar '+record['kind']+'.')
                    if data[required[0]] != record['record_id']:
                        raise ValueError('El identificador del catálogo no coincide con record_id.')
        except (ValueError, KeyError, TypeError, AttributeError, RuntimeError, NotImplementedError, zipfile.BadZipFile, zlib.error) as error:
            raise ValueError('Paquete no válido: '+str(error)[:400]) from None
        ticket = secrets.token_urlsafe(32)
        self.pending = (ticket, bytes(content), self.clock())
        return dict(ticket=ticket, dataset_id=identity, company=manifest['company'],
                    as_of_date=manifest['as_of_date'], documents=len(documents),
                    record_counts=manifest['record_counts'], records=len(records),
                    material_nature='SYNTHETIC', operational_path='FORBIDDEN',
                    message='Paquete validado técnicamente. Aún no se ha importado ni admite uso operacional.')

    def commit(self, ticket):
        pending = self.pending
        if pending is None or not isinstance(ticket,str) or not secrets.compare_digest(ticket,pending[0]):
            raise ValueError('La vista previa ya no es válida. Vuelve a comprobar el paquete.')
        if self.clock()-pending[2] > PREVIEW_TTL_SECONDS:
            self.pending = None
            raise ValueError('La vista previa ha caducado. Vuelve a comprobar el paquete.')
        with TemporaryDirectory() as temp:
            path = Path(temp) / 'company.zip'
            path.write_bytes(pending[1])
            result = self.store.import_dataset(path)
        self.pending = None
        return result
