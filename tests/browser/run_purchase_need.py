"""HTTP+DOM test of the independent step-two stock explanation."""
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tests.test_company_exclusive_workbook import ExclusiveWorkbookTest
from tests.test_company_workbook_stock_activation import planned_book
from eios.company_exclusive_workbook import activate


def main():
    case=ExclusiveWorkbookTest();case.setUp();server=None
    try:
        activate(case.path,'one',case.receive(planned_book()))
        with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        server=subprocess.Popen([sys.executable,'-m','eios.company_app','--db',str(case.path),'--port',str(port)],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        url=f'http://127.0.0.1:{port}'
        for _ in range(100):
            try:
                urllib.request.urlopen(url,timeout=1).close();break
            except OSError:time.sleep(.1)
        subprocess.run(['node',str(Path(__file__).with_name(os.environ.get('EIOS_NEED_SCRIPT','purchase_need.cjs')))],cwd=ROOT,env={**os.environ,'EIOS_TEST_URL':url},check=True,timeout=60)
    finally:
        if server:server.terminate();server.wait(timeout=10)
        case.tearDown()


if __name__=='__main__':main()
