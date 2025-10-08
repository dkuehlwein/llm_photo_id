#!/usr/bin/env python3
"""Run the full experiment on multiple image pairs."""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.llm_clients import GeminiClient
from src.experiment import ExperimentRunner, PromptBuilder


def main():
    """Run experiment on specified pairs."""
    parser = argparse.ArgumentParser(description="Run sea turtle re-identification experiment")
    parser.add_argument(
        "--pairs",
        type=str,
        default="1-10",
        help="Pairs to run (e.g., '1-10' or 'pair_001,pair_002')"
    )
    parser.add_argument(
        "--prompts",
        type=str,
        default="naive,expert",
        help="Comma-separated prompt types (naive, expert)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini",
        help="Model to use (gemini, claude, openai)"
    )
    args = parser.parse_args()

    # Load environment
    load_dotenv()

    # Parse pairs argument
    pairs_metadata_path = Path(__file__).parent.parent / "data" / "pairs_metadata.json"
    with open(pairs_metadata_path) as f:
        all_pairs = json.load(f)

    # Select pairs to run
    if "-" in args.pairs:
        # Range format: "1-10"
        start, end = map(int, args.pairs.split("-"))
        selected_pairs = all_pairs[start-1:end]
    elif "," in args.pairs:
        # List format: "pair_001,pair_002"
        pair_ids = [p.strip() for p in args.pairs.split(",")]
        selected_pairs = [p for p in all_pairs if p["pair_id"] in pair_ids]
    else:
        # Single number: "5"
        idx = int(args.pairs) - 1
        selected_pairs = [all_pairs[idx]]

    # Parse prompt types
    prompt_types = [p.strip() for p in args.prompts.split(",")]

    print(f"Sea Turtle Re-ID Experiment")
    print("=" * 70)
    print(f"Model: {args.model}")
    print(f"Pairs: {len(selected_pairs)}")
    print(f"Prompts: {', '.join(prompt_types)}")
    print(f"Total queries: {len(selected_pairs) * len(prompt_types)}")
    print("=" * 70)

    # Initialize client
    if args.model == "gemini":
        client = GeminiClient()
    else:
        print(f"Error: Model '{args.model}' not yet implemented")
        return 1

    # Create results directory
    results_dir = Path(__file__).parent.parent / "results" / "raw_responses" / args.model
    results_dir.mkdir(parents=True, exist_ok=True)

    # Initialize experiment runner
    runner = ExperimentRunner(
        llm_client=client,
        pairs_metadata_path=pairs_metadata_path,
        results_dir=results_dir
    )

    # Prepare pairs for runner
    pairs_to_run = []
    for pair in selected_pairs:
        pairs_to_run.append({
            "pair_id": pair["pair_id"],
            "image1_path": pair["image1_path"],
            "image2_path": pair["image2_path"],
            "metadata": {
                "location": pair["location"],
                "date1": pair["date1"],
                "date2": pair["date2"],
                "orientation": pair["orientation_desc"]
            },
            "ground_truth": pair["ground_truth"],
            "category": pair["category"],
            "md_similarity": pair["md_similarity"]
        })

    # Run experiment
    print(f"\nStarting experiment at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)

    results = runner.run_experiment(
        pairs_to_run=pairs_to_run,
        prompt_types=prompt_types,
        save_interval=5
    )

    # Save final results with ground truth
    processed_dir = Path(__file__).parent.parent / "results" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    processed_file = processed_dir / f"experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    # Add ground truth and category info to results
    for result in results:
        if "error" not in result:
            pair_id = result["pair_id"]
            pair_data = next((p for p in selected_pairs if p["pair_id"] == pair_id), None)
            if pair_data:
                result["ground_truth"] = pair_data["ground_truth"]
                result["category"] = pair_data["category"]
                result["md_similarity"] = pair_data["md_similarity"]

    with open(processed_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Processed results saved to: {processed_file}")

    # Print summary
    print("\n" + "=" * 70)
    print("EXPERIMENT COMPLETE")
    print("=" * 70)
    successful = len([r for r in results if "error" not in r])
    failed = len([r for r in results if "error" in r])
    print(f"Successful queries: {successful}/{len(results)}")
    if failed > 0:
        print(f"Failed queries: {failed}")

    # Calculate token usage
    total_tokens = sum(
        r.get("token_usage", {}).get("total_tokens", 0)
        for r in results if "error" not in r
    )
    print(f"Total tokens used: {total_tokens:,}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
