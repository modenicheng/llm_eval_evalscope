#!/usr/bin/env python3
"""
Merge specific evaluation dataset results into Chart.js compatible JSON files.

This script reads evaluation result JSON files for specific datasets,
extracts scores for each model across all subsets/categories, and creates
consolidated JSON files suitable for Chart.js visualizations.

Usage:
    python merge_specific_datasets.py --datasets multi_if math_500 general_qa
    python merge_specific_datasets.py --datasets chinese_simpleqa --output-prefix custom_

Output format:
{
  "type": "bar",
  "data": {
    "labels": ["subset1", "subset2", ...],
    "datasets": [
      {
        "label": "model1",
        "data": [score1, score2, ...],
        "backgroundColor": "#FF638422",
        "borderColor": "#FF6384FF",
        "borderWidth": 2,
        "hoverBackgroundColor": "#FF6384FF",
        "hoverBorderColor": "#FF6384FF",
        "hoverBorderWidth": 3
      },
      ...
    ]
  },
  "options": {
    "responsive": true,
    "maintainAspectRatio": false,
    "aspectRatio": 2.0,
    "animation": {
      "duration": 1000,
      "easing": "easeOutQuart"
    },
    "plugins": {
      "title": {
        "display": true,
        "text": "Model Performance on [Dataset] Subsets",
        "font": { "size": 18, "weight": "bold" }
      },
      "legend": {
        "display": true,
        "position": "top",
        "labels": { "font": { "size": 12 } }
      },
      "tooltip": {
        "enabled": true,
        "mode": "index",
        "intersect": false
      },
      "datalabels": {
        "display": true,
        "color": "#333",
        "font": { "size": 11, "weight": "bold" },
        "anchor": "end",
        "align": "top",
        "formatter": "function(value) { return value !== null ? value.toFixed(4) : 'N/A'; }",
        "backgroundColor": "rgba(255, 255, 255, 0.7)",
        "borderRadius": 3,
        "padding": 4
      }
    },
    "scales": {
      "x": {
        "type": "category",
        "display": true,
        "title": {
          "display": true,
          "text": "Subset",
          "color": "#666",
          "font": { "size": 14 }
        },
        "grid": { "display": false }
      },
      "y": {
        "type": "linear",
        "display": true,
        "beginAtZero": true,
        "max": 1.0,
        "title": {
          "display": true,
          "text": "Score",
          "color": "#666",
          "font": { "size": 14 }
        },
        "grid": { "display": true, "color": "rgba(0, 0, 0, 0.1)" },
        "ticks": {
          "callback": "function(value) { return value.toFixed(2); }"
        }
      }
    }
  }
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


def collect_dataset_results(
    data_dir: str,
    target_dataset: str
) -> Tuple[Dict[str, Dict[str, float]], List[str], str]:
    """
    Collect evaluation results for a specific dataset.

    Args:
        data_dir: Directory containing evaluation results
        target_dataset: Name of the dataset to collect (e.g., "multi_if", "math_500", "general_qa")

    Returns:
        Tuple of (results_dict, all_subsets, dataset_pretty_name)
        results_dict: model_name -> subset_name -> score
        all_subsets: List of all subset names in consistent order
        dataset_pretty_name: Pretty name of the dataset
    """
    # Pattern to find all JSON report files
    pattern = os.path.join(data_dir, "reports", "**", "*.json")
    json_files = glob.glob(pattern, recursive=True)

    print(f"Found {len(json_files)} JSON files")

    # Dictionary to store results: model -> subset -> score
    results = defaultdict(dict)
    all_subsets = set()
    dataset_pretty_name = target_dataset  # Default to target_dataset if not found

    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check if this is the target dataset
            dataset_name = data.get("dataset_name", "")
            if dataset_name != target_dataset:
                continue

            # Extract model name from file path
            # Path format: .../reports/{model_name}/{dataset}.json
            path_parts = file_path.split(os.sep)
            model_name = "unknown"
            for i, part in enumerate(path_parts):
                if part == "reports" and i + 1 < len(path_parts):
                    model_name = path_parts[i + 1]
                    break

            # Get dataset pretty name from first file
            if dataset_pretty_name == target_dataset:
                dataset_pretty_name = data.get("dataset_pretty_name", target_dataset)

            # Try to extract subset scores from metrics
            # Look for the first metric that has subset information
            subsets_found = False
            for metric in data.get("metrics", []):
                for category in metric.get("categories", []):
                    for subset in category.get("subsets", []):
                        subset_name = subset.get("name", "unknown")
                        subset_score = subset.get("score", 0.0)

                        # Store the result
                        results[model_name][subset_name] = subset_score
                        all_subsets.add(subset_name)
                        subsets_found = True

                # If we found subsets in this metric, break to avoid duplicates
                if subsets_found:
                    break

            # If no subsets found, use overall score as a single "overall" subset
            if not subsets_found:
                overall_score = data.get("score", 0.0)
                results[model_name]["overall"] = overall_score
                all_subsets.add("overall")

        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    return dict(results), sorted(list(all_subsets)), dataset_pretty_name


def create_chartjs_config(
    results: Dict[str, Dict[str, float]],
    all_subsets: List[str],
    dataset_pretty_name: str
) -> Dict[str, Any]:
    """
    Create Chart.js configuration from collected results.

    Args:
        results: Dictionary mapping model_name -> subset_name -> score
        all_subsets: List of all subset names
        dataset_pretty_name: Pretty name of the dataset for chart title

    Returns:
        Chart.js configuration dictionary
    """
    # Get color palette
    color_palette = get_color_palette()

    # Create Chart.js instance
    chart = ChartJS(ChartType.BAR)

    # Set labels (subsets)
    chart.set_labels(all_subsets)

    # Add each model as a dataset
    for i, (model_name, model_scores) in enumerate(results.items()):
        # Get colors for this model (cycle through palette if needed)
        color_idx = i % len(color_palette)
        border_color, background_color = color_palette[color_idx]

        # Create data array for this model (in same order as all_subsets)
        data = []
        for subset in all_subsets:
            score = model_scores.get(subset, None)
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
    # NOTE: Don't specify title color as requested
    chart.set_title(
        f"Model Performance on {dataset_pretty_name} Subsets",
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
            text='Subset',
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


def process_dataset(
    data_dir: str,
    dataset_name: str,
    output_prefix: str = "",
    pretty: bool = False
) -> bool:
    """
    Process a single dataset and generate JSON output.

    Args:
        data_dir: Directory containing evaluation results
        dataset_name: Name of the dataset to process
        output_prefix: Prefix for output filename
        pretty: Whether to generate pretty-printed JSON

    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"Processing dataset: {dataset_name}")
    print(f"{'='*60}")

    # Collect results for this dataset
    results, all_subsets, dataset_pretty_name = collect_dataset_results(data_dir, dataset_name)

    if not results:
        print(f"No evaluation results found for dataset: {dataset_name}")
        return False

    print(f"Found {len(results)} models:")
    for model in results.keys():
        print(f"  - {model}")

    print(f"\nFound {len(all_subsets)} subsets:")
    for subset in all_subsets:
        print(f"  - {subset}")

    # Create Chart.js configuration
    print("\nCreating Chart.js configuration...")
    chart_config = create_chartjs_config(results, all_subsets, dataset_pretty_name)

    # Generate output filename
    output_filename = f"{output_prefix}{dataset_name}_merged.json"
    if pretty:
        output_filename = f"{output_prefix}{dataset_name}_merged_pretty.json"

    # Write output file
    output_dir = os.path.dirname(output_filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    indent = 2 if pretty else None
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(chart_config, f, indent=indent, ensure_ascii=False)

    print(f"\nSuccessfully created merged data file: {output_filename}")
    print(f"  - Dataset: {dataset_pretty_name}")
    print(f"  - Models: {len(results)}")
    print(f"  - Subsets: {len(all_subsets)}")
    print(f"  - Total data points: {len(results) * len(all_subsets)}")

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

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Merge specific evaluation datasets into Chart.js JSON files'
    )
    parser.add_argument(
        '--data-dir',
        default='eval_result',
        help='Directory containing evaluation results (default: eval_result)'
    )
    parser.add_argument(
        '--datasets',
        nargs='+',
        default=['multi_if', 'math_500', 'general_qa'],
        help='Datasets to process (default: multi_if math_500 general_qa)'
    )
    parser.add_argument(
        '--output-prefix',
        default='',
        help='Prefix for output filenames (default: empty)'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Generate pretty-printed JSON output'
    )
    parser.add_argument(
        '--all-datasets',
        action='store_true',
        help='Process all available datasets'
    )

    args = parser.parse_args()

    # If --all-datasets is specified, discover all available datasets
    datasets_to_process = args.datasets
    if args.all_datasets:
        print("Discovering all available datasets...")
        # Find all JSON files to discover datasets
        pattern = os.path.join(args.data_dir, "reports", "**", "*.json")
        json_files = glob.glob(pattern, recursive=True)

        all_datasets = set()
        for file_path in json_files[:100]:  # Check first 100 files
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                dataset_name = data.get("dataset_name", "")
                if dataset_name:
                    all_datasets.add(dataset_name)
            except:
                pass

        datasets_to_process = sorted(list(all_datasets))
        print(f"Found {len(datasets_to_process)} datasets: {datasets_to_process}")

    print(f"Processing {len(datasets_to_process)} datasets: {datasets_to_process}")

    successful = 0
    failed = 0

    for dataset_name in datasets_to_process:
        try:
            if process_dataset(args.data_dir, dataset_name, args.output_prefix, args.pretty):
                successful += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\nError processing dataset {dataset_name}: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"{'='*60}")

    if successful > 0:
        print("\nGenerated files:")
        for dataset_name in datasets_to_process:
            filename = f"{args.output_prefix}{dataset_name}_merged.json"
            if args.pretty:
                filename = f"{args.output_prefix}{dataset_name}_merged_pretty.json"
            print(f"  - {filename}")


if __name__ == "__main__":
    main()