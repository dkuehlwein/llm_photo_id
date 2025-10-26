# Expert Prompt V3 - Diagnostic Approach

## The Problem We're Solving

After analyzing v1 and v2 results, we discovered that **the model is hallucinating matching geometric patterns that don't actually exist**:

- V1: 55.3% accuracy, with 100% SAME, 11% DIFFERENT
- V2: 47.4% accuracy, with 89% SAME, 5% DIFFERENT (worse!)

**Example from v2 (pair_016, ground truth: DIFFERENT turtles):**
```
Model claimed to see:
- "3-scale post-ocular cluster arranged identically"
- "Primary tympanic scale has identical shape"
- "T-shaped intersection in both images"
- "Precise geometry of junctions"
→ ANSWER: YES, CERTAINTY: HIGH

Reality: G15-03 ≠ gtJ204 (different individuals)
```

The model was **asserting** that patterns match without actually describing what it saw.

## Root Hypothesis

We need to understand: **What does the model actually see?**

Three possibilities:
1. Model sees different patterns but incorrectly claims they match
2. Model hallucinates similar patterns in both images
3. Model cannot see fine details but invents them to fill in gaps

## V3 Diagnostic Strategy

### Core Innovation: "Describe First, Then Compare"

Instead of asking the model to **compare** images directly, we:

1. **Force separate, detailed descriptions** of each image FIRST
2. **Then** have the model compare its own descriptions
3. **Require explicit evidence** by pointing back to what it described

### Key Mechanisms

#### 1. Structured Separate Descriptions (Step 3)

```
### IMAGE 1 - Detailed Description:
**Post-ocular scales:**
- Count: [X scales]
- Arrangement: [...]
- Individual shapes: [...]

**Tympanic region:**
- Overall pattern: [...]
- Largest scale(s): [...]
- Scale junctions: [Describe 2-3 specific junction points...]
- Distinctive irregularities: [...]

### IMAGE 2 - Detailed Description:
[Same structure - described independently]
```

**Why this works:**
- Prevents model from saying "both have X" without describing what X actually is
- Creates a record we can check for specificity
- Forces model to commit to what it sees before claiming a match

#### 2. Explicit "Cannot See" Options

Every field now includes options like:
- "Cannot see scale boundaries clearly enough"
- "Cannot identify specific junctions"
- "Cannot determine count accurately"
- "No distinctive irregularities visible"

**Why this matters:**
- Gives model permission to admit uncertainty
- Prevents hallucination by offering an honest alternative
- If model uses these frequently → automatic NO answer

#### 3. Point-by-Point Comparison (Step 4)

```
**Tympanic comparison:**
- Do the SPECIFIC junction points you described match?
  - Junction 1: [Does Image 1's junction 1 match Image 2's junction 1? Be explicit]
  - Junction 2: [...]
  - Junction 3: [...]
```

**Why this works:**
- Model must refer back to its Step 3 descriptions
- Can't make up new observations in the comparison phase
- Reveals whether descriptions were actually specific or vague

#### 4. Mandatory Evidence Quality Check (Step 5 & 6)

**Step 5: Can You See Well Enough?**
```
If you answered "Cannot see clearly" for multiple fields:
→ You MUST answer NO with LOW certainty

If you only described GENERIC/TYPICAL features:
→ You MUST answer NO with MEDIUM certainty
```

**Step 6: Evidence Checkboxes**
```
For SAME orientation:
☐ I can name at least 2-3 SPECIFIC geometric features that match precisely
☐ These features are UNUSUAL/DISTINCTIVE, not typical
☐ Someone reading my descriptions would conclude same individual

OR

☐ I can only say "both have 3 scales and typical patterns"
☐ My descriptions are vague or generic
☐ Patterns are common/typical for species
```

**Why this works:**
- Forces self-awareness about evidence quality
- Checkboxes create clear decision tree
- If negative boxes checked → must answer NO

#### 5. Updated Self-Check Questions

New questions specifically target the hallucination problem:

1. **Description Test**: "Did I identify SPECIFIC unusual features, or only generic patterns?"
2. **Comparison Test**: "Did I find PRECISE matches of specific features, or just general similarity?"
3. **Uniqueness Test**: "Could my descriptions apply to 10 turtles, or are they so specific only 1 would match?"

### Examples Include "Cannot See" Case

Added Example 4 showing how to handle insufficient image quality:
- Model admits it cannot see clearly
- Uses "Cannot see X" for multiple fields
- Step 5 triggers automatic NO with LOW certainty

## Expected Diagnostic Value

### What We'll Learn

**If v3 works better (accuracy improves):**
→ The model CAN see the differences when forced to describe separately
→ The problem was the comparison methodology
→ Solution: Keep the "describe first, compare second" approach

**If v3 still fails similarly:**
→ The model genuinely cannot see fine geometric details
→ Or it hallucinates similar patterns in its descriptions
→ Solution: This task may be beyond current multimodal LLM capabilities

**What to check in results:**
1. Are Step 3 descriptions specific or vague?
2. Does model use "Cannot see" options frequently?
3. When model says YES, can we verify the described features actually match?
4. When model says NO, are the Step 3 descriptions actually different?

### Specific Test Cases

**Pair 016 (v1 & v2: YES/HIGH, truth: DIFFERENT):**
- Will v3 describe different patterns in Step 3?
- Or will it describe "identical T-junctions" in both?

**Pair 036-038 (v1 & v2: YES/HIGH, truth: DIFFERENT):**
- Will v3 admit "no distinctive irregularities visible"?
- Or will it still claim to see specific matching features?

**Pair 002 (v2: NO/MEDIUM, truth: SAME):**
- V2 correctly identified insufficient evidence for opposite orientations
- Will v3 maintain this conservative approach?

## Implementation Notes

### How to Use This Prompt

1. **Update prompt builder** to use `expert_prompt_v3.txt` instead of v2
2. **Run on same 40 pairs** for direct comparison
3. **Analyze Step 3 descriptions carefully** - this is the diagnostic data
4. **Check correlation** between:
   - Description specificity vs. answer correctness
   - "Cannot see" usage vs. certainty levels
   - Generic descriptions vs. false positives

### Success Metrics

**Minimum acceptable improvement:**
- Overall accuracy > 55% (better than v2's 47%)
- DIFFERENT accuracy > 15% (better than v2's 5%)

**Good improvement:**
- Overall accuracy > 65%
- DIFFERENT accuracy > 40%
- More frequent use of NO/MEDIUM or NO/LOW

**Excellent improvement:**
- Overall accuracy > 75%
- DIFFERENT accuracy > 60%
- Balanced precision/recall

## Next Steps Based on Results

### Scenario A: V3 Works Well
→ The structured "describe first" approach solves the hallucination problem
→ Keep this methodology for production
→ May need minor tuning of thresholds

### Scenario B: V3 Improves but Still Suboptimal
→ The model can see some details but not reliably
→ Consider ensemble: v3 + MegaDescriptor + human review
→ Or use v3 only for initial filtering (high-confidence matches)

### Scenario C: V3 Doesn't Improve
→ The model genuinely cannot see fine geometric details
→ Or it hallucinates consistently in its descriptions too
→ Conclusion: This task exceeds current multimodal LLM capabilities
→ Alternatives:
  - Stick with MegaDescriptor (70%+ accuracy baseline)
  - Try different models (Claude, GPT-4V)
  - Require human verification for all matches
  - Use LLMs only for metadata extraction or quality assessment

## File Locations

- Prompt: `/prompts/expert_prompt_v3.txt`
- This doc: `/docs/expert_prompt_v3_changes.md`
- V2 analysis: `/docs/expert_prompt_v2_changes.md`
