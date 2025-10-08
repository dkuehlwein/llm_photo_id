"""Experiment orchestration and execution."""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import time

from ..llm_clients.base import BaseLLMClient
from .prompt_builder import PromptBuilder


class ExperimentRunner:
    """Orchestrates the experiment execution."""

    def __init__(
        self,
        llm_client: BaseLLMClient,
        pairs_metadata_path: Path,
        results_dir: Path,
        prompt_builder: Optional[PromptBuilder] = None
    ):
        """
        Initialize experiment runner.

        Args:
            llm_client: LLM client instance
            pairs_metadata_path: Path to JSON/CSV with pair metadata
            results_dir: Directory to save results
            prompt_builder: PromptBuilder instance (creates default if None)
        """
        self.llm_client = llm_client
        self.pairs_metadata_path = Path(pairs_metadata_path)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.prompt_builder = prompt_builder or PromptBuilder()

        # Load pairs metadata
        self.pairs_metadata = self._load_pairs_metadata()

    def _load_pairs_metadata(self) -> List[Dict[str, Any]]:
        """Load pairs metadata from file."""
        if not self.pairs_metadata_path.exists():
            raise FileNotFoundError(f"Pairs metadata not found: {self.pairs_metadata_path}")

        # For now, return empty list - will be populated when data is organized
        return []

    def run_single_query(
        self,
        pair_id: str,
        image1_path: Path,
        image2_path: Path,
        prompt_type: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Run a single query on one image pair.

        Args:
            pair_id: Unique identifier for this pair
            image1_path: Path to first image
            image2_path: Path to second image
            prompt_type: "naive" or "expert"
            metadata: Metadata for expert prompt (location, dates, orientation)

        Returns:
            Result dictionary with response and metadata
        """
        # Build prompt
        if prompt_type == "naive":
            prompt = self.prompt_builder.build_naive_prompt()
        elif prompt_type == "expert":
            if metadata is None:
                raise ValueError("Metadata required for expert prompt")
            prompt = self.prompt_builder.build_expert_prompt(metadata)
        else:
            raise ValueError(f"Invalid prompt_type: {prompt_type}")

        # Query LLM
        print(f"Querying {pair_id} with {prompt_type} prompt...")
        response = self.llm_client.query_with_images(
            prompt=prompt,
            image_paths=[image1_path, image2_path]
        )

        # Package result
        result = {
            "pair_id": pair_id,
            "image1": str(image1_path),
            "image2": str(image2_path),
            "prompt_type": prompt_type,
            "prompt_metadata": metadata,
            "llm_response": response["response"],
            "model": response["model"],
            "timestamp": response["timestamp"],
            "token_usage": response["metadata"]
        }

        return result

    def run_experiment(
        self,
        pairs_to_run: List[Dict[str, Any]],
        prompt_types: List[str] = ["naive", "expert"],
        save_interval: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Run experiment on multiple pairs.

        Args:
            pairs_to_run: List of dicts with:
                - pair_id: str
                - image1_path: Path or str
                - image2_path: Path or str
                - metadata: Dict (for expert prompt)
            prompt_types: List of prompt types to run
            save_interval: Save results every N queries

        Returns:
            List of all results
        """
        all_results = []
        results_file = self.results_dir / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        total_queries = len(pairs_to_run) * len(prompt_types)
        current_query = 0

        for pair_info in pairs_to_run:
            pair_id = pair_info["pair_id"]
            image1 = Path(pair_info["image1_path"])
            image2 = Path(pair_info["image2_path"])
            metadata = pair_info.get("metadata", {})

            for prompt_type in prompt_types:
                current_query += 1
                print(f"\n[{current_query}/{total_queries}] Processing {pair_id} - {prompt_type}")

                try:
                    result = self.run_single_query(
                        pair_id=pair_id,
                        image1_path=image1,
                        image2_path=image2,
                        prompt_type=prompt_type,
                        metadata=metadata if prompt_type == "expert" else None
                    )
                    all_results.append(result)

                    # Save periodically
                    if len(all_results) % save_interval == 0:
                        self._save_results(all_results, results_file)
                        print(f"  → Saved {len(all_results)} results to {results_file.name}")

                except Exception as e:
                    print(f"  ✗ Error: {e}")
                    all_results.append({
                        "pair_id": pair_id,
                        "prompt_type": prompt_type,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })

                # Small delay to avoid rate limits
                time.sleep(0.5)

        # Final save
        self._save_results(all_results, results_file)
        print(f"\n✓ Experiment complete! Results saved to {results_file}")

        return all_results

    def _save_results(self, results: List[Dict[str, Any]], output_path: Path):
        """Save results to JSON file."""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
