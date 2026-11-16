"""Deprecated F3.2 import path — compatibility bridge, NOT parameter core.

The concrete historical LOCAL SYNTHETIC finance activation reader now belongs
to the company application at eios.company_local_finance_version_source.
This explicit legacy bridge stays ONLY to avoid breaking existing consumers.
Do not bundle this module in a standalone parameter/kernel distribution.
F4.3 must exclude it; no authority is added by keeping the import working.
"""

from eios.company_local_finance_version_source import LocalSyntheticFinanceVersionSource

__all__ = ["LocalSyntheticFinanceVersionSource"]
