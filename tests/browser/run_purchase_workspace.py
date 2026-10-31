"""Run the purchase workspace DOM integration check against an isolated test company.

Requires Node and jsdom (or EIOS_JSDOM_MODULE pointing to its installed package).
Run from the repository root: python tests/browser/run_sales_proposal_workspace.py
"""
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tests.test_company_sales_negotiation import SalesNegotiationTest


def main():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    case = SalesNegotiationTest()
    case.setUp()
    from tests.test_company_finance_activation import FinanceActivationTest
    FinanceActivationTest.prepare(case,revision=1)
    FinanceActivationTest.activate(case,revision=2)
    server = None
    try:
        server = subprocess.Popen(
            [sys.executable, '-m', 'eios.company_app', '--db', str(case.path), '--port', str(port)],
            cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        url = f'http://127.0.0.1:{port}'
        for _ in range(100):
            if server.poll() is not None:
                raise RuntimeError('The isolated test server exited before startup.')
            try:
                with urllib.request.urlopen(url, timeout=1):
                    break
            except OSError:
                time.sleep(.1)
        else:
            raise RuntimeError('The isolated test server did not start.')
        subprocess.run(
            ['node', str(Path(__file__).with_name('purchase_workspace.cjs'))],
            cwd=ROOT, env={**os.environ, 'EIOS_TEST_URL': url}, check=True, timeout=120,
        )
    finally:
        if server:
            server.terminate()
            server.wait(timeout=10)
        case.tearDown()


if __name__ == '__main__':
    main()
