#!/usr/bin/env python3
"""
Extract rate metrics from SWE-bench evaluation JSONL files.

This script reads the JSONL files in data_process/eval_result/reviews/*/swe_bench_verified_mini_default.jsonl
and extracts only the four rate metrics specified by the user:
1. acc_rate (average accuracy)
2. patch_successfully_applied_rate (patch_successfully_applied_count / total_samples)
3. fail_to_pass_rate (FAIL_TO_PASS.success / (FAIL_TO_PASS.success + FAIL_TO_PASS.failure))
4. pass_to_pass_rate (PASS_TO_PASS.success / (PASS_TO_PASS.success + PASS_TO_PASS.failure))

Usage:
    python extract_swebench_rates.py
    python extract_swebench_rates.py --output swebench_rates.json

Output format:
{
    "model_name": {
        "acc_rate": 0.3,
        "patch_successfully_applied_rate": 0.46,
        "fail_to_pass_rate": 0.65,
        "pass_to_pass_rate": 0.85
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
        # Extract model name from path: .../reviews/{model_name}/file.jsonl
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
    (Reused from extract_swebench_metrics.py)

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

            # Extract patch-related metrics
            metadata = score.get("metadata", {})
            patch_is_none = False
            patch_exists = False
            patch_successfully_applied = False

            # Extract test results and patch metrics from metadata.report
            test_results = {}
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
                "test_results": test_results,
                "patch_is_none": patch_is_none,
                "patch_exists": patch_exists,
                "patch_successfully_applied": patch_successfully_applied
            }

            samples.append(sample_metrics)

    return samples


def calculate_rates(samples: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate the four rate metrics from samples.

    Args:
        samples: List of sample metrics dictionaries

    Returns:
        Dictionary with four rate metrics
    """
    if not samples:
        return {
            "acc_rate": 0.0,
            "patch_successfully_applied_rate": 0.0,
            "fail_to_pass_rate": 0.0,
            "pass_to_pass_rate": 0.0
        }

    total = len(samples)
    acc_values = [s["acc"] for s in samples]
    acc_rate = statistics.mean(acc_values) if acc_values else 0.0

    patch_successfully_applied_count = sum(1 for s in samples if s.get("patch_successfully_applied", False))
    patch_successfully_applied_rate = patch_successfully_applied_count / total

    # Aggregate test results for fail_to_pass and pass_to_pass
    fail_to_pass_success = 0
    fail_to_pass_failure = 0
    pass_to_pass_success = 0
    pass_to_pass_failure = 0
    error_samples = 0

    for sample in samples:
        test_results = sample.get("test_results", {})
        if "error" in test_results:
            error_samples += 1
            continue

        # fail_to_pass
        fail_to_pass = test_results.get("fail_to_pass", {})
        if isinstance(fail_to_pass, dict):
            fail_to_pass_success += fail_to_pass.get("success", 0)
            fail_to_pass_failure += fail_to_pass.get("failure", 0)

        # pass_to_pass
        pass_to_pass = test_results.get("pass_to_pass", {})
        if isinstance(pass_to_pass, dict):
            pass_to_pass_success += pass_to_pass.get("success", 0)
            pass_to_pass_failure += pass_to_pass.get("failure", 0)

    # Calculate fail_to_pass_rate
    fail_to_pass_total = fail_to_pass_success + fail_to_pass_failure
    if fail_to_pass_total > 0:
        fail_to_pass_rate = fail_to_pass_success / fail_to_pass_total
    else:
        fail_to_pass_rate = 0.0

    # Calculate pass_to_pass_rate
    pass_to_pass_total = pass_to_pass_success + pass_to_pass_failure
    if pass_to_pass_total > 0:
        pass_to_pass_rate = pass_to_pass_success / pass_to_pass_total
    else:
        pass_to_pass_rate = 0.0

    return {
        "acc_rate": acc_rate,
        "patch_successfully_applied_rate": patch_successfully_applied_rate,
        "fail_to_pass_rate": fail_to_pass_rate,
        "pass_to_pass_rate": pass_to_pass_rate
    }


def main():
    parser = argparse.ArgumentParser(
        description='Extract rate metrics from SWE-bench evaluation JSONL files'
    )
    parser.add_argument(
        '--data-dir',
        default='eval_result',
        help='Directory containing evaluation results (default: eval_result)'
    )
    parser.add_argument(
        '--output',
        default='swebench_rates.json',
        help='Output JSON file path (default: swebench_rates.json)'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Generate pretty-printed JSON output'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print detailed progress information'
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
    all_rates = {}

    for model_name, file_path in model_files.items():
        if args.verbose:
            print(f"\nProcessing {model_name}...")

        # Extract sample metrics
        samples = extract_sample_metrics(file_path)

        if not samples:
            print(f"  Warning: No valid samples found in {file_path}")
            continue

        # Calculate rates
        rates = calculate_rates(samples)
        all_rates[model_name] = rates

        if args.verbose:
            print(f"  Processed {len(samples)} samples")
            print(f"  acc_rate: {rates['acc_rate']:.4f}")
            print(f"  patch_successfully_applied_rate: {rates['patch_successfully_applied_rate']:.4f}")
            print(f"  fail_to_pass_rate: {rates['fail_to_pass_rate']:.4f}")
            print(f"  pass_to_pass_rate: {rates['pass_to_pass_rate']:.4f}")

    # Write output file
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    indent = 2 if args.pretty else None
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(all_rates, f, indent=indent, ensure_ascii=False)

    print(f"\nSuccessfully extracted rate metrics to: {args.output}")
    print(f"Total models processed: {len(all_rates)}")

    # Print summary table
    print("\nSummary Table:")
    print(f"{'Model':<30} {'acc_rate':>10} {'patch_rate':>10} {'fail_to_pass':>12} {'pass_to_pass':>12}")
    print("-" * 76)
    for model_name, rates in all_rates.items():
        print(f"{model_name:<30} {rates['acc_rate']:>10.4f} "
              f"{rates['patch_successfully_applied_rate']:>10.4f} "
              f"{rates['fail_to_pass_rate']:>12.4f} "
              f"{rates['pass_to_pass_rate']:>12.4f}")


if __name__ == "__main__":
    main()