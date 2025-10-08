"""Base class for LLM API clients."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pathlib import Path


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    def __init__(self, model_name: str, temperature: float = 0.0):
        """
        Initialize the LLM client.

        Args:
            model_name: The model identifier
            temperature: Sampling temperature (0 for deterministic)
        """
        self.model_name = model_name
        self.temperature = temperature

    @abstractmethod
    def query_with_images(
        self,
        prompt: str,
        image_paths: List[Path]
    ) -> Dict[str, Any]:
        """
        Send a prompt with images to the LLM.

        Args:
            prompt: The text prompt
            image_paths: List of paths to image files

        Returns:
            Dict with keys:
                - 'response': The model's text response
                - 'model': Model name used
                - 'timestamp': ISO timestamp
                - 'metadata': Additional metadata (tokens, etc)
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test if the API connection works.

        Returns:
            True if connection successful, False otherwise
        """
        pass
