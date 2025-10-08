#!/usr/bin/env python3
"""Combine multiple experiment result files."""
import sys
import json
from pathlib import Path


def combine_results(result_files):
    """Combine multiple result files into one."""
    all_results = []
    seen_pairs = set()

    for file_path in result_files:
        print(f"Loading {file_path.name}...")
        with open(file_path) as f:
            results = json.load(f)

        for result in results:
            # Skip errors and duplicates
            if "error" in result:
                continue

            pair_prompt_key = (result["pair_id"], result["prompt_type"])
            if pair_prompt_key in seen_pairs:
                continue

            seen_pairs.add(pair_prompt_key)
            all_results.append(result)

    print(f"\nCombined {len(all_results)} results")

    # Sort by pair_id and prompt_type
    all_results.sort(key=lambda r: (r["pair_id"], r["prompt_type"]))

    return all_results


if __name__ == "__main__":
    processed_dir = Path(__file__).parent.parent / "results" / "processed"

    # Get all result files
    result_files = sorted(processed_dir.glob("experiment_*.json"))

    if not result_files:
        print("No result files found!")
        sys.exit(1)

    print(f"Found {len(result_files)} result files")

    # Combine
    combined = combine_results(result_files)

    # Save
    output_file = processed_dir / "combined_results.json"
    with open(output_file, 'w') as f:
        json.dump(combined, f, indent=2)

    print(f"✓ Saved to {output_file}")

    # Summary
    by_prompt = {}
    for r in combined:
        pt = r["prompt_type"]
        by_prompt[pt] = by_prompt.get(pt, 0) + 1

    print(f"\nSummary:")
    for pt, count in sorted(by_prompt.items()):
        print(f"  {pt}: {count} queries")

    unique_pairs = len(set(r["pair_id"] for r in combined))
    print(f"  Total unique pairs: {unique_pairs}")
