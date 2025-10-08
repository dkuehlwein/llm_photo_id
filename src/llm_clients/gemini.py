"""Gemini API client for multi-modal queries."""
import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import time

import google.generativeai as genai
from PIL import Image

from .base import BaseLLMClient


class GeminiClient(BaseLLMClient):
    """Client for Google Gemini API."""

    def __init__(self, api_key: str = None, model_name: str = "models/gemini-2.0-flash-exp", temperature: float = 0.0):
        """
        Initialize Gemini client.

        Args:
            api_key: Google API key (if None, reads from GOOGLE_API_KEY env var)
            model_name: Gemini model identifier
            temperature: Sampling temperature
        """
        super().__init__(model_name, temperature)

        # Configure API
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment or parameters")

        genai.configure(api_key=api_key)

        # Initialize model
        generation_config = {
            "temperature": self.temperature,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }

        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=generation_config
        )

    def query_with_images(
        self,
        prompt: str,
        image_paths: List[Path],
        retry_attempts: int = 3,
        retry_delay: float = 1.0
    ) -> Dict[str, Any]:
        """
        Send a prompt with images to Gemini.

        Args:
            prompt: The text prompt
            image_paths: List of paths to image files
            retry_attempts: Number of retry attempts on failure
            retry_delay: Delay between retries in seconds

        Returns:
            Dict with response data and metadata
        """
        # Load images
        images = []
        for img_path in image_paths:
            if not img_path.exists():
                raise FileNotFoundError(f"Image not found: {img_path}")
            images.append(Image.open(img_path))

        # Prepare content: [image1, image2, ..., prompt]
        content = images + [prompt]

        # Try with retries
        last_error = None
        for attempt in range(retry_attempts):
            try:
                timestamp = datetime.now().isoformat()
                response = self.model.generate_content(content)

                return {
                    "response": response.text,
                    "model": self.model_name,
                    "timestamp": timestamp,
                    "metadata": {
                        "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else None,
                        "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else None,
                        "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else None,
                    }
                }

            except Exception as e:
                last_error = e
                if attempt < retry_attempts - 1:
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    raise Exception(f"Failed after {retry_attempts} attempts: {str(last_error)}")

    def test_connection(self) -> bool:
        """
        Test Gemini API connection with a simple query.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Simple text-only test
            response = self.model.generate_content("Say 'OK' if you can read this.")
            return "OK" in response.text or "ok" in response.text.lower()
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
