"""A second company can cross the existing synthetic material boundary."""
from hashlib import sha256
import json
from pathlib import Path
import shutil

import pytest

from eios.core.case_provenance import classify_reference_operational_simulation
from eios.core.projection_mock_dataset import load_projection_mock_dataset
from eios.core.projection_synthetic_adapter import build_projection_only_synthetic_material_bundle


FIXTURE = Path(__file__).parent / "fixtures" / "reference_business_case_002_semantic"


def test_second_company_builds_distinct_synthetic_bundle():
    dataset = load_projection_mock_dataset(FIXTURE)
    bundle = build_projection_only_synthetic_material_bundle(dataset)
    provenance = classify_reference_operational_simulation(
        bundle=bundle, reference_case_id="REF-BUSINESS-002",
    ).to_payload()
    purchase = bundle.envelope.to_payload()["preparation"]["payload"]["capture"][
        "finance_package"]["decision_input_package"]["purchase"]

    assert dataset.to_payload()["dataset_id"] == "EIOS-REFERENCE-BUSINESS-002-SEMANTIC"
    assert (purchase["article_id"], purchase["supplier_id"], purchase["quantity"],
            purchase["unit_price"]) == (
                "ARTICLE-MOCK-002", "SUPPLIER-MOCK-002", "15", "21.00",
            )
    assert provenance["source_fingerprint"] == bundle.fingerprint
    assert provenance["reference_case_id"] == "REF-BUSINESS-002"
    assert (provenance["material_nature"], provenance["qtg_mode_policy"],
            provenance["operational_path"], provenance["effect_scope"],
            provenance["decision_authority"]) == (
                "SYNTHETIC", "SYNTHETIC_TEST_ONLY", "FORBIDDEN",
                "NO_OPERATIONAL_EFFECT", False,
            )


def test_second_company_rejects_cross_company_finance_after_hash_refresh(tmp_path):
    target = tmp_path / "second-company"
    shutil.copytree(FIXTURE, target)
    finance_path = target / "finance" / "finance_input.json"
    finance = json.loads(finance_path.read_text(encoding="utf-8"))
    finance["company_id"] = "COMPANY-MOCK-001"
    raw = (json.dumps(finance, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")) + "\n").encode("utf-8")
    finance_path.write_bytes(raw)
    manifest_path = target / "dataset_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["components"]["finance_input"]["sha256"] = sha256(raw).hexdigest()
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True,
                                        separators=(",", ":")) + "\n", encoding="utf-8")

    dataset = load_projection_mock_dataset(target)
    with pytest.raises(ValueError, match="Financial snapshot company/context mismatch"):
        build_projection_only_synthetic_material_bundle(dataset)
