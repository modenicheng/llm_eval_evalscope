#!/usr/bin/env python3
"""
Markdown Report Generator for LLM Evaluation Results

This script generates a markdown report with dynamically loaded Chart.js visualizations
from the generated chart configurations.

Usage:
    python generate_markdown_report.py [--chart-dir CHART_DIR] [--output OUTPUT_MD]

Output:
    A markdown file with embedded HTML/JavaScript for interactive charts.
"""

import json
import os
import glob
import argparse
from typing import List, Dict, Any
import sys


def load_index(chart_dir: str) -> Dict[str, Any]:
    """Load the index.json file from chart directory."""
    index_path = os.path.join(chart_dir, "index.json")
    if not os.path.exists(index_path):
        return {"charts_generated": 0, "models": [], "datasets": [], "chart_files": []}

    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_markdown_report(chart_dir: str, output_file: str) -> None:
    """
    Generate a markdown report with embedded charts.

    Args:
        chart_dir: Directory containing chart JSON configurations
        output_file: Path to output markdown file
    """

    # Load index data
    index_data = load_index(chart_dir)
    chart_files = index_data.get("chart_files", [])
    models = index_data.get("models", [])
    datasets = index_data.get("datasets", [])

    # Group chart files by type
    model_comparison_charts = [f for f in chart_files if f.startswith("model_comparison_")]
    dataset_comparison_charts = [f for f in chart_files if f.startswith("dataset_comparison_")]
    category_radar_charts = [f for f in chart_files if f.startswith("category_radar_")]
    metric_comparison_charts = [f for f in chart_files if f.startswith("metric_comparison_")]

    # Create markdown content
    md_content = []

    # Header
    md_content.append("# LLM Evaluation Results Visualization Report")
    md_content.append(f"\n*Generated on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    md_content.append(f"\n**Total Charts Generated:** {index_data.get('charts_generated', 0)}")
    md_content.append(f"\n**Models Evaluated:** {len(models)}")
    md_content.append(f"\n**Datasets Used:** {len(datasets)}")

    # Table of Contents
    md_content.append("\n## Table of Contents")
    md_content.append("\n1. [Overview](#overview)")
    md_content.append("2. [Model Comparisons](#model-comparisons)")
    md_content.append("3. [Dataset Comparisons](#dataset-comparisons)")
    md_content.append("4. [Category Analysis](#category-analysis)")
    md_content.append("5. [Metric Analysis](#metric-analysis)")
    md_content.append("6. [How to Use](#how-to-use)")

    # Overview Section
    md_content.append("\n---\n")
    md_content.append("\n## Overview")
    md_content.append("\nThis report contains interactive visualizations of LLM evaluation results.")
    md_content.append("All charts are rendered using Chart.js and load data dynamically from JSON files.")

    # JavaScript and CSS setup
    md_content.append("""
<div id="chart-container">
    <!-- Charts will be loaded here dynamically -->
</div>

<style>
.chart-section {
    margin: 40px 0;
    padding: 20px;
    border: 1px solid #e1e4e8;
    border-radius: 6px;
    background-color: #f6f8fa;
}
.chart-title {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 15px;
    color: #24292e;
}
.chart-wrapper {
    position: relative;
    height: 400px;
    margin-bottom: 20px;
}
.chart-description {
    margin-top: 10px;
    color: #586069;
    font-size: 14px;
}
.nav-buttons {
    display: flex;
    gap: 10px;
    margin: 20px 0;
    flex-wrap: wrap;
}
.nav-button {
    padding: 8px 16px;
    background-color: #2ea44f;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
}
.nav-button:hover {
    background-color: #2c974b;
}
.loading {
    text-align: center;
    padding: 40px;
    color: #586069;
}
.error {
    color: #cb2431;
    padding: 10px;
    background-color: #ffeef0;
    border-radius: 6px;
}
</style>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
// Global chart instances
let chartInstances = {};

// Load and render a chart
async function loadChart(chartFile, canvasId) {
    try {
        // Show loading
        const container = document.getElementById(canvasId).parentElement;
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading';
        loadingDiv.textContent = 'Loading chart...';
        container.appendChild(loadingDiv);

        // Load chart configuration
        const response = await fetch(chartFile);
        if (!response.ok) {
            throw new Error(`Failed to load ${chartFile}: ${response.status}`);
        }

        const config = await response.json();

        // Remove loading indicator
        container.removeChild(loadingDiv);

        // Get canvas context
        const ctx = document.getElementById(canvasId).getContext('2d');

        // Destroy existing chart if it exists
        if (chartInstances[canvasId]) {
            chartInstances[canvasId].destroy();
        }

        // Create new chart
        chartInstances[canvasId] = new Chart(ctx, config);

    } catch (error) {
        console.error('Error loading chart:', error);
        const container = document.getElementById(canvasId).parentElement;
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error';
        errorDiv.textContent = `Error loading chart: ${error.message}`;
        container.appendChild(errorDiv);
    }
}

// Initialize all charts on page load
document.addEventListener('DOMContentLoaded', function() {
    // We'll load charts when sections become visible
    console.log('Chart loader ready. Charts will load when needed.');
});
</script>
""")

    # Model Comparisons Section
    md_content.append("\n---\n")
    md_content.append("\n## Model Comparisons")
    md_content.append("\nCompare performance of different models on the same dataset.")

    for chart_file in sorted(model_comparison_charts):
        # Extract dataset name from filename
        dataset_name = chart_file.replace("model_comparison_", "").replace(".json", "")

        # Create unique ID for this chart
        chart_id = f"model_comp_{dataset_name}"
        chart_path = f"{chart_dir}/{chart_file}"

        md_content.append(f"""
<div class="chart-section">
    <div class="chart-title">Model Comparison: {dataset_name}</div>
    <div class="chart-wrapper">
        <canvas id="{chart_id}"></canvas>
    </div>
    <div class="chart-description">
        This chart compares all evaluated models on the {dataset_name} dataset.
        Higher scores indicate better performance.
    </div>
    <button class="nav-button" onclick="loadChart('{chart_path}', '{chart_id}')">
        Load Chart
    </button>
</div>
""")

    # Dataset Comparisons Section
    md_content.append("\n---\n")
    md_content.append("\n## Dataset Comparisons")
    md_content.append("\nCompare a model's performance across different datasets.")

    for chart_file in sorted(dataset_comparison_charts):
        # Extract model name from filename
        model_name = chart_file.replace("dataset_comparison_", "").replace(".json", "")

        # Create unique ID for this chart
        chart_id = f"dataset_comp_{model_name.replace('-', '_')}"
        chart_path = f"{chart_dir}/{chart_file}"

        md_content.append(f"""
<div class="chart-section">
    <div class="chart-title">Dataset Comparison: {model_name}</div>
    <div class="chart-wrapper">
        <canvas id="{chart_id}"></canvas>
    </div>
    <div class="chart-description">
        This chart shows how {model_name} performs across all evaluated datasets.
    </div>
    <button class="nav-button" onclick="loadChart('{chart_path}', '{chart_id}')">
        Load Chart
    </button>
</div>
""")

    # Category Analysis Section
    md_content.append("\n---\n")
    md_content.append("\n## Category Analysis")
    md_content.append("\nDetailed breakdown of performance across categories within datasets.")

    # Group radar charts by dataset
    radar_by_dataset = {}
    for chart_file in sorted(category_radar_charts):
        # Extract model and dataset from filename
        # Format: category_radar_{model}_{dataset}.json
        base_name = chart_file.replace("category_radar_", "").replace(".json", "")
        parts = base_name.split("_", 1)
        if len(parts) == 2:
            model_name, dataset_name = parts
            if dataset_name not in radar_by_dataset:
                radar_by_dataset[dataset_name] = []
            radar_by_dataset[dataset_name].append((model_name, chart_file))

    for dataset_name, model_charts in radar_by_dataset.items():
        md_content.append(f"\n### {dataset_name}")
        md_content.append(f"\nPerformance breakdown across categories for {dataset_name}:")

        for model_name, chart_file in model_charts:
            chart_id = f"radar_{model_name.replace('-', '_')}_{dataset_name}"
            chart_path = f"{chart_dir}/{chart_file}"

            md_content.append(f"""
<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">{model_name} - {dataset_name} Categories</div>
    <div class="chart-wrapper">
        <canvas id="{chart_id}"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing {model_name}'s performance across different categories in {dataset_name}.
    </div>
    <button class="nav-button" onclick="loadChart('{chart_path}', '{chart_id}')">
        Load Chart
    </button>
</div>
""")

    # Metric Analysis Section
    md_content.append("\n---\n")
    md_content.append("\n## Metric Analysis")
    md_content.append("\nComparison of different evaluation metrics for the same model-dataset pair.")

    # Group metric charts by dataset
    metric_by_dataset = {}
    for chart_file in sorted(metric_comparison_charts):
        # Extract model and dataset from filename
        # Format: metric_comparison_{model}_{dataset}.json
        base_name = chart_file.replace("metric_comparison_", "").replace(".json", "")
        parts = base_name.split("_", 1)
        if len(parts) == 2:
            model_name, dataset_name = parts
            if dataset_name not in metric_by_dataset:
                metric_by_dataset[dataset_name] = []
            metric_by_dataset[dataset_name].append((model_name, chart_file))

    for dataset_name, model_charts in metric_by_dataset.items():
        md_content.append(f"\n### {dataset_name}")
        md_content.append(f"\nMetric comparison for {dataset_name}:")

        for model_name, chart_file in model_charts:
            chart_id = f"metric_{model_name.replace('-', '_')}_{dataset_name}"
            chart_path = f"{chart_dir}/{chart_file}"

            md_content.append(f"""
<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">{model_name} - {dataset_name} Metrics</div>
    <div class="chart-wrapper">
        <canvas id="{chart_id}"></canvas>
    </div>
    <div class="chart-description">
        Comparison of different evaluation metrics for {model_name} on {dataset_name}.
    </div>
    <button class="nav-button" onclick="loadChart('{chart_path}', '{chart_id}')">
        Load Chart
    </button>
</div>
""")

    # How to Use Section
    md_content.append("\n---\n")
    md_content.append("\n## How to Use")
    md_content.append("""
### Interactive Features
1. Click "Load Chart" buttons to render individual charts
2. Hover over chart elements to see detailed values
3. Charts are responsive and work on mobile devices

### Chart Types
- **Bar Charts**: Used for model and dataset comparisons
- **Radar Charts**: Used for category analysis
- **Color Coding**:
  - Green: Score ≥ 0.8 (Good)
  - Yellow: 0.6 ≤ Score < 0.8 (Average)
  - Red: Score < 0.6 (Needs Improvement)

### Technical Details
- Charts are rendered using [Chart.js](https://www.chartjs.org/)
- Data is loaded dynamically from JSON configuration files
- All charts are generated from evaluation result files

### Viewing Options
1. **In GitHub**: This markdown will display as static text with clickable buttons
2. **In VS Code/Preview**: Charts may render if HTML/JS is supported
3. **In a Web Browser**: Save as HTML or use a markdown viewer that supports JavaScript

### Regenerating Charts
To regenerate the charts with new data:
```bash
cd data_process
python generate_charts.py --output-dir visualization_data
python generate_markdown_report.py --chart-dir visualization_data --output report.md
```
""")

    # Footer
    md_content.append("\n---\n")
    md_content.append("\n*Report generated automatically by LLM Evaluation Visualization Tool*")

    # Write markdown file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_content))

    print(f"Markdown report generated: {output_file}")
    print(f"Total sections: {len(model_comparison_charts) + len(dataset_comparison_charts)}")
    print(f"Total charts available: {len(chart_files)}")


def main():
    parser = argparse.ArgumentParser(description='Generate markdown report with embedded charts')
    parser.add_argument('--chart-dir', default='visualization_data',
                       help='Directory containing chart JSON configurations (default: visualization_data)')
    parser.add_argument('--output', default='evaluation_report.md',
                       help='Output markdown file (default: evaluation_report.md)')

    args = parser.parse_args()

    # Check if chart directory exists
    if not os.path.exists(args.chart_dir):
        print(f"Error: Chart directory '{args.chart_dir}' not found.")
        print("Please generate charts first using generate_charts.py")
        sys.exit(1)

    # Generate report
    generate_markdown_report(args.chart_dir, args.output)


if __name__ == "__main__":
    main()