import json
import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.logging import setup_logging
from app.ml.dataset import DevelopmentSmokeTestDataset, ContemporaryHoldoutDataset, AdversarialTestDataset
from app.ml.train import ModelTrainer


def main():
    setup_logging()
    print("=" * 75)
    print("SentinelJob AI — ML Pipeline (Development Smoke-Test Benchmark Evaluation)")
    print("=" * 75)

    dataset = DevelopmentSmokeTestDataset()
    df = dataset.load()
    print(f"\n1. Dataset Provenance & Limitations:")
    print(f"   - Name: {dataset.metadata['name']}")
    print(f"   - Type: {dataset.metadata['type']}")
    print(f"   - Limitation Notice: {dataset.metadata['limitation']}")
    print(f"   - Sample Count: {len(df)} records (Fraud: {sum(df['label'] == 1)}, Legitimate: {sum(df['label'] == 0)})")

    train_df, val_df, test_df = dataset.get_splits(test_size=0.15, val_size=0.15, random_state=42)
    print(f"\n2. Stratified Data Split (Reproducible, Anti-Leakage):")
    print(f"   - Train (70%): {len(train_df)} samples")
    print(f"   - Val (15%): {len(val_df)} samples")
    print(f"   - Test (15%): {len(test_df)} samples")

    trainer = ModelTrainer(artifacts_dir="artifacts/models")
    results = trainer.train_and_evaluate(dataset=dataset)

    logreg_m = results["logreg_metrics"]
    svm_m = results["svm_metrics"]
    sel_m = results["selected_metrics"]

    print("\n" + "-" * 75)
    print("Model Evaluation Summary Table (Development Benchmark):")
    print("-" * 75)
    print(f"{'Metric':<25} | {'TF-IDF + LogReg':<22} | {'TF-IDF + Calibrated SVM':<22}")
    print("-" * 75)
    print(f"{'Accuracy':<25} | {logreg_m.accuracy:<22.4f} | {svm_m.accuracy:<22.4f}")
    print(f"{'Precision':<25} | {logreg_m.precision:<22.4f} | {svm_m.precision:<22.4f}")
    print(f"{'Recall':<25} | {logreg_m.recall:<22.4f} | {svm_m.recall:<22.4f}")
    print(f"{'F1 Score':<25} | {logreg_m.f1_score:<22.4f} | {svm_m.f1_score:<22.4f}")
    print(f"{'ROC-AUC':<25} | {str(round(logreg_m.roc_auc, 4)) if logreg_m.roc_auc else 'N/A':<22} | {str(round(svm_m.roc_auc, 4)) if svm_m.roc_auc else 'N/A':<22}")
    print(f"{'False Positives (FP)':<25} | {logreg_m.false_positives:<22} | {svm_m.false_positives:<22}")
    print(f"{'False Negatives (FN)':<25} | {logreg_m.false_negatives:<22} | {svm_m.false_negatives:<22}")
    print(f"{'Confusion Matrix':<25} | {str(logreg_m.confusion_matrix):<22} | {str(svm_m.confusion_matrix):<22}")
    print("-" * 75)

    print(f"\n3. Selected Model: {sel_m.algorithm} ({sel_m.version})")
    print(f"   - Artifact: {results['artifact_path']}")
    print(f"   - Manifest: {results['metadata_path']}")
    print("=" * 75)


if __name__ == "__main__":
    main()
