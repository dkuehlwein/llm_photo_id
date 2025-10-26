# Expert Prompt V2 - Changes and Rationale

## Problem Summary

The original expert prompt (v1) resulted in catastrophic performance with Gemini 2.5 Pro:
- **Overall accuracy: 55.3%**
- **SAME individuals: 100% correct (19/19)**
- **DIFFERENT individuals: Only 11% correct (2/19)**

The model was saying "YES" in almost all cases, creating massive false positive rate.

## Root Causes Identified

### From Review 1:
1. **Too permissive with matching criteria** - Multiple alternative pathways to say YES
2. **No conservative bias** - No guidance to favor NO when uncertain
3. **Hallucination problem** - Model "seeing" matching patterns that don't exist
4. **Insufficient negative examples** - Only 1 of 4 scenarios showed non-match
5. **Self-check questions reinforcing errors** - Validating confidence instead of catching mistakes
6. **No threshold guidance** - Didn't specify how distinctive features must be

### From Review 2:
1. **Over-reliance on high-level features** - Model using coarse descriptions like "both have 3 scales"
2. **Post-ocular count as confirmation bias** - Matching counts treated as strong evidence (but it's like saying "both have 5 fingers")
3. **Insufficient guidance on "distinctive"** - Model not understanding difference between "similar" vs "uniquely matching"
4. **Decision framework ambiguity** - "Multiple features match" being satisfied by generic similarities
5. **Self-check questions not catching errors** - Model thinks it IS using geometric patterns (but at wrong level of detail)
6. **Image quality overconfidence** - Good images leading to false confidence

## Major Changes in V2

### 1. **Added "Resemblance ≠ Identity" Fundamental Principle** (NEW - Lines 5-6)

```
**Resemblance ≠ Identity.** Sea turtles of the same species often look very similar.
Your task is NOT to determine if they look similar, but whether they are definitively
the SAME individual. This requires finding UNIQUE, INDIVIDUAL-SPECIFIC features,
not just general similarity.
```

**Why:** Addresses the core conceptual error - model was matching based on similarity, not identity.

### 2. **Added Conservative Bias Warning** (NEW - Lines 8-10)

```
⚠️ **CRITICAL BIAS WARNING:**
**False positives (matching different individuals) are FAR MORE HARMFUL than false
negatives (missing a true match).** When in doubt, answer NO.
```

**Why:** Explicitly tells model to favor NO when uncertain, addressing lack of conservative threshold.

### 3. **Enhanced Post-Ocular Scale Guidance** (Lines 45-51)

**Original:**
```
- Count the number of scales
- Note their arrangement pattern
- Look at their geometric shapes
```

**New V2:**
```
- Count the number of scales
- ⚠️ **CRITICAL:** Matching scale count is NOT sufficient evidence for a match
- Many turtles of the same species have the same count (e.g., 3 post-ocular scales
  is common in loggerheads)
- Think of this like "both humans have 5 fingers" - it's necessary but NOT sufficient
- Look at their arrangement pattern and geometric shapes for UNIQUE configurations
```

**Why:** Prevents confirmation bias from matching scale counts. Addresses Review 2 issue #2.

### 4. **Explicit Guidance on Tympanic Pattern Specificity** (Lines 53-60)

**Added:**
```
- 🚨 **AVOID VAGUE DESCRIPTIONS:** Do not say "patterns are similar" or "arrangement is consistent"
- ✓ **BE SPECIFIC:** Identify exact junctions, unusual scale shapes, or unique irregularities
```

**Why:** Forces model to be specific instead of using generic descriptions. Addresses Review 2 issue #1.

### 5. **Complete Rewrite of Same-Orientation Comparison** (Lines 64-95)

**New Section: "CRITICAL REQUIREMENT FOR ANSWERING YES"**

Added concrete examples of acceptable vs. insufficient evidence:

**✓ ACCEPTABLE evidence:**
- "Both images show an unusual 5-way junction of scales at coordinates X, with a pentagonal scale immediately posterior..."

**✗ INSUFFICIENT evidence:**
- "Both have 3 post-ocular scales" (common, not distinctive)
- "The tympanic patterns are similar" (too vague)
- "Overall pattern matches" (be specific)

**Added KEY TEST:**
```
Ask yourself: "Could this description apply to 10 different turtles, or is it so
specific that only ONE individual would match?"

If your description could apply to many turtles → Answer NO
If your description identifies truly unique features → Consider YES
```

**Why:** This is the most critical change. Provides calibration for what "distinctive" means. Addresses Review 1 issues #3, #6 and Review 2 issues #3, #4.

### 6. **Enhanced Opposite Orientation Requirements** (Lines 97-122)

**Added specific examples:**
- ✓ "Both show an unusual tricolor pattern: dark brown vertical stripe from eye to jaw..."
- ✗ "Similar mottled pigmentation" (too vague)

**Added higher bar warning:**
```
🚨 **CRITICAL:** For opposite orientations, the bar for answering YES is MUCH HIGHER.
Default to NO unless you have truly compelling, specific evidence.
```

**Why:** Prevents false positives on opposite orientation pairs. Addresses Review 1 issue #5.

### 7. **Strengthened Secondary Features Warning** (Lines 124-147)

**Original:** "Use as confirmation"

**New V2:**
```
🚨 **CRITICAL WARNING:** Secondary features can ONLY support a match that is already
established by primary features...

**NEVER answer YES based solely on secondary features.**
```

**Removed problematic barnacle guidance:**
- Original: "But do rely on them if you know that the photos were taken a few weeks apart"
- V2: "Exception: If photos are from the same day/week AND you have other strong evidence, barnacles can provide weak supporting confirmation. But barnacles alone NEVER justify a YES"

**Why:** Prevents over-weighting of secondary features. Addresses Review 1 issue #1.

### 8. **Rewrote Decision Framework** (Lines 164-205)

**Added caveat at top:**
```
🚨 **REMEMBER:** You are claiming these are the SAME INDIVIDUAL, not just
similar-looking turtles. Be certain.
```

**HIGH certainty now requires:**
- Original: "Facial scale geometric patterns clearly match"
- V2: "You have identified MULTIPLE SPECIFIC, UNIQUE geometric features that match precisely (not just 'similar arrangements')" + "You can articulate EXACTLY which unique features match"

**MEDIUM certainty warning:**
```
⚠️ **DO NOT use MEDIUM certainty as a way to hedge when features are only
"generally similar."** If you're hedging, answer NO instead.
```

**NO/MEDIUM now explicitly includes:**
- "Features are only 'generally similar' but lack truly distinctive unique matches"
- "Post-ocular count matches but you cannot find SPECIFIC unique matching patterns in tympanic region"

**Why:** Prevents model from using MEDIUM as a hedge. Makes HIGH require true specificity. Addresses Review 2 issue #4.

### 9. **Enhanced Output Format** (Lines 211-259)

**Added new required fields:**
- "Quality caveat: [Note that good quality alone doesn't guarantee a match is possible]"
- "Post-ocular count significance: [Matching counts are necessary but NOT sufficient]"
- "Pattern assessment: [Clear match with specific unique features / Generically similar but not distinctively matched / ...]"

**Enhanced Tympanic pattern comparison field:**
- Original: "[Detailed description of whether patterns match or differ]"
- V2: "[DETAILED, SPECIFIC description - identify EXACT unique features or state that patterns are only generically similar]"

**Why:** Forces model to explicitly acknowledge quality/count limitations and be specific. Addresses Review 2 issue #6.

### 10. **Completely Rewritten Self-Check Questions** (Lines 261-278)

**NEW Questions (replacing old ones that reinforced errors):**

1. **Specificity Check**: "Have I identified SPECIFIC, UNIQUE geometric features... Or am I relying on generic similarities?"

2. **Vagueness Detection**: "Are my descriptions precise and detailed... or vague?" [If vague, you lack sufficient evidence for YES]

3. **False Positive Risk**: "If I'm wrong and these are different individuals, what would be the consequence?"

4. **Metadata Independence**: (kept from v1)

5. **Conservative Principle**: "When in doubt, have I defaulted to NO rather than hedging with a weak YES?"

6. **Orientation-Appropriate Evidence**:
   - Same: "Can I describe at least 2-3 SPECIFIC unique geometric features that match precisely, beyond just scale counts?"
   - Opposite: "Do I have HIGHLY distinctive pigmentation or scars that are truly individual-specific, not just generic similarity?"

**Why:** New questions actively catch the errors instead of reinforcing them. Addresses Review 1 issue #5.

### 11. **Expanded Example Scenarios** (Lines 290-390)

**Original:** 4 scenarios (1 non-match)

**New V2:** 6 scenarios (4 non-matches, including 2 "COMMON ERROR CASES")

**New Scenario 3: "Insufficient Evidence - Same Orientation (COMMON ERROR CASE)"**
- Shows a case where scale counts match and patterns are "similar" but lack truly distinctive features
- Answer: NO, CERTAINTY: MEDIUM
- Directly mirrors the error pattern from actual results (pairs 036, 037, 038)

**New Scenario 5: "Insufficient Evidence - Opposite Orientations (COMMON ERROR CASE)"**
- Shows generic pigmentation similarity ("yellowish-tan with dark mottling")
- Explicitly states this describes most loggerheads
- Answer: NO, CERTAINTY: MEDIUM
- Mirrors error pattern from opposite orientation wrong matches

**Why:** Provides calibration examples showing when to say NO despite similarity. Addresses Review 1 issue #4 and Review 2 issue #3.

### 12. **Restructured Critical Reminders** (Lines 296-320)

**Reordered priorities:**
1. **MOST IMPORTANT:** Conservative matching principle (NEW - was not in v1)
2. **SECOND MOST IMPORTANT:** Ignore metadata (was "most important" in v1)

**Added to INSUFFICIENT EVIDENCE list:**
- Matching post-ocular scale count alone (NEW)
- "Similar patterns" or "consistent arrangement" (NEW)
- "Overall similarity" or "appears to match" (NEW)

**Why:** Conservative matching is now the top priority. Explicitly lists all the vague descriptions that appeared in error cases.

## Summary of Approach

The V2 prompt uses **multiple reinforcing strategies** to prevent false positives:

1. **Conceptual framing:** "Resemblance ≠ Identity" sets the right mental model
2. **Explicit bias:** "When in doubt, answer NO" overrides natural tendency to find matches
3. **Concrete calibration:** Examples show exactly what counts as "distinctive" vs "generic"
4. **Forced specificity:** Output format requires acknowledging when evidence is insufficient
5. **Error-catching questions:** Self-checks designed to detect vague reasoning
6. **Negative examples:** Multiple scenarios showing when to say NO despite similarity
7. **Removed loopholes:** Eliminated alternative pathways to YES via secondary features

## Expected Impact

The V2 prompt should:

1. **Reduce false positives:** Model should stop matching based on "3 post-ocular scales" or "similar patterns"
2. **Increase specificity:** Model forced to describe exact junctions, unique irregularities
3. **Better calibration:** Model learns difference between "looks similar" and "same individual"
4. **More NOs:** Conservative bias should increase NO answers on ambiguous pairs
5. **Better MEDIUM/LOW usage:** Model should use lower certainty or switch to NO instead of hedging with weak YES

## Testing Recommendations

1. **Re-run experiment** with same pairs using expert_prompt_v2
2. **Key metrics to watch:**
   - Different individuals accuracy (currently 11%, target >70%)
   - Overall false positive rate (currently 45%, target <15%)
   - Distribution of certainty levels (should see more LOW/MEDIUM for uncertain cases)
3. **Qualitative analysis:**
   - Check if model uses specific geometric descriptions
   - Verify model acknowledges when features are "generic"
   - Confirm model uses NO for "similar but not distinctive" cases

## File Location

New prompt: `/prompts/expert_prompt_v2.txt`
Original prompt: `/prompts/expert_prompt.txt` (preserved for comparison)
