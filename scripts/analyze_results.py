#!/usr/bin/env python3
"""Quick analysis of experiment results."""
import sys
import json
import re
from pathlib import Path
from collections import defaultdict


def extract_decision(llm_response, prompt_type):
    """Extract Yes/No decision from LLM response."""
    response_lower = llm_response.lower()

    if prompt_type == "naive":
        # Look for "Answer: Yes" or "Answer: No" or **Yes** at start
        if re.search(r'\*\*answer:\s*yes\*\*', response_lower) or response_lower.startswith("**yes**"):
            return "yes"
        elif re.search(r'\*\*answer:\s*no\*\*', response_lower) or response_lower.startswith("**no**"):
            return "no"

    elif prompt_type == "expert":
        # Look for "Final Decision: Yes" or "Final Decision: No"
        match = re.search(r'final decision:\s*\*?\*?(yes|no)\*?\*?', response_lower)
        if match:
            return match.group(1)

    # Fallback: check if "yes" or "no" appears early in response
    first_100 = response_lower[:100]
    if "yes" in first_100 and "no" not in first_100:
        return "yes"
    elif "no" in first_100 and "yes" not in first_100:
        return "no"

    return "unclear"


def analyze_results(results_file):
    """Analyze experiment results."""
    with open(results_file) as f:
        results = json.load(f)

    print(f"Analyzing: {results_file}")
    print("=" * 70)

    # Overall stats
    total = len(results)
    by_prompt = defaultdict(list)

    for result in results:
        prompt_type = result["prompt_type"]
        by_prompt[prompt_type].append(result)

    print(f"Total queries: {total}")
    print(f"Naive prompts: {len(by_prompt['naive'])}")
    print(f"Expert prompts: {len(by_prompt['expert'])}")
    print()

    # Analyze each prompt type
    for prompt_type in ["naive", "expert"]:
        print("=" * 70)
        print(f"ANALYSIS: {prompt_type.upper()} PROMPT")
        print("=" * 70)

        prompt_results = by_prompt[prompt_type]
        correct = 0
        incorrect = 0
        unclear = 0
        error = 0

        by_category = defaultdict(lambda: {"correct": 0, "incorrect": 0, "total": 0, "error": 0})

        for result in prompt_results:
            try:
                ground_truth = result["ground_truth"]  # "same" or "different"
                llm_response = result["llm_response"]
                category = result["category"]

                decision = extract_decision(llm_response, prompt_type)

                # Map decision to ground truth
                if decision == "yes":
                    predicted = "same"
                elif decision == "no":
                    predicted = "different"
                else:
                    predicted = "unclear"

                # Check correctness
                if predicted == ground_truth:
                    correct += 1
                    by_category[category]["correct"] += 1
                elif predicted == "unclear":
                    unclear += 1
                else:
                    incorrect += 1
                    by_category[category]["incorrect"] += 1
                by_category[category]["total"] += 1
            except Exception as e:
                print(f"Error processing result for pair {result.get('pair_id')}: {e}")
                error += 1
                by_category['na']["error"] += 1
            

        # Overall accuracy
        total_clear = correct + incorrect
        accuracy = (correct / total_clear * 100) if total_clear > 0 else 0

        print(f"\nOverall Results:")
        print(f"  Correct: {correct}/{total_clear} ({accuracy:.1f}%)")
        print(f"  Incorrect: {incorrect}/{total_clear}")
        if unclear > 0:
            print(f"  Unclear: {unclear}")
        if error > 0:
            print(f"  Errors: {error}")

        # By category
        print(f"\nResults by Category:")
        for category in sorted(by_category.keys()):
            stats = by_category[category]
            cat_acc = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"  {category}")
            print(f"    {stats['correct']}/{stats['total']} correct ({cat_acc:.0f}%)")

        """
        # Token stats
        total_tokens = sum(r["token_usage"]["total_tokens"] for r in prompt_results)
        avg_tokens = total_tokens / len(prompt_results) if prompt_results else 0
        print(f"\nToken Usage:")
        print(f"  Total: {total_tokens:,}")
        print(f"  Average per query: {avg_tokens:.0f}")
        print()
        """

    # Compare prompts
    print("=" * 70)
    print("COMPARISON")
    print("=" * 70)

    """
    naive_correct = sum(1 for r in by_prompt['naive']
                       if extract_decision(r["llm_response"], "naive") ==
                       ("yes" if r["ground_truth"] == "same" else "no"))
    expert_correct = sum(1 for r in by_prompt['expert']
                        if extract_decision(r["llm_response"], "expert") ==
                        ("yes" if r["ground_truth"] == "same" else "no"))

    n_naive = len(by_prompt['naive'])
    n_expert = len(by_prompt['expert'])

    naive_acc = (naive_correct / n_naive * 100) if n_naive > 0 else 0
    expert_acc = (expert_correct / n_expert * 100) if n_expert > 0 else 0

    print(f"Naive accuracy:  {naive_correct}/{n_naive} ({naive_acc:.1f}%)")
    print(f"Expert accuracy: {expert_correct}/{n_expert} ({expert_acc:.1f}%)")
    print(f"Improvement: {expert_acc - naive_acc:+.1f} percentage points")
    """

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Find most recent results file
        processed_dir = Path(__file__).parent.parent / "results" / "processed"
        results_files = sorted(processed_dir.glob("experiment_*.json"), reverse=True)
        if results_files:
            results_file = results_files[0]
        else:
            print("No results files found!")
            sys.exit(1)
    else:
        results_file = Path(sys.argv[1])

    analyze_results(results_file)
