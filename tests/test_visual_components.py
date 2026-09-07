from eios.frontend.visual.components import (
    AppShell,
    ExecutiveDashboard,
    OperationForm,
    EvidencePanel,
    DecisionContextPanel,
    ExecutionStatus,
    ExecutiveResult,
    ScenarioList,
    TwinComparison,
)


def test_u11_mvp_components_are_presentation_adapters():
    assert all(cls.__dataclass_params__.frozen for cls in (
        AppShell,
        ExecutiveDashboard,
        OperationForm,
        EvidencePanel,
        DecisionContextPanel,
        ExecutionStatus,
        ExecutiveResult,
        ScenarioList,
        TwinComparison,
    ))


def test_u11_components_do_not_expose_decision_authority_methods():
    forbidden = {"approve", "reject", "rank", "recommend", "execute", "calculate"}
    classes = (
        AppShell, ExecutiveDashboard, OperationForm, EvidencePanel,
        DecisionContextPanel, ExecutionStatus, ExecutiveResult,
        ScenarioList, TwinComparison,
    )
    for cls in classes:
        assert not forbidden.intersection(dir(cls))
