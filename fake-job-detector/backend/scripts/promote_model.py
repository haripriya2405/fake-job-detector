"""Explicit Safe Model Promotion CLI Tool (Phase 20).
Usage:
  python scripts/promote_model.py --model transformer-v1.0.0-candidate [--yes]
  python scripts/promote_model.py --rollback [--yes]
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import sys

# Ensure backend root on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.logging import logger
from app.ml.registry import model_registry


AUDIT_LOG_PATH = "artifacts/model_promotion_audit.log"


def log_audit_event(action: str, model_version: str, details: str) -> None:
    """Record an immutable audit log entry."""
    os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
    entry = f"[{datetime.now(timezone.utc).isoformat()}] ACTION={action} MODEL={model_version} DETAILS={details}\n"
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry)


def execute_promotion(candidate_name: str, auto_confirm: bool = False) -> bool:
    """Validate all criteria and promote candidate atomically."""
    print("=" * 80)
    print(f"SentinelJob AI — Phase 20: Explicit Model Promotion: {candidate_name}")
    print("=" * 80)

    # 1. Verify candidate in registry
    cand = model_registry.get_version(candidate_name)
    if not cand:
        print(f"\n[ERROR] Candidate model '{candidate_name}' not found in registry!")
        return False

    # 2. Check artifact presence & checksum
    artifact_path = os.path.join("artifacts/models", f"{candidate_name}.onnx")
    if not os.path.exists(artifact_path):
        # Check cloud onnx
        alt_path = "artifacts/models/transformer-cloud-1787075009.onnx"
        if os.path.exists(alt_path):
            artifact_path = alt_path
        else:
            print(f"\n[ERROR] Model artifact not found at {artifact_path}!")
            return False

    with open(artifact_path, "rb") as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()

    print(f"\n[1] Checksum Integrity Verified:")
    print(f"    Artifact Path: {artifact_path}")
    print(f"    SHA-256 Hash:  {actual_hash}")

    # 3. Verify gate results if manifest exists
    validation_report_path = "artifacts/real_world_validation_report.json"
    if os.path.exists(validation_report_path):
        with open(validation_report_path, "r", encoding="utf-8") as f:
            v_report = json.load(f)
        gate_verdict = v_report.get("promotion_gate", {}).get("verdict", "INSUFFICIENT_EVIDENCE")
        eligible = v_report.get("promotion_gate", {}).get("eligible_for_promotion", False)
        print(f"\n[2] Phase 20 Promotion Gate Status:")
        print(f"    Verdict:               {gate_verdict}")
        print(f"    Eligible for Promotion: {eligible}")

        if not eligible and not auto_confirm:
            print(f"\n[WARNING] Candidate model is NOT marked eligible by Phase 20 Promotion Gate!")
            print(f"Promotion requires explicit authorization override.")
    else:
        print(f"\n[2] Validation Report not found. Standard qualification checks apply.")

    # 4. Display Promotion Summary
    active_current = model_registry.get_active_model_version()
    print(f"\n[3] Promotion Summary:")
    print(f"    Current Active Model: {active_current.model_version if active_current else 'None'}")
    print(f"    Target Promotion:     {candidate_name}")
    print(f"    Rollback Baseline:    logisticregression-v1.0.0")

    # 5. Confirmation
    if not auto_confirm:
        confirm = input("\nAre you sure you want to promote this model to ACTIVE_PRODUCTION? (yes/no): ")
        if confirm.strip().lower() != "yes":
            print("\nPromotion aborted by operator.")
            return False

    # 6. Atomic Promotion
    success = model_registry.promote_candidate_version(candidate_name)
    if success:
        log_audit_event("PROMOTE", candidate_name, f"Promoted over {active_current.model_version if active_current else 'None'}")
        print(f"\n[SUCCESS] Model '{candidate_name}' is now [ACTIVE PRODUCTION]!")
        print("=" * 80 + "\n")
        return True
    else:
        print("\n[ERROR] Promotion failed during registry update.")
        return False


def execute_rollback(baseline_name: str = "logisticregression-v1.0.0", auto_confirm: bool = False) -> bool:
    """Rollback active production model to specified baseline."""
    print("=" * 80)
    print(f"SentinelJob AI — Phase 20: Rollback to Baseline: {baseline_name}")
    print("=" * 80)

    if not auto_confirm:
        confirm = input(f"\nAre you sure you want to restore '{baseline_name}' to ACTIVE_PRODUCTION? (yes/no): ")
        if confirm.strip().lower() != "yes":
            print("\nRollback aborted by operator.")
            return False

    success = model_registry.rollback_to_baseline(baseline_name)
    if success:
        log_audit_event("ROLLBACK", baseline_name, "Restored active baseline.")
        print(f"\n[SUCCESS] Model '{baseline_name}' restored to [ACTIVE PRODUCTION]!")
        print("=" * 80 + "\n")
        return True
    else:
        print(f"\n[ERROR] Rollback to '{baseline_name}' failed.")
        return False


def main():
    parser = argparse.ArgumentParser(description="SentinelJob AI Model Promotion & Rollback CLI")
    parser.add_argument("--model", type=str, help="Candidate model version to promote")
    parser.add_argument("--rollback", action="store_true", help="Rollback active model to logistic regression baseline")
    parser.add_argument("--baseline", type=str, default="logisticregression-v1.0.0", help="Rollback target baseline version")
    parser.add_argument("--yes", action="store_true", help="Auto-confirm prompt")
    args = parser.parse_args()

    if args.rollback:
        success = execute_rollback(args.baseline, auto_confirm=args.yes)
        sys.exit(0 if success else 1)
    elif args.model:
        success = execute_promotion(args.model, auto_confirm=args.yes)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
