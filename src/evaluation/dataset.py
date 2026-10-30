from deepeval.dataset import EvaluationDataset, Golden

import json
from pathlib import Path
from deepeval.test_case import ToolCall


def build_dataset():
        
    DATASET_PATH = (
            Path(__file__).resolve().parents[1]
            / "assets"
            / "agent_eval"
            / "agent_goldens.json"
        )

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
            eval_data = json.load(f)
            
    goldens = []
    for item in eval_data:

        expected_tools =[ 
            ToolCall(
                name = i["tool_name"],
                input_parameters = i["input_parameters"]
            )
            for i in item["expected_tools"]
        ]

        goldens.append(
            Golden(
                input = item["query"],
                expected_output = item["ground_truth"],
                expected_tools = expected_tools
            )
        )   


    return EvaluationDataset(goldens=goldens)

dataset = build_dataset()
# print(dataset)