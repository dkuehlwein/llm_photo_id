#!/usr/bin/env python3
"""Quick analysis of experiment results."""
import sys
import json
import re
from pathlib import Path
from collections import defaultdict


def load_pairs_metadata():
    """Load pairs metadata for ground truth."""
    metadata_path = Path(__file__).parent.parent / "data" / "pairs_metadata.json"
    with open(metadata_path) as f:
        metadata = json.load(f)

    # Create lookup by pair_id
    return {pair["pair_id"]: pair for pair in metadata}


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
        # Look for "ANSWER: YES" or "ANSWER: NO" (expert format)
        match = re.search(r'answer:\s*(yes|no)', response_lower)
        if match:
            return match.group(1)

    # Fallback: check if "yes" or "no" appears early in response
    first_100 = response_lower[:100]
    if "yes" in first_100 and "no" not in first_100:
        return "yes"
    elif "no" in first_100 and "yes" not in first_100:
        return "no"

    return "unclear"


def extract_certainty(llm_response):
    """Extract certainty level from expert response."""
    response_lower = llm_response.lower()
    match = re.search(r'certainty:\s*(high|medium|low)', response_lower)
    if match:
        return match.group(1)
    return "unknown"


def analyze_results(results_file):
    """Analyze experiment results."""
    # Load pairs metadata for ground truth
    pairs_metadata = load_pairs_metadata()

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
    print(f"Naive prompts: {len(by_prompt.get('naive', []))}")
    print(f"Expert prompts: {len(by_prompt.get('expert', []))}")
    print()

    # Analyze each prompt type
    for prompt_type in ["naive", "expert"]:
        if prompt_type not in by_prompt:
            continue

        print("=" * 70)
        print(f"ANALYSIS: {prompt_type.upper()} PROMPT")
        print("=" * 70)

        prompt_results = by_prompt[prompt_type]
        correct = 0
        incorrect = 0
        unclear = 0
        error = 0

        by_category = defaultdict(lambda: {"correct": 0, "incorrect": 0, "total": 0, "error": 0})
        by_certainty = defaultdict(lambda: {"correct": 0, "incorrect": 0, "total": 0})

        # Track specific error patterns
        same_orientation_stats = {"correct": 0, "incorrect": 0, "total": 0}
        opposite_orientation_stats = {"correct": 0, "incorrect": 0, "total": 0}

        # Track by ground truth (same vs different)
        by_ground_truth = {
            "same": {"correct": 0, "incorrect": 0, "total": 0},
            "different": {"correct": 0, "incorrect": 0, "total": 0}
        }

        for result in prompt_results:
            try:
                pair_id = result["pair_id"]

                # Get ground truth from metadata
                if pair_id not in pairs_metadata:
                    print(f"Warning: {pair_id} not found in metadata")
                    error += 1
                    continue

                pair_meta = pairs_metadata[pair_id]
                ground_truth = pair_meta["ground_truth"]  # "same" or "different"
                category = pair_meta["category"]

                llm_response = result["llm_response"]
                decision = extract_decision(llm_response, prompt_type)

                # Map decision to ground truth
                if decision == "yes":
                    predicted = "same"
                elif decision == "no":
                    predicted = "different"
                else:
                    predicted = "unclear"

                # Extract certainty if expert prompt
                certainty = extract_certainty(llm_response) if prompt_type == "expert" else None

                # Check correctness
                is_correct = predicted == ground_truth

                if predicted == "unclear":
                    unclear += 1
                elif is_correct:
                    correct += 1
                    by_category[category]["correct"] += 1
                    by_ground_truth[ground_truth]["correct"] += 1
                    if certainty:
                        by_certainty[certainty]["correct"] += 1
                elif predicted != "unclear":
                    incorrect += 1
                    by_category[category]["incorrect"] += 1
                    by_ground_truth[ground_truth]["incorrect"] += 1
                    if certainty:
                        by_certainty[certainty]["incorrect"] += 1

                if predicted != "unclear":
                    by_category[category]["total"] += 1
                    by_ground_truth[ground_truth]["total"] += 1
                    if certainty:
                        by_certainty[certainty]["total"] += 1

                # Track orientation performance
                if "same_orientiation" in category:
                    same_orientation_stats["total"] += 1
                    if is_correct:
                        same_orientation_stats["correct"] += 1
                    else:
                        same_orientation_stats["incorrect"] += 1
                elif "opposite_orientiation" in category:
                    opposite_orientation_stats["total"] += 1
                    if is_correct:
                        opposite_orientation_stats["correct"] += 1
                    else:
                        opposite_orientation_stats["incorrect"] += 1

            except Exception as e:
                print(f"Error processing result for pair {result.get('pair_id')}: {e}")
                error += 1
                by_category['ERROR']["error"] += 1

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

        # By ground truth (main issue identified by Kostas)
        print(f"\nResults by Ground Truth:")
        for gt in ["same", "different"]:
            stats = by_ground_truth[gt]
            if stats["total"] > 0:
                acc = (stats["correct"] / stats["total"] * 100)
                print(f"  {gt.upper()}: {stats['correct']}/{stats['total']} correct ({acc:.0f}%)")

        # By orientation (main issue identified by Kostas)
        print(f"\nResults by Orientation:")
        if same_orientation_stats["total"] > 0:
            acc = (same_orientation_stats["correct"] / same_orientation_stats["total"] * 100)
            print(f"  Same orientation: {same_orientation_stats['correct']}/{same_orientation_stats['total']} correct ({acc:.0f}%)")
        if opposite_orientation_stats["total"] > 0:
            acc = (opposite_orientation_stats["correct"] / opposite_orientation_stats["total"] * 100)
            print(f"  Opposite orientation: {opposite_orientation_stats['correct']}/{opposite_orientation_stats['total']} correct ({acc:.0f}%)")

        # By certainty (if expert prompt)
        if prompt_type == "expert" and by_certainty:
            print(f"\nResults by Certainty Level:")
            for cert in ["high", "medium", "low"]:
                if cert in by_certainty:
                    stats = by_certainty[cert]
                    acc = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
                    print(f"  {cert.upper()}: {stats['correct']}/{stats['total']} correct ({acc:.0f}%)")

        # By category
        print(f"\nResults by Category:")
        for category in sorted(by_category.keys()):
            if category == 'ERROR':
                continue
            stats = by_category[category]
            cat_acc = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
            # Simplify category name for display
            cat_display = category.replace("_similarity_", "_sim_").replace("_match_", "_").replace("_orientiation", "")
            print(f"  {cat_display}")
            print(f"    {stats['correct']}/{stats['total']} correct ({cat_acc:.0f}%)")

        # Token stats
        if "token_usage" in results[0]:
            total_tokens = sum(r.get("token_usage", {}).get("total_tokens", 0) for r in prompt_results)
            avg_tokens = total_tokens / len(prompt_results) if prompt_results else 0
            print(f"\nToken Usage:")
            print(f"  Total: {total_tokens:,}")
            print(f"  Average per query: {avg_tokens:.0f}")
        print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Find most recent results file
        processed_dir = Path(__file__).parent.parent / "results" / "processed"
        raw_dir = Path(__file__).parent.parent / "results" / "raw_responses"

        # Check both locations
        results_files = []
        if processed_dir.exists():
            results_files.extend(processed_dir.glob("experiment_*.json"))
            results_files.extend(processed_dir.glob("results_*.json"))
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

    analyze_results(results_file)
