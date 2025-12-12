# PDD SOP Evaluation

Evaluation to prove that the PDD SOP jumps to implementation planning before confirming design iteration is complete.

**GitHub Issue:** https://github.com/strands-agents/agent-sop/issues/28

## Problem Statement

The PDD SOP's Step 6 (Create Detailed Design) proceeds to Step 7 (Develop Implementation Plan) without explicitly asking the user if they are done iterating on the design. This wastes time and context window.

## Expected Behavior

After completing the design phase, the agent should ask: "Are we done with the design?" before moving to implementation planning.

## Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Run Evaluation

```bash
python eval/run_evaluation.py
```

## Project Structure

```
pdd-sop-eval/
├── requirements.txt        # Dependencies
├── pdd_sop.md             # PDD SOP being evaluated
├── eval/
│   ├── eval-plan.md       # Evaluation plan
│   ├── test-cases.jsonl   # Test scenarios
│   └── run_evaluation.py  # Evaluation script
├── results/               # Evaluation outputs
└── README.md              # This file
```

## Test Cases

1. **basic_design_completion**: Agent completes design, user says "Looks good" → Should ask if done iterating
2. **design_with_feedback**: Agent incorporates user feedback → Should ask before implementation

## Expected Results

If the evaluation shows scores of 0.0 or 0.5, it confirms the issue: the PDD SOP does not ask for design confirmation before proceeding to implementation.
