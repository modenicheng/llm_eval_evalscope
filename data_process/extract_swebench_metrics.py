#!/usr/bin/env python3
"""
Extract detailed metrics from SWE-bench evaluation JSONL files.

This script reads the JSONL files in data_process/eval_result/reviews/*/swe_bench_verified_mini_default.jsonl
and extracts detailed metrics from the sample_score.score field for analysis.

Usage:
    python extract_swebench_metrics.py
    python extract_swebench_metrics.py --output swebench_detailed_metrics.json

Output format:
{
    "model_name": {
        "total_samples": 50,
        "avg_acc": 0.0,
        "completed_rate": 1.0,
        "resolved_rate": 0.0,
        "test_stats": {
            "fail_to_pass_success": 0,
            "fail_to_pass_failure": 1,
            "pass_to_pass_success": 0,
            "pass_to_pass_failure": 16,
            ...
        },
        "samples": [
            {
                "sample_id": 17,
                "acc": 0.0,
                "completed": true,
                "resolved": false,
                "extracted_prediction": "...",
                "prediction": "...",
                "test_results": {...}
            },
            ...
        ]
    },
    ...
}
"""

import json
import os
import glob
import argparse
import sys
from typing import Dict, List, Any, Optional
from collections import defaultdict
import statistics


def find_jsonl_files(data_dir: str = "eval_result") -> Dict[str, str]:
    """
    Find all SWE-bench JSONL files in the reviews subdirectories.

    Args:
        data_dir: Base directory containing evaluation results

    Returns:
        Dictionary mapping model_name -> file_path
    """
    pattern = os.path.join(data_dir, "reviews", "*", "swe_bench_verified_mini_default.jsonl")
    files = glob.glob(pattern)

    model_files = {}
    for file_path in files:
        # Extract model name from path: .../reports/{model_name}/file.jsonl
        path_parts = file_path.split(os.sep)
        model_name = "unknown"
        for i, part in enumerate(path_parts):
            if part == "reviews" and i + 1 < len(path_parts):
                model_name = path_parts[i + 1]
                break
        model_files[model_name] = file_path

    return model_files


def extract_sample_metrics(file_path: str) -> List[Dict[str, Any]]:
    """
    Extract metrics from a JSONL file.

    Args:
        file_path: Path to JSONL file

    Returns:
        List of sample metrics dictionaries
    """
    samples = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num} in {file_path}: {e}")
                continue

            # Extract sample_score.score field
            sample_score = data.get("sample_score", {})
            score = sample_score.get("score", {})

            # Extract basic metrics
            sample_id = sample_score.get("sample_id", line_num)
            acc = score.get("value", {}).get("acc", 0.0)
            completed = score.get("metadata", {}).get("completed", False)
            resolved = score.get("metadata", {}).get("resolved", False)
            extracted_prediction = score.get("extracted_prediction", "")
            prediction = score.get("prediction", "")
            explanation = score.get("explanation")
            main_score_name = score.get("main_score_name")

            # Extract patch-related metrics
            # Note: patch fields are inside report.{repo_name}, not in metadata directly
            metadata = score.get("metadata", {})
            patch_is_none = False
            patch_exists = False
            patch_successfully_applied = False

            # Extract test results and patch metrics from metadata.report
            test_results = {}
            # metadata variable already defined above
            report = metadata.get("report", {})

            # Handle different report formats: could be dict, string (error), or None
            if isinstance(report, dict):
                # The report seems to have keys like "django__django-12304"
                # Extract test status from the first key (there's typically only one)
                for key, repo_report in report.items():
                    if isinstance(repo_report, dict):
                        # Extract patch-related metrics from repo_report
                        patch_is_none = repo_report.get("patch_is_None", False)
                        patch_exists = repo_report.get("patch_exists", False)
                        patch_successfully_applied = repo_report.get("patch_successfully_applied", False)

                        test_status = repo_report.get("tests_status", {})
                        test_results = {
                            "fail_to_pass": {
                                "success": len(test_status.get("FAIL_TO_PASS", {}).get("success", [])),
                                "failure": len(test_status.get("FAIL_TO_PASS", {}).get("failure", []))
                            },
                            "pass_to_pass": {
                                "success": len(test_status.get("PASS_TO_PASS", {}).get("success", [])),
                                "failure": len(test_status.get("PASS_TO_PASS", {}).get("failure", []))
                            },
                            "fail_to_fail": {
                                "success": len(test_status.get("FAIL_TO_FAIL", {}).get("success", [])),
                                "failure": len(test_status.get("FAIL_TO_FAIL", {}).get("failure", []))
                            },
                            "pass_to_fail": {
                                "success": len(test_status.get("PASS_TO_FAIL", {}).get("success", [])),
                                "failure": len(test_status.get("PASS_TO_FAIL", {}).get("failure", []))
                            }
                        }
                    else:
                        # repo_report is not a dict (might be string error)
                        test_results = {"error": str(repo_report)}
                    break  # Only process first repo
            elif report is not None:
                # Report is a string or other non-dict type
                test_results = {"error": str(report)}

            sample_metrics = {
                "sample_id": sample_id,
                "acc": acc,
                "completed": completed,
                "resolved": resolved,
                "extracted_prediction": extracted_prediction,
                "prediction": prediction,
                "explanation": explanation,
                "main_score_name": main_score_name,
                "test_results": test_results,
                "patch_is_none": patch_is_none,
                "patch_exists": patch_exists,
                "patch_successfully_applied": patch_successfully_applied
            }

            samples.append(sample_metrics)

    return samples


def aggregate_model_metrics(samples: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate metrics across all samples for a model.

    Args:
        samples: List of sample metrics dictionaries

    Returns:
        Aggregated metrics dictionary
    """
    if not samples:
        return {}

    total = len(samples)
    acc_values = [s["acc"] for s in samples]
    completed_count = sum(1 for s in samples if s["completed"])
    resolved_count = sum(1 for s in samples if s["resolved"])

    # Count patch-related metrics
    patch_is_none_count = sum(1 for s in samples if s.get("patch_is_none", False))
    patch_exists_count = sum(1 for s in samples if s.get("patch_exists", False))
    patch_successfully_applied_count = sum(1 for s in samples if s.get("patch_successfully_applied", False))

    # Aggregate test results
    test_stats = defaultdict(lambda: defaultdict(int))
    error_samples = 0
    for sample in samples:
        test_results = sample.get("test_results", {})
        # test_results could be:
        # 1. Dict with test categories (fail_to_pass, pass_to_pass, etc.)
        # 2. Dict with "error" key indicating an error string
        # 3. Empty dict
        if "error" in test_results:
            error_samples += 1
            continue  # Skip error samples for test stats

        for test_type, results in test_results.items():
            if isinstance(results, dict):
                for result_type, count in results.items():
                    if isinstance(count, (int, float)):
                        test_stats[test_type][result_type] += int(count)

    return {
        "total_samples": total,
        "avg_acc": statistics.mean(acc_values) if acc_values else 0.0,
        "acc_std": statistics.stdev(acc_values) if len(acc_values) > 1 else 0.0,
        "completed_rate": completed_count / total,
        "resolved_rate": resolved_count / total,
        "error_samples": error_samples,
        "test_stats": dict(test_stats),
        "patch_stats": {
            "patch_is_none_count": patch_is_none_count,
            "patch_is_none_rate": patch_is_none_count / total,
            "patch_exists_count": patch_exists_count,
            "patch_exists_rate": patch_exists_count / total,
            "patch_successfully_applied_count": patch_successfully_applied_count,
            "patch_successfully_applied_rate": patch_successfully_applied_count / total
        },
        "samples": samples  # Include all samples for detailed analysis
    }


def main():
    parser = argparse.ArgumentParser(
        description='Extract detailed metrics from SWE-bench evaluation JSONL files'
    )
    parser.add_argument(
        '--data-dir',
        default='eval_result',
        help='Directory containing evaluation results (default: eval_result)'
    )
    parser.add_argument(
        '--output',
        default='swebench_detailed_metrics.json',
        help='Output JSON file path (default: swebench_detailed_metrics.json)'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Generate pretty-printed JSON output'
    )
    parser.add_argument(
        '--summary-only',
        action='store_true',
        help='Only output summary statistics, not individual samples'
    )

    args = parser.parse_args()

    # Find all JSONL files
    print(f"Looking for SWE-bench JSONL files in {args.data_dir}...")
    model_files = find_jsonl_files(args.data_dir)

    if not model_files:
        print(f"No JSONL files found matching pattern: {args.data_dir}/reviews/*/swe_bench_verified_mini_default.jsonl")
        return

    print(f"Found {len(model_files)} models:")
    for model in model_files.keys():
        print(f"  - {model}")

    # Process each model
    all_metrics = {}

    for model_name, file_path in model_files.items():
        print(f"\nProcessing {model_name}...")

        # Extract sample metrics
        samples = extract_sample_metrics(file_path)

        if not samples:
            print(f"  Warning: No valid samples found in {file_path}")
            continue

        # Aggregate metrics
        model_metrics = aggregate_model_metrics(samples)

        if args.summary_only:
            # Remove individual samples to reduce file size
            model_metrics.pop("samples", None)

        all_metrics[model_name] = model_metrics

        print(f"  Processed {len(samples)} samples")
        print(f"  Average accuracy: {model_metrics['avg_acc']:.4f}")
        print(f"  Completed rate: {model_metrics['completed_rate']:.2%}")
        print(f"  Resolved rate: {model_metrics['resolved_rate']:.2%}")

    # Write output file
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    indent = 2 if args.pretty else None
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(all_metrics, f, indent=indent, ensure_ascii=False)

    print(f"\nSuccessfully extracted metrics to: {args.output}")
    print(f"Total models processed: {len(all_metrics)}")

    # Print summary table
    print("\nSummary Table:")
    print(f"{'Model':<30} {'Samples':>8} {'Avg Acc':>10} {'Completed':>10} {'Resolved':>10}")
    print("-" * 78)
    for model_name, metrics in all_metrics.items():
        print(f"{model_name:<30} {metrics['total_samples']:>8} {metrics['avg_acc']:>10.4f} "
              f"{metrics['completed_rate']:>10.2%} {metrics['resolved_rate']:>10.2%}")


if __name__ == "__main__":
    main()