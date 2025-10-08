#!/usr/bin/env python3
"""Create unified metadata file for all image pairs."""
import sys
import json
import csv
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def parse_date(date_str):
    """Parse date from DD_MM_YYYY format."""
    try:
        day, month, year = date_str.split('_')
        return f"{year}-{month}-{day}"
    except:
        return date_str


def create_pairs_metadata():
    """Read all category CSVs and create unified metadata."""
    data_dir = Path(__file__).parent.parent / "data" / "raw"
    images_dir = data_dir / "ZakynthosTurtles" / "images"

    categories = [
        "High_similarity_correct_match_opposite_orientiation",
        "High_similarity_correct_match_same_orientiation",
        "High_similarity_wrong_match_opposite_orientiation",
        "High_similarity_wrong_match_same_orientiation",
        "Low_similarity_correct_match_opposite_orientiation",
        "Low_similarity_correct_match_same_orientiation",
        "Low_similarity_wrong_match_opposite_orientiation",
        "Low_similarity_wrong_match_same_orientiation"
    ]

    all_pairs = []
    pair_counter = 1

    for category in categories:
        csv_path = data_dir / category / f"{category}.csv"

        if not csv_path.exists():
            print(f"Warning: {csv_path} not found, skipping...")
            continue

        print(f"Processing {category}...")

        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Pairs are consecutive rows (row 0-1, 2-3, 4-5, etc.)
        for i in range(0, len(rows), 2):
            if i + 1 >= len(rows):
                break

            row1 = rows[i]
            row2 = rows[i + 1]

            # Verify it's a pair (same identity for correct matches, different for wrong matches)
            identity1 = row1['identity']
            identity2 = row2['identity']

            # Parse data
            image1_path = images_dir / Path(row1['path']).name
            image2_path = images_dir / Path(row2['path']).name

            date1 = parse_date(row1['date'])
            date2 = parse_date(row2['date'])

            orientation1 = row1['orientation']
            orientation2 = row2['orientation']

            # Determine ground truth
            is_correct = "correct" in category
            is_high_sim = "High_similarity" in category
            is_same_orientation = "same_orientiation" in category

            # Ground truth: same individual or not?
            if is_correct and is_high_sim:
                ground_truth = "same"  # High sim, correct = same individual
            elif is_correct and not is_high_sim:
                ground_truth = "different"  # Low sim, correct = different individuals
            elif not is_correct and is_high_sim:
                ground_truth = "different"  # High sim, wrong = different individuals
            else:  # not is_correct and not is_high_sim
                ground_truth = "same"  # Low sim, wrong = same individual

            # Orientation description
            if is_same_orientation:
                if orientation1 == "left":
                    orientation_desc = "both left profile"
                else:
                    orientation_desc = "both right profile"
            else:
                orientation_desc = "left and right profile (opposite orientations)"

            pair_id = f"pair_{pair_counter:03d}"

            pair_data = {
                "pair_id": pair_id,
                "category": category,
                "ground_truth": ground_truth,
                "identity1": identity1,
                "identity2": identity2,
                "image1_path": str(image1_path),
                "image2_path": str(image2_path),
                "date1": date1,
                "date2": date2,
                "orientation1": orientation1,
                "orientation2": orientation2,
                "orientation_desc": orientation_desc,
                "md_similarity": float(row1['Similarity']),
                "location": "Zakynthos, Greece"
            }

            all_pairs.append(pair_data)
            pair_counter += 1

    # Save to JSON
    output_path = Path(__file__).parent.parent / "data" / "pairs_metadata.json"
    with open(output_path, 'w') as f:
        json.dump(all_pairs, f, indent=2)

    print(f"\n✓ Created metadata for {len(all_pairs)} pairs")
    print(f"  Saved to: {output_path}")

    # Print summary
    print("\nSummary by category:")
    category_counts = {}
    for pair in all_pairs:
        cat = pair['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1

    for cat, count in sorted(category_counts.items()):
        print(f"  {cat}: {count} pairs")

    return all_pairs


if __name__ == "__main__":
    create_pairs_metadata()
