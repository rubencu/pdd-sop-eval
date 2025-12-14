# PDD SOP Evaluation

Evaluation framework to test and fix the PDD SOP's phase transition behavior.

**GitHub Issue:** https://github.com/strands-agents/agent-sop/issues/28

## Problem

The PDD SOP's Step 6 (Create Detailed Design) was missing explicit "ask before proceeding" constraints, allowing agents to jump to implementation without user confirmation.

## Solution

Added constraints to Step 6 matching the pattern in Step 3:
```markdown
- You MUST explicitly ask the user if they are ready to proceed to implementation before moving to Step 7
- You MUST NOT proceed to the implementation plan step without explicit user confirmation
```

## Results Summary

| Model | Before Fix | After Fix |
|-------|------------|-----------|
| Nova Micro | 50% | 100% ✅ |
| Nova Lite | 50% | 100% ✅ |
| Nova Pro | 25% | 100% ✅ |
| Claude 3 Haiku | 25% | 75% |
| Mistral Small | 50% | 50% |

See [REPORT.md](REPORT.md) for detailed results.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Evaluation

```bash
python eval/run_evaluation.py
```

## Models Tested

- `anthropic.claude-3-haiku-20240307-v1:0`
- `amazon.nova-micro-v1:0`
- `amazon.nova-lite-v1:0`
- `amazon.nova-pro-v1:0`
- `mistral.mistral-small-2402-v1:0`

## Project Structure

```
pdd-sop-eval/
├── pdd_sop.md             # PDD SOP with fix applied
├── eval/
│   ├── run_evaluation.py  # Multi-model evaluation script
│   └── test-cases.jsonl   # Test scenarios
├── REPORT.md              # Detailed evaluation report
└── results/               # Evaluation outputs (gitignored)
```

## Key Finding

Nova models follow SOP constraints literally and pass all tests. Claude and Mistral interpret "Perfect" as a completion signal and sometimes skip the confirmation step.

For SOP execution, literal instruction-following beats general intelligence.
