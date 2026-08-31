from eios.quality.gate import QualityCheck, evaluate_quality


def test_all_applicable_checks_satisfied_are_apt_and_high_confidence():
    checks = [
        QualityCheck("existencia", True),
        QualityCheck("integridad", True),
        QualityCheck("validez", True),
    ]

    result = evaluate_quality(checks)

    assert result.status == "APTO"
    assert result.confidence == "ALTA"


def test_non_critical_defect_produces_warning_and_medium_confidence():
    checks = [
        QualityCheck("existencia", True),
        QualityCheck("consistencia", False, critical=False),
    ]

    result = evaluate_quality(checks)

    assert result.status == "APTO_CON_ADVERTENCIAS"
    assert result.confidence == "MEDIA"


def test_material_non_critical_limitation_lowers_confidence():
    checks = [
        QualityCheck("existencia", True),
        QualityCheck("temporalidad", False, critical=False, material=True),
    ]

    result = evaluate_quality(checks)

    assert result.status == "APTO_CON_ADVERTENCIAS"
    assert result.confidence == "BAJA"


def test_critical_failure_produces_no_apt_and_low_confidence():
    checks = [
        QualityCheck("existencia", True),
        QualityCheck("contradiccion_critica", False, critical=True),
    ]

    result = evaluate_quality(checks)

    assert result.status == "NO_APTO"
    assert result.confidence == "BAJA"


def test_critical_not_assessable_is_not_silent_success():
    checks = [
        QualityCheck("integridad", None, critical=True),
    ]

    result = evaluate_quality(checks)

    assert result.status == "NO_APTO"
    assert result.confidence == "BAJA"


def test_non_applicable_check_does_not_change_result():
    checks = [
        QualityCheck("existencia", True),
        QualityCheck("modificacion_humana", False, critical=True, applicable=False),
    ]

    result = evaluate_quality(checks)

    assert result.status == "APTO"
    assert result.confidence == "ALTA"


def test_critical_failure_has_precedence_over_non_critical_warning():
    checks = [
        QualityCheck("consistencia", False, critical=False),
        QualityCheck("validez", False, critical=True),
    ]

    result = evaluate_quality(checks)

    assert result.status == "NO_APTO"
    assert result.confidence == "BAJA"


def test_same_input_is_deterministic():
    checks = (
        QualityCheck("existencia", True),
        QualityCheck("semantica", False, critical=False, material=True),
    )

    first = evaluate_quality(checks)
    second = evaluate_quality(checks)

    assert first == second


def test_quality_gate_does_not_produce_business_decision():
    result = evaluate_quality([QualityCheck("existencia", True)])

    assert not hasattr(result, "decision")
    assert result.status == "APTO"
