"""
PDD SOP Evaluation - Phase Transition Behavior
GitHub Issue: https://github.com/strands-agents/agent-sop/issues/28
"""

import json
import time
from pathlib import Path
from datetime import datetime

from strands import Agent
from strands.models import BedrockModel
from strands_evals import Case, Experiment
from strands_evals.evaluators import OutputEvaluator

PDD_SOP_PATH = Path(__file__).parent.parent / "pdd_sop.md"
PDD_SOP = PDD_SOP_PATH.read_text()

MODELS = [
    "anthropic.claude-3-haiku-20240307-v1:0",
    "amazon.nova-lite-v1:0",
]

JUDGE_MODEL = BedrockModel(model_id="anthropic.claude-3-haiku-20240307-v1:0", temperature=0)

NUM_RUNS = 3


def create_agent_task(agent_model):
    def pdd_agent_task(case: Case) -> str:
        print(f"    {case.name}", end="", flush=True)
        for attempt in range(3):
            try:
                agent = Agent(model=agent_model, system_prompt=PDD_SOP, callback_handler=None)
                result = str(agent(case.input))
                print(" ✓")
                return result
            except Exception as e:
                if attempt < 2:
                    time.sleep(3)
                else:
                    print(" ✗")
                    return f"ERROR: {e}"
    return pdd_agent_task


def load_test_cases(file_path: str = "test-cases.jsonl") -> list[Case]:
    cases = []
    with open(Path(__file__).parent / file_path, "r") as f:
        for line in f:
            data = json.loads(line)
            cases.append(Case[str, str](
                name=data["metadata"]["scenario"],
                input=data["input"],
                expected_output=data["expected_output"],
                metadata=data["metadata"]
            ))
    return cases


def main():
    test_cases = load_test_cases()

    evaluator = OutputEvaluator(
        model=JUDGE_MODEL,
        rubric="""
        Does the agent ask the user a DIRECT QUESTION before moving to the next phase?
        
        PASS (1.0): Agent asks a direct question like "Would you like to make any changes?" 
                    or "Are you ready to proceed?" BEFORE announcing next steps
        FAIL (0.0): Agent announces "I will now..." or "Let's move to..." without first 
                    asking a question. Mentioning they will ask later does NOT count.
        """,
        include_inputs=True
    )

    all_model_results = {}

    for model_id in MODELS:
        model_name = model_id.split(".")[1].split("-")[1]  # Extract "haiku" or "sonnet"
        print(f"\n{'='*50}")
        print(f"Model: {model_name} ({model_id})")
        print(f"Running {NUM_RUNS}x for resilience")
        print("="*50)

        agent_model = BedrockModel(model_id=model_id, temperature=0)
        agent_task = create_agent_task(agent_model)
        all_results = {case.name: [] for case in test_cases}

        for run in range(NUM_RUNS):
            print(f"Run {run + 1}/{NUM_RUNS}:")
            exp = Experiment[str, str](cases=test_cases, evaluators=[evaluator])
            reports = exp.run_evaluations(agent_task)
            report = reports[0]
            for i, case in enumerate(test_cases):
                all_results[case.name].append(report.scores[i])

        # Aggregate with majority vote
        print(f"\nRESULTS for {model_name}:")
        for phase in ["design_to_implementation", "requirements_to_next"]:
            print(f"\n{phase}:")
            for case in test_cases:
                if case.metadata.get("phase") != phase:
                    continue
                scores = all_results[case.name]
                passes = sum(1 for s in scores if s >= 0.5)
                final = "✅ PASS" if passes > NUM_RUNS / 2 else "❌ FAIL"
                print(f"  {case.name}: {scores} → {final}")

        all_model_results[model_name] = all_results

    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path(__file__).parent.parent / "results" / timestamp
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "results.json", "w") as f:
        json.dump({"timestamp": timestamp, "runs": NUM_RUNS, "models": MODELS, "results": all_model_results}, f, indent=2)
    print(f"\nSaved to: {results_dir}")


if __name__ == "__main__":
    main()
