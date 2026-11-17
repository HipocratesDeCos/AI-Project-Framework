"""F6.4 synthetic local custody adapter, outside the canonical EIOS engine."""
from .custody import (
    CustodyError, DocumentBinding, SyntheticCustodyVault, VaultDocumentProvider,
)

__all__ = (
    "CustodyError", "DocumentBinding", "SyntheticCustodyVault",
    "VaultDocumentProvider",
)
