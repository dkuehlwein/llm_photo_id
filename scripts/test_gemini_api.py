#!/usr/bin/env python3
"""Test script to verify Gemini API connectivity."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.llm_clients import GeminiClient


def main():
    """Test Gemini API connection."""
    # Load environment variables
    load_dotenv()

    print("Testing Gemini API connection...")
    print("-" * 50)

    try:
        # Initialize client
        client = GeminiClient()
        print(f"✓ Client initialized")
        print(f"  Model: {client.model_name}")
        print(f"  Temperature: {client.temperature}")

        # Test connection
        print("\nTesting API connection...")
        if client.test_connection():
            print("✓ API connection successful!")
            print("\nGemini API is ready to use.")
            return 0
        else:
            print("✗ API connection failed")
            return 1

    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
