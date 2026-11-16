"""Read-only, company-scoped inventory of *physically connected* UI parameters.

This is an evidence ledger, not a parameter resolver or an authorization gate.
Only two local synthetic Finance consumers are currently proved by the
company application's activation and execution path. Other EIOS core rules
may consume the same parameter IDs in separate authorized contracts.
"""
from __future__ import annotations

from datetime import date, datetime, time, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
from typing import Mapping, Sequence


SCHEMA_VERSION = "COMPANY-PARAMETER-BINDINGS-01"
LOCAL_FINANCE_CONSUMERS = {
    "P-FIN-001": ("eios.company_finance_execution.execute_documentary_finance", "días"),
    "P-FIN-002": ("eios.company_finance_execution.execute_documentary_finance", "EUR"),
}
ACTIVE_SCOPE = "LOCAL_SYNTHETIC_FINANCE_PARAMETERS_AT_CUTOFF"


def _verified_local_activation(
    activation: object, *, company_id: str, dataset_id: str, as_of_date: str,
) -> bool:
    """Check persisted-record consistency; SHA-256 is not external authentication."""
    if not isinstance(activation, dict):
        return False
    if any(activation.get(key) != expected for key, expected in {
        "company_id": company_id, "dataset_id": dataset_id,
        "as_of_date": as_of_date, "scope": ACTIVE_SCOPE,
        "decision_authority": False, "operational_path": "FORBIDDEN",
    }.items()):
        return False

    fingerprint = activation.get("fingerprint")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        return False
    original = {k: v for k, v in activation.items() if k != "fingerprint"}
    digest = sha256(
        json.dumps(
            original, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    if digest != fingerprint:
        return False

    values, configs = activation.get("values"), activation.get("configurations")
    if not isinstance(values, dict) or set(values) != set(LOCAL_FINANCE_CONSUMERS):
        return False
    if not isinstance(configs, list) or len(configs) != len(LOCAL_FINANCE_CONSUMERS):
        return False
    if type(activation.get("request_revision")) is not int:
        return False

    try:
        cutoff = date.fromisoformat(as_of_date)
        moment = datetime.combine(cutoff, time.min, timezone.utc)
        horizon = Decimal(values["P-FIN-001"])
        minimum = Decimal(values["P-FIN-002"])
        if (
            not horizon.is_finite() or horizon <= 0
            or horizon != horizon.to_integral_value()
            or not minimum.is_finite() or minimum < 0
        ):
            return False
        found = set()
        for config in configs:
            if not isinstance(config, dict):
                return False
            pid = config.get("parameter_id")
            if pid not in LOCAL_FINANCE_CONSUMERS or pid in found:
                return False
            found.add(pid)
            if (
                config.get("company_id") != company_id
                or config.get("value") != values[pid]
                or config.get("unit") != LOCAL_FINANCE_CONSUMERS[pid][1]
            ):
                return False
            if (pid == "P-FIN-001" and config.get("value_type") != "INTEGER") or (
                pid == "P-FIN-002" and config.get("value_type") != "DECIMAL"
            ):
                return False
            start = datetime.fromisoformat(config["valid_from"])
            end = datetime.fromisoformat(config["valid_to"])
            if start.tzinfo is None or end.tzinfo is None:
                return False
            if not start <= moment < end:
                return False
        return found == set(LOCAL_FINANCE_CONSUMERS)
    except (KeyError, ValueError, TypeError, InvalidOperation, OverflowError):
        return False


def describe_company_parameter_bindings(
    *, catalogue: Sequence[Mapping], activation: object,
    company_id: str, dataset_id: str, as_of_date: str,
    current_revision: int,
) -> dict:
    """Describe application-level wiring without treating saved values as active.

    A prior activation is a valid historic snapshot even if the current request
    revision differs. The new request does not silently replace that snapshot.
    """
    if not all(isinstance(value, str) and value.strip() for value in (
        company_id, dataset_id, as_of_date,
    )):
        raise ValueError("company, dataset and cutoff are mandatory")
    if type(current_revision) is not int or current_revision < 0:
        raise ValueError("current_revision must be a non-negative integer")

    ids = [entry["parameter_id"] for entry in catalogue]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate parameter IDs in company catalogue")

    active = _verified_local_activation(
        activation, company_id=company_id,
        dataset_id=dataset_id, as_of_date=as_of_date,
    )
    statuses = {}
    for pid in ids:
        consumer = LOCAL_FINANCE_CONSUMERS.get(pid)
        if consumer is None:
            statuses[pid] = dict(
                status="PENDING_COMPANY_CONSUMER",
                consumer=None, effective_value=None,
                activation_ref=None, scope="COMPANY_APP",
            )
            continue
        if active:
            status = (
                "ACTIVE_LOCAL_SYNTHETIC_AT_CUTOFF"
                if activation["request_revision"] == current_revision else
                "ACTIVE_LOCAL_SYNTHETIC_PRIOR_REQUEST"
            )
            value = activation["values"][pid]
            reference = activation["fingerprint"]
        else:
            status = (
                "ACTIVATION_RECORD_UNVERIFIED"
                if activation is not None else "AVAILABLE_NOT_ACTIVATED"
            )
            value = reference = None
        statuses[pid] = dict(
            status=status, consumer=consumer[0],
            effective_value=value, activation_ref=reference,
            scope="LOCAL_SYNTHETIC_ONLY",
        )

    return dict(
        schema=SCHEMA_VERSION, company_id=company_id,
        dataset_id=dataset_id, as_of_date=as_of_date,
        decision_authority=False, operational_path="FORBIDDEN",
        entries=statuses,
    )


__all__ = [
    "SCHEMA_VERSION", "LOCAL_FINANCE_CONSUMERS",
    "describe_company_parameter_bindings",
]
