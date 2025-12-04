#!/usr/bin/env python3
"""
Merge all evaluation result JSON files into a single Chart.js compatible JSON file.

This script reads all evaluation result JSON files from the reports directory,
extracts scores for each model across all datasets, and creates a consolidated
JSON file suitable for Chart.js visualizations.

Output format:
{
  "labels": ["dataset1", "dataset2", ...],
  "datasets": [
    {
      "label": "model1",
      "data": [score1, score2, ...],
      "backgroundColor": "#FF638433",
      "borderColor": "#FF6384FF",
      "borderWidth": 2
    },
    ...
  ]
}
"""

import json
import os
import glob
import argparse
import sys
from typing import Dict, List, Any, Tuple
from collections import defaultdict

# Import the chartjs_wrap module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from chartjs_wrap import ChartJS, ChartType, Color, Font, Position, TextAlign, Easing, ScaleType
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


def collect_all_results(data_dir: str = "eval_result") -> Dict[str, Dict[str, float]]:
    """
    Collect evaluation results from all JSON files.

    Args:
        data_dir: Directory containing evaluation results

    Returns:
        Dictionary mapping model_name -> dataset_name -> score
    """
    # Pattern to find all JSON report files
    pattern = os.path.join(data_dir, "reports", "**", "*.json")
    json_files = glob.glob(pattern, recursive=True)

    print(f"Found {len(json_files)} JSON files")

    # Dictionary to store results: model -> dataset -> score
    results = defaultdict(dict)
    all_datasets = set()

    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract model name from file path
            # Path format: .../reports/{model_name}/{dataset}.json
            path_parts = file_path.split(os.sep)
            model_name = "unknown"
            for i, part in enumerate(path_parts):
                if part == "reports" and i + 1 < len(path_parts):
                    model_name = path_parts[i + 1]
                    break

            dataset_name = data.get("dataset_name", "unknown")
            score = data.get("score", 0.0)

            # Store the result
            results[model_name][dataset_name] = score
            all_datasets.add(dataset_name)

        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    return dict(results), sorted(list(all_datasets))


def create_chartjs_config(
    results: Dict[str, Dict[str, float]],
    all_datasets: List[str]
) -> Dict[str, Any]:
    """
    Create Chart.js configuration from collected results.

    Args:
        results: Dictionary mapping model_name -> dataset_name -> score
        all_datasets: List of all dataset names

    Returns:
        Chart.js configuration dictionary
    """
    # Get color palette
    color_palette = get_color_palette()

    # Create Chart.js instance
    chart = ChartJS(ChartType.BAR)

    # Set labels (datasets)
    chart.set_labels(all_datasets)

    # Add each model as a dataset
    for i, (model_name, model_scores) in enumerate(results.items()):
        # Get colors for this model (cycle through palette if needed)
        color_idx = i % len(color_palette)
        border_color, background_color = color_palette[color_idx]

        # Create data array for this model (in same order as all_datasets)
        data = []
        for dataset in all_datasets:
            score = model_scores.get(dataset, None)
            data.append(score)

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
        "Model Performance Across Datasets",
        color="#666",
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
        title=ScaleTitle(
            display=True,
            text='Dataset',
            color='#666',
            font=Font(size=14)
        ),
        grid=GridLine(
            display=False
        )
    )

    chart.set_scales(x_scale=x_scale, y_scale=y_scale)

    # Add ticks callback for y-axis
    if 'y' in chart.scales:
        chart.scales['y']['ticks'] = {
            "callback": "function(value) { return value.toFixed(4); }",
            "display": True
        }

    chart.set_responsive(True, True)
    chart.set_animation(duration=1000, easing=Easing.EASE_OUT_QUART)

    # Get the chart configuration
    chart_config = chart.to_dict()

    # Ensure options exist
    chart_config.setdefault('options', {})

    # Set aspect ratio to control height (width:height = 2:1, so height won't be too tall)
    chart_config['options']['aspectRatio'] = 2.0
    # Override maintainAspectRatio to use our aspect ratio
    chart_config['options']['maintainAspectRatio'] = False

    # Ensure plugins section exists in options
    chart_config['options'].setdefault('plugins', {})

    # Add data labels plugin configuration to show 4-digit precision values on bars
    # Merge with existing plugins configuration if any
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

    return chart_config


def main():
    parser = argparse.ArgumentParser(
        description='Merge evaluation results into a single Chart.js JSON file'
    )
    parser.add_argument(
        '--data-dir',
        default='eval_result',
        help='Directory containing evaluation results (default: eval_result)'
    )
    parser.add_argument(
        '--output',
        default='merged_evaluation_data.json',
        help='Output JSON file path (default: merged_evaluation_data.json)'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Generate pretty-printed JSON output'
    )

    args = parser.parse_args()

    # Collect all results
    print(f"Collecting evaluation results from {args.data_dir}...")
    results, all_datasets = collect_all_results(args.data_dir)

    if not results:
        print("No evaluation results found!")
        return

    print(f"Found {len(results)} models:")
    for model in results.keys():
        print(f"  - {model}")

    print(f"\nFound {len(all_datasets)} datasets:")
    for dataset in all_datasets:
        print(f"  - {dataset}")

    # Create Chart.js configuration
    print("\nCreating Chart.js configuration...")
    chart_config = create_chartjs_config(results, all_datasets)

    # Write output file
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    indent = 2 if args.pretty else None
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(chart_config, f, indent=indent, ensure_ascii=False)

    print(f"\nSuccessfully created merged data file: {args.output}")
    print(f"  - Models: {len(results)}")
    print(f"  - Datasets: {len(all_datasets)}")
    print(f"  - Total data points: {len(results) * len(all_datasets)}")

    # Print sample of the output structure
    print("\nSample of output structure:")
    print(json.dumps({
        "type": chart_config["type"],
        "data": {
            "labels": chart_config["data"]["labels"][:3] + ["..."],
            "datasets_count": len(chart_config["data"]["datasets"])
        },
        "first_dataset_sample": {
            "label": chart_config["data"]["datasets"][0]["label"] if chart_config["data"]["datasets"] else None,
            "data_first_3": chart_config["data"]["datasets"][0]["data"][:3] if chart_config["data"]["datasets"] else None,
            "backgroundColor": chart_config["data"]["datasets"][0]["backgroundColor"] if chart_config["data"]["datasets"] else None,
            "borderColor": chart_config["data"]["datasets"][0]["borderColor"] if chart_config["data"]["datasets"] else None
        }
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()