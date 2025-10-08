"""Prompt template builder with metadata injection."""
from pathlib import Path
from typing import Dict, Any


class PromptBuilder:
    """Build prompts from templates with metadata."""

    def __init__(self, prompts_dir: Path = None):
        """
        Initialize prompt builder.

        Args:
            prompts_dir: Directory containing prompt templates (default: project_root/prompts)
        """
        if prompts_dir is None:
            prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        self.prompts_dir = Path(prompts_dir)

        # Load templates
        self.naive_template = self._load_template("naive_prompt.txt")
        self.expert_template = self._load_template("expert_prompt.txt")

    def _load_template(self, filename: str) -> str:
        """Load a prompt template from file."""
        path = self.prompts_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Prompt template not found: {path}")
        return path.read_text()

    def build_naive_prompt(self) -> str:
        """
        Build the naive prompt (no customization needed).

        Returns:
            The naive prompt text
        """
        return self.naive_template

    def build_expert_prompt(self, metadata: Dict[str, Any]) -> str:
        """
        Build the expert prompt with metadata injection.

        Args:
            metadata: Dictionary with keys:
                - location: str (e.g., "Zakynthos, Greece")
                - date1: str (e.g., "2019-06-15")
                - date2: str (e.g., "2020-07-20")
                - orientation: str (e.g., "both left profile" or "left and right profile")

        Returns:
            The customized expert prompt
        """
        required_keys = ["location", "date1", "date2", "orientation"]
        missing = [k for k in required_keys if k not in metadata]
        if missing:
            raise ValueError(f"Missing required metadata keys: {missing}")

        return self.expert_template.format(**metadata)
