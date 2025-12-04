# Chart.js Configuration Generator for LLM Evaluation Results

This tool automatically generates Chart.js configurations from LLM evaluation result JSON files.

## Overview

The script `generate_charts.py` reads evaluation result JSON files from the `eval_result/reports/` directory and generates various types of Chart.js configurations for visualizing model performance.

## Features

1. **Model Comparison Charts**: Compare different models on the same dataset
2. **Dataset Comparison Charts**: Compare a model's performance across different datasets
3. **Category Radar Charts**: Show performance across categories/subsets within a dataset
4. **Metric Comparison Charts**: Compare different metrics for a single model-dataset pair

## Usage

### Basic Usage

```bash
# Generate all chart types
python generate_charts.py --data-dir eval_result --output-dir chart_configs

# Generate specific chart types
python generate_charts.py --chart-type model_comparison
python generate_charts.py --chart-type dataset_comparison
python generate_charts.py --chart-type category_radar
python generate_charts.py --chart-type metric_comparison
```

### Command Line Arguments

- `--data-dir`: Directory containing evaluation results (default: `eval_result`)
- `--output-dir`: Output directory for chart configurations (default: `chart_configs`)
- `--chart-type`: Type of charts to generate: `all`, `model_comparison`, `dataset_comparison`, `category_radar`, `metric_comparison` (default: `all`)

## Output Files

The script generates:

1. **Chart Configuration JSON files**: Each file contains a complete Chart.js configuration
2. **Index file**: `index.json` with metadata about all generated charts
3. **Example HTML**: `example.html` demonstrating how to use the charts

### File Naming Convention

- `model_comparison_{dataset_name}.json`: Model comparison for a specific dataset
- `dataset_comparison_{model_name}.json`: Dataset comparison for a specific model
- `category_radar_{model_name}_{dataset_name}.json`: Radar chart for categories within a dataset
- `metric_comparison_{model_name}_{dataset_name}.json`: Metric comparison for a model-dataset pair

## Using the Generated Charts

### In a Web Application

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <canvas id="myChart"></canvas>

    <script>
        // Load chart configuration
        fetch('chart_configs/model_comparison_chinese_simpleqa.json')
            .then(response => response.json())
            .then(config => {
                const ctx = document.getElementById('myChart').getContext('2d');
                new Chart(ctx, config);
            });
    </script>
</body>
</html>
```

### Programmatic Usage

```javascript
// Using fetch API
async function loadChart(configFile) {
    const response = await fetch(configFile);
    const config = await response.json();
    const ctx = document.getElementById('chartCanvas').getContext('2d');

    // Destroy existing chart if it exists
    if (window.myChartInstance) {
        window.myChartInstance.destroy();
    }

    window.myChartInstance = new Chart(ctx, config);
}

// Example usage
loadChart('chart_configs/dataset_comparison_deepseek-reasoner-v3.2.json');
```

## Chart Types Explained

### 1. Model Comparison Charts
- **Type**: Bar chart
- **X-axis**: Model names
- **Y-axis**: Scores (0-1 scale)
- **Colors**: Green (≥0.8), Yellow (0.6-0.8), Red (<0.6)
- **Use case**: Compare which model performs best on a specific dataset

### 2. Dataset Comparison Charts
- **Type**: Bar chart
- **X-axis**: Dataset names
- **Y-axis**: Scores (0-1 scale)
- **Colors**: Blue (≥0.8), Yellow (0.6-0.8), Red (<0.6)
- **Use case**: See which datasets a model performs best/worst on

### 3. Category Radar Charts
- **Type**: Radar chart
- **Axes**: Different categories/subsets within a dataset
- **Radius**: Scores (0-1 scale)
- **Use case**: Visualize performance breakdown across different aspects of a dataset

### 4. Metric Comparison Charts
- **Type**: Bar chart
- **X-axis**: Metric names
- **Y-axis**: Scores (0-1 scale)
- **Colors**: Green (≥0.8), Yellow (0.6-0.8), Purple (<0.6)
- **Use case**: Compare different evaluation metrics for the same model-dataset pair

## Data Structure Requirements

The script expects evaluation result JSON files in the following structure:

```json
{
    "model_name": "model-name",
    "dataset_name": "dataset-name",
    "dataset_pretty_name": "Dataset Pretty Name",
    "score": 0.85,
    "metrics": [
        {
            "name": "metric_name",
            "score": 0.85,
            "categories": [
                {
                    "name": ["default"],
                    "subsets": [
                        {
                            "name": "subset_name",
                            "score": 0.90
                        }
                    ]
                }
            ]
        }
    ]
}
```

## Customization

### Modifying Chart Styles

You can modify the chart generation functions in `generate_charts.py` to:

1. Change color schemes
2. Adjust chart dimensions
3. Modify animation settings
4. Change axis configurations

### Adding New Chart Types

To add a new chart type:

1. Create a new chart generation function following the existing patterns
2. Add the chart type to the command line argument choices
3. Add the generation logic to the main function

## Dependencies

- Python 3.6+
- `chartjs_wrap.py` module (included in the same directory)

## Example

```bash
# Generate charts for all evaluation results
cd data_process
python generate_charts.py

# Open the example HTML file in a browser
# (Navigate to test_charts/example.html)
```

The generated charts are fully responsive and include:
- Titles and legends
- Tooltips with score information
- Animations
- Color-coded scores based on performance
- Proper axis scaling