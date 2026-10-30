from deepeval.metrics import (
    ArgumentCorrectnessMetric,
    GEval,
    PlanAdherenceMetric,
    PlanQualityMetric,
    StepEfficiencyMetric,
    TaskCompletionMetric,
    ToolCorrectnessMetric,
)
from deepeval.test_case import SingleTurnParams, ToolCallParams
eval_model = "gpt-4o-mini"
SUCCESSFUL_TASK_DESCRIPTION = """
The AI fashion stylist successfully fulfills customer requests
using accurate information from the product catalog, inventory,
size charts, and knowledge base.

Success requires understanding customer intent, selecting the
appropriate tools efficiently, retrieving relevant products,
applying requested filters, verifying prices and availability,
recommending suitable sizes and outfits, and respecting budgets
and preferences.

The agent must provide clear, helpful, and accurate responses,
handle missing information appropriately, and never invent
products, prices, stock levels, or store policies.
"""

def build_metrics():
    """Keep the thresholds and evaluator model used by the individual scripts."""
    trace_metrics = [
        TaskCompletionMetric(
            threshold=0.7,
            model=eval_model,
            include_reason=True,
        )
        # ,
        # StepEfficiencyMetric(
        #     threshold=0.8, model=eval_model, include_reason=True,
        # ),
        # PlanQualityMetric(
        #     threshold=0.8, model=eval_model, include_reason=True,
        # ),
        # PlanAdherenceMetric(
        #     threshold=0.8, model=eval_model, include_reason=True,
        # ),
    ]
    single_turn_metrics = [
        ArgumentCorrectnessMetric(
            threshold=0.80, 
            model=eval_model,
            include_reason=True,
        ),
        ToolCorrectnessMetric(
            threshold=0.8, 
            model=eval_model,
            include_reason=True,
            # evaluation_params=[ToolCallParams.INPUT_PARAMETERS]
        ),
        GEval(
            name="Answer Correctness",
            evaluation_params=[
                SingleTurnParams.INPUT,
                SingleTurnParams.ACTUAL_OUTPUT,
                SingleTurnParams.EXPECTED_OUTPUT,
            ],
            evaluation_steps=[
                "Identify exactly what the user requested.",
                "Evaluate whether the actual output correctly answers that request.",
                "Compare factual information with the expected output. "
                "Treat semantically equivalent answers as correct even when "
                "their wording, formatting, or level of detail differs.",
                "Do not penalize additional helpful information, such as "
                "offering assistance or suggesting alternatives, provided "
                "it is relevant and does not contradict the expected answer.",
                "Award a high score when the requested information is fully "
                "and accurately provided, even if the actual output differs "
                "from the reference answer in presentation."
            ],
            threshold=0.75,
            model=eval_model,
            verbose_mode=True,
        ),
    ]
    return trace_metrics, single_turn_metrics
