"""Phase 8B tests for real FORTRESS gateway evaluation."""

from deepeval.test_case import LLMTestCase

from fortress_mcp.evaluation.gateway_evaluation import (
    build_security_scenarios,
    evaluate_scenario,
)
from fortress_mcp.evaluation.metrics import FortressSecurityMetric


def test_all_security_scenarios_execute_through_real_gateway() -> None:
    """Every evaluation scenario must execute through FortressGateway."""
    scenarios = build_security_scenarios()

    assert len(scenarios) == 5

    for scenario in scenarios:
        test_case, response = evaluate_scenario(scenario)

        assert isinstance(test_case, LLMTestCase)
        assert response.decision == scenario.expected_decision
        assert response.success is scenario.expected_success


def test_real_gateway_outputs_can_be_scored_by_deepeval() -> None:
    """Real gateway outcomes must be scoreable by the security metric."""
    metric = FortressSecurityMetric()

    for scenario in build_security_scenarios():
        test_case, response = evaluate_scenario(scenario)

        actual_output = (
            f"decision={response.decision};"
            f"success={response.success}"
        )

        expected_output = (
            f"decision={scenario.expected_decision};"
            f"success={scenario.expected_success}"
        )

        evaluation_case = LLMTestCase(
            input=test_case.input,
            actual_output=actual_output,
            expected_output=expected_output,
        )

        score = metric.measure(evaluation_case)

        assert score == 1.0
        assert metric.is_successful() is True


def test_prompt_injection_is_denied_by_real_gateway() -> None:
    """Prompt injection must not independently grant authorization."""
    scenarios = build_security_scenarios()

    scenario = next(
        item
        for item in scenarios
        if item.name == "prompt injection cannot authorize"
    )

    _, response = evaluate_scenario(scenario)

    assert response.decision == scenario.expected_decision
    assert response.success is False

