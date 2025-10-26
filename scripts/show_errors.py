#!/usr/bin/env python3
"""Show incorrect predictions in detail."""
import sys
import json
import re
from pathlib import Path


def extract_decision(llm_response, prompt_type):
    """Extract Yes/No decision from LLM response."""
    response_lower = llm_response.lower()

        # Look for "ANSWER: YES" or "ANSWER: NO" (expert format)
    match = re.search(r'answer:\s*(yes|no)', response_lower)
    if match:
        return match.group(1)

    return "unclear"


def load_pairs_metadata():
    """Load pairs metadata for ground truth."""
    metadata_path = Path(__file__).parent.parent / "data" / "pairs_metadata.json"
    with open(metadata_path) as f:
        metadata = json.load(f)
    return {pair["pair_id"]: pair for pair in metadata}


def show_errors(results_file):
    """Show detailed error cases."""
    # Load ground truth metadata
    pairs_metadata = load_pairs_metadata()

    with open(results_file) as f:
        results = json.load(f)

    errors = []
    for result in results:
        pair_id = result["pair_id"]

        # Get ground truth from metadata
        if pair_id not in pairs_metadata:
            continue

        pair_meta = pairs_metadata[pair_id]
        ground_truth = pair_meta["ground_truth"].lower()

        decision = extract_decision(result["llm_response"], result["prompt_type"])

        if decision == "yes":
            predicted = "same"
        elif decision == "no":
            predicted = "different"
        else:
            predicted = "unclear"

        if predicted != ground_truth:
            # Add metadata to result for display
            result["ground_truth"] = ground_truth
            result["category"] = pair_meta["category"]
            result["md_similarity"] = pair_meta.get("md_similarity", 0.0)
            result["orientation"] = pair_meta.get("orientation", "unknown")
            result["certainty"] = extract_certainty(result["llm_response"])
            errors.append(result)

    if not errors:
        print("✓ No errors found! All predictions were correct.")
        return

    print(f"Found {len(errors)} error(s):")
    print("=" * 70)

    for i, error in enumerate(errors, 1):
        print(f"\nERROR {i}:")
        print(f"Pair: {error['pair_id']}")
        print(f"Category: {error['category']}")
        print(f"Ground truth: {error['ground_truth'].upper()}")
        print(f"Orientation: {error['orientation']}")
        print(f"MD similarity: {error['md_similarity']:.4f}")

        decision = extract_decision(error["llm_response"], error["prompt_type"])
        predicted = "same" if decision == "yes" else "different" if decision == "no" else "unclear"
        print(f"LLM decision: {decision.upper()} (predicted: {predicted.upper()})")
        print(f"Certainty: {error['certainty']}")

        print(f"\nLLM Response (first 500 chars):")
        print("-" * 70)
        print(error["llm_response"][:500])
        if len(error["llm_response"]) > 500:
            print("... (truncated)")
        print("-" * 70)


def extract_certainty(llm_response):
    """Extract certainty level from expert response."""
    response_lower = llm_response.lower()
    match = re.search(r'certainty:\s*(high|medium|low)', response_lower)
    if match:
        return match.group(1).upper()
    return "UNKNOWN"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Check both processed and raw directories
        base_dir = Path(__file__).parent.parent / "results"
        results_files = []

        processed_dir = base_dir / "processed"
        if processed_dir.exists():
            results_files.extend(processed_dir.glob("experiment_*.json"))
            results_files.extend(processed_dir.glob("results_*.json"))

        raw_dir = base_dir / "raw_responses"
        if raw_dir.exists():
            for subdir in raw_dir.iterdir():
                if subdir.is_dir():
                    results_files.extend(subdir.glob("results_*.json"))

        results_files = sorted(results_files, reverse=True)
        if results_files:
            results_file = results_files[0]
            print(f"No file specified, using most recent: {results_file.name}\n")
        else:
            print("No results files found!")
            sys.exit(1)
    else:
        results_file = Path(sys.argv[1])

    show_errors(results_file)
