# LLM Evaluation Results Visualization Report

*Generated on: 2025-12-03 17:58:59*

**Total Charts Generated:** 66

**Models Evaluated:** 6

**Datasets Used:** 6

## Table of Contents

1. [Overview](#overview)
2. [Model Comparisons](#model-comparisons)
3. [Dataset Comparisons](#dataset-comparisons)
4. [Category Analysis](#category-analysis)
5. [Metric Analysis](#metric-analysis)
6. [How to Use](#how-to-use)

---


## Overview

This report contains interactive visualizations of LLM evaluation results.
All charts are rendered using Chart.js and load data dynamically from JSON files.

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


---


## Model Comparisons

Compare performance of different models on the same dataset.

<div class="chart-section">
    <div class="chart-title">Model Comparison: chinese_simpleqa</div>
    <div class="chart-wrapper">
        <canvas id="model_comp_chinese_simpleqa"></canvas>
    </div>
    <div class="chart-description">
        This chart compares all evaluated models on the chinese_simpleqa dataset.
        Higher scores indicate better performance.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/model_comparison_chinese_simpleqa.json', 'model_comp_chinese_simpleqa')">
        Load Chart
    </button>
</div>


<div class="chart-section">
    <div class="chart-title">Model Comparison: general_qa</div>
    <div class="chart-wrapper">
        <canvas id="model_comp_general_qa"></canvas>
    </div>
    <div class="chart-description">
        This chart compares all evaluated models on the general_qa dataset.
        Higher scores indicate better performance.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/model_comparison_general_qa.json', 'model_comp_general_qa')">
        Load Chart
    </button>
</div>


<div class="chart-section">
    <div class="chart-title">Model Comparison: ifeval</div>
    <div class="chart-wrapper">
        <canvas id="model_comp_ifeval"></canvas>
    </div>
    <div class="chart-description">
        This chart compares all evaluated models on the ifeval dataset.
        Higher scores indicate better performance.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/model_comparison_ifeval.json', 'model_comp_ifeval')">
        Load Chart
    </button>
</div>


<div class="chart-section">
    <div class="chart-title">Model Comparison: math_500</div>
    <div class="chart-wrapper">
        <canvas id="model_comp_math_500"></canvas>
    </div>
    <div class="chart-description">
        This chart compares all evaluated models on the math_500 dataset.
        Higher scores indicate better performance.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/model_comparison_math_500.json', 'model_comp_math_500')">
        Load Chart
    </button>
</div>


<div class="chart-section">
    <div class="chart-title">Model Comparison: multi_if</div>
    <div class="chart-wrapper">
        <canvas id="model_comp_multi_if"></canvas>
    </div>
    <div class="chart-description">
        This chart compares all evaluated models on the multi_if dataset.
        Higher scores indicate better performance.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/model_comparison_multi_if.json', 'model_comp_multi_if')">
        Load Chart
    </button>
</div>


<div class="chart-section">
    <div class="chart-title">Model Comparison: swe_bench_verified_mini</div>
    <div class="chart-wrapper">
        <canvas id="model_comp_swe_bench_verified_mini"></canvas>
    </div>
    <div class="chart-description">
        This chart compares all evaluated models on the swe_bench_verified_mini dataset.
        Higher scores indicate better performance.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/model_comparison_swe_bench_verified_mini.json', 'model_comp_swe_bench_verified_mini')">
        Load Chart
    </button>
</div>


---


## Dataset Comparisons

Compare a model's performance across different datasets.

<div class="chart-section">
    <div class="chart-title">Dataset Comparison: deepseek-reasoner-v3.2-exp</div>
    <div class="chart-wrapper">
        <canvas id="dataset_comp_deepseek_reasoner_v3.2_exp"></canvas>
    </div>
    <div class="chart-description">
        This chart shows how deepseek-reasoner-v3.2-exp performs across all evaluated datasets.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/dataset_comparison_deepseek-reasoner-v3.2-exp.json', 'dataset_comp_deepseek_reasoner_v3.2_exp')">
        Load Chart
    </button>
</div>


<div class="chart-section">
    <div class="chart-title">Dataset Comparison: deepseek-reasoner-v3.2-special</div>
    <div class="chart-wrapper">
        <canvas id="dataset_comp_deepseek_reasoner_v3.2_special"></canvas>
    </div>
    <div class="chart-description">
        This chart shows how deepseek-reasoner-v3.2-special performs across all evaluated datasets.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/dataset_comparison_deepseek-reasoner-v3.2-special.json', 'dataset_comp_deepseek_reasoner_v3.2_special')">
        Load Chart
    </button>
</div>


<div class="chart-section">
    <div class="chart-title">Dataset Comparison: deepseek-reasoner-v3.2</div>
    <div class="chart-wrapper">
        <canvas id="dataset_comp_deepseek_reasoner_v3.2"></canvas>
    </div>
    <div class="chart-description">
        This chart shows how deepseek-reasoner-v3.2 performs across all evaluated datasets.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/dataset_comparison_deepseek-reasoner-v3.2.json', 'dataset_comp_deepseek_reasoner_v3.2')">
        Load Chart
    </button>
</div>


<div class="chart-section">
    <div class="chart-title">Dataset Comparison: doubao-seed-1-6-251015</div>
    <div class="chart-wrapper">
        <canvas id="dataset_comp_doubao_seed_1_6_251015"></canvas>
    </div>
    <div class="chart-description">
        This chart shows how doubao-seed-1-6-251015 performs across all evaluated datasets.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/dataset_comparison_doubao-seed-1-6-251015.json', 'dataset_comp_doubao_seed_1_6_251015')">
        Load Chart
    </button>
</div>


<div class="chart-section">
    <div class="chart-title">Dataset Comparison: qwen-plus</div>
    <div class="chart-wrapper">
        <canvas id="dataset_comp_qwen_plus"></canvas>
    </div>
    <div class="chart-description">
        This chart shows how qwen-plus performs across all evaluated datasets.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/dataset_comparison_qwen-plus.json', 'dataset_comp_qwen_plus')">
        Load Chart
    </button>
</div>


<div class="chart-section">
    <div class="chart-title">Dataset Comparison: qwen3-max</div>
    <div class="chart-wrapper">
        <canvas id="dataset_comp_qwen3_max"></canvas>
    </div>
    <div class="chart-description">
        This chart shows how qwen3-max performs across all evaluated datasets.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/dataset_comparison_qwen3-max.json', 'dataset_comp_qwen3_max')">
        Load Chart
    </button>
</div>


---


## Category Analysis

Detailed breakdown of performance across categories within datasets.

### chinese_simpleqa

Performance breakdown across categories for chinese_simpleqa:

<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2-exp - chinese_simpleqa Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_deepseek_reasoner_v3.2_exp_chinese_simpleqa"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing deepseek-reasoner-v3.2-exp's performance across different categories in chinese_simpleqa.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_deepseek-reasoner-v3.2-exp_chinese_simpleqa.json', 'radar_deepseek_reasoner_v3.2_exp_chinese_simpleqa')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2-special - chinese_simpleqa Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_deepseek_reasoner_v3.2_special_chinese_simpleqa"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing deepseek-reasoner-v3.2-special's performance across different categories in chinese_simpleqa.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_deepseek-reasoner-v3.2-special_chinese_simpleqa.json', 'radar_deepseek_reasoner_v3.2_special_chinese_simpleqa')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2 - chinese_simpleqa Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_deepseek_reasoner_v3.2_chinese_simpleqa"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing deepseek-reasoner-v3.2's performance across different categories in chinese_simpleqa.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_deepseek-reasoner-v3.2_chinese_simpleqa.json', 'radar_deepseek_reasoner_v3.2_chinese_simpleqa')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">doubao-seed-1-6-251015 - chinese_simpleqa Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_doubao_seed_1_6_251015_chinese_simpleqa"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing doubao-seed-1-6-251015's performance across different categories in chinese_simpleqa.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_doubao-seed-1-6-251015_chinese_simpleqa.json', 'radar_doubao_seed_1_6_251015_chinese_simpleqa')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">qwen-plus - chinese_simpleqa Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_qwen_plus_chinese_simpleqa"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing qwen-plus's performance across different categories in chinese_simpleqa.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_qwen-plus_chinese_simpleqa.json', 'radar_qwen_plus_chinese_simpleqa')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">qwen3-max - chinese_simpleqa Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_qwen3_max_chinese_simpleqa"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing qwen3-max's performance across different categories in chinese_simpleqa.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_qwen3-max_chinese_simpleqa.json', 'radar_qwen3_max_chinese_simpleqa')">
        Load Chart
    </button>
</div>


### general_qa

Performance breakdown across categories for general_qa:

<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2-exp - general_qa Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_deepseek_reasoner_v3.2_exp_general_qa"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing deepseek-reasoner-v3.2-exp's performance across different categories in general_qa.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_deepseek-reasoner-v3.2-exp_general_qa.json', 'radar_deepseek_reasoner_v3.2_exp_general_qa')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2-special - general_qa Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_deepseek_reasoner_v3.2_special_general_qa"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing deepseek-reasoner-v3.2-special's performance across different categories in general_qa.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_deepseek-reasoner-v3.2-special_general_qa.json', 'radar_deepseek_reasoner_v3.2_special_general_qa')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2 - general_qa Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_deepseek_reasoner_v3.2_general_qa"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing deepseek-reasoner-v3.2's performance across different categories in general_qa.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_deepseek-reasoner-v3.2_general_qa.json', 'radar_deepseek_reasoner_v3.2_general_qa')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">doubao-seed-1-6-251015 - general_qa Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_doubao_seed_1_6_251015_general_qa"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing doubao-seed-1-6-251015's performance across different categories in general_qa.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_doubao-seed-1-6-251015_general_qa.json', 'radar_doubao_seed_1_6_251015_general_qa')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">qwen-plus - general_qa Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_qwen_plus_general_qa"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing qwen-plus's performance across different categories in general_qa.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_qwen-plus_general_qa.json', 'radar_qwen_plus_general_qa')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">qwen3-max - general_qa Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_qwen3_max_general_qa"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing qwen3-max's performance across different categories in general_qa.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_qwen3-max_general_qa.json', 'radar_qwen3_max_general_qa')">
        Load Chart
    </button>
</div>


### ifeval

Performance breakdown across categories for ifeval:

<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2-exp - ifeval Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_deepseek_reasoner_v3.2_exp_ifeval"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing deepseek-reasoner-v3.2-exp's performance across different categories in ifeval.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_deepseek-reasoner-v3.2-exp_ifeval.json', 'radar_deepseek_reasoner_v3.2_exp_ifeval')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2-special - ifeval Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_deepseek_reasoner_v3.2_special_ifeval"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing deepseek-reasoner-v3.2-special's performance across different categories in ifeval.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_deepseek-reasoner-v3.2-special_ifeval.json', 'radar_deepseek_reasoner_v3.2_special_ifeval')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2 - ifeval Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_deepseek_reasoner_v3.2_ifeval"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing deepseek-reasoner-v3.2's performance across different categories in ifeval.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_deepseek-reasoner-v3.2_ifeval.json', 'radar_deepseek_reasoner_v3.2_ifeval')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">doubao-seed-1-6-251015 - ifeval Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_doubao_seed_1_6_251015_ifeval"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing doubao-seed-1-6-251015's performance across different categories in ifeval.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_doubao-seed-1-6-251015_ifeval.json', 'radar_doubao_seed_1_6_251015_ifeval')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">qwen-plus - ifeval Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_qwen_plus_ifeval"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing qwen-plus's performance across different categories in ifeval.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_qwen-plus_ifeval.json', 'radar_qwen_plus_ifeval')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">qwen3-max - ifeval Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_qwen3_max_ifeval"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing qwen3-max's performance across different categories in ifeval.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_qwen3-max_ifeval.json', 'radar_qwen3_max_ifeval')">
        Load Chart
    </button>
</div>


### math_500

Performance breakdown across categories for math_500:

<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2-exp - math_500 Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_deepseek_reasoner_v3.2_exp_math_500"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing deepseek-reasoner-v3.2-exp's performance across different categories in math_500.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_deepseek-reasoner-v3.2-exp_math_500.json', 'radar_deepseek_reasoner_v3.2_exp_math_500')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2-special - math_500 Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_deepseek_reasoner_v3.2_special_math_500"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing deepseek-reasoner-v3.2-special's performance across different categories in math_500.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_deepseek-reasoner-v3.2-special_math_500.json', 'radar_deepseek_reasoner_v3.2_special_math_500')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2 - math_500 Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_deepseek_reasoner_v3.2_math_500"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing deepseek-reasoner-v3.2's performance across different categories in math_500.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_deepseek-reasoner-v3.2_math_500.json', 'radar_deepseek_reasoner_v3.2_math_500')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">doubao-seed-1-6-251015 - math_500 Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_doubao_seed_1_6_251015_math_500"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing doubao-seed-1-6-251015's performance across different categories in math_500.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_doubao-seed-1-6-251015_math_500.json', 'radar_doubao_seed_1_6_251015_math_500')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">qwen-plus - math_500 Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_qwen_plus_math_500"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing qwen-plus's performance across different categories in math_500.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_qwen-plus_math_500.json', 'radar_qwen_plus_math_500')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">qwen3-max - math_500 Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_qwen3_max_math_500"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing qwen3-max's performance across different categories in math_500.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_qwen3-max_math_500.json', 'radar_qwen3_max_math_500')">
        Load Chart
    </button>
</div>


### multi_if

Performance breakdown across categories for multi_if:

<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2-exp - multi_if Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_deepseek_reasoner_v3.2_exp_multi_if"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing deepseek-reasoner-v3.2-exp's performance across different categories in multi_if.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_deepseek-reasoner-v3.2-exp_multi_if.json', 'radar_deepseek_reasoner_v3.2_exp_multi_if')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2-special - multi_if Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_deepseek_reasoner_v3.2_special_multi_if"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing deepseek-reasoner-v3.2-special's performance across different categories in multi_if.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_deepseek-reasoner-v3.2-special_multi_if.json', 'radar_deepseek_reasoner_v3.2_special_multi_if')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2 - multi_if Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_deepseek_reasoner_v3.2_multi_if"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing deepseek-reasoner-v3.2's performance across different categories in multi_if.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_deepseek-reasoner-v3.2_multi_if.json', 'radar_deepseek_reasoner_v3.2_multi_if')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">doubao-seed-1-6-251015 - multi_if Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_doubao_seed_1_6_251015_multi_if"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing doubao-seed-1-6-251015's performance across different categories in multi_if.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_doubao-seed-1-6-251015_multi_if.json', 'radar_doubao_seed_1_6_251015_multi_if')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">qwen-plus - multi_if Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_qwen_plus_multi_if"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing qwen-plus's performance across different categories in multi_if.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_qwen-plus_multi_if.json', 'radar_qwen_plus_multi_if')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">qwen3-max - multi_if Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_qwen3_max_multi_if"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing qwen3-max's performance across different categories in multi_if.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_qwen3-max_multi_if.json', 'radar_qwen3_max_multi_if')">
        Load Chart
    </button>
</div>


### swe_bench_verified_mini

Performance breakdown across categories for swe_bench_verified_mini:

<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2-exp - swe_bench_verified_mini Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_deepseek_reasoner_v3.2_exp_swe_bench_verified_mini"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing deepseek-reasoner-v3.2-exp's performance across different categories in swe_bench_verified_mini.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_deepseek-reasoner-v3.2-exp_swe_bench_verified_mini.json', 'radar_deepseek_reasoner_v3.2_exp_swe_bench_verified_mini')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2-special - swe_bench_verified_mini Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_deepseek_reasoner_v3.2_special_swe_bench_verified_mini"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing deepseek-reasoner-v3.2-special's performance across different categories in swe_bench_verified_mini.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_deepseek-reasoner-v3.2-special_swe_bench_verified_mini.json', 'radar_deepseek_reasoner_v3.2_special_swe_bench_verified_mini')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2 - swe_bench_verified_mini Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_deepseek_reasoner_v3.2_swe_bench_verified_mini"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing deepseek-reasoner-v3.2's performance across different categories in swe_bench_verified_mini.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_deepseek-reasoner-v3.2_swe_bench_verified_mini.json', 'radar_deepseek_reasoner_v3.2_swe_bench_verified_mini')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">doubao-seed-1-6-251015 - swe_bench_verified_mini Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_doubao_seed_1_6_251015_swe_bench_verified_mini"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing doubao-seed-1-6-251015's performance across different categories in swe_bench_verified_mini.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_doubao-seed-1-6-251015_swe_bench_verified_mini.json', 'radar_doubao_seed_1_6_251015_swe_bench_verified_mini')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">qwen-plus - swe_bench_verified_mini Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_qwen_plus_swe_bench_verified_mini"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing qwen-plus's performance across different categories in swe_bench_verified_mini.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_qwen-plus_swe_bench_verified_mini.json', 'radar_qwen_plus_swe_bench_verified_mini')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">qwen3-max - swe_bench_verified_mini Categories</div>
    <div class="chart-wrapper">
        <canvas id="radar_qwen3_max_swe_bench_verified_mini"></canvas>
    </div>
    <div class="chart-description">
        Radar chart showing qwen3-max's performance across different categories in swe_bench_verified_mini.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/category_radar_qwen3-max_swe_bench_verified_mini.json', 'radar_qwen3_max_swe_bench_verified_mini')">
        Load Chart
    </button>
</div>


---


## Metric Analysis

Comparison of different evaluation metrics for the same model-dataset pair.

### chinese_simpleqa

Metric comparison for chinese_simpleqa:

<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2-exp - chinese_simpleqa Metrics</div>
    <div class="chart-wrapper">
        <canvas id="metric_deepseek_reasoner_v3.2_exp_chinese_simpleqa"></canvas>
    </div>
    <div class="chart-description">
        Comparison of different evaluation metrics for deepseek-reasoner-v3.2-exp on chinese_simpleqa.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/metric_comparison_deepseek-reasoner-v3.2-exp_chinese_simpleqa.json', 'metric_deepseek_reasoner_v3.2_exp_chinese_simpleqa')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2-special - chinese_simpleqa Metrics</div>
    <div class="chart-wrapper">
        <canvas id="metric_deepseek_reasoner_v3.2_special_chinese_simpleqa"></canvas>
    </div>
    <div class="chart-description">
        Comparison of different evaluation metrics for deepseek-reasoner-v3.2-special on chinese_simpleqa.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/metric_comparison_deepseek-reasoner-v3.2-special_chinese_simpleqa.json', 'metric_deepseek_reasoner_v3.2_special_chinese_simpleqa')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2 - chinese_simpleqa Metrics</div>
    <div class="chart-wrapper">
        <canvas id="metric_deepseek_reasoner_v3.2_chinese_simpleqa"></canvas>
    </div>
    <div class="chart-description">
        Comparison of different evaluation metrics for deepseek-reasoner-v3.2 on chinese_simpleqa.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/metric_comparison_deepseek-reasoner-v3.2_chinese_simpleqa.json', 'metric_deepseek_reasoner_v3.2_chinese_simpleqa')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">doubao-seed-1-6-251015 - chinese_simpleqa Metrics</div>
    <div class="chart-wrapper">
        <canvas id="metric_doubao_seed_1_6_251015_chinese_simpleqa"></canvas>
    </div>
    <div class="chart-description">
        Comparison of different evaluation metrics for doubao-seed-1-6-251015 on chinese_simpleqa.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/metric_comparison_doubao-seed-1-6-251015_chinese_simpleqa.json', 'metric_doubao_seed_1_6_251015_chinese_simpleqa')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">qwen-plus - chinese_simpleqa Metrics</div>
    <div class="chart-wrapper">
        <canvas id="metric_qwen_plus_chinese_simpleqa"></canvas>
    </div>
    <div class="chart-description">
        Comparison of different evaluation metrics for qwen-plus on chinese_simpleqa.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/metric_comparison_qwen-plus_chinese_simpleqa.json', 'metric_qwen_plus_chinese_simpleqa')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">qwen3-max - chinese_simpleqa Metrics</div>
    <div class="chart-wrapper">
        <canvas id="metric_qwen3_max_chinese_simpleqa"></canvas>
    </div>
    <div class="chart-description">
        Comparison of different evaluation metrics for qwen3-max on chinese_simpleqa.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/metric_comparison_qwen3-max_chinese_simpleqa.json', 'metric_qwen3_max_chinese_simpleqa')">
        Load Chart
    </button>
</div>


### ifeval

Metric comparison for ifeval:

<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2-exp - ifeval Metrics</div>
    <div class="chart-wrapper">
        <canvas id="metric_deepseek_reasoner_v3.2_exp_ifeval"></canvas>
    </div>
    <div class="chart-description">
        Comparison of different evaluation metrics for deepseek-reasoner-v3.2-exp on ifeval.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/metric_comparison_deepseek-reasoner-v3.2-exp_ifeval.json', 'metric_deepseek_reasoner_v3.2_exp_ifeval')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2-special - ifeval Metrics</div>
    <div class="chart-wrapper">
        <canvas id="metric_deepseek_reasoner_v3.2_special_ifeval"></canvas>
    </div>
    <div class="chart-description">
        Comparison of different evaluation metrics for deepseek-reasoner-v3.2-special on ifeval.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/metric_comparison_deepseek-reasoner-v3.2-special_ifeval.json', 'metric_deepseek_reasoner_v3.2_special_ifeval')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2 - ifeval Metrics</div>
    <div class="chart-wrapper">
        <canvas id="metric_deepseek_reasoner_v3.2_ifeval"></canvas>
    </div>
    <div class="chart-description">
        Comparison of different evaluation metrics for deepseek-reasoner-v3.2 on ifeval.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/metric_comparison_deepseek-reasoner-v3.2_ifeval.json', 'metric_deepseek_reasoner_v3.2_ifeval')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">doubao-seed-1-6-251015 - ifeval Metrics</div>
    <div class="chart-wrapper">
        <canvas id="metric_doubao_seed_1_6_251015_ifeval"></canvas>
    </div>
    <div class="chart-description">
        Comparison of different evaluation metrics for doubao-seed-1-6-251015 on ifeval.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/metric_comparison_doubao-seed-1-6-251015_ifeval.json', 'metric_doubao_seed_1_6_251015_ifeval')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">qwen-plus - ifeval Metrics</div>
    <div class="chart-wrapper">
        <canvas id="metric_qwen_plus_ifeval"></canvas>
    </div>
    <div class="chart-description">
        Comparison of different evaluation metrics for qwen-plus on ifeval.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/metric_comparison_qwen-plus_ifeval.json', 'metric_qwen_plus_ifeval')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">qwen3-max - ifeval Metrics</div>
    <div class="chart-wrapper">
        <canvas id="metric_qwen3_max_ifeval"></canvas>
    </div>
    <div class="chart-description">
        Comparison of different evaluation metrics for qwen3-max on ifeval.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/metric_comparison_qwen3-max_ifeval.json', 'metric_qwen3_max_ifeval')">
        Load Chart
    </button>
</div>


### multi_if

Metric comparison for multi_if:

<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2-exp - multi_if Metrics</div>
    <div class="chart-wrapper">
        <canvas id="metric_deepseek_reasoner_v3.2_exp_multi_if"></canvas>
    </div>
    <div class="chart-description">
        Comparison of different evaluation metrics for deepseek-reasoner-v3.2-exp on multi_if.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/metric_comparison_deepseek-reasoner-v3.2-exp_multi_if.json', 'metric_deepseek_reasoner_v3.2_exp_multi_if')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2-special - multi_if Metrics</div>
    <div class="chart-wrapper">
        <canvas id="metric_deepseek_reasoner_v3.2_special_multi_if"></canvas>
    </div>
    <div class="chart-description">
        Comparison of different evaluation metrics for deepseek-reasoner-v3.2-special on multi_if.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/metric_comparison_deepseek-reasoner-v3.2-special_multi_if.json', 'metric_deepseek_reasoner_v3.2_special_multi_if')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">deepseek-reasoner-v3.2 - multi_if Metrics</div>
    <div class="chart-wrapper">
        <canvas id="metric_deepseek_reasoner_v3.2_multi_if"></canvas>
    </div>
    <div class="chart-description">
        Comparison of different evaluation metrics for deepseek-reasoner-v3.2 on multi_if.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/metric_comparison_deepseek-reasoner-v3.2_multi_if.json', 'metric_deepseek_reasoner_v3.2_multi_if')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">doubao-seed-1-6-251015 - multi_if Metrics</div>
    <div class="chart-wrapper">
        <canvas id="metric_doubao_seed_1_6_251015_multi_if"></canvas>
    </div>
    <div class="chart-description">
        Comparison of different evaluation metrics for doubao-seed-1-6-251015 on multi_if.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/metric_comparison_doubao-seed-1-6-251015_multi_if.json', 'metric_doubao_seed_1_6_251015_multi_if')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">qwen-plus - multi_if Metrics</div>
    <div class="chart-wrapper">
        <canvas id="metric_qwen_plus_multi_if"></canvas>
    </div>
    <div class="chart-description">
        Comparison of different evaluation metrics for qwen-plus on multi_if.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/metric_comparison_qwen-plus_multi_if.json', 'metric_qwen_plus_multi_if')">
        Load Chart
    </button>
</div>


<div class="chart-section" style="margin: 20px 0;">
    <div class="chart-title">qwen3-max - multi_if Metrics</div>
    <div class="chart-wrapper">
        <canvas id="metric_qwen3_max_multi_if"></canvas>
    </div>
    <div class="chart-description">
        Comparison of different evaluation metrics for qwen3-max on multi_if.
    </div>
    <button class="nav-button" onclick="loadChart('visualization_data/metric_comparison_qwen3-max_multi_if.json', 'metric_qwen3_max_multi_if')">
        Load Chart
    </button>
</div>


---


## How to Use

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


---


*Report generated automatically by LLM Evaluation Visualization Tool*