# Full Experiment Analysis - 30 Pairs

**Date:** October 8, 2025
**Model:** Gemini 2.0 Flash Experimental
**Completed:** 30/40 pairs (quota limit reached at pair 31)
**Total queries:** 40 (10 naive + 30 expert)

## Overall Results

### Accuracy by Prompt Type

| Prompt | Correct | Total | Accuracy |
|--------|---------|-------|----------|
| **Naive** | 8 | 10 | **80.0%** |
| **Expert** | 12 | 30 | **40.0%** |

**Critical Finding:** Expert prompt performed WORSE overall due to harder categories.

## Results by Category

### Expert Prompt Performance

| Category | Correct | Total | Accuracy | MD Similarity Range |
|----------|---------|-------|----------|---------------------|
| **High sim, correct match, opposite** | 5/5 | 100% | ✅ 0.65-0.74 |
| **High sim, correct match, same** | 5/5 | 100% | ✅ 0.66-0.79 |
| **High sim, WRONG match, opposite** | 1/5 | 20% | ❌ 0.50-0.58 |
| **High sim, WRONG match, same** | 1/5 | 20% | ❌ 0.50-0.55 |
| **Low sim, correct match, opposite** | 0/5 | 0% | ❌ -0.05 to +0.06 |
| **Low sim, correct match, same** | 0/5 | 0% | ❌ -0.04 to +0.03 |

### Error Pattern Analysis

**Perfect Categories (100% accuracy):**
- When MegaDescriptor is HIGH similarity AND correct (same turtle)
- Both same and opposite orientations

**Failed Categories (0-20% accuracy):**
1. **High similarity, WRONG matches:** MD says high similarity but they're DIFFERENT turtles
   - LLM also fooled: Said "same" when ground truth is "different"
   - **False positive rate: 80%**

2. **Low similarity, correct matches:** MD says low similarity AND they're DIFFERENT turtles
   - LLM incorrectly said "same" when they're different
   - **False positive rate: 100%**

## Key Findings

### 1. LLM Mirrors MegaDescriptor Errors

The LLM is **highly susceptible to the same visual confusion** that fools MegaDescriptor:

- When MD gives high similarity to different turtles → LLM also says "same"
- When MD gives low similarity to different turtles → LLM STILL says "same" (even worse!)

### 2. Strong False Positive Bias

The expert prompt appears to have a **bias toward saying "Yes" (same turtle)**:

**Evidence:**
- 18/30 incorrect predictions
- 17/18 errors were **false positives** (said "same" when actually different)
- Only 1/18 error was false negative

**Hypothesis:** The structured expert prompt may be encouraging the model to find matching features, leading to confirmation bias.

### 3. Expert Prompt Works ONLY on Easy Cases

| Difficulty | Expert Accuracy | Notes |
|------------|-----------------|-------|
| Easy (high sim, correct) | 100% | Where MD is also correct |
| Hard (high sim, wrong) | 20% | Where MD is fooled |
| Very Hard (low sim) | 0% | Complete failure |

### 4. Naive vs Expert on Same Cases

On the first 10 pairs (only high-sim correct matches):
- Naive: 80% (2 errors)
- Expert: 100% (0 errors)

But on harder cases (pairs 11-30):
- Expert: Only 20-0% on challenging categories

## Error Examples

### False Positive (Expert, pair_011)
**Ground truth:** DIFFERENT turtles (t551 vs tsb056)
**MD similarity:** 0.577 (high - MD wrong)
**LLM decision:** "Yes" (same) - WRONG

**LLM reasoning:** "Facial scute patterns... appear to match when accounting for opposite orientations... head shape similar"

**Problem:** Model found superficial similarities and confirmed them, ignoring subtle but critical differences.

### False Positive (Expert, pair_021)
**Ground truth:** DIFFERENT turtles
**MD similarity:** -0.046 (very low - MD correct)
**LLM decision:** "Yes" (same) - WRONG

**Problem:** Even with NEGATIVE MD similarity (suggesting very different), LLM still said "same"!

## Token Usage

| Metric | Naive | Expert |
|--------|-------|--------|
| Avg tokens/query | 701 | 1,209 |
| Cost multiplier | 1.0x | 1.7x |

Expert prompt uses **71% more tokens** but doesn't improve accuracy on hard cases.

## Hypothesis Evaluation

### H1: Expert prompt outperforms naive ✅/❌ **PARTIALLY SUPPORTED**
- True on easy cases (100% vs 80%)
- False on hard cases (20% vs unknown)
- Overall: 40% vs 80% due to difficulty mix

### H2: LLMs show comparable accuracy ❓ **NEEDS MORE MODELS**
- Only tested Gemini so far
- Need Claude and GPT-4o for comparison

### H3: LLMs may outperform MD on hard cases ❌ **REJECTED**
- LLM shows **same failure modes** as MD
- High similarity errors: Both fooled
- Low similarity: LLM performs WORSE

### H4: Opposite orientations are harder ❌ **REJECTED**
- Opposite: 100% (naive), 100% (expert on easy)
- Same: 60% (naive), 100% (expert on easy)
- No evidence that opposite is harder

## Implications for Research

### 1. The Task is Harder Than Expected

The "wrong match" and "low similarity" categories represent cases where:
- Even human-guided expert prompts fail
- Visual similarity is genuinely ambiguous
- Individual loggerheads may have similar facial features

### 2. Expert Prompt Needs Refinement

Current issues:
- Too lenient / confirmation bias
- May need explicit "look for DIFFERENCES" instruction
- Should emphasize when features DON'T match

### 3. MegaDescriptor's Value is Clearer

MD's similarity scores are actually informative:
- High sim (>0.65) + correct: Both MD and LLM succeed
- High sim (0.50-0.58) + wrong: Both MD and LLM fail
- Low sim (<0.06): MD correct, LLM fails

**Insight:** MD is capturing real visual similarity, but that doesn't always correspond to individual identity.

## Recommendations

### Short-term
1. **Add negative examples to expert prompt:** Show what differences look like
2. **Reduce false positive bias:** Add "If uncertain, answer No"
3. **Test on remaining 10 pairs** (pairs 31-40) when quota resets

### Medium-term
1. **Compare multiple LLMs:** Claude, GPT-4o may have different biases
2. **Try ensemble approach:** Combine MD score + LLM decision
3. **Qualitative analysis:** Review reasoning for errors

### Long-term
1. **Few-shot learning:** Include example pairs in prompt
2. **Fine-tuning:** If patterns emerge, fine-tune on turtle ID
3. **Hybrid system:** MD for initial ranking, LLM for verification

## Remaining Work

**Incomplete:** Pairs 31-40 (quota limit)
- Categories: Low similarity wrong matches
- Need to complete for full dataset coverage

**Status:** 30/40 pairs complete (75%)

## Files

- Combined results: `results/processed/combined_results.json`
- Individual runs: `results/processed/experiment_*.json`
- Raw responses: `results/raw_responses/gemini/`

**Total tokens used:** ~43,000 (7k naive + 36k expert)
