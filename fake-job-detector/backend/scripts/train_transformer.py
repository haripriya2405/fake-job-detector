"""SentinelJob AI — Transformer Training & Export CLI Script (Phase 19).
Usage:
  python scripts/train_transformer.py [--base-model microsoft/deberta-v3-small] [--epochs 3] [--output-dir artifacts/models]
"""

import argparse
import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.logging import logger
from app.ml.production_dataset import ProductionDatasetIngestion
from app.ml.transformer_trainer import TransformerModelTrainer


def main():
    parser = argparse.ArgumentParser(description="Fine-tune Hugging Face Transformer and export to ONNX INT8.")
    parser.add_argument("--base-model", type=str, default="microsoft/deberta-v3-small", help="Hugging Face base model identifier")
    parser.add_argument("--epochs", type=int, default=3, help="Training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    parser.add_argument("--learning-rate", type=float, default=2e-5, help="Learning rate")
    parser.add_argument("--output-dir", type=str, default="artifacts/models", help="Output directory for model artifacts")
    parser.add_argument("--no-quantize", action="store_true", help="Disable dynamic INT8 quantization")
    args = parser.parse_args()

    print("=" * 80)
    print(f"SentinelJob AI — Transformer Fine-Tuning Pipeline: {args.base_model}")
    print("=" * 80)

    # 1. Ingest production training dataset
    ingestion = ProductionDatasetIngestion()
    df, stats = ingestion.ingest_and_clean()
    logger.info(f"Ingested {len(df)} verified samples across {stats['sources_count']} sources.")

    # 2. Partition into leakage-free train, val, holdout sets
    train_df, val_df, holdout_df = ingestion.create_leakage_free_splits(df, random_state=42)
    logger.info(f"Splits Created: {len(train_df)} Train | {len(val_df)} Val | {len(holdout_df)} Holdout")

    # 3. Fine-tune and export ONNX
    trainer = TransformerModelTrainer(
        base_model_name=args.base_model,
        max_length=512,
        random_state=42,
    )
    meta = trainer.train_and_export(
        train_df=train_df,
        val_df=val_df,
        holdout_df=holdout_df,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        output_dir=args.output_dir,
        quantize_onnx=not args.no_quantize,
    )

    print("\n" + "=" * 80)
    print("Transformer Candidate Model Training Complete!")
    print(f"Model Version: {meta['model_version']}")
    print(f"Algorithm:     {meta['algorithm']}")
    print(f"SHA-256 Hash:  {meta['sha256_checksum']}")
    print(f"PR-AUC:        {meta['metrics']['val_pr_auc']:.4f}")
    print(f"Recall:        {meta['metrics']['val_recall']:.4f}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
