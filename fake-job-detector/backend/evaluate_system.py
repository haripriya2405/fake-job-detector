import json
import os
import sys

# Ensure backend directory is in python search path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.logging import setup_logging
from evaluation.harness import SystemEvaluationHarness


def main():
    setup_logging()
    print("=" * 80)
    print("SentinelJob AI — Phase 6 System Validation & Risk Calibration Harness")
    print("=" * 80)

    harness = SystemEvaluationHarness()
    report = harness.run_full_evaluation()

    m = report["metrics"]
    cm = report["confusion_matrix"]

    print("\n1. Overall Statistical Classification Performance (Threshold >= 50):")
    print("-" * 80)
    print(f"   • Total Test Cases Evaluated : {report['total_cases']}")
    print(f"   • Accuracy                   : {m['accuracy'] * 100:.2f}%")
    print(f"   • Precision                  : {m['precision']:.4f}")
    print(f"   • Recall                     : {m['recall']:.4f}")
    print(f"   • F1-Score                   : {m['f1_score']:.4f}")
    print(f"   • False Positive Rate (FPR)  : {m['false_positive_rate'] * 100:.2f}% ({cm['FP']} false alarms)")
    print(f"   • False Negative Rate (FNR)  : {m['false_negative_rate'] * 100:.2f}% ({cm['FN']} missed threats)")
    print(f"   • Confusion Matrix           : TP={cm['TP']}, TN={cm['TN']}, FP={cm['FP']}, FN={cm['FN']}")

    print("\n2. Mean Risk Score & Score Stability by Test Cohort:")
    print("-" * 80)
    print(f"{'Cohort Name':<30} | {'Count':<6} | {'Mean Score':<12} | {'Score Range':<14} | {'Std Dev':<8}")
    print("-" * 80)
    for cohort, stats in report["cohort_summary"].items():
        print(f"{cohort:<30} | {stats['count']:<6} | {stats['mean_score']:<12.2f} | {stats['min_score']} - {stats['max_score']:<10} | {stats['std_dev']:<8.2f}")
    print("-" * 80)

    print("\n3. Risk Tier Distribution Across All Evaluated Cases:")
    print("-" * 80)
    for tier, count in report["tier_distribution"].items():
        pct = (count / report["total_cases"]) * 100
        print(f"   • {tier.upper():<10} Risk Tier (0-100) : {count:>2} cases ({pct:>5.1f}%)")

    cal = report["calibration"]
    print("\n4. Probability & Risk Score Calibration Metrics:")
    print("-" * 80)
    print(f"   • Expected Calibration Error (ECE) : {cal.get('expected_calibration_error', 'N/A')}")
    print(f"   • Brier Score Loss (0.0 = perfect) : {cal.get('brier_score', 'N/A')}")

    if report["false_positives"]:
        print("\n5. False Positives Breakdown (Legitimate postings scored as threats):")
        for fp in report["false_positives"]:
            print(f"   • [{fp['id']}] {fp['title']} -> Score: {fp['score']} ({fp['tier']})")
    else:
        print("\n5. False Positives: ZERO (0) false alarms on clean legitimate postings.")

    if report["false_negatives"]:
        print("\n6. False Negatives Breakdown (Scam postings missed):")
        for fn in report["false_negatives"]:
            print(f"   • [{fn['id']}] {fn['title']} -> Score: {fn['score']} ({fn['tier']})")
    else:
        print("\n6. False Negatives: ZERO (0) missed threat cases.")

    print("\n" + "=" * 80)
    print("Phase 6 System Validation Complete.")
    print("=" * 80)


if __name__ == "__main__":
    main()
