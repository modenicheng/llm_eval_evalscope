# Evaluation Data Merger

This script merges all evaluation result JSON files into a single Chart.js compatible JSON file.

## Files Created

1. **`merge_evaluation_data.py`** - The main script that merges evaluation data
2. **`merged_evaluation_data.json`** - Minified JSON output (default)
3. **`merged_evaluation_data_pretty.json`** - Pretty-printed JSON output
4. **`example_chart.html`** - Example visualization using Chart.js

## Usage

### Basic Usage
```bash
python merge_evaluation_data.py
```

This will read evaluation results from `eval_result/` and create `merged_evaluation_data.json`.

### With Options
```bash
# Specify custom data directory
python merge_evaluation_data.py --data-dir path/to/eval_results

# Specify output file
python merge_evaluation_data.py --output custom_output.json

# Generate pretty-printed JSON
python merge_evaluation_data.py --pretty

# Combine options
python merge_evaluation_data.py --data-dir eval_result --output merged_data.json --pretty
```

## Output Format

The generated JSON file has the following structure:

```json
{
  "type": "bar",
  "data": {
    "labels": ["dataset1", "dataset2", "dataset3", ...],
    "datasets": [
      {
        "label": "model1",
        "data": [score1, score2, score3, ...],
        "backgroundColor": "#FF638422",
        "borderColor": "#FF6384FF",
        "borderWidth": 2,
        "hoverBackgroundColor": "#FF6384FF",
        "hoverBorderColor": "#FF6384FF",
        "hoverBorderWidth": 3
      },
      {
        "label": "model2",
        "data": [...],
        "backgroundColor": "#36A2EB33",
        "borderColor": "#36A2EBFF",
        "borderWidth": 2,
        "hoverBackgroundColor": "#36A2EBFF",
        "hoverBorderColor": "#36A2EBFF",
        "hoverBorderWidth": 3
      },
      ...
    ]
  },
  "options": {
    "responsive": true,
    "maintainAspectRatio": true,
    "animation": {
      "duration": 1000,
      "easing": "easeOutQuart"
    },
    "plugins": {
      "title": {
        "display": true,
        "text": "Model Performance Across Datasets",
        "color": "#333",
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
      }
    },
    "scales": {
      "x": {
        "type": "category",
        "display": true,
        "title": {
          "display": true,
          "text": "Dataset",
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
```

### Color Scheme
- **Border colors**: `#xxxxxxFF` (full opacity)
- **Background colors**: `#xxxxxx22` or `#xxxxxx33` (low opacity)
- Each model gets a distinct color from a predefined palette

## Example Visualization

Open `example_chart.html` in a web browser to see an interactive visualization of the merged data. The example includes:

- Interactive bar/line/radar charts
- Model and dataset statistics
- Export functionality
- Customizable display options

## Data Source

The script reads JSON files from:
```
eval_result/reports/{model_name}/{dataset_name}.json
```

Each JSON file should have the following structure:
```json
{
  "dataset_name": "chinese_simpleqa",
  "model_name": "deepseek-reasoner",
  "score": 0.6953,
  "metrics": [...]
}
```

## Integration with Existing Pipeline

This script complements the existing visualization pipeline:

1. **Existing**: `generate_charts.py` creates individual chart configurations
2. **New**: `merge_evaluation_data.py` creates consolidated data for comparison charts
3. **Usage**: The merged JSON can be used directly with Chart.js for:
   - Model comparison across datasets
   - Dataset comparison across models
   - Radar charts for category/subset analysis

## Requirements

- Python 3.6+
- No external dependencies (uses standard library only)

## Notes

- Missing scores (if a model wasn't evaluated on a dataset) will be `null` in the data array
- The color palette cycles if there are more models than predefined colors
- The script handles nested directory structures automatically