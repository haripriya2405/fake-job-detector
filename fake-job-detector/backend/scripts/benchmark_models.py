"""CPU Latency & Resource Benchmarking Tool (Phase 20).
Executes >= 100 sequential inference passes on CPU per model, separating warm-up and
measuring mean, p50, p95, p99, min, max, throughput, and peak memory.
"""

import gc
import json
import os
import sys
import time
import tracemalloc
import numpy as np

# Ensure backend root on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.logging import logger
from app.ml.predictor import MLPredictor


BENCHMARK_SAMPLES = [
    "Senior Python Developer: Seeking backend engineer with experience in FastAPI, PostgreSQL, and Docker. 401(k) match.",
    "Immediate Selection: We will mail a cashier check of $4,500 for equipment. Deposit and wire remaining to vendor.",
    "Data Entry Typist: Work 2 hours daily. Pay $50 registration fee via CashApp before scheduling technical test.",
    "Product Designer: 4+ years UX/UI design with Figma and design systems. Competitive compensation and equity.",
    "Remote E-Commerce Associate: Recharge workstation balance with 100 USDT to unlock daily product ratings.",
]


def benchmark_predictor(predictor: MLPredictor, iterations: int = 100) -> dict:
    """Run sequential benchmark iterations on CPU."""
    tracemalloc.start()

    sample_pool = BENCHMARK_SAMPLES * (iterations // len(BENCHMARK_SAMPLES) + 1)
    sample_pool = sample_pool[:iterations]

    # 1. Warm-up pass (3 samples, timed separately)
    warmup_times = []
    for s in sample_pool[:3]:
        t0 = time.perf_counter()
        _ = predictor.predict(s)
        warmup_times.append((time.perf_counter() - t0) * 1000.0)

    # 2. Benchmark passes
    latencies_ms = []
    start_total = time.perf_counter()
    for s in sample_pool:
        t0 = time.perf_counter()
        _ = predictor.predict(s)
        lat_ms = (time.perf_counter() - t0) * 1000.0
        latencies_ms.append(lat_ms)
    total_time_sec = time.perf_counter() - start_total

    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_mem_mb = peak_mem / (1024 * 1024)

    lat_arr = np.array(latencies_ms)
    throughput = iterations / max(0.001, total_time_sec)

    return {
        "model_version": predictor.model_version,
        "algorithm": predictor.algorithm,
        "model_type": predictor.model_type,
        "iterations": iterations,
        "warmup_mean_ms": round(float(np.mean(warmup_times)), 2),
        "mean_latency_ms": round(float(np.mean(lat_arr)), 2),
        "p50_latency_ms": round(float(np.percentile(lat_arr, 50)), 2),
        "p95_latency_ms": round(float(np.percentile(lat_arr, 95)), 2),
        "p99_latency_ms": round(float(np.percentile(lat_arr, 99)), 2),
        "min_latency_ms": round(float(np.min(lat_arr)), 2),
        "max_latency_ms": round(float(np.max(lat_arr)), 2),
        "throughput_req_per_sec": round(float(throughput), 2),
        "peak_ram_mb": round(float(peak_mem_mb), 2),
        "meets_50ms_p95_target": bool(np.percentile(lat_arr, 95) <= 50.0),
    }


def main():
    print("=" * 80)
    print("SentinelJob AI — Phase 20: CPU Latency & Resource Benchmark")
    print("=" * 80)

    # Baseline Model Benchmark
    base_pred = MLPredictor(artifact_path="artifacts/models/tfidf_logistic_regression_v1.0.0.joblib")
    print(f"\n[1] Benchmarking Baseline: {base_pred.algorithm} (Version: {base_pred.model_version})...")
    base_metrics = benchmark_predictor(base_pred, iterations=100)
    print(f"    Warm-up Mean:     {base_metrics['warmup_mean_ms']} ms")
    print(f"    Mean Latency:     {base_metrics['mean_latency_ms']} ms")
    print(f"    p50 Latency:      {base_metrics['p50_latency_ms']} ms")
    print(f"    p95 Latency:      {base_metrics['p95_latency_ms']} ms (Target <= 50ms: {base_metrics['meets_50ms_p95_target']})")
    print(f"    p99 Latency:      {base_metrics['p99_latency_ms']} ms")
    print(f"    Throughput:       {base_metrics['throughput_req_per_sec']} req/sec")
    print(f"    Peak RAM:         {base_metrics['peak_ram_mb']} MB")

    # Candidate Model Benchmark
    onnx_path = "artifacts/models/transformer-cloud-1787075009.onnx"
    if os.path.exists(onnx_path):
        cand_pred = MLPredictor(artifact_path=onnx_path)
        print(f"\n[2] Benchmarking Candidate: {cand_pred.algorithm} (Version: {cand_pred.model_version})...")
        cand_metrics = benchmark_predictor(cand_pred, iterations=100)
        print(f"    Warm-up Mean:     {cand_metrics['warmup_mean_ms']} ms")
        print(f"    Mean Latency:     {cand_metrics['mean_latency_ms']} ms")
        print(f"    p50 Latency:      {cand_metrics['p50_latency_ms']} ms")
        print(f"    p95 Latency:      {cand_metrics['p95_latency_ms']} ms (Target <= 50ms: {cand_metrics['meets_50ms_p95_target']})")
        print(f"    p99 Latency:      {cand_metrics['p99_latency_ms']} ms")
        print(f"    Throughput:       {cand_metrics['throughput_req_per_sec']} req/sec")
        print(f"    Peak RAM:         {cand_metrics['peak_ram_mb']} MB")
    else:
        print(f"\n[2] Candidate artifact not found at {onnx_path}. Skipping candidate benchmark.")
        cand_metrics = None

    # Save benchmark artifact
    output_path = "artifacts/latency_benchmark.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "baseline": base_metrics,
            "candidate": cand_metrics,
        }, f, indent=2)

    print(f"\n[3] Latency Benchmark Saved -> {output_path}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
