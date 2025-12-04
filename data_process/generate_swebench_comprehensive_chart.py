#!/usr/bin/env python3
"""
Generate a comprehensive Chart.js configuration for all SWE-bench metrics.

This script reads the swebench_detailed_metrics.json file and creates a single
Chart.js configuration where:
- X-axis (labels): All metric names
- Datasets: Each model is a dataset, containing values for all metrics

Output format: A single Chart.js configuration with all models and metrics.

Usage:
    python generate_swebench_comprehensive_chart.py
    python generate_swebench_comprehensive_chart.py --input swebench_detailed_metrics.json --output swebench_comprehensive_chart.json --pretty
"""

import json
import os
import argparse
import sys
from typing import Dict, List, Any, Tuple

# Import the chartjs_wrap module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from chartjs_wrap import ChartJS, ChartType, Font, Position, TextAlign, Easing, ScaleType
from chartjs_wrap import BarDataset, LineDataset, RadarDataset, PieDataset, DoughnutDataset
from chartjs_wrap import TitleConfig, LegendConfig, TooltipConfig, ScaleConfig, ScaleTitle, GridLine
from chartjs_wrap import AnimationConfig, RadialLinearScale, AngleLine, PointLabel


def get_color_palette() -> List[Tuple[str, str]]:
    """Return a list of (border_color, background_color) pairs for models.

    Border color format: #RRGGBBFF (full opacity)
    Background color format: #RRGGBB22 or #RRGGBB33 (low opacity)
    """
    # Predefined color palette with distinct colors
    base_colors = [
        "#FF6384",  # Red
        "#36A2EB",  # Blue
        "#FFCE56",  # Yellow
        "#4BC0C0",  # Teal
        "#9966FF",  # Purple
        "#FF9F40",  # Orange
        "#C9CBCF",  # Gray
        "#7EB26D",  # Green
        "#E377C2",  # Pink
        "#1F77B4",  # Dark Blue
        "#FF7F0E",  # Dark Orange
        "#2CA02C",  # Dark Green
    ]

    palette = []
    for base in base_colors:
        # Remove # if present
        if base.startswith("#"):
            hex_code = base[1:]
        else:
            hex_code = base

        # Border color with full opacity (FF)
        border_color = f"#{hex_code}FF"

        # Background color with low opacity (22 or 33)
        # Alternate between 22 and 33 for variety
        if len(palette) % 2 == 0:
            background_color = f"#{hex_code}22"
        else:
            background_color = f"#{hex_code}33"

        palette.append((border_color, background_color))

    return palette


def load_metrics(input_file: str) -> Dict[str, Dict[str, Any]]:
    """Load metrics from JSON file.

    Args:
        input_file: Path to swebench_detailed_metrics.json

    Returns:
        Dictionary mapping model_name -> metrics_dict
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


def extract_all_metrics(models_data: Dict[str, Dict[str, Any]]) -> Tuple[Dict[str, Dict[str, Any]], List[str], List[str]]:
    """Extract all metrics from models data and reorganize.

    Args:
        models_data: Dictionary mapping model_name -> metrics_dict

    Returns:
        Tuple of (model_metrics, all_metric_names, all_model_names)
        model_metrics: Dictionary mapping model_name -> {metric_name -> value}
        all_metric_names: List of all metric names (sorted)
        all_model_names: List of all model names (sorted)
    """
    # First pass: collect all metric names
    all_metric_names_set = set()

    for model_name, metrics in models_data.items():
        # Add top-level metrics
        for key in metrics.keys():
            if key != 'test_stats' and key != 'samples' and key != 'patch_stats':
                all_metric_names_set.add(key)

        # Add test_stats sub-metrics
        test_stats = metrics.get('test_stats', {})
        for test_type, results in test_stats.items():
            if isinstance(results, dict):
                for result_type, count in results.items():
                    metric_name = f"test_stats.{test_type}.{result_type}"
                    all_metric_names_set.add(metric_name)

        # Add patch_stats sub-metrics
        patch_stats = metrics.get('patch_stats', {})
        for stat_name, stat_value in patch_stats.items():
            metric_name = f"patch_stats.{stat_name}"
            all_metric_names_set.add(metric_name)

    all_metric_names = sorted(all_metric_names_set)
    all_model_names = sorted(models_data.keys())

    # Second pass: build model_metrics dictionary
    model_metrics = {}
    for model_name in all_model_names:
        model_metrics[model_name] = {}
        metrics = models_data[model_name]

        for metric_name in all_metric_names:
            value = None

            if '.' in metric_name:
                # Nested metric (e.g., test_stats.fail_to_pass.success)
                parts = metric_name.split('.')
                current = metrics
                for part in parts:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        current = None
                        break
                value = current
            else:
                # Top-level metric
                value = metrics.get(metric_name)

            model_metrics[model_name][metric_name] = value

    return model_metrics, all_metric_names, all_model_names


def create_comprehensive_chart(
    model_metrics: Dict[str, Dict[str, Any]],
    all_metric_names: List[str],
    all_model_names: List[str],
    color_palette: List[Tuple[str, str]]
) -> Dict[str, Any]:
    """Create a comprehensive Chart.js configuration with all models and metrics.

    Args:
        model_metrics: Dictionary mapping model_name -> {metric_name -> value}
        all_metric_names: List of all metric names
        all_model_names: List of all model names
        color_palette: List of (border_color, background_color) pairs

    Returns:
        Chart.js configuration dictionary
    """
    # Create chart
    chart = ChartJS(ChartType.BAR)

    # Set labels (metric names)
    # Truncate long metric names for better display
    display_labels = []
    for metric_name in all_metric_names:
        # Create shorter display names for test_stats metrics
        if metric_name.startswith('test_stats.'):
            parts = metric_name.split('.')
            if len(parts) >= 3:
                # Format: test_type.result_type (e.g., fail_to_pass.success)
                display_name = f"{parts[1]}.{parts[2]}"
            else:
                display_name = metric_name
        else:
            display_name = metric_name

        display_labels.append(display_name)

    chart.set_labels(display_labels)

    # Add each model as a dataset
    for i, model_name in enumerate(all_model_names):
        # Get colors for this model (cycle through palette if needed)
        color_idx = i % len(color_palette)
        border_color, background_color = color_palette[color_idx]

        # Create data array for this model (in same order as all_metric_names)
        data = []
        for metric_name in all_metric_names:
            value = model_metrics[model_name].get(metric_name, None)
            data.append(value)

        # Create dataset configuration using chartjs_wrap
        dataset = chart.create_dataset(ChartType.BAR)
        dataset.label = model_name
        dataset.data = data
        dataset.backgroundColor = background_color
        dataset.borderColor = border_color
        dataset.borderWidth = 2
        dataset.hoverBackgroundColor = border_color  # Use border color on hover
        dataset.hoverBorderColor = border_color
        dataset.hoverBorderWidth = 3

        chart.add_dataset(dataset)

    # Configure chart options
    chart.set_title(
        "SWE-bench: Comprehensive Model Performance Comparison",
        font=Font(size=18, weight='bold')
    )

    chart.set_legend(
        display=True,
        position=Position.TOP,
        labels={"font": Font(size=12).to_dict()}
    )

    # Configure scales
    # Note: Since metrics have different scales (0-1 for rates, large numbers for counts),
    # we'll use a linear scale and let Chart.js auto-adjust
    y_scale = ScaleConfig(
        type=ScaleType.LINEAR,
        display=True,
        title=ScaleTitle(
            display=True,
            text='Value',
            color='#666',
            font=Font(size=14)
        ),
        min=0,  # Start from zero for better comparison
        grid=GridLine(
            display=True,
        )
    )

    x_scale = ScaleConfig(
        type=ScaleType.CATEGORY,
        display=True,
        title=ScaleTitle(
            display=True,
            text='Metric',
            color='#666',
            font=Font(size=14)
        ),
        grid=GridLine(
            display=False
        )
    )

    chart.set_scales(x_scale=x_scale, y_scale=y_scale)

    # Configure ticks for better readability
    if 'x' in chart.scales:
        chart.scales['x']['ticks'] = {
            "maxRotation": 45,  # Rotate labels for better readability
            "minRotation": 45
        }

    chart.set_responsive(True, True)
    chart.set_animation(duration=1000, easing=Easing.EASE_OUT_QUART)

    # Get the chart configuration
    chart_config = chart.to_dict()

    # Ensure options exist
    chart_config.setdefault('options', {})

    # Set aspect ratio to control height
    chart_config['options']['aspectRatio'] = 2.5  # Wider for more metrics
    chart_config['options']['maintainAspectRatio'] = False

    # Ensure plugins section exists in options
    chart_config['options'].setdefault('plugins', {})

    # Add tooltip configuration
    chart_config['options']['plugins']['tooltip'] = {
        "enabled": True,
        "mode": "index",
        "intersect": False,
        "callbacks": {
            "label": "function(context) { return context.dataset.label + ': ' + context.parsed.y; }",
            "title": "function(tooltipItems) { return 'Metric: ' + tooltipItems[0].label; }"
        }
    }

    # Add data labels plugin configuration
    # We'll disable data labels by default for this comprehensive chart
    # because there are too many bars (models × metrics)
    chart_config['options']['plugins']['datalabels'] = {
        "display": False  # Too many bars to show all values
    }

    return chart_config


def main():
    parser = argparse.ArgumentParser(
        description='Generate comprehensive Chart.js configuration for all SWE-bench metrics'
    )
    parser.add_argument(
        '--input',
        default='swebench_detailed_metrics.json',
        help='Input JSON file with detailed metrics (default: swebench_detailed_metrics.json)'
    )
    parser.add_argument(
        '--output',
        default='swebench_comprehensive_chart.json',
        help='Output JSON file path (default: swebench_comprehensive_chart.json)'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Generate pretty-printed JSON output'
    )
    parser.add_argument(
        '--include-samples',
        action='store_true',
        help='Include individual samples in metrics extraction (if available)'
    )

    args = parser.parse_args()

    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found!")
        print("Please run extract_swebench_metrics.py first to generate the metrics file.")
        return

    # Load metrics
    print(f"Loading metrics from {args.input}...")
    models_data = load_metrics(args.input)

    # Remove 'samples' from each model's data to reduce clutter (unless requested)
    if not args.include_samples:
        for model_name in models_data:
            models_data[model_name].pop('samples', None)

    print(f"Found {len(models_data)} models:")
    for model_name in models_data.keys():
        print(f"  - {model_name}")

    # Extract and reorganize all metrics
    print("\nExtracting and reorganizing metrics...")
    model_metrics, all_metric_names, all_model_names = extract_all_metrics(models_data)

    print(f"Found {len(all_metric_names)} metrics:")
    for metric_name in all_metric_names:
        print(f"  - {metric_name}")

    # Get color palette
    color_palette = get_color_palette()

    # Create comprehensive chart configuration
    print("\nCreating comprehensive chart configuration...")
    chart_config = create_comprehensive_chart(
        model_metrics, all_metric_names, all_model_names, color_palette
    )

    # Write output file
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    indent = 2 if args.pretty else None
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(chart_config, f, indent=indent, ensure_ascii=False)

    print(f"\nSuccessfully created comprehensive chart file: {args.output}")
    print(f"  - Total models: {len(all_model_names)}")
    print(f"  - Total metrics: {len(all_metric_names)}")
    print(f"  - Total data points: {len(all_model_names) * len(all_metric_names)}")

    # Print summary of the chart structure
    print("\nChart structure summary:")
    print(f"  - Chart type: {chart_config['type']}")
    print(f"  - X-axis labels (metrics): {len(chart_config['data']['labels'])}")
    print(f"  - Datasets (models): {len(chart_config['data']['datasets'])}")

    # Print sample of labels and first dataset
    print("\nSample of X-axis labels (first 5):")
    for i, label in enumerate(chart_config['data']['labels'][:5]):
        print(f"    {i+1}. {label}")
    if len(chart_config['data']['labels']) > 5:
        print(f"    ... and {len(chart_config['data']['labels']) - 5} more")

    print("\nSample of first dataset:")
    first_dataset = chart_config['data']['datasets'][0]
    print(f"    Model: {first_dataset['label']}")
    print(f"    Data points: {len(first_dataset['data'])}")
    print(f"    First 5 values: {first_dataset['data'][:5]}")

    # Print metric types and ranges
    print("\nMetric value ranges (sample):")
    sample_metrics = all_metric_names[:3] if len(all_metric_names) >= 3 else all_metric_names
    for metric_name in sample_metrics:
        values = [model_metrics[model][metric_name] for model in all_model_names
                 if model_metrics[model][metric_name] is not None]
        if values:
            min_val = min(values)
            max_val = max(values)
            print(f"    {metric_name}: {min_val:.4f} to {max_val:.4f}")


if __name__ == "__main__":
    main()