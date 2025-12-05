#!/usr/bin/env python3
"""
Generate a Chart.js configuration for SWE-bench rate metrics.

This script reads the swebench_rates.json file and creates a single
Chart.js configuration with:
- X-axis (labels): Four rate metrics (acc_rate, patch_successfully_applied_rate, fail_to_pass_rate, pass_to_pass_rate)
- Datasets: Each model is a dataset, containing values for all four metrics

Output format: A single Chart.js configuration with all models and the four rate metrics.

Usage:
    python generate_swebench_rates_chart.py
    python generate_swebench_rates_chart.py --input swebench_rates.json --output swebench_rates_chart.json --pretty
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


def load_rates(input_file: str) -> Dict[str, Dict[str, float]]:
    """Load rate metrics from JSON file.

    Args:
        input_file: Path to swebench_rates.json

    Returns:
        Dictionary mapping model_name -> rates_dict
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


def create_rates_chart(
    rates_data: Dict[str, Dict[str, float]],
    color_palette: List[Tuple[str, str]]
) -> Dict[str, Any]:
    """Create a Chart.js configuration for the four rate metrics.

    Args:
        rates_data: Dictionary mapping model_name -> rates_dict
        color_palette: List of (border_color, background_color) pairs

    Returns:
        Chart.js configuration dictionary
    """
    # Define the four metrics in order
    metric_names = [
        "acc_rate",
        "patch_successfully_applied_rate",
        "fail_to_pass_rate",
        "pass_to_pass_rate"
    ]

    # Create user-friendly labels
    metric_labels = [
        "Accuracy Rate",
        "Patch Successfully Applied Rate",
        "Fail-to-Pass Rate",
        "Pass-to-Pass Rate"
    ]

    # Get sorted model names
    model_names = sorted(rates_data.keys())

    # Create datasets for each model
    datasets = []
    for i, model_name in enumerate(model_names):
        model_rates = rates_data[model_name]

        # Get colors from palette (cycle if needed)
        border_color, background_color = color_palette[i % len(color_palette)]

        # Collect values for all four metrics
        values = []
        for metric in metric_names:
            value = model_rates.get(metric, 0.0)
            values.append(value)

        # Create dataset dictionary
        dataset = {
            "label": model_name,
            "data": values,
            "backgroundColor": background_color,
            "borderColor": border_color,
            "borderWidth": 2,
            "hoverBackgroundColor": border_color,
            "hoverBorderColor": border_color,
            "hoverBorderWidth": 3
        }
        datasets.append(dataset)

    # Build the complete chart configuration
    chart_config = {
        "type": "bar",
        "data": {
            "labels": metric_labels,
            "datasets": datasets
        },
        "options": {
            "responsive": True,
            "maintainAspectRatio": False,
            "animation": {
                "duration": 1000,
                "easing": "easeOutQuart"
            },
            "plugins": {
                "title": {
                    "display": True,
                    "text": "SWE-bench: Rate Metrics Comparison",
                    "font": {
                        "size": 18,
                        "weight": "bold"
                    }
                },
                "legend": {
                    "display": True,
                    "position": "top",
                    "labels": {
                        "font": {
                            "size": 12
                        }
                    }
                },
                "tooltip": {
                    "enabled": True,
                    "mode": "index",
                    "intersect": False,
                    "callbacks": {
                        "label": "function(context) { return context.dataset.label + ': ' + context.parsed.y; }",
                        "title": "function(tooltipItems) { return 'Metric: ' + tooltipItems[0].label; }"
                    }
                },
                "datalabels": {
                    "display": False  # Too many bars to show all values
                }
            },
            "scales": {
                "x": {
                    "type": "category",
                    "display": True,
                    "title": {
                        "display": True,
                        "text": "Metric",
                        "color": "#666",
                        "font": {
                            "size": 14
                        }
                    },
                    "grid": {
                        "display": False
                    },
                    "ticks": {
                        "maxRotation": 45,
                        "minRotation": 45
                    }
                },
                "y": {
                    "type": "linear",
                    "display": True,
                    "title": {
                        "display": True,
                        "text": "Rate",
                        "color": "#666",
                        "font": {
                            "size": 14
                        }
                    },
                    "min": 0,
                    "max": 1.0,
                    "grid": {
                        "display": True
                    }
                }
            },
            "aspectRatio": 2.0
        }
    }

    return chart_config


def main():
    parser = argparse.ArgumentParser(
        description='Generate Chart.js configuration for SWE-bench rate metrics'
    )
    parser.add_argument(
        '--input',
        default='swebench_rates.json',
        help='Input JSON file with rate metrics (default: swebench_rates.json)'
    )
    parser.add_argument(
        '--output',
        default='swebench_rates_chart.json',
        help='Output JSON file path (default: swebench_rates_chart.json)'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Generate pretty-printed JSON output'
    )

    args = parser.parse_args()

    # Load rate metrics
    print(f"Loading rate metrics from {args.input}...")
    rates_data = load_rates(args.input)

    print(f"Found {len(rates_data)} models:")
    for model_name in sorted(rates_data.keys()):
        print(f"  - {model_name}")

    # Get color palette
    color_palette = get_color_palette()

    # Create chart
    print("\nCreating chart configuration...")
    chart_config = create_rates_chart(rates_data, color_palette)

    # Write output file
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    indent = 2 if args.pretty else None
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(chart_config, f, indent=indent, ensure_ascii=False)

    print(f"\nSuccessfully created chart configuration: {args.output}")
    print(f"  - Metrics: 4 rate metrics")
    print(f"  - Models: {len(rates_data)}")

    # Print sample of the data
    print("\nSample data (first model):")
    first_model = sorted(rates_data.keys())[0]
    rates = rates_data[first_model]
    for metric, value in rates.items():
        print(f"  - {metric}: {value:.4f}")


if __name__ == "__main__":
    main()