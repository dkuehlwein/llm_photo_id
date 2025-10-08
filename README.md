# Sea Turtle Re-Identification with Multi-Modal LLMs

A comparative study evaluating state-of-the-art multi-modal Large Language Models (Claude, Gemini, GPT) against MegaDescriptor for sea turtle photo identification tasks.

## 🎯 Objective

Assess the capabilities of leading multi-modal LLMs in both standard and challenging re-identification scenarios, comparing their performance against specialized computer vision models (MegaDescriptor). We evaluate the impact of expert-guided prompting on accuracy and reasoning quality.

## 📊 Dataset

**Source:** SeaTurtleID2022 dataset - ZakynthosTurtles subset
- **Species:** Loggerhead sea turtles (*Caretta caretta*)
- **Location:** Zakynthos, Greece
- **Images:** 160 total (40 individuals × 4 photos each)
- **Profiles:** Left and right profiles across two years
- **Image type:** Full body with head bounding box annotations

### Experimental Pairs (40 total, 5 per category)

| Category | MegaDescriptor Performance | Ground Truth | Orientation |
|----------|---------------------------|--------------|-------------|
| High similarity, correct match | High similarity (>0.9) | Same individual | Same / Opposite |
| High similarity, wrong match | High similarity (>0.9) | Different individuals | Same / Opposite |
| Low similarity, correct match | Low similarity (<0.1) | Different individuals | Same / Opposite |
| Low similarity, wrong match | Low similarity (<0.1) | Same individual | Same / Opposite |

**Note:** Opposite-orientation pairs (left vs. right profile) test whether LLMs can recognize the same individual from different viewing angles.

## 🧪 Methodology

### Models Under Test
1. **OpenAI GPT-4o / o3** (via OpenAI API)
2. **Google Gemini 2.5 Pro** (via Google AI API)
3. **Anthropic Claude 4 Opus** (via Anthropic API)

All models configured with `temperature=0` for deterministic, reproducible outputs.

### Prompting Strategies

**Naive Prompt:** Direct question without domain guidance
```
"Do these images show the same sea turtle? Answer 'Yes' or 'No' and explain your reasoning."
```

**Expert Prompt:** Structured prompt incorporating:
- Contextual metadata (capture dates, locations, individual IDs if applicable)
- Biometric feature guidance (facial scute patterns, flipper notches, head shape)
- Transient feature exclusion (algae, barnacles, lighting variations)
- Step-by-step reasoning requirement

### Experimental Design

**Total evaluations:** 40 pairs × 3 LLMs × 2 prompts = **240 data points**

Each LLM processes:
- Both same-orientation and opposite-orientation pairs
- Cases where MegaDescriptor succeeds and fails
- Full-body images (potentially head-cropped variants as well)

## 📈 Analysis Plan

### Quantitative Analysis
- **Primary metric:** Accuracy (% correct match/no-match decisions)
- **Breakdown by:**
  - LLM provider
  - Prompt type (naive vs. expert)
  - MegaDescriptor performance category
  - Orientation (same vs. opposite profile)
- **Statistical tests:** McNemar's test for paired comparisons
- **Visualizations:** Confusion matrices, accuracy heatmaps

### Qualitative Analysis
- Extract and categorize reasoning chains from expert prompt responses
- Assess scientific validity of biometric feature identification
- Identify common failure modes and hallucinations
- Compare reasoning quality across models

## 🔬 Research Hypotheses

1. **H1:** Expert prompts significantly outperform naive prompts, demonstrating value of domain knowledge integration
2. **H2:** LLMs show comparable overall accuracy but differ in reasoning quality and failure modes
3. **H3:** LLMs may outperform MegaDescriptor in "hard" cases with visual ambiguity where contextual reasoning aids decisions
4. **H4:** Opposite-orientation pairs pose greater challenge than same-orientation pairs for all models

## 🛠️ Setup & Usage

### Prerequisites
```bash
# Python 3.13+ with uv
uv venv
source .venv/bin/activate
uv pip install python-dotenv google-generativeai pillow
```

### Configuration
1. `.env` file with API keys (already configured for testing):
   ```
   GOOGLE_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here  # Optional
   OPENAI_API_KEY=your_key_here     # Optional
   ```

### Setup Data
```bash
# 1. Extract data (already done)
# DATA_FOR_DANIEL.zip -> data/raw/

# 2. Create pairs metadata
python scripts/create_pairs_metadata.py
# Creates data/pairs_metadata.json with all 40 pairs

# 3. Test with a single pair
python scripts/test_single_pair.py pair_001
```

### Run Experiment
```bash
# Test single pair (quick validation)
python scripts/test_single_pair.py pair_001

# Run full experiment (coming soon)
python scripts/run_experiment.py

# Run specific pairs
python scripts/run_experiment.py --pairs pair_001,pair_002,pair_003
```

### Analyze Results
```bash
# Generate summary report (coming soon)
python scripts/generate_report.py

# Or use Jupyter notebooks for interactive analysis
jupyter notebook notebooks/02_results_analysis.ipynb
```

## 📁 Project Structure

```
├── data/
│   ├── raw/                           # Extracted dataset
│   │   ├── ZakynthosTurtles/         # 160 images, 40 individuals
│   │   └── [8 category folders]/     # MegaDescriptor performance categories
│   └── pairs_metadata.json           # ✅ Unified metadata for 40 pairs
├── prompts/
│   ├── naive_prompt.txt              # ✅ Simple direct question
│   └── expert_prompt.txt             # ✅ Structured domain-expert prompt
├── src/
│   ├── llm_clients/
│   │   ├── base.py                   # ✅ Abstract base class
│   │   └── gemini.py                 # ✅ Gemini API client (tested)
│   └── experiment/
│       ├── prompt_builder.py         # ✅ Template management
│       └── runner.py                 # ✅ Experiment orchestration
├── scripts/
│   ├── test_gemini_api.py            # ✅ API connectivity test
│   ├── create_pairs_metadata.py      # ✅ Generate metadata from CSVs
│   └── test_single_pair.py           # ✅ End-to-end single pair test
├── results/                           # Results will be saved here
└── docs/
    └── data_structure.md              # ✅ Dataset documentation
```

See [docs/data_structure.md](docs/data_structure.md) for detailed data documentation.

## 📝 Publication Goals

This research aims to produce a conference paper demonstrating:
- **Capabilities** of foundation models on specialized scientific tasks
- **Current limitations** requiring domain-specific training
- **Practical value** of prompt engineering for scientific applications
- **Comparative insights** between general-purpose and specialized models

Target venues: CVPR, ICCV, NeurIPS (Vision & Applications track), or domain-specific conferences in conservation technology.

## 👥 Team

- **Daniel Kühlwein** - Experiment implementation, quantitative analysis
- **Kostas Papafitsoros** (QMUL) - Dataset curation, qualitative analysis, domain expertise

## 📄 License

[MIT License](LICENSE)

## 🙏 Acknowledgments

- **Dataset:** SeaTurtleID2022 (ZakynthosTurtles subset)
- **Baseline Model:** MegaDescriptor
- **Data Provider:** Kostas Papafitsoros, Queen Mary University of London

---

## 🚀 Current Status

**Phase:** Testing & Validation ✅

**Completed:**
- ✅ Project structure and environment setup
- ✅ Gemini API client with retry logic and error handling
- ✅ Naive and expert prompt templates
- ✅ Experiment orchestration framework
- ✅ Data extraction and metadata generation (40 pairs)
- ✅ End-to-end testing with single image pair
- ✅ Documentation (data structure, setup guide)

**Next Steps:**
1. Run full experiment (40 pairs × 2 prompts = 80 queries)
2. Build analysis tools (accuracy calculation, response parsing)
3. Add Claude and GPT-4 clients
4. Create visualization notebooks
5. Generate results report

**Test Results (pair_001):**
- Naive prompt: ✅ Correct ("Yes", same turtle)
- Expert prompt: ✅ Correct ("Yes", high confidence)
- Ground truth: SAME (tsb056 vs tsb056)
- MegaDescriptor: 0.7423 similarity

**Last Updated:** October 8, 2025
