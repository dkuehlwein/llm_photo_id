#!/usr/bin/env python3
"""Test script to run a single image pair through the system."""
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.llm_clients import GeminiClient
from src.experiment import PromptBuilder


def test_single_pair(pair_id="pair_001"):
    """Test with a single image pair."""
    # Load environment
    load_dotenv()

    # Load pairs metadata
    metadata_path = Path(__file__).parent.parent / "data" / "pairs_metadata.json"
    with open(metadata_path) as f:
        pairs = json.load(f)

    # Find the requested pair
    pair = None
    for p in pairs:
        if p['pair_id'] == pair_id:
            pair = p
            break

    if not pair:
        print(f"Error: Pair {pair_id} not found")
        return 1

    print(f"Testing with {pair_id}")
    print("=" * 70)
    print(f"Category: {pair['category']}")
    print(f"Ground truth: {pair['ground_truth']} individual(s)")
    print(f"Identities: {pair['identity1']} vs {pair['identity2']}")
    print(f"Images: {Path(pair['image1_path']).name} and {Path(pair['image2_path']).name}")
    print(f"Dates: {pair['date1']} and {pair['date2']}")
    print(f"Orientations: {pair['orientation_desc']}")
    print(f"MegaDescriptor similarity: {pair['md_similarity']:.4f}")
    print("=" * 70)

    # Initialize client and prompt builder
    client = GeminiClient()
    prompt_builder = PromptBuilder()

    # Test 1: Naive prompt
    print("\n" + "=" * 70)
    print("TEST 1: NAIVE PROMPT")
    print("=" * 70)
    naive_prompt = prompt_builder.build_naive_prompt()
    print(f"\nPrompt:\n{naive_prompt}\n")

    image1 = Path(pair['image1_path'])
    image2 = Path(pair['image2_path'])

    print("Querying Gemini...")
    try:
        naive_response = client.query_with_images(
            prompt=naive_prompt,
            image_paths=[image1, image2]
        )
        print(f"\nResponse:\n{naive_response['response']}")
        print(f"\nTokens used: {naive_response['metadata']['total_tokens']}")
    except Exception as e:
        print(f"Error: {e}")
        return 1

    # Test 2: Expert prompt
    print("\n" + "=" * 70)
    print("TEST 2: EXPERT PROMPT")
    print("=" * 70)
    expert_metadata = {
        "location": pair['location'],
        "date1": pair['date1'],
        "date2": pair['date2'],
        "orientation": pair['orientation_desc']
    }
    expert_prompt = prompt_builder.build_expert_prompt(expert_metadata)
    print(f"\nPrompt:\n{expert_prompt}\n")

    print("Querying Gemini...")
    try:
        expert_response = client.query_with_images(
            prompt=expert_prompt,
            image_paths=[image1, image2]
        )
        print(f"\nResponse:\n{expert_response['response']}")
        print(f"\nTokens used: {expert_response['metadata']['total_tokens']}")
    except Exception as e:
        print(f"Error: {e}")
        return 1

    # Summary
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print(f"Ground truth: {pair['ground_truth'].upper()}")
    print(f"MegaDescriptor similarity: {pair['md_similarity']:.4f}")
    print("\nNaive and expert prompts both completed successfully!")

    return 0


if __name__ == "__main__":
    # Allow command-line argument for pair_id
    pair_id = sys.argv[1] if len(sys.argv) > 1 else "pair_001"
    sys.exit(test_single_pair(pair_id))
