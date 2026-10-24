import csv
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from eios.company_app import PAGE
from eios.company_stock_export_ui import FILTER_JS, JS
from eios.company_stock_family_ui import JS as FAMILY_JS


@unittest.skipUnless(shutil.which('node'), 'Node not installed')
class StockCSVTest(unittest.TestCase):
    def test_complete_filtered_csv_roundtrip_and_missing_values(self):
        date_start = PAGE.index('function stockDate(')
        script = r'''
const assert=require('node:assert/strict');
const fields={dataset:{value:'one'},'stock-family':{value:'family:Riego'},'stock-search':{value:''},'stock-provider':{value:''},'stock-order':{value:'SKU'},'stock-alert-only':{checked:false},'stock-export':{}};
const $=id=>fields[id];let stockExactArticle=null;
const state={info:{dataset_id:'one',company:{company_id:'EMP',legal_name:'Empresa ficticia'},as_of_date:'2026-09-30'},data_status:{dataset_id:'one',material_nature:'SYNTHETIC'},articles:[],inventory:{},stock_minimums:{},stock_metrics:{}};
for(let i=0;i<102;i++){const id='A'+String(i).padStart(3,'0');state.articles.push({article_id:id,description:i===0?'=1+1; "Prueba"\nSegunda línea':'Artículo',family:i===101?'Otra':'Riego',unit_as_documented:'uds.'});state.stock_minimums[id]={value:'1.25',draft:'999',unit:'uds.',source:'MANUAL',label:'Aviso',status:'LOW'}}
state.inventory.A000={physical:0,reserved:null,available:'-1.5',unit:'uds.',as_of_date:'2026-09-29',material_nature:'SYNTHETIC',source_ref:{filename:'inventario; "septiembre".csv',source_row:2}};
'''+PAGE[date_start:PAGE.index('\n', date_start)]+'\n'+FAMILY_JS+FILTER_JS+JS+r'''
const before=JSON.stringify(state),result=stockCSV();assert.equal(result.count,101);assert.equal(JSON.stringify(state),before);
stockExactArticle='A000';assert.equal(stockCSV().count,1);stockExactArticle=null;
$('stock-family').value='missing';assert.throws(()=>stockCSV(),/No hay artículos/);$('stock-family').value='family:Riego';
$('dataset').value='two';assert.throws(()=>stockCSV(),/termine la carga/);
console.log(JSON.stringify(result));
'''
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'stock-csv.js'
            path.write_text(script, encoding='utf-8')
            result = subprocess.run(['node', str(path)], capture_output=True,
                                    text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        exported = json.loads(result.stdout)
        self.assertTrue(exported['text'].startswith('\ufeff'))
        rows = list(csv.reader(io.StringIO(exported['text'].lstrip('\ufeff')), delimiter=';'))
        self.assertEqual(len(rows), 102)  # Header plus all 101 matching articles.
        self.assertTrue(all(len(row) == 22 for row in rows))
        first = dict(zip(rows[0], rows[1]))
        self.assertEqual(first['Descripción'], "'=1+1; \"Prueba\"\nSegunda línea")
        self.assertEqual(first['Físico'], '0')
        self.assertEqual(first['Reservado'], '')
        self.assertEqual(first['Disponible'], '-1,5')
        self.assertEqual(first['Mínimo aplicado'], '1,25')
        self.assertEqual(first['Corte documental'], '30/09/2026')
        self.assertEqual(first['Fecha de inventario'], '29/09/2026')
        self.assertEqual(first['Naturaleza del expediente'], 'SYNTHETIC')
        self.assertEqual(first['Archivo de inventario'], 'inventario; "septiembre".csv')
        self.assertEqual(first['Fila de inventario'], '2')
        missing = dict(zip(rows[0], rows[2]))
        self.assertEqual(missing['Físico'], '')
        self.assertEqual(missing['Fecha de inventario'], '')
        self.assertEqual(rows[-1][5], 'A100')
