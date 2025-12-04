#!/usr/bin/env python3
"""
HTML Report Generator for LLM Evaluation Results

This script generates an HTML report with embedded Chart.js visualizations
from the generated chart configurations.

Usage:
    python generate_html_report.py [--chart-dir CHART_DIR] [--output OUTPUT_HTML]

Output:
    A standalone HTML file with interactive charts.
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


def generate_html_report(chart_dir: str, output_file: str) -> None:
    """
    Generate an HTML report with embedded charts.

    Args:
        chart_dir: Directory containing chart JSON configurations
        output_file: Path to output HTML file
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

    # Create HTML content
    html_content = []

    # HTML header
    html_content.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Evaluation Results Visualization Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #24292e;
            background-color: #f6f8fa;
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            background-color: #2c3e50;
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
            margin-bottom: 20px;
        }

        .stats {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }

        .stat-card {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 8px;
            min-width: 150px;
        }

        .stat-value {
            font-size: 2em;
            font-weight: bold;
        }

        .stat-label {
            font-size: 0.9em;
            opacity: 0.8;
        }

        .toc {
            background-color: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .toc h2 {
            margin-bottom: 15px;
            color: #2c3e50;
        }

        .toc ul {
            list-style-type: none;
            column-count: 2;
        }

        .toc li {
            margin-bottom: 8px;
        }

        .toc a {
            color: #0366d6;
            text-decoration: none;
            padding: 5px 10px;
            border-radius: 4px;
            transition: background-color 0.2s;
        }

        .toc a:hover {
            background-color: #f1f8ff;
        }

        .section {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .section h2 {
            color: #2c3e50;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
            margin-bottom: 25px;
        }

        .chart-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
            gap: 25px;
            margin-top: 20px;
        }

        .chart-card {
            background-color: #f8f9fa;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            padding: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .chart-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        }

        .chart-title {
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #24292e;
        }

        .chart-wrapper {
            position: relative;
            height: 300px;
            margin-bottom: 15px;
        }

        .chart-description {
            color: #586069;
            font-size: 0.95em;
            margin-bottom: 15px;
            line-height: 1.5;
        }

        .chart-controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 10px;
        }

        .load-btn {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: background-color 0.2s;
        }

        .load-btn:hover {
            background-color: #45a049;
        }

        .load-btn:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }

        .status {
            font-size: 0.9em;
            padding: 5px 10px;
            border-radius: 4px;
        }

        .status.loading {
            background-color: #fff3cd;
            color: #856404;
        }

        .status.loaded {
            background-color: #d4edda;
            color: #155724;
        }

        .status.error {
            background-color: #f8d7da;
            color: #721c24;
        }

        footer {
            text-align: center;
            padding: 30px;
            color: #6a737d;
            font-size: 0.9em;
            border-top: 1px solid #e1e4e8;
            margin-top: 30px;
        }

        @media (max-width: 768px) {
            .chart-grid {
                grid-template-columns: 1fr;
            }

            .toc ul {
                column-count: 1;
            }

            .stats {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>LLM Evaluation Results Visualization Report</h1>
        <div class="subtitle">Interactive visualization of model performance across datasets and metrics</div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">""" + str(index_data.get('charts_generated', 0)) + """</div>
                <div class="stat-label">Charts Generated</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">""" + str(len(models)) + """</div>
                <div class="stat-label">Models Evaluated</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">""" + str(len(datasets)) + """</div>
                <div class="stat-label">Datasets Used</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">""" + str(len(chart_files)) + """</div>
                <div class="stat-label">Chart Files</div>
            </div>
        </div>
    </header>

    <div class="toc">
        <h2>Table of Contents</h2>
        <ul>
            <li><a href="#model-comparisons">Model Comparisons</a></li>
            <li><a href="#dataset-comparisons">Dataset Comparisons</a></li>
            <li><a href="#category-analysis">Category Analysis</a></li>
            <li><a href="#metric-analysis">Metric Analysis</a></li>
            <li><a href="#how-to-use">How to Use</a></li>
        </ul>
    </div>
""")

    # JavaScript for chart loading
    html_content.append("""
    <script>
        // Global chart instances and state
        const chartInstances = {};
        const chartStates = {};

        // Load and render a chart
        async function loadChart(chartFile, canvasId, btnId, statusId) {
            const button = document.getElementById(btnId);
            const status = document.getElementById(statusId);

            try {
                // Update UI state
                button.disabled = true;
                status.textContent = 'Loading...';
                status.className = 'status loading';

                // Load chart configuration
                const response = await fetch(chartFile);
                if (!response.ok) {
                    throw new Error(`Failed to load chart: ${response.status} ${response.statusText}`);
                }

                const config = await response.json();

                // Get canvas context
                const canvas = document.getElementById(canvasId);
                if (!canvas) {
                    throw new Error(`Canvas element not found: ${canvasId}`);
                }
                const ctx = canvas.getContext('2d');

                // Destroy existing chart if it exists
                if (chartInstances[canvasId]) {
                    chartInstances[canvasId].destroy();
                }

                // Create new chart
                chartInstances[canvasId] = new Chart(ctx, config);
                chartStates[canvasId] = 'loaded';

                // Update UI state
                status.textContent = 'Loaded ✓';
                status.className = 'status loaded';
                button.textContent = 'Reload Chart';
                button.disabled = false;

            } catch (error) {
                console.error('Error loading chart:', error);
                status.textContent = `Error: ${error.message}`;
                status.className = 'status error';
                button.disabled = false;
            }
        }

        // Load all charts in a section
        function loadAllCharts(sectionId) {
            const section = document.getElementById(sectionId);
            if (!section) return;

            const buttons = section.querySelectorAll('.load-btn');
            buttons.forEach(btn => {
                if (!btn.disabled) {
                    btn.click();
                }
            });
        }

        // Initialize tooltips
        document.addEventListener('DOMContentLoaded', function() {
            // Add any initialization code here
            console.log('LLM Evaluation Report loaded');
        });
    </script>
""")

    # Model Comparisons Section
    html_content.append(f"""
    <div class="section" id="model-comparisons">
        <h2>Model Comparisons</h2>
        <p>Compare performance of different models on the same dataset. Higher scores indicate better performance.</p>

        <div class="chart-controls" style="margin-bottom: 20px;">
            <button class="load-btn" onclick="loadAllCharts('model-comparisons')">Load All Model Charts</button>
        </div>

        <div class="chart-grid">
    """)

    for i, chart_file in enumerate(sorted(model_comparison_charts)):
        dataset_name = chart_file.replace("model_comparison_", "").replace(".json", "")
        chart_id = f"model_comp_{dataset_name}"
        btn_id = f"btn_model_comp_{dataset_name}"
        status_id = f"status_model_comp_{dataset_name}"
        chart_path = f"{chart_dir}/{chart_file}"

        html_content.append(f"""
            <div class="chart-card">
                <div class="chart-title">Model Comparison: {dataset_name}</div>
                <div class="chart-wrapper">
                    <canvas id="{chart_id}"></canvas>
                </div>
                <div class="chart-description">
                    Compares all evaluated models on the {dataset_name} dataset.
                </div>
                <div class="chart-controls">
                    <button id="{btn_id}" class="load-btn"
                            onclick="loadChart('{chart_path}', '{chart_id}', '{btn_id}', '{status_id}')">
                        Load Chart
                    </button>
                    <div id="{status_id}" class="status">Ready</div>
                </div>
            </div>
        """)

    html_content.append("""
        </div>
    </div>
    """)

    # Dataset Comparisons Section
    html_content.append(f"""
    <div class="section" id="dataset-comparisons">
        <h2>Dataset Comparisons</h2>
        <p>Compare how each model performs across different datasets.</p>

        <div class="chart-controls" style="margin-bottom: 20px;">
            <button class="load-btn" onclick="loadAllCharts('dataset-comparisons')">Load All Dataset Charts</button>
        </div>

        <div class="chart-grid">
    """)

    for i, chart_file in enumerate(sorted(dataset_comparison_charts)):
        model_name = chart_file.replace("dataset_comparison_", "").replace(".json", "")
        chart_id = f"dataset_comp_{model_name.replace('-', '_')}"
        btn_id = f"btn_dataset_comp_{model_name.replace('-', '_')}"
        status_id = f"status_dataset_comp_{model_name.replace('-', '_')}"
        chart_path = f"{chart_dir}/{chart_file}"

        html_content.append(f"""
            <div class="chart-card">
                <div class="chart-title">Dataset Comparison: {model_name}</div>
                <div class="chart-wrapper">
                    <canvas id="{chart_id}"></canvas>
                </div>
                <div class="chart-description">
                    Shows {model_name}'s performance across all evaluated datasets.
                </div>
                <div class="chart-controls">
                    <button id="{btn_id}" class="load-btn"
                            onclick="loadChart('{chart_path}', '{chart_id}', '{btn_id}', '{status_id}')">
                        Load Chart
                    </button>
                    <div id="{status_id}" class="status">Ready</div>
                </div>
            </div>
        """)

    html_content.append("""
        </div>
    </div>
    """)

    # Category Analysis Section (Radar Charts)
    html_content.append(f"""
    <div class="section" id="category-analysis">
        <h2>Category Analysis</h2>
        <p>Detailed breakdown of model performance across categories within datasets (radar charts).</p>

        <div class="chart-controls" style="margin-bottom: 20px;">
            <button class="load-btn" onclick="loadAllCharts('category-analysis')">Load All Category Charts</button>
        </div>
    """)

    # Group radar charts by dataset
    radar_by_dataset = {}
    for chart_file in sorted(category_radar_charts):
        base_name = chart_file.replace("category_radar_", "").replace(".json", "")
        parts = base_name.split("_", 1)
        if len(parts) == 2:
            model_name, dataset_name = parts
            if dataset_name not in radar_by_dataset:
                radar_by_dataset[dataset_name] = []
            radar_by_dataset[dataset_name].append((model_name, chart_file))

    for dataset_name, model_charts in radar_by_dataset.items():
        html_content.append(f"""
        <h3 style="margin-top: 30px; color: #495057; border-bottom: 1px solid #dee2e6; padding-bottom: 10px;">
            {dataset_name}
        </h3>
        <div class="chart-grid">
        """)

        for model_name, chart_file in model_charts:
            chart_id = f"radar_{model_name.replace('-', '_')}_{dataset_name}"
            btn_id = f"btn_radar_{model_name.replace('-', '_')}_{dataset_name}"
            status_id = f"status_radar_{model_name.replace('-', '_')}_{dataset_name}"
            chart_path = f"{chart_dir}/{chart_file}"

            html_content.append(f"""
                <div class="chart-card">
                    <div class="chart-title">{model_name} - {dataset_name} Categories</div>
                    <div class="chart-wrapper">
                        <canvas id="{chart_id}"></canvas>
                    </div>
                    <div class="chart-description">
                        Radar chart showing performance across categories in {dataset_name}.
                    </div>
                    <div class="chart-controls">
                        <button id="{btn_id}" class="load-btn"
                                onclick="loadChart('{chart_path}', '{chart_id}', '{btn_id}', '{status_id}')">
                            Load Chart
                        </button>
                        <div id="{status_id}" class="status">Ready</div>
                    </div>
                </div>
            """)

        html_content.append("""
        </div>
        """)

    html_content.append("""
    </div>
    """)

    # Metric Analysis Section
    html_content.append(f"""
    <div class="section" id="metric-analysis">
        <h2>Metric Analysis</h2>
        <p>Comparison of different evaluation metrics for the same model-dataset pair.</p>

        <div class="chart-controls" style="margin-bottom: 20px;">
            <button class="load-btn" onclick="loadAllCharts('metric-analysis')">Load All Metric Charts</button>
        </div>
    """)

    # Group metric charts by dataset
    metric_by_dataset = {}
    for chart_file in sorted(metric_comparison_charts):
        base_name = chart_file.replace("metric_comparison_", "").replace(".json", "")
        parts = base_name.split("_", 1)
        if len(parts) == 2:
            model_name, dataset_name = parts
            if dataset_name not in metric_by_dataset:
                metric_by_dataset[dataset_name] = []
            metric_by_dataset[dataset_name].append((model_name, chart_file))

    for dataset_name, model_charts in metric_by_dataset.items():
        html_content.append(f"""
        <h3 style="margin-top: 30px; color: #495057; border-bottom: 1px solid #dee2e6; padding-bottom: 10px;">
            {dataset_name}
        </h3>
        <div class="chart-grid">
        """)

        for model_name, chart_file in model_charts:
            chart_id = f"metric_{model_name.replace('-', '_')}_{dataset_name}"
            btn_id = f"btn_metric_{model_name.replace('-', '_')}_{dataset_name}"
            status_id = f"status_metric_{model_name.replace('-', '_')}_{dataset_name}"
            chart_path = f"{chart_dir}/{chart_file}"

            html_content.append(f"""
                <div class="chart-card">
                    <div class="chart-title">{model_name} - {dataset_name} Metrics</div>
                    <div class="chart-wrapper">
                        <canvas id="{chart_id}"></canvas>
                    </div>
                    <div class="chart-description">
                        Comparison of evaluation metrics for {model_name} on {dataset_name}.
                    </div>
                    <div class="chart-controls">
                        <button id="{btn_id}" class="load-btn"
                                onclick="loadChart('{chart_path}', '{chart_id}', '{btn_id}', '{status_id}')">
                            Load Chart
                        </button>
                        <div id="{status_id}" class="status">Ready</div>
                    </div>
                </div>
            """)

        html_content.append("""
        </div>
        """)

    html_content.append("""
    </div>
    """)

    # How to Use Section
    html_content.append("""
    <div class="section" id="how-to-use">
        <h2>How to Use This Report</h2>

        <h3>Interactive Features</h3>
        <ul style="margin-left: 20px; margin-bottom: 20px;">
            <li>Click "Load Chart" buttons to render individual charts</li>
            <li>Use "Load All Charts" buttons to load all charts in a section</li>
            <li>Hover over chart elements to see detailed values</li>
            <li>Charts are responsive and work on mobile devices</li>
        </ul>

        <h3>Chart Types</h3>
        <ul style="margin-left: 20px; margin-bottom: 20px;">
            <li><strong>Bar Charts</strong>: Used for model and dataset comparisons</li>
            <li><strong>Radar Charts</strong>: Used for category analysis</li>
            <li><strong>Color Coding</strong>:
                <ul>
                    <li>Green: Score ≥ 0.8 (Good performance)</li>
                    <li>Yellow: 0.6 ≤ Score < 0.8 (Average performance)</li>
                    <li>Red: Score < 0.6 (Needs improvement)</li>
                </ul>
            </li>
        </ul>

        <h3>Technical Details</h3>
        <ul style="margin-left: 20px; margin-bottom: 20px;">
            <li>Charts are rendered using <a href="https://www.chartjs.org/" target="_blank">Chart.js</a></li>
            <li>Data is loaded dynamically from JSON configuration files</li>
            <li>All charts are generated from evaluation result files</li>
            <li>This is a standalone HTML file - no server required</li>
        </ul>

        <h3>Regenerating Charts</h3>
        <p>To regenerate the charts with new data:</p>
        <pre style="background-color: #f8f9fa; padding: 15px; border-radius: 6px; margin: 15px 0;">
cd data_process
python generate_charts.py --output-dir visualization_data
python generate_html_report.py --chart-dir visualization_data --output report.html</pre>
    </div>

    <footer>
        <p>Report generated automatically by LLM Evaluation Visualization Tool</p>
        <p>Generated on: """ + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
    </footer>

    <script>
        // Auto-load first chart in each section for preview
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(() => {
                // Load first model comparison chart
                const firstModelBtn = document.querySelector('#model-comparisons .load-btn');
                if (firstModelBtn && !firstModelBtn.id.includes('All')) {
                    firstModelBtn.click();
                }
            }, 500);
        });
    </script>
</body>
</html>
""")

    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_content))

    print(f"HTML report generated: {output_file}")
    print(f"Total charts included: {len(chart_files)}")
    print(f"Models: {len(models)}")
    print(f"Datasets: {len(datasets)}")


def main():
    parser = argparse.ArgumentParser(description='Generate HTML report with embedded charts')
    parser.add_argument('--chart-dir', default='visualization_data',
                       help='Directory containing chart JSON configurations (default: visualization_data)')
    parser.add_argument('--output', default='evaluation_report.html',
                       help='Output HTML file (default: evaluation_report.html)')

    args = parser.parse_args()

    # Check if chart directory exists
    if not os.path.exists(args.chart_dir):
        print(f"Error: Chart directory '{args.chart_dir}' not found.")
        print("Please generate charts first using generate_charts.py")
        sys.exit(1)

    # Generate report
    generate_html_report(args.chart_dir, args.output)


if __name__ == "__main__":
    main()