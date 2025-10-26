# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Research project comparing multi-modal LLMs (Claude, Gemini, GPT) against MegaDescriptor for sea turtle photo re-identification. The experiment evaluates 40 image pairs across 8 categories testing both same/different individuals and same/opposite orientations.

**Key Dataset Details:**
- 40 pairs from SeaTurtleID2022 (ZakynthosTurtles subset)
- 8 experimental categories: High/Low MegaDescriptor similarity × Correct/Wrong match × Same/Opposite orientation
- Ground truth in `data/pairs_metadata.json` with fields: pair_id, category, ground_truth (same/different), identity1/2, image paths, dates, orientations, md_similarity

## Development Commands

### Environment Setup
```bash
# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Running Experiments
```bash
# Test single pair (quick validation)
python scripts/test_single_pair.py pair_001

# Run experiment on specific pairs
python scripts/run_experiment.py --pairs 1-10           # Range of pairs
python scripts/run_experiment.py --pairs pair_001,pair_002  # Specific pairs

# Run with specific prompts (default: naive,expert)
python scripts/run_experiment.py --pairs 1-10 --prompts expert

# Specify model (currently only gemini implemented)
python scripts/run_experiment.py --model gemini
```

### Analyzing Results
```bash
# Analyze most recent results
python scripts/analyze_results.py

# Analyze specific results file
python scripts/analyze_results.py results/processed/experiment_20251008_162645.json

# Show detailed errors (incorrect predictions)
python scripts/show_errors.py

# Combine multiple result files
python scripts/combine_results.py
```

### Configuration
Environment variables in `.env`:
- `GOOGLE_API_KEY` - Required for Gemini
- `GEMINI_MODEL` - Model name (defaults to "models/gemini-2.0-flash-exp")
- `ANTHROPIC_API_KEY` - For Claude (not yet implemented)
- `OPENAI_API_KEY` - For GPT (not yet implemented)

## Code Architecture

### Core Components

**LLM Client System** (`src/llm_clients/`)
- `base.py`: Abstract `BaseLLMClient` class defining interface for all LLM clients
  - `query_with_images(prompt, image_paths)`: Core method returning dict with response, model, timestamp, metadata
  - `test_connection()`: API connectivity check
- `gemini.py`: `GeminiClient` implementation with retry logic and exponential backoff
  - Model name from `GEMINI_MODEL` env var or constructor parameter
  - Automatic retry on failures (default 3 attempts)
  - Returns token usage metadata (prompt_tokens, completion_tokens, total_tokens)

**Experiment Framework** (`src/experiment/`)
- `prompt_builder.py`: `PromptBuilder` class loads templates from `prompts/` directory
  - `build_naive_prompt()`: Static simple prompt
  - `build_expert_prompt(metadata)`: Injects location, date1, date2, orientation into template
  - Metadata keys required: location, date1, date2, orientation
- `runner.py`: `ExperimentRunner` orchestrates execution
  - `run_single_query()`: Execute one pair with specified prompt_type
  - `run_experiment()`: Batch process multiple pairs with periodic saves (default every 5 queries)
  - Results saved to `results/raw_responses/{model}/results_{timestamp}.json`
  - Errors captured as entries with "error" field instead of raising exceptions

**Analysis Scripts** (`scripts/`)
- `run_experiment.py`: Main experiment runner with command-line interface
  - Reads pairs from `data/pairs_metadata.json`
  - Saves raw responses to `results/raw_responses/{model}/`
  - Saves processed results with ground truth to `results/processed/`
- `analyze_results.py`: Computes accuracy metrics by prompt type, category, orientation
  - Decision extraction via regex patterns (naive: "Answer: Yes/No", expert: "ANSWER: YES/NO")
  - Breaks down by ground_truth (same/different), orientation (same/opposite), certainty level
  - Automatically finds most recent results if no file specified
- `show_errors.py`: Displays detailed incorrect predictions with metadata
- `combine_results.py`: Merges multiple experiment runs

### Prompt System

**Naive Prompt** (`prompts/naive_prompt.txt`):
Simple direct question with no domain guidance.

**Expert Prompt** (`prompts/expert_prompt.txt`):
Comprehensive 305-line structured prompt with:
- Metadata context injection (location, dates, orientation)
- **Critical instruction**: Base decision ONLY on visual features, NOT metadata
- Step-by-step analysis protocol (image quality → facial scales → secondary features → metadata sanity check → decision)
- Facial scale pattern analysis as PRIMARY identifier (post-ocular, tympanic, prefrontal scales)
- Orientation-specific guidance (same orientation: geometric patterns; opposite: pigmentation/coloration)
- Output format with species ID, quality assessment, pattern analysis, certainty level
- De-biasing self-check questions to prevent metadata anchoring
- Example scenarios demonstrating correct reasoning

**Important**: The expert prompt is designed to AVOID metadata bias while still providing context. It explicitly instructs the LLM to ignore dates/locations as evidence and base decisions purely on visual morphological features.

### Data Flow

1. **Input**: Pair metadata loaded from `data/pairs_metadata.json`
2. **Prompt Building**: PromptBuilder generates prompt with optional metadata injection
3. **LLM Query**: Client sends images + prompt, returns response with metadata
4. **Raw Storage**: Results saved to `results/raw_responses/{model}/results_{timestamp}.json`
5. **Processing**: Ground truth and category added, saved to `results/processed/experiment_{timestamp}.json`
6. **Analysis**: Scripts extract decisions, compute accuracy, identify errors

### Results Structure

**Raw response format**:
```json
{
  "pair_id": "pair_001",
  "image1": "/path/to/image1.JPG",
  "image2": "/path/to/image2.JPG",
  "prompt_type": "expert",
  "prompt_metadata": {"location": "...", "date1": "...", "date2": "...", "orientation": "..."},
  "llm_response": "...",
  "model": "models/gemini-2.0-flash-exp",
  "timestamp": "2025-10-08T16:26:45.123456",
  "token_usage": {"prompt_tokens": 1234, "completion_tokens": 567, "total_tokens": 1801}
}
```

**Processed format** (adds ground_truth, category, md_similarity from pairs_metadata)

### Key Design Decisions

1. **Separation of concerns**: LLM clients, experiment orchestration, and analysis are independent modules
2. **Retry resilience**: Gemini client implements exponential backoff for API failures
3. **Progressive saves**: Experiment runner saves every N queries to prevent data loss
4. **Metadata-aware prompting**: Expert prompt receives context but instructs LLM to ignore it for matching
5. **Dual storage**: Raw responses separate from processed results with ground truth
6. **Decision extraction**: Regex patterns adapted per prompt type (naive vs expert formatting differs)

## Adding New LLM Clients

To add Claude or OpenAI support:

1. Create `src/llm_clients/claude.py` or `openai.py` inheriting from `BaseLLMClient`
2. Implement `query_with_images()` and `test_connection()` methods
3. Return same dict format: `{"response": str, "model": str, "timestamp": str, "metadata": dict}`
4. Add client initialization in `scripts/run_experiment.py` (around line 74)
5. Update `src/llm_clients/__init__.py` to export new client

## Important Conventions

- **Pair IDs**: Format `pair_001` to `pair_040` (zero-padded)
- **Ground truth values**: "same" or "different" (lowercase)
- **Prompt types**: "naive" or "expert" (lowercase)
- **Temperature**: Always 0.0 for deterministic outputs
- **Orientation terminology**: Note dataset uses "orientiation" (typo in original CSV) but code handles this
- **Decision extraction**: Naive prompt expects "Answer: Yes/No", expert expects "ANSWER: YES/NO"
- **Certainty levels**: "high", "medium", "low" (lowercase in regex matching)

## Common Issues

- **Missing pairs_metadata.json**: Run `python scripts/create_pairs_metadata.py` to generate from CSV files
- **API key errors**: Ensure `.env` file exists with appropriate `*_API_KEY` variables
- **Image path issues**: Paths in pairs_metadata.json must be absolute or relative to project root
- **Decision extraction failures**: Returns "unclear" if response doesn't match expected format patterns
- **Model name format**: Gemini requires "models/" prefix (e.g., "models/gemini-2.0-flash-exp")
