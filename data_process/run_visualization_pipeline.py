#!/usr/bin/env python3
"""
Master script to run the complete visualization pipeline.

This script runs all steps to generate visualization files and reports:
1. Generate Chart.js configurations from evaluation results
2. Generate markdown report with dynamic charts
3. Generate HTML report with interactive interface

Usage:
    python run_visualization_pipeline.py [--data-dir DATA_DIR] [--output-dir OUTPUT_DIR]

Default output directory: 'visualization_output'
"""

import os
import sys
import subprocess
import argparse


def run_command(cmd, description):
    """Run a command and print status."""
    print(f"\n{'='*60}")
    print(f"Step: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"Success!\n{result.stdout}")
        if result.stderr:
            print(f"Warnings:\n{result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command:")
        print(f"Exit code: {e.returncode}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Run complete visualization pipeline')
    parser.add_argument('--data-dir', default='eval_result',
                       help='Directory containing evaluation results (default: eval_result)')
    parser.add_argument('--output-dir', default='visualization_output',
                       help='Output directory for all generated files (default: visualization_output)')
    parser.add_argument('--skip-charts', action='store_true',
                       help='Skip chart generation (use existing charts)')
    parser.add_argument('--skip-markdown', action='store_true',
                       help='Skip markdown report generation')
    parser.add_argument('--skip-html', action='store_true',
                       help='Skip HTML report generation')

    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Step 1: Generate Chart.js configurations
    chart_dir = os.path.join(args.output_dir, "chart_configs")
    if not args.skip_charts:
        cmd = f'python generate_charts.py --data-dir "{args.data_dir}" --output-dir "{chart_dir}" --chart-type all'
        if not run_command(cmd, "Generate Chart.js configurations"):
            print("Failed to generate charts. Exiting.")
            sys.exit(1)
    else:
        print(f"\nSkipping chart generation. Using existing charts in: {chart_dir}")
        if not os.path.exists(chart_dir):
            print(f"Error: Chart directory '{chart_dir}' not found.")
            sys.exit(1)

    # Step 2: Generate markdown report
    if not args.skip_markdown:
        md_report = os.path.join(args.output_dir, "evaluation_report.md")
        cmd = f'python generate_markdown_report.py --chart-dir "{chart_dir}" --output "{md_report}"'
        if not run_command(cmd, "Generate markdown report"):
            print("Warning: Markdown report generation failed, continuing...")

    # Step 3: Generate HTML report
    if not args.skip_html:
        html_report = os.path.join(args.output_dir, "evaluation_report.html")
        cmd = f'python generate_html_report.py --chart-dir "{chart_dir}" --output "{html_report}"'
        if not run_command(cmd, "Generate HTML report"):
            print("Warning: HTML report generation failed, continuing...")

    # Summary
    print(f"\n{'='*60}")
    print("VISUALIZATION PIPELINE COMPLETE")
    print(f"{'='*60}")

    print(f"\nOutput directory: {args.output_dir}")
    print("\nGenerated files:")

    if not args.skip_charts and os.path.exists(chart_dir):
        chart_files = [f for f in os.listdir(chart_dir) if f.endswith('.json')]
        print(f"  • Chart configurations: {len(chart_files)} files in {chart_dir}/")

    if not args.skip_markdown and os.path.exists(md_report):
        print(f"  • Markdown report: {md_report}")

    if not args.skip_html and os.path.exists(html_report):
        print(f"  • HTML report: {html_report}")

    print(f"\nTo view the reports:")
    print(f"  1. HTML report: Open '{html_report}' in a web browser")
    print(f"  2. Markdown report: View '{md_report}' in a markdown viewer that supports HTML/JS")
    print(f"\nTo regenerate individual components:")
    print(f"  python generate_charts.py --data-dir {args.data_dir} --output-dir {chart_dir}")
    print(f"  python generate_markdown_report.py --chart-dir {chart_dir} --output {md_report}")
    print(f"  python generate_html_report.py --chart-dir {chart_dir} --output {html_report}")

    print(f"\n{'='*60}")


if __name__ == "__main__":
    main()