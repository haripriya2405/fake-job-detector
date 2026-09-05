"""Prepare Validation Dataset Script (Phase 20).
Ingests, normalizes, deduplicates, and splits the real-world dataset into leakage-free
TRAIN, VALIDATION, and UNTOUCHED HOLDOUT partitions, generating machine and human reports.
"""

import json
import os
import sys

# Ensure backend directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.logging import logger
from app.ml.real_world_validation import RealWorldValidationPipeline


def main():
    print("=" * 80)
    print("SentinelJob AI — Phase 20: Real-World Dataset Preparation Pipeline")
    print("=" * 80)

    pipeline = RealWorldValidationPipeline()
    records, stats = pipeline.validate_and_ingest()

    print(f"\n[1] Ingestion & Provenance Summary:")
    print(f"    Total Input Records:     {stats['total_input_records']}")
    print(f"    Accepted Valid Records:  {stats['accepted_records']}")
    print(f"    Rejected Records:        {stats['rejected_records_count']}")
    print(f"    Legitimate Class (0):    {stats['legitimate_count']}")
    print(f"    Fraudulent Class (1):    {stats['fraud_count']}")
    print(f"    Provenance Sources ({len(stats['provenance_sources'])}): {', '.join(stats['provenance_sources'][:5])}...")

    # Partition into isolated subsets
    partitions = pipeline.create_leakage_free_partitions(records, val_ratio=0.20, holdout_ratio=0.20, random_state=42)
    train_df = partitions["train"]
    val_df = partitions["validation"]
    holdout_df = partitions["holdout"]

    print(f"\n[2] Leakage-Free Partitions Created:")
    print(f"    TRAIN Partition:         {len(train_df)} samples")
    print(f"    VALIDATION Partition:    {len(val_df)} samples")
    print(f"    UNTOUCHED HOLDOUT:       {len(holdout_df)} samples")

    # Sample Power Adequacy Assessment
    power = pipeline.assess_sample_power(len(holdout_df))
    print(f"\n[3] Statistical Power Adequacy on Holdout (N={len(holdout_df)}):")
    print(f"    Target N:                {power['min_required_sample_size']}")
    print(f"    Adequately Powered:      {power['is_adequately_powered']}")
    print(f"    Margin of Error (95%):   ±{power['estimated_margin_of_error']:.2%}")
    print(f"    Status:                  {power['status']}")

    # Export Manifest
    output_dir = "artifacts/datasets"
    os.makedirs(output_dir, exist_ok=True)
    manifest_path = os.path.join(output_dir, "validation_dataset_manifest.json")

    manifest = {
        "dataset_version": "real-world-v20.0",
        "ingestion_stats": stats,
        "partitions": {
            "train_count": len(train_df),
            "validation_count": len(val_df),
            "holdout_count": len(holdout_df),
        },
        "power_assessment": power,
        "holdout_records": holdout_df.to_dict(orient="records"),
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n[4] Dataset Manifest Written -> {manifest_path}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
