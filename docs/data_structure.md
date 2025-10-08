# Data Structure Documentation

## Overview

The dataset consists of 40 image pairs from the SeaTurtleID2022 ZakynthosTurtles subset, organized into 8 categories based on MegaDescriptor performance.

## Directory Structure

```
data/
├── raw/
│   ├── ZakynthosTurtles/
│   │   ├── images/              # 160 full-body turtle images
│   │   ├── annotations.csv      # Individual identities and capture metadata
│   │   └── bbox.csv             # Head bounding boxes
│   ├── High_similarity_correct_match_same_orientiation/
│   │   └── *.csv
│   ├── High_similarity_correct_match_opposite_orientiation/
│   │   └── *.csv
│   ├── High_similarity_wrong_match_same_orientiation/
│   │   └── *.csv
│   ├── High_similarity_wrong_match_opposite_orientiation/
│   │   └── *.csv
│   ├── Low_similarity_correct_match_same_orientiation/
│   │   └── *.csv
│   ├── Low_similarity_correct_match_opposite_orientiation/
│   │   └── *.csv
│   ├── Low_similarity_wrong_match_same_orientiation/
│   │   └── *.csv
│   └── Low_similarity_wrong_match_opposite_orientiation/
│       └── *.csv
└── pairs_metadata.json          # Unified metadata for all 40 pairs
```

## Dataset Details

### Full Dataset (ZakynthosTurtles)
- **Total images:** 160
- **Individuals:** 40
- **Images per individual:** 4 (2 years × 2 orientations)
- **Orientations:** Left and right profiles
- **Years:** Multiple years (2018-2024)
- **Location:** Zakynthos, Greece

### Experimental Pairs

**40 pairs total, organized into 8 categories (5 pairs each):**

| Category | MegaDescriptor | Ground Truth | Same/Opposite | Count |
|----------|----------------|--------------|---------------|-------|
| High_similarity_correct_match_same_orientiation | High (>0.6) | Same turtle | Same profile | 5 |
| High_similarity_correct_match_opposite_orientiation | High (>0.6) | Same turtle | Opposite profiles | 5 |
| High_similarity_wrong_match_same_orientiation | High (>0.6) | Different turtles | Same profile | 5 |
| High_similarity_wrong_match_opposite_orientiation | High (>0.6) | Different turtles | Opposite profiles | 5 |
| Low_similarity_correct_match_same_orientiation | Low (<0.3) | Different turtles | Same profile | 5 |
| Low_similarity_correct_match_opposite_orientiation | Low (<0.3) | Different turtles | Opposite profiles | 5 |
| Low_similarity_wrong_match_same_orientiation | Low (<0.3) | Same turtle | Same profile | 5 |
| Low_similarity_wrong_match_opposite_orientiation | Low (<0.3) | Same turtle | Opposite profiles | 5 |

### Category Interpretation

**High similarity, correct match:** MD correctly assigns high similarity to same individual
**High similarity, wrong match:** MD incorrectly assigns high similarity to different individuals
**Low similarity, correct match:** MD correctly assigns low similarity to different individuals
**Low similarity, wrong match:** MD incorrectly assigns low similarity to same individual

## Metadata Format

### pairs_metadata.json

Each pair entry contains:

```json
{
  "pair_id": "pair_001",
  "category": "High_similarity_correct_match_same_orientiation",
  "ground_truth": "same",
  "identity1": "tsb022",
  "identity2": "tsb022",
  "image1_path": "/path/to/rightIMG_1030.JPG",
  "image2_path": "/path/to/rightIMG_7689.JPG",
  "date1": "2020-07-07",
  "date2": "2022-06-21",
  "orientation1": "right",
  "orientation2": "right",
  "orientation_desc": "both right profile",
  "md_similarity": 0.7859602,
  "location": "Zakynthos, Greece"
}
```

### Field Descriptions

- **pair_id:** Unique identifier (pair_001 to pair_040)
- **category:** One of 8 experimental categories
- **ground_truth:** "same" or "different" (whether images show same individual)
- **identity1/2:** Individual turtle IDs from dataset
- **image1/2_path:** Full paths to image files
- **date1/2:** Capture dates (YYYY-MM-DD format)
- **orientation1/2:** "left" or "right" profile
- **orientation_desc:** Human-readable orientation description for prompts
- **md_similarity:** MegaDescriptor similarity score (0-1)
- **location:** Capture location

## Image Files

- **Format:** JPG/JPEG
- **Content:** Full-body sea turtle images
- **Quality:** High-resolution field photographs
- **Head bounding boxes:** Available in `bbox.csv` (not used in current experiment)

## Usage

Load metadata in Python:

```python
import json
from pathlib import Path

with open("data/pairs_metadata.json") as f:
    pairs = json.load(f)

# Get first pair
pair = pairs[0]
print(f"Pair {pair['pair_id']}: {pair['ground_truth']}")
print(f"  Images: {pair['image1_path']}, {pair['image2_path']}")
print(f"  MD similarity: {pair['md_similarity']:.3f}")
```
