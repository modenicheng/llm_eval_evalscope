#!/usr/bin/env python3
"""
Chart.js Configuration Generator for LLM Evaluation Results

This script reads evaluation result JSON files and generates Chart.js configurations
for visualizing model performance across different datasets and metrics.

Usage:
    python generate_charts.py [--output-dir OUTPUT_DIR] [--chart-type TYPE]

Output:
    Chart.js JSON configuration files in the specified output directory.
"""

import json
import os
import glob
import argparse
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import sys

# Import the chartjs_wrap module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from chartjs_wrap import ChartJS, ChartType, Color, Font, Position, TextAlign, Easing, ScaleType
from chartjs_wrap import BarDataset, LineDataset, RadarDataset, PieDataset, DoughnutDataset
from chartjs_wrap import TitleConfig, LegendConfig, TooltipConfig, ScaleConfig, ScaleTitle, GridLine
from chartjs_wrap import AnimationConfig, RadialLinearScale, AngleLine, PointLabel

# =====================
# Data Structures
# =====================

@dataclass
class EvaluationResult:
    """Represents a single evaluation result from a JSON file."""
    model_name: str
    dataset_name: str
    dataset_pretty_name: str
    overall_score: float
    metrics: List[Dict[str, Any]]
    file_path: str

    @classmethod
    def from_json_file(cls, file_path: str) -> 'EvaluationResult':
        """Load evaluation result from a JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract model variant from file path (directory name)
        # Path format: .../reports/{model_variant}/{dataset}.json
        path_parts = file_path.split(os.sep)
        model_variant = 'unknown'
        if len(path_parts) >= 2:
            # The model variant is the directory name in the reports folder
            reports_index = -1
            for i, part in enumerate(path_parts):
                if part == 'reports' and i + 1 < len(path_parts):
                    model_variant = path_parts[i + 1]
                    break

        return cls(
            model_name=model_variant,  # Use the directory name as model name
            dataset_name=data.get('dataset_name', 'unknown'),
            dataset_pretty_name=data.get('dataset_pretty_name', data.get('dataset_name', 'unknown')),
            overall_score=data.get('score', 0.0),
            metrics=data.get('metrics', []),
            file_path=file_path
        )

@dataclass
class ChartData:
    """Container for chart data."""
    labels: List[str]
    datasets: List[Dict[str, Any]]
    title: str
    description: str


# =====================
# Data Collection
# =====================

def collect_evaluation_results(data_dir: str) -> List[EvaluationResult]:
    """
    Collect all evaluation results from JSON files in the data directory.

    Args:
        data_dir: Directory containing evaluation result JSON files

    Returns:
        List of EvaluationResult objects
    """
    results = []

    # Find all JSON files in the reports directory
    pattern = os.path.join(data_dir, "reports", "**", "*.json")
    json_files = glob.glob(pattern, recursive=True)

    print(f"Found {len(json_files)} JSON files")

    for file_path in json_files:
        try:
            result = EvaluationResult.from_json_file(file_path)
            results.append(result)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    return results


def organize_results_by_model(results: List[EvaluationResult]) -> Dict[str, List[EvaluationResult]]:
    """Organize results by model name."""
    organized = {}
    for result in results:
        if result.model_name not in organized:
            organized[result.model_name] = []
        organized[result.model_name].append(result)
    return organized


def organize_results_by_dataset(results: List[EvaluationResult]) -> Dict[str, List[EvaluationResult]]:
    """Organize results by dataset name."""
    organized = {}
    for result in results:
        if result.dataset_name not in organized:
            organized[result.dataset_name] = []
        organized[result.dataset_name].append(result)
    return organized


# =====================
# Chart Generators
# =====================

def generate_model_comparison_chart(
    dataset_name: str,
    results: List[EvaluationResult],
    metric_name: str = "overall"
) -> Dict[str, Any]:
    """
    Generate a bar chart comparing different models on a specific dataset.

    Args:
        dataset_name: Name of the dataset
        results: List of evaluation results for different models on this dataset
        metric_name: Metric to compare (default: "overall" for overall score)

    Returns:
        Chart.js configuration dictionary
    """
    chart = ChartJS(ChartType.BAR)

    # Extract model names and scores
    labels = []
    scores = []

    for result in results:
        labels.append(result.model_name)

        if metric_name == "overall":
            scores.append(result.overall_score)
        else:
            # Find the specific metric
            metric_score = None
            for metric in result.metrics:
                if metric.get('name') == metric_name:
                    metric_score = metric.get('score', 0.0)
                    break

            if metric_score is None:
                # Try to find any metric with subsets
                for metric in result.metrics:
                    if 'categories' in metric and metric['categories']:
                        for category in metric['categories']:
                            if 'subsets' in category and category['subsets']:
                                metric_score = metric.get('score', 0.0)
                                break
                    if metric_score is not None:
                        break

            scores.append(metric_score or 0.0)

    # Create dataset
    dataset = chart.create_dataset(ChartType.BAR)
    dataset.label = f"{metric_name} Score"
    dataset.data = scores

    # Set colors based on score (green for high, red for low)
    colors = []
    for score in scores:
        if score >= 0.8:
            colors.append("rgba(75, 192, 192, 0.7)")  # Green
        elif score >= 0.6:
            colors.append("rgba(255, 206, 86, 0.7)")  # Yellow
        else:
            colors.append("rgba(255, 99, 132, 0.7)")  # Red

    dataset.backgroundColor = colors
    dataset.borderColor = [color.replace('0.7', '1.0') for color in colors]
    dataset.borderWidth = 2

    chart.set_labels(labels)
    chart.add_dataset(dataset)

    # Configure chart
    chart.set_title(f"Model Comparison on {dataset_name}",
                   color="#333",
                   font=Font(size=18, weight='bold'))

    chart.set_legend(position=Position.TOP)

    chart.set_tooltip(enabled=True,
                     mode='index',
                     intersect=False)

    # Configure scales
    y_scale = ScaleConfig(
        type=ScaleType.LINEAR,
        display=True,
        title=ScaleTitle(
            display=True,
            text='Score',
            color='#666',
            font=Font(size=14)
        ),
        min=0,
        max=1.0,
        grid=GridLine(
            display=True,
        )
    )

    x_scale = ScaleConfig(
        type=ScaleType.CATEGORY,
        display=True,
        grid=GridLine(
            display=False
        )
    )

    chart.set_scales(x_scale=x_scale, y_scale=y_scale)

    chart.set_responsive(True, True)
    chart.set_animation(duration=1000, easing=Easing.EASE_OUT_QUART)

    return chart.to_dict()


def generate_dataset_comparison_chart(
    model_name: str,
    results: List[EvaluationResult],
    metric_name: str = "overall"
) -> Dict[str, Any]:
    """
    Generate a bar chart comparing a model's performance across different datasets.

    Args:
        model_name: Name of the model
        results: List of evaluation results for this model on different datasets
        metric_name: Metric to compare (default: "overall" for overall score)

    Returns:
        Chart.js configuration dictionary
    """
    chart = ChartJS(ChartType.BAR)

    # Extract dataset names and scores
    labels = []
    scores = []

    for result in results:
        labels.append(result.dataset_pretty_name)

        if metric_name == "overall":
            scores.append(result.overall_score)
        else:
            # Find the specific metric
            metric_score = None
            for metric in result.metrics:
                if metric.get('name') == metric_name:
                    metric_score = metric.get('score', 0.0)
                    break

            if metric_score is None:
                # Try to find any metric with subsets
                for metric in result.metrics:
                    if 'categories' in metric and metric['categories']:
                        for category in metric['categories']:
                            if 'subsets' in category and category['subsets']:
                                metric_score = metric.get('score', 0.0)
                                break
                    if metric_score is not None:
                        break

            scores.append(metric_score or 0.0)

    # Create dataset
    dataset = chart.create_dataset(ChartType.BAR)
    dataset.label = f"{metric_name} Score"
    dataset.data = scores

    # Set colors
    colors = []
    for score in scores:
        if score >= 0.8:
            colors.append("rgba(54, 162, 235, 0.7)")  # Blue
        elif score >= 0.6:
            colors.append("rgba(255, 206, 86, 0.7)")  # Yellow
        else:
            colors.append("rgba(255, 99, 132, 0.7)")  # Red

    dataset.backgroundColor = colors
    dataset.borderColor = [color.replace('0.7', '1.0') for color in colors]
    dataset.borderWidth = 2

    chart.set_labels(labels)
    chart.add_dataset(dataset)

    # Configure chart
    chart.set_title(f"{model_name} Performance Across Datasets",
                   color="#333",
                   font=Font(size=18, weight='bold'))

    chart.set_legend(position=Position.TOP)

    chart.set_tooltip(enabled=True,
                     mode='index',
                     intersect=False)

    # Configure scales
    y_scale = ScaleConfig(
        type=ScaleType.LINEAR,
        display=True,
        title=ScaleTitle(
            display=True,
            text='Score',
            color='#666',
            font=Font(size=14)
        ),
        min=0,
        max=1.0,
        grid=GridLine(
            display=True,
        )
    )

    x_scale = ScaleConfig(
        type=ScaleType.CATEGORY,
        display=True,
        grid=GridLine(
            display=False
        )
    )

    chart.set_scales(x_scale=x_scale, y_scale=y_scale)

    chart.set_responsive(True, True)
    chart.set_animation(duration=1000, easing=Easing.EASE_OUT_QUART)

    return chart.to_dict()


def generate_category_radar_chart(
    result: EvaluationResult,
    metric_index: int = 0
) -> Dict[str, Any]:
    """
    Generate a radar chart showing performance across categories/subsets.

    Args:
        result: Evaluation result for a specific model and dataset
        metric_index: Index of the metric to use (default: 0)

    Returns:
        Chart.js configuration dictionary
    """
    chart = ChartJS(ChartType.RADAR)

    # Get the metric
    if metric_index >= len(result.metrics):
        metric_index = 0

    metric = result.metrics[metric_index]
    metric_name = metric.get('name', 'unknown')

    # Extract categories and subsets
    labels = []
    scores = []

    if 'categories' in metric and metric['categories']:
        for category in metric['categories']:
            if 'subsets' in category and category['subsets']:
                for subset in category['subsets']:
                    labels.append(subset.get('name', 'unknown'))
                    scores.append(subset.get('score', 0.0))

    # If no subsets, use the overall score
    if not labels:
        labels = [f"{metric_name} Score"]
        scores = [metric.get('score', 0.0)]

    # Create dataset
    dataset = chart.create_dataset(ChartType.RADAR)
    dataset.label = f"{result.model_name} - {metric_name}"
    dataset.data = scores

    # Style the dataset
    dataset.fill = True
    dataset.backgroundColor = "rgba(54, 162, 235, 0.2)"
    dataset.borderColor = "rgb(54, 162, 235)"
    dataset.pointBackgroundColor = "rgb(54, 162, 235)"
    dataset.pointBorderColor = "#fff"
    dataset.pointHoverBackgroundColor = "#fff"
    dataset.pointHoverBorderColor = "rgb(54, 162, 235)"
    dataset.borderWidth = 2

    chart.set_labels(labels)
    chart.add_dataset(dataset)

    # Configure chart
    chart.set_title(f"{result.model_name} on {result.dataset_pretty_name} - {metric_name}",
                   color="#333",
                   font=Font(size=18, weight='bold'))

    chart.set_legend(position=Position.TOP)

    # Configure radial scale
    radial_scale = RadialLinearScale(
        angleLines=AngleLine(
            display=True,
        ),
        suggestedMin=0,
        suggestedMax=1.0,
        pointLabels=PointLabel(
            font=Font(size=12),
            color="#666"
        )
    )

    chart.set_radial_scale(radial_scale)

    chart.set_responsive(True, True)
    chart.set_animation(duration=1000, easing=Easing.EASE_OUT_QUART)

    return chart.to_dict()


def generate_metric_comparison_chart(
    result: EvaluationResult
) -> Dict[str, Any]:
    """
    Generate a bar chart comparing different metrics for a single model-dataset pair.

    Args:
        result: Evaluation result for a specific model and dataset

    Returns:
        Chart.js configuration dictionary
    """
    chart = ChartJS(ChartType.BAR)

    # Extract metric names and scores
    labels = []
    scores = []

    for metric in result.metrics:
        labels.append(metric.get('name', 'unknown'))
        scores.append(metric.get('score', 0.0))

    # Create dataset
    dataset = chart.create_dataset(ChartType.BAR)
    dataset.label = "Metric Scores"
    dataset.data = scores

    # Set colors
    colors = []
    for score in scores:
        if score >= 0.8:
            colors.append("rgba(75, 192, 192, 0.7)")  # Green
        elif score >= 0.6:
            colors.append("rgba(255, 206, 86, 0.7)")  # Yellow
        else:
            colors.append("rgba(153, 102, 255, 0.7)")  # Purple

    dataset.backgroundColor = colors
    dataset.borderColor = [color.replace('0.7', '1.0') for color in colors]
    dataset.borderWidth = 2

    chart.set_labels(labels)
    chart.add_dataset(dataset)

    # Configure chart
    chart.set_title(f"{result.model_name} on {result.dataset_pretty_name} - Metric Comparison",
                   color="#333",
                   font=Font(size=18, weight='bold'))

    chart.set_legend(position=Position.TOP)

    # Configure scales
    y_scale = ScaleConfig(
        type=ScaleType.LINEAR,
        display=True,
        title=ScaleTitle(
            display=True,
            text='Score',
            color='#666',
            font=Font(size=14)
        ),
        min=0,
        max=1.0,
        grid=GridLine(
            display=True,
        )
    )

    x_scale = ScaleConfig(
        type=ScaleType.CATEGORY,
        display=True,
        grid=GridLine(
            display=False
        )
    )

    chart.set_scales(x_scale=x_scale, y_scale=y_scale)

    chart.set_responsive(True, True)
    chart.set_animation(duration=1000, easing=Easing.EASE_OUT_QUART)

    return chart.to_dict()


# =====================
# Main Function
# =====================

def main():
    parser = argparse.ArgumentParser(description='Generate Chart.js configurations from evaluation results')
    parser.add_argument('--data-dir', default='eval_result',
                       help='Directory containing evaluation results (default: eval_result)')
    parser.add_argument('--output-dir', default='chart_configs',
                       help='Output directory for chart configurations (default: chart_configs)')
    parser.add_argument('--chart-type', choices=['all', 'model_comparison', 'dataset_comparison',
                                                'category_radar', 'metric_comparison'],
                       default='all',
                       help='Type of charts to generate (default: all)')

    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Collect evaluation results
    print(f"Collecting evaluation results from {args.data_dir}...")
    results = collect_evaluation_results(args.data_dir)

    if not results:
        print("No evaluation results found!")
        return

    print(f"Loaded {len(results)} evaluation results")

    # Organize results
    by_model = organize_results_by_model(results)
    by_dataset = organize_results_by_dataset(results)

    print(f"Found {len(by_model)} models: {list(by_model.keys())}")
    print(f"Found {len(by_dataset)} datasets: {list(by_dataset.keys())}")

    # Generate charts based on type
    charts_generated = 0

    # 1. Model comparison charts (one per dataset)
    if args.chart_type in ['all', 'model_comparison']:
        print("\nGenerating model comparison charts...")
        for dataset_name, dataset_results in by_dataset.items():
            if len(dataset_results) > 1:  # Need at least 2 models to compare
                chart_config = generate_model_comparison_chart(dataset_name, dataset_results)

                # Save chart configuration
                filename = f"model_comparison_{dataset_name}.json"
                filepath = os.path.join(args.output_dir, filename)

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(chart_config, f, indent=2, ensure_ascii=False)

                print(f"  Saved: {filename}")
                charts_generated += 1

    # 2. Dataset comparison charts (one per model)
    if args.chart_type in ['all', 'dataset_comparison']:
        print("\nGenerating dataset comparison charts...")
        for model_name, model_results in by_model.items():
            if len(model_results) > 1:  # Need at least 2 datasets
                chart_config = generate_dataset_comparison_chart(model_name, model_results)

                # Save chart configuration
                filename = f"dataset_comparison_{model_name}.json"
                filepath = os.path.join(args.output_dir, filename)

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(chart_config, f, indent=2, ensure_ascii=False)

                print(f"  Saved: {filename}")
                charts_generated += 1

    # 3. Category radar charts (one per model-dataset pair with subsets)
    if args.chart_type in ['all', 'category_radar']:
        print("\nGenerating category radar charts...")
        for result in results:
            # Check if this result has subsets
            has_subsets = False
            for metric in result.metrics:
                if 'categories' in metric and metric['categories']:
                    for category in metric['categories']:
                        if 'subsets' in category and category['subsets']:
                            has_subsets = True
                            break
                if has_subsets:
                    break

            if has_subsets:
                chart_config = generate_category_radar_chart(result)

                # Save chart configuration
                filename = f"category_radar_{result.model_name}_{result.dataset_name}.json"
                filepath = os.path.join(args.output_dir, filename)

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(chart_config, f, indent=2, ensure_ascii=False)

                print(f"  Saved: {filename}")
                charts_generated += 1

    # 4. Metric comparison charts (one per model-dataset pair with multiple metrics)
    if args.chart_type in ['all', 'metric_comparison']:
        print("\nGenerating metric comparison charts...")
        for result in results:
            if len(result.metrics) > 1:  # Need at least 2 metrics
                chart_config = generate_metric_comparison_chart(result)

                # Save chart configuration
                filename = f"metric_comparison_{result.model_name}_{result.dataset_name}.json"
                filepath = os.path.join(args.output_dir, filename)

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(chart_config, f, indent=2, ensure_ascii=False)

                print(f"  Saved: {filename}")
                charts_generated += 1

    print(f"\nGenerated {charts_generated} chart configurations in {args.output_dir}/")

    # Generate an index file with all chart configurations
    index_file = os.path.join(args.output_dir, "index.json")
    index_data = {
        "charts_generated": charts_generated,
        "models": list(by_model.keys()),
        "datasets": list(by_dataset.keys()),
        "chart_files": []
    }

    # List all generated chart files
    chart_files = glob.glob(os.path.join(args.output_dir, "*.json"))
    for chart_file in chart_files:
        if os.path.basename(chart_file) != "index.json":
            index_data["chart_files"].append(os.path.basename(chart_file))

    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)

    print(f"Index file created: {index_file}")


if __name__ == "__main__":
    main()