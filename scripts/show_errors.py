#!/usr/bin/env python3
"""Show incorrect predictions in detail."""
import sys
import json
import re
from pathlib import Path


def extract_decision(llm_response, prompt_type):
    """Extract Yes/No decision from LLM response."""
    response_lower = llm_response.lower()

    if prompt_type == "naive":
        if re.search(r'\*\*answer:\s*yes\*\*', response_lower) or response_lower.startswith("**yes**"):
            return "yes"
        elif re.search(r'\*\*answer:\s*no\*\*', response_lower) or response_lower.startswith("**no**"):
            return "no"
    elif prompt_type == "expert":
        match = re.search(r'final decision:\s*\*?\*?(yes|no)\*?\*?', response_lower)
        if match:
            return match.group(1)

    first_100 = response_lower[:100]
    if "yes" in first_100 and "no" not in first_100:
        return "yes"
    elif "no" in first_100 and "yes" not in first_100:
        return "no"

    return "unclear"


def show_errors(results_file):
    """Show detailed error cases."""
    with open(results_file) as f:
        results = json.load(f)

    errors = []
    for result in results:
        ground_truth = result["ground_truth"]
        decision = extract_decision(result["llm_response"], result["prompt_type"])

        if decision == "yes":
            predicted = "same"
        elif decision == "no":
            predicted = "different"
        else:
            predicted = "unclear"

        if predicted != ground_truth:
            errors.append(result)

    if not errors:
        print("✓ No errors found! All predictions were correct.")
        return

    print(f"Found {len(errors)} error(s):")
    print("=" * 70)

    for i, error in enumerate(errors, 1):
        print(f"\nERROR {i}:")
        print(f"Pair: {error['pair_id']}")
        print(f"Prompt: {error['prompt_type']}")
        print(f"Category: {error['category']}")
        print(f"Ground truth: {error['ground_truth'].upper()}")
        print(f"MD similarity: {error['md_similarity']:.4f}")

        decision = extract_decision(error["llm_response"], error["prompt_type"])
        predicted = "same" if decision == "yes" else "different" if decision == "no" else "unclear"
        print(f"LLM decision: {decision.upper()} (predicted: {predicted.upper()})")

        print(f"\nLLM Response (first 500 chars):")
        print("-" * 70)
        print(error["llm_response"][:500])
        if len(error["llm_response"]) > 500:
            print("... (truncated)")
        print("-" * 70)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        processed_dir = Path(__file__).parent.parent / "results" / "processed"
        results_files = sorted(processed_dir.glob("experiment_*.json"), reverse=True)
        if results_files:
            results_file = results_files[0]
        else:
            print("No results files found!")
            sys.exit(1)
    else:
        results_file = Path(sys.argv[1])

    show_errors(results_file)
