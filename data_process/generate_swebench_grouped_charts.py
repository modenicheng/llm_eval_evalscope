#!/usr/bin/env python3
"""
Generate grouped Chart.js configurations for SWE-bench metrics by magnitude.

This script reads the swebench_detailed_metrics.json file and creates multiple
Chart.js configurations where metrics are grouped by their magnitude:
- Group 1: Rates and percentages (0-1 range)
- Group 2: Small integer counts (0-100 range)
- Group 3: Large integer counts (100+ range)
- Group 4: Zero-value metrics (optional, can be hidden or grouped)

Zero-value metrics are either hidden or grouped into a single label.

Usage:
    python generate_swebench_grouped_charts.py
    python generate_swebench_grouped_charts.py --input swebench_detailed_metrics.json --output swebench_grouped_charts.json --pretty
"""

import json
import os
import argparse
import sys
from typing import Dict, List, Any, Tuple, Set
from collections import defaultdict

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


def categorize_metrics_by_magnitude(
    model_metrics: Dict[str, Dict[str, Any]],
    all_metric_names: List[str],
    all_model_names: List[str],
    include_zero_metrics: bool = False
) -> Dict[str, List[str]]:
    """Categorize metrics into groups based on their magnitude.

    Groups:
    - rates: 0-1 range (acc_std, avg_acc, completed_rate, resolved_rate)
    - small_counts: 0-100 range (error_samples, test_stats.*.failure/success except pass_to_pass.success)
    - large_counts: 100+ range (pass_to_pass.success)
    - zero_metrics: all values are zero (optional, can be excluded)

    Args:
        model_metrics: Dictionary mapping model_name -> {metric_name -> value}
        all_metric_names: List of all metric names
        all_model_names: List of all model names
        include_zero_metrics: Whether to include zero-value metrics in a separate group

    Returns:
        Dictionary mapping group_name -> list of metric names in that group
    """
    # Initialize groups
    groups = {
        "rates": [],        # 0-1 range
        "small_counts": [], # 0-100 range
        "large_counts": [], # 100+ range
        "zero_metrics": []  # All values zero (if include_zero_metrics is True)
    }

    # Helper function to check if all values for a metric are zero
    def all_values_zero(metric_name: str) -> bool:
        for model_name in all_model_names:
            value = model_metrics[model_name].get(metric_name)
            if value is not None and value != 0:
                return False
        return True

    # Helper function to get typical max value for a metric
    def get_max_value(metric_name: str) -> float:
        max_val = 0
        for model_name in all_model_names:
            value = model_metrics[model_name].get(metric_name)
            if value is not None:
                max_val = max(max_val, abs(float(value)))
        return max_val

    # Predefined rate metrics
    rate_metrics = {
        'acc_std', 'avg_acc', 'completed_rate', 'resolved_rate',
        'patch_stats.patch_is_none_rate', 'patch_stats.patch_exists_rate',
        'patch_stats.patch_successfully_applied_rate'
    }

    # Patch count metrics that should be shown even if all zero
    patch_count_metrics = {
        'patch_stats.patch_is_none_count',
        'patch_stats.patch_exists_count',
        'patch_stats.patch_successfully_applied_count'
    }

    for metric_name in all_metric_names:
        # First, handle special metric categories that should always be shown
        # 1. Patch count metrics go to small_counts group (counts are 0-100 range)
        if metric_name in patch_count_metrics:
            groups["small_counts"].append(metric_name)
            continue

        # 2. Rate metrics go to rates group (0-1 range)
        if metric_name in rate_metrics:
            groups["rates"].append(metric_name)
            continue

        # Check if all values are zero for this metric
        is_all_zero = all_values_zero(metric_name)
        if is_all_zero:
            if include_zero_metrics:
                groups["zero_metrics"].append(metric_name)
            continue  # Skip zero metrics if not including them

        # For remaining metrics, classify by magnitude
        max_val = get_max_value(metric_name)

        # Check for large counts (pass_to_pass.success typically has large values)
        if metric_name == "test_stats.pass_to_pass.success" or max_val >= 100:
            groups["large_counts"].append(metric_name)
        elif max_val <= 100:
            groups["small_counts"].append(metric_name)
        else:
            # Default to small counts
            groups["small_counts"].append(metric_name)

    # Filter out empty groups
    return {group: metrics for group, metrics in groups.items() if metrics}


def create_display_name(metric_name: str) -> str:
    """Create a user-friendly display name for a metric."""
    if metric_name.startswith('test_stats.'):
        parts = metric_name.split('.')
        if len(parts) >= 3:
            # Format: test_type.result_type (e.g., fail_to_pass.success)
            display_name = f"{parts[1]}.{parts[2]}"
        else:
            display_name = metric_name
    elif metric_name.startswith('patch_stats.'):
        parts = metric_name.split('.')
        if len(parts) >= 2:
            # Format: patch_stat_name (e.g., patch_is_none_rate)
            # Convert snake_case to Title Case with spaces
            stat_name = parts[1]
            # Replace underscores with spaces and capitalize each word
            display_name = ' '.join(word.capitalize() for word in stat_name.split('_'))
            # Special handling for common terms
            display_name = display_name.replace('Is None', 'Is None')
            display_name = display_name.replace('Successfully Applied', 'Successfully Applied')
        else:
            display_name = metric_name
    else:
        display_name = metric_name

    # Add descriptions for certain metrics
    descriptions = {
        'acc_std': 'Accuracy Std Dev',
        'avg_acc': 'Average Accuracy',
        'completed_rate': 'Completion Rate',
        'resolved_rate': 'Resolution Rate',
        'error_samples': 'Error Samples',
        'total_samples': 'Total Samples',
        'patch_stats.patch_is_none_count': 'Patch Is None Count',
        'patch_stats.patch_is_none_rate': 'Patch Is None Rate',
        'patch_stats.patch_exists_count': 'Patch Exists Count',
        'patch_stats.patch_exists_rate': 'Patch Exists Rate',
        'patch_stats.patch_successfully_applied_count': 'Patch Successfully Applied Count',
        'patch_stats.patch_successfully_applied_rate': 'Patch Successfully Applied Rate',
    }

    return descriptions.get(metric_name, display_name)


def create_grouped_chart(
    group_name: str,
    metric_names: List[str],
    model_metrics: Dict[str, Dict[str, Any]],
    all_model_names: List[str],
    color_palette: List[Tuple[str, str]]
) -> Dict[str, Any]:
    """Create a Chart.js configuration for a group of metrics.

    Args:
        group_name: Name of the group (e.g., "rates", "small_counts")
        metric_names: List of metric names in this group
        model_metrics: Dictionary mapping model_name -> {metric_name -> value}
        all_model_names: List of all model names
        color_palette: List of (border_color, background_color) pairs

    Returns:
        Chart.js configuration dictionary
    """
    # Create chart
    chart = ChartJS(ChartType.BAR)

    # Set labels (metric names with display names)
    display_labels = [create_display_name(name) for name in metric_names]
    chart.set_labels(display_labels)

    # Add each model as a dataset
    for i, model_name in enumerate(all_model_names):
        # Get colors for this model (cycle through palette if needed)
        color_idx = i % len(color_palette)
        border_color, background_color = color_palette[color_idx]

        # Create data array for this model (in same order as metric_names)
        data = []
        for metric_name in metric_names:
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

    # Determine appropriate Y-axis range based on group type
    y_min = 0
    y_max = None

    if group_name == "rates":
        y_max = 1.0
        y_axis_title = "Rate / Score"
    elif group_name == "small_counts":
        # Auto-scale for small counts
        y_axis_title = "Count"
    elif group_name == "large_counts":
        # Auto-scale for large counts
        y_axis_title = "Count"
    elif group_name == "zero_metrics":
        # For zero metrics, use a small range
        y_max = 1.0
        y_axis_title = "Count"

    # Configure chart title based on group
    group_titles = {
        "rates": "Rates and Scores (0-1 range)",
        "small_counts": "Small Counts (0-100 range)",
        "large_counts": "Large Counts (100+ range)",
        "zero_metrics": "Zero-Value Metrics"
    }

    title_text = f"SWE-bench: {group_titles.get(group_name, group_name)}"

    # Configure chart options
    chart.set_title(
        title_text,
        font=Font(size=18, weight='bold')
    )

    chart.set_legend(
        display=True,
        position=Position.TOP,
        labels={"font": Font(size=12).to_dict()}
    )

    # Configure scales
    y_scale = ScaleConfig(
        type=ScaleType.LINEAR,
        display=True,
        title=ScaleTitle(
            display=True,
            text=y_axis_title,
            color='#666',
            font=Font(size=14)
        ),
        min=y_min,
        max=y_max,  # None means auto-scale
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

    # Set aspect ratio based on number of metrics
    num_metrics = len(metric_names)
    if num_metrics <= 5:
        aspect_ratio = 1.5
    elif num_metrics <= 10:
        aspect_ratio = 2.0
    else:
        aspect_ratio = 2.5

    chart_config['options']['aspectRatio'] = aspect_ratio
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
    # For zero metrics group, we might want to show "0" labels
    if group_name == "zero_metrics":
        chart_config['options']['plugins']['datalabels'] = {
            "display": True,
            "font": {
                "size": 11,
                "weight": "bold"
            },
            "anchor": "end",
            "align": "top",
            "formatter": "function(value) { return value !== null ? value.toFixed(0) : 'N/A'; }",
            "backgroundColor": "rgba(255, 255, 255, 0.7)",
            "borderRadius": 3,
            "padding": 4
        }
    else:
        # For other groups, decide based on number of bars
        total_bars = len(all_model_names) * len(metric_names)
        if total_bars <= 30:  # Reasonable number to show labels
            chart_config['options']['plugins']['datalabels'] = {
                "display": True,
                "font": {
                    "size": 11,
                    "weight": "bold"
                },
                "anchor": "end",
                "align": "top",
                "formatter": "function(value) { return value !== null ? value.toFixed(4) : 'N/A'; }",
                "backgroundColor": "rgba(255, 255, 255, 0.7)",
                "borderRadius": 3,
                "padding": 4
            }
        else:
            chart_config['options']['plugins']['datalabels'] = {
                "display": False  # Too many bars
            }

    return chart_config


def create_zero_metrics_summary_chart(
    zero_metric_names: List[str],
    all_model_names: List[str],
    color_palette: List[Tuple[str, str]]
) -> Dict[str, Any]:
    """Create a special chart showing that all zero-value metrics are zero.

    Instead of showing each zero metric separately, we create a single bar
    labeled "All Zero Metrics" with value 0 for all models.

    Args:
        zero_metric_names: List of metric names that are all zero
        all_model_names: List of all model names
        color_palette: List of (border_color, background_color) pairs

    Returns:
        Chart.js configuration dictionary
    """
    chart = ChartJS(ChartType.BAR)

    # Single label for all zero metrics
    chart.set_labels(["All Zero Metrics"])

    # Add each model as a dataset with value 0
    for i, model_name in enumerate(all_model_names):
        color_idx = i % len(color_palette)
        border_color, background_color = color_palette[color_idx]

        dataset = chart.create_dataset(ChartType.BAR)
        dataset.label = model_name
        dataset.data = [0]
        dataset.backgroundColor = background_color
        dataset.borderColor = border_color
        dataset.borderWidth = 2
        dataset.hoverBackgroundColor = border_color
        dataset.hoverBorderColor = border_color
        dataset.hoverBorderWidth = 3

        chart.add_dataset(dataset)

    # Configure chart
    chart.set_title(
        "SWE-bench: Zero-Value Metrics Summary",
        font=Font(size=18, weight='bold')
    )

    chart.set_legend(
        display=True,
        position=Position.TOP,
        labels={"font": Font(size=12).to_dict()}
    )

    # Configure scales
    y_scale = ScaleConfig(
        type=ScaleType.LINEAR,
        display=True,
        title=ScaleTitle(
            display=True,
            text='Value',
            color='#666',
            font=Font(size=14)
        ),
        min=-0.5,
        max=1.0,  # Small range to show the zero value clearly
        grid=GridLine(
            display=True,
        )
    )

    x_scale = ScaleConfig(
        type=ScaleType.CATEGORY,
        display=True,
        title=ScaleTitle(
            display=True,
            text='Metrics',
            color='#666',
            font=Font(size=14)
        ),
        grid=GridLine(
            display=False
        )
    )

    chart.set_scales(x_scale=x_scale, y_scale=y_scale)

    chart.set_responsive(True, True)
    chart.set_animation(duration=1000, easing=Easing.EASE_OUT_QUART)

    # Get chart configuration
    chart_config = chart.to_dict()
    chart_config.setdefault('options', {})
    chart_config['options']['aspectRatio'] = 1.0
    chart_config['options']['maintainAspectRatio'] = False

    # Add plugins
    chart_config['options'].setdefault('plugins', {})

    # Tooltip showing which metrics are zero
    zero_metric_list = ", ".join([create_display_name(name) for name in zero_metric_names])
    chart_config['options']['plugins']['tooltip'] = {
        "enabled": True,
        "mode": "index",
        "intersect": False,
        "callbacks": {
            "label": "function(context) { return context.dataset.label + ': 0'; }",
            "title": f"function(tooltipItems) {{ return 'All zero metrics: {zero_metric_list}'; }}"
        }
    }

    # Data labels showing 0
    chart_config['options']['plugins']['datalabels'] = {
        "display": True,
        "font": {
            "size": 11,
            "weight": "bold"
        },
        "anchor": "end",
        "align": "top",
        "formatter": "function(value) { return '0'; }",
        "backgroundColor": "rgba(255, 255, 255, 0.7)",
        "borderRadius": 3,
        "padding": 4
    }

    return chart_config


def main():
    parser = argparse.ArgumentParser(
        description='Generate grouped Chart.js configurations for SWE-bench metrics by magnitude'
    )
    parser.add_argument(
        '--input',
        default='swebench_detailed_metrics.json',
        help='Input JSON file with detailed metrics (default: swebench_detailed_metrics.json)'
    )
    parser.add_argument(
        '--output-dir',
        default='swebench_grouped_charts',
        help='Output directory for individual chart JSON files (default: swebench_grouped_charts)'
    )
    parser.add_argument(
        '--output',
        default=None,
        help='Optional single output JSON file containing all charts (if not specified, generates individual files)'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Generate pretty-printed JSON output'
    )
    parser.add_argument(
        '--include-zero-metrics',
        action='store_true',
        help='Include zero-value metrics in output (as a separate group or summary)'
    )
    parser.add_argument(
        '--zero-metrics-summary',
        action='store_true',
        default=True,
        help='Show zero metrics as a single summary chart instead of individual metrics (default: True)'
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

    # Categorize metrics by magnitude
    print("\nCategorizing metrics by magnitude...")
    metric_groups = categorize_metrics_by_magnitude(
        model_metrics, all_metric_names, all_model_names, args.include_zero_metrics
    )

    print(f"Created {len(metric_groups)} metric groups:")
    for group_name, metrics in metric_groups.items():
        print(f"  - {group_name}: {len(metrics)} metrics")
        for metric in metrics[:5]:  # Show first 5 metrics
            print(f"    * {metric}")
        if len(metrics) > 5:
            print(f"    ... and {len(metrics) - 5} more")

    # Get color palette
    color_palette = get_color_palette()

    # Create chart configurations for each group
    print("\nCreating chart configurations for each group...")
    charts = {}

    for group_name, metrics in metric_groups.items():
        if group_name == "zero_metrics" and args.zero_metrics_summary and metrics:
            # Create special summary chart for zero metrics
            print(f"  Creating zero metrics summary chart for {len(metrics)} metrics...")
            chart_config = create_zero_metrics_summary_chart(
                metrics, all_model_names, color_palette
            )
            charts["zero_metrics_summary"] = chart_config
        elif metrics:  # Skip empty groups
            print(f"  Creating chart for {group_name} group ({len(metrics)} metrics)...")
            chart_config = create_grouped_chart(
                group_name, metrics, model_metrics, all_model_names, color_palette
            )
            charts[group_name] = chart_config

    # Determine output mode
    indent = 2 if args.pretty else None

    if args.output:
        # Mode 1: Single output file containing all charts
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(charts, f, indent=indent, ensure_ascii=False)

        print(f"\nSuccessfully created single charts file: {args.output}")
        print(f"  - Total chart groups: {len(charts)}")
        print(f"  - Groups included: {', '.join(sorted(charts.keys()))}")
    else:
        # Mode 2: Individual files for each chart group
        output_dir = args.output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        files_created = []
        for group_name, chart_config in charts.items():
            # Create filename for this group
            if group_name == "zero_metrics_summary":
                filename = "zero_metrics_summary.json"
            else:
                filename = f"{group_name}_chart.json"

            filepath = os.path.join(output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(chart_config, f, indent=indent, ensure_ascii=False)

            files_created.append(filename)
            print(f"  Created: {filename}")

        print(f"\nSuccessfully created {len(files_created)} chart files in directory: {output_dir}")
        print(f"  - Files created: {', '.join(sorted(files_created))}")

        # Create an index file listing all generated files
        index_file = os.path.join(output_dir, "index.json")
        index_data = {
            "charts_generated": len(files_created),
            "groups": list(charts.keys()),
            "files": files_created,
            "models": all_model_names,
            "total_metrics": len(all_metric_names)
        }

        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)

        print(f"  Index file created: {index_file}")

    # Print summary of each chart (common to both modes)
    print("\nChart group summaries:")
    for group_name, chart_config in charts.items():
        num_metrics = len(chart_config['data']['labels'])
        num_datasets = len(chart_config['data']['datasets'])
        print(f"  - {group_name}: {num_metrics} metrics × {num_datasets} models = {num_metrics * num_datasets} data points")

    # Print sample of the output structure (for single file mode only)
    if args.output:
        print("\nSample of output structure:")
        sample_keys = list(charts.keys())[:3] if len(charts) >= 3 else list(charts.keys())
        sample_data = {}
        for key in sample_keys:
            chart = charts[key]
            sample_data[key] = {
                "type": chart["type"],
                "labels": chart["data"]["labels"][:3] + ["..."] if chart["data"]["labels"] else [],
                "datasets_count": len(chart["data"]["datasets"]),
                "first_dataset_label": chart["data"]["datasets"][0]["label"] if chart["data"]["datasets"] else None
            }

        print(json.dumps(sample_data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()