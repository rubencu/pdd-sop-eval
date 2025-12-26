# PDD SOP Evaluation Report

## Overview

This evaluation tests whether the PDD (Prompt-Driven Development) SOP properly requires user confirmation before transitioning between phases. Specifically, it tests the design→implementation transition (Step 6→7) against the requirements→next transition (Step 3→4).

**Related Issue:** https://github.com/strands-agents/agent-sop/issues/28

## The Bug

The original SOP had explicit "ask before proceeding" constraints in Step 3 (Requirements):
```markdown
- You MUST explicitly ask the user if they feel the requirements clarification is complete before moving to the next step
- You MUST NOT proceed with any other steps until explicitly directed by the user
```

But Step 6 (Design) only had:
```markdown
- You MUST review the design with the user and iterate based on feedback
```

This allowed agents to jump from design to implementation without asking, even when users gave ambiguous responses like "Looks good" or "Perfect".

## The Fix

Added explicit constraints to Step 6:
```markdown
- You MUST explicitly ask the user if they are ready to proceed to implementation before moving to Step 7
- You MUST NOT proceed to the implementation plan step without explicit user confirmation because this could skip important design refinement
```

## Test Cases

| Test Case | Phase | User Response | Expected Behavior |
|-----------|-------|---------------|-------------------|
| design_looks_good | Design → Implementation | "Looks good" | Ask before proceeding |
| design_perfect | Design → Implementation | "Perfect" | Ask before proceeding |
| reqs_looks_good | Requirements → Next | "Looks good" | Ask before proceeding |
| reqs_perfect | Requirements → Next | "Perfect" | Ask before proceeding |

## Methodology

- Each model runs 3x per test case for resilience
- Majority vote determines pass/fail
- LLM judge (Haiku) evaluates if agent asks a direct question before proceeding
- Pass threshold: ≥0.5 score on majority of runs

## Results

### Before Fix

| Model | design_looks_good | design_perfect | reqs_looks_good | reqs_perfect |
|-------|-------------------|----------------|-----------------|--------------|
| Claude 3 Haiku | ❌ 1/3 | ❌ 0/3 | ✅ 3/3 | ✅ 3/3 |
| Nova Micro | ✅ 3/3 | ❌ 0/3 | ✅ 3/3 | ✅ 2/3 |
| Nova Lite | ✅ 3/3 | ❌ 0/3 | ✅ 3/3 | ✅ 2/3 |
| Nova Pro | ❌ 0/3 | ❌ 0/3 | ✅ 3/3 | ❌ 0/3 |
| Mistral Small | ✅ 3/3 | ❌ 0/3 | ✅ 3/3 | ❌ 0/3 |

**Summary Before Fix:**
- `design_looks_good`: 10/15 (67%)
- `design_perfect`: 0/15 (0%) ← Clear bug
- `reqs_looks_good`: 15/15 (100%)
- `reqs_perfect`: 10/15 (67%)

### After Fix

| Model | design_looks_good | design_perfect | reqs_looks_good | reqs_perfect |
|-------|-------------------|----------------|-----------------|--------------|
| Claude 3 Haiku | ✅ 3/3 | ❌ 0/3 | ✅ 3/3 | ✅ 3/3 |
| Nova Micro | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| Nova Lite | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 2/3 |
| Nova Pro | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| Mistral Small | ✅ 3/3 | ❌ 0/3 | ✅ 3/3 | ❌ 0/3 |

**Summary After Fix:**
- `design_looks_good`: 15/15 (100%) ← Fixed
- `design_perfect`: 9/15 (60%) ← Improved from 0%
- `reqs_looks_good`: 15/15 (100%)
- `reqs_perfect`: 11/15 (73%)

## Analysis

### Fix Effectiveness

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| design_looks_good | 67% | 100% | +33% ✅ |
| design_perfect | 0% | 60% | +60% ✅ |

The fix successfully brings `design_looks_good` to 100% pass rate, matching `reqs_looks_good`.

### Model Behavior Patterns

**Nova Models (Micro, Lite, Pro):**
- Pass all tests after fix
- Most literal instruction-followers
- Best suited for SOP execution

**Claude 3 Haiku & Mistral Small:**
- Pass `looks_good` tests
- Fail `perfect` tests consistently
- Interpret "Perfect" as strong completion signal, overriding constraints
- "Too smart" - infer user intent rather than following literal instructions

### The "Perfect" Edge Case

The word "Perfect" triggers different behavior than "Looks good":
- Models interpret it as definitive approval
- Some models override explicit SOP constraints
- This is a model limitation, not an SOP issue
- The SOP fix helps but cannot fully overcome this for all models

## Conclusions

1. **The fix works** - Design transition now behaves like requirements transition for the common case (`looks_good`)

2. **Nova models are best for SOPs** - They follow instructions literally without inferring user intent

3. **"Perfect" is a hard edge case** - Strong completion signals can override constraints in some models

4. **The SOP is now consistent** - Both Step 3 and Step 6 have explicit "ask before proceeding" constraints

## Constraint Formulation Experiment

We tested whether the two-line constraint could be simplified to a single line.

### Variants Tested

1. **Two lines (original):**
   ```markdown
   - You MUST explicitly ask the user if they are ready to proceed to implementation before moving to Step 7
   - You MUST NOT proceed to the implementation plan step without explicit user confirmation because this could skip important design refinement
   ```

2. **MUST only:**
   ```markdown
   - You MUST explicitly ask the user if they are ready to proceed to implementation before moving to Step 7
   ```

3. **MUST NOT only:**
   ```markdown
   - You MUST NOT proceed to the implementation plan step without explicit user confirmation
   ```

### Results (design_to_implementation pass rate)

| Variant | Haiku | Nova Micro | Nova Lite | Nova Pro | Mistral |
|---------|-------|------------|-----------|----------|---------|
| Two lines | 75% | 100% | 100% | 100% | 50% |
| MUST only | 0% | 100% | 100% | 50% | 100% |
| MUST NOT only | 50% | 50% | 0% | 0% | 0% |

### Analysis

- **MUST NOT alone performs worst** - Models know what not to do but lack guidance on what to do instead
- **MUST alone is inconsistent** - Works for some models but Haiku dropped to 0%, Pro to 50%
- **Two lines together is most robust** - The positive constraint tells models what to do, the negative reinforces it

### Conclusion

Keep both constraints. The MUST + MUST NOT pattern provides:
1. Clear action to take (ask)
2. Clear prohibition (don't proceed without confirmation)
3. Rationale for the prohibition (helps models understand intent)

## Recommendations

1. **Apply the fix to the main PDD SOP** in the agent-sop repository

2. **For SOP authors:** Always include explicit "MUST ask" and "MUST NOT proceed without confirmation" constraints at phase transitions - use both together for robustness

3. **For model selection:** Prefer Nova models for SOP execution when literal instruction-following is critical

4. **For users:** Avoid strong completion signals like "Perfect" if you want the agent to pause and confirm
