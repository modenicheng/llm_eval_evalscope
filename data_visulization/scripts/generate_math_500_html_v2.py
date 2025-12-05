#!/usr/bin/env python3
"""
生成一个独立的HTML文件，用于浏览和对比六个模型的math-500评测结果。
从review文件夹下的jsonl文件提取数据，不需要原始输出。
包含题目、正确答案、模型回答和评分。
使用安全的JSON嵌入方式：将JSON放在<script type="application/json">标签中。
简化版本，避免复杂的嵌套字符串。
"""

import json
import os
import sys
import html

def load_json_data(json_path):
    """加载JSON数据"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_html(data):
    """生成HTML内容"""
    # 将数据转换为JSON字符串，用于嵌入
    json_str = json.dumps(data, ensure_ascii=False)
    # HTML转义，然后还原双引号（因为JSON需要原始双引号）
    json_str_escaped = html.escape(json_str)
    json_str_escaped = json_str_escaped.replace('&quot;', '"')
    # 额外安全措施：转义 </script> 序列
    json_str_escaped = json_str_escaped.replace('</script>', '<\\/script>')

    # 统计信息
    total_categories = len(data)
    total_samples = sum(len(indices) for indices in data.values())
    model_count = 0
    if total_categories > 0:
        first_cat = list(data.keys())[0]
        if data[first_cat]:
            first_idx = list(data[first_cat].keys())[0]
            model_count = len(data[first_cat][first_idx].get('models', {}))

    # 模型名称和颜色映射
    model_colors = {
        "deepseek-reasoner-v3.2": "#FF6384",      # 红色
        "deepseek-reasoner-v3.2-exp": "#36A2EB",  # 蓝色
        "deepseek-reasoner-v3.2-special": "#FFCE56",  # 黄色
        "doubao-seed-1-6-251015": "#4BC0C0",      # 青色
        "qwen3-max": "#9966FF",                   # 紫色
        "qwen-plus": "#FF9F40"                    # 橙色
    }

    model_display_names = {
        "deepseek-reasoner-v3.2": "DeepSeek Reasoner v3.2",
        "deepseek-reasoner-v3.2-exp": "DeepSeek Reasoner v3.2-exp",
        "deepseek-reasoner-v3.2-special": "DeepSeek Reasoner v3.2-special",
        "doubao-seed-1-6-251015": "Doubao Seed 1.6-251015",
        "qwen3-max": "Qwen3-max",
        "qwen-plus": "Qwen-plus"
    }

    # HTML模板 - 使用字符串拼接避免嵌套问题
    html_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Math-500 评测结果对比</title>
    <style>
        /* 基础重置 */
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
            padding: 10px;
            min-height: 100vh;
        }

        .app-header {
            text-align: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #dee2e6;
        }

        .app-header h1 {
            font-size: 1.8rem;
            color: #2c3e50;
            margin-bottom: 5px;
        }

        .app-header .stats {
            font-size: 0.9rem;
            color: #7f8c8d;
        }

        /* 主容器 - 电脑端侧边栏布局 */
        .app-container {
            display: flex;
            flex-direction: row;
            gap: 20px;
            max-width: 1800px;
            margin: 0 auto;
            align-items: flex-start;
            min-height: calc(100vh - 120px);
        }

        /* 电脑端布局：侧边栏 + 主内容区 */
        .samples-panel {
            flex: 0 0 400px; /* 固定宽度 */
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            max-height: calc(100vh - 140px);
        }

        .samples-list {
            flex: 1;
            overflow-y: auto;
            max-height: none;
        }

        .detail-panel {
            flex: 1;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            max-height: calc(100vh - 140px);
        }

        .detail-content {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }

        /* 移动端响应式设计 */
        @media (max-width: 1200px) {
            .app-container {
                flex-direction: column;
                max-width: 100%;
            }

            .samples-panel {
                flex: 0 0 auto;
                width: 100%;
                max-height: 500px;
            }

            .detail-panel {
                width: 100%;
                max-height: none;
            }
        }

        /* 样本列表头部等样式保留 */

        .samples-header {
            padding: 15px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .samples-header h2 {
            font-size: 1.2rem;
            color: #2c3e50;
        }

        .samples-controls {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .search-box {
            padding: 8px 12px;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            font-size: 0.9rem;
            width: 300px;
        }

        .category-filter {
            padding: 8px 12px;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            font-size: 0.9rem;
            background: white;
        }


        .sample-item {
            padding: 15px;
            border-bottom: 1px solid #f0f0f0;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .sample-item:hover {
            background-color: #f8f9fa;
        }

        .sample-item.selected {
            background-color: #e8f4f8;
            border-left: 4px solid #3498db;
        }

        .sample-title {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 5px;
            font-size: 1rem;
        }

        .sample-meta {
            font-size: 0.85rem;
            color: #7f8c8d;
            display: flex;
            gap: 15px;
        }

        .sample-preview {
            font-size: 0.9rem;
            color: #666;
            margin-top: 8px;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        /* 详情面板头部等样式保留 */

        .detail-header {
            padding: 15px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .detail-header h2 {
            font-size: 1.2rem;
            color: #2c3e50;
        }

        .detail-header .sample-info {
            font-size: 0.9rem;
            color: #7f8c8d;
        }


        /* 问题部分 */
        .question-section {
            background: #f8f9fa;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 25px;
        }

        .question-header {
            font-size: 1rem;
            color: #2c3e50;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .question-header .category-badge {
            background: #3498db;
            color: white;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
        }

        .question-content {
            font-size: 0.95rem;
            line-height: 1.6;
            color: #444;
            white-space: pre-wrap;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        }

        .answer-section {
            background: #e8f5e8;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 25px;
        }

        .answer-label {
            font-weight: 600;
            color: #27ae60;
            margin-bottom: 8px;
            font-size: 0.95rem;
        }

        .answer-content {
            font-size: 0.95rem;
            color: #2ecc71;
            font-weight: 600;
        }

        /* 模型比较 */
        .models-section {
            margin-top: 25px;
        }

        .models-header {
            font-size: 1.1rem;
            color: #2c3e50;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #dee2e6;
        }

        .models-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
            gap: 20px;
        }

        @media (max-width: 1100px) {
            .models-grid {
                grid-template-columns: 1fr;
            }
        }

        .model-card {
            border: 1px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
            background: white;
        }

        .model-card-header {
            padding: 15px;
            background: linear-gradient(135deg, var(--model-color, #3498db), var(--model-color-dark, #2980b9));
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .model-name {
            font-weight: 600;
            font-size: 1rem;
        }

        .model-score {
            background: rgba(255, 255, 255, 0.2);
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9rem;
        }

        .model-score.correct {
            background: rgba(46, 204, 113, 0.2);
        }

        .model-score.incorrect {
            background: rgba(231, 76, 60, 0.2);
        }

        .model-content {
            padding: 15px;
        }

        .prediction-section {
            margin-bottom: 15px;
        }

        .prediction-label {
            font-weight: 600;
            color: #7f8c8d;
            margin-bottom: 8px;
            font-size: 0.9rem;
        }

        .prediction-content {
            font-size: 0.95rem;
            line-height: 1.6;
            white-space: pre-wrap;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            background: #f8f9fa;
            padding: 12px;
            border-radius: 4px;
            max-height: 300px;
            overflow-y: auto;
        }

        .extracted-answer {
            margin-top: 15px;
            padding: 12px;
            background: #e8f4f8;
            border-radius: 4px;
            border-left: 4px solid #3498db;
        }

        .extracted-label {
            font-weight: 600;
            color: #3498db;
            margin-bottom: 5px;
            font-size: 0.9rem;
        }

        .extracted-content {
            font-size: 0.95rem;
            font-weight: 600;
            color: #2c3e50;
        }

        /* 空状态 */
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
            font-style: italic;
        }

        /* 工具类 */
        .hidden {
            display: none !important;
        }

        /* 加载指示器 */
        .loading {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="app-header">
        <h1>Math-500 评测结果对比</h1>
        <div class="stats">
            共 <span id="total-samples">''' + str(total_samples) + '''</span> 个样本 •
            <span id="total-categories">''' + str(total_categories) + '''</span> 个难度等级 •
            <span id="total-models">''' + str(model_count) + '''</span> 个模型
        </div>
    </div>

    <div class="app-container">
        <!-- 样本列表 -->
        <div class="samples-panel">
            <div class="samples-header">
                <h2>题目列表</h2>
                <div class="samples-controls">
                    <select class="category-filter" id="categoryFilter">
                        <option value="">所有难度等级</option>
                    </select>
                    <input type="text" class="search-box" id="searchBox" placeholder="搜索题目...">
                </div>
            </div>
            <div class="samples-list" id="samplesList">
                <div class="loading">加载样本列表...</div>
            </div>
        </div>

        <!-- 详情面板 -->
        <div class="detail-panel" id="detailPanel">
            <div class="detail-header">
                <h2>题目详情</h2>
                <div class="sample-info">选择题目以查看详情</div>
            </div>
            <div class="detail-content">
                <div class="empty-state" id="emptyState">
                    请从左侧列表中选择一个题目以查看详情
                </div>
                <div id="detailContent" class="hidden">
                    <!-- 动态生成的内容 -->
                </div>
            </div>
        </div>
    </div>

    <!-- 嵌入数据 -->
    <script type="application/json" id="appData">
''' + json_str_escaped + '''
    </script>

    <!-- 应用JavaScript -->
    <script>
        // 应用数据
        const appData = JSON.parse(document.getElementById('appData').textContent);
        const modelColors = ''' + json.dumps(model_colors, ensure_ascii=False) + ''';
        const modelDisplayNames = ''' + json.dumps(model_display_names, ensure_ascii=False) + ''';

        // 状态管理
        let currentCategory = '';
        let currentSampleIndex = null;
        let allSamples = [];

        // DOM元素
        const samplesListEl = document.getElementById('samplesList');
        const categoryFilterEl = document.getElementById('categoryFilter');
        const searchBoxEl = document.getElementById('searchBox');
        const detailContentEl = document.getElementById('detailContent');
        const emptyStateEl = document.getElementById('emptyState');

        // HTML转义工具函数
        function escapeHtml(text) {
            if (!text) return '';

            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML.replace(/\\n/g, '<br>').replace(/  /g, ' &nbsp;');
        }

        // 初始化
        function init() {
            // 构建所有样本的扁平化列表
            buildAllSamples();

            // 填充分类过滤器
            populateCategoryFilter();

            // 渲染样本列表
            renderSampleList();

            // 绑定事件
            setupEventListeners();
        }

        // 构建所有样本的扁平化列表
        function buildAllSamples() {
            allSamples = [];

            for (const [category, indices] of Object.entries(appData)) {
                for (const [index, sampleData] of Object.entries(indices)) {
                    allSamples.push({
                        category,
                        index: parseInt(index),
                        sampleData,
                        displayIndex: allSamples.length + 1
                    });
                }
            }

            console.log(`共加载 ${allSamples.length} 个样本`);
        }

        // 填充分类过滤器
        function populateCategoryFilter() {
            const categories = Object.keys(appData).sort();

            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category;
                option.textContent = category.replace('math_500_', '');
                categoryFilterEl.appendChild(option);
            });
        }

        // 渲染样本列表
        function renderSampleList(filteredSamples = null) {
            const samplesToRender = filteredSamples || allSamples;

            if (samplesToRender.length === 0) {
                samplesListEl.innerHTML = '<div class="empty-state">没有找到匹配的题目</div>';
                return;
            }

            let html = '';

            samplesToRender.forEach(sample => {
                const category = sample.category;
                const index = sample.index;
                const sampleData = sample.sampleData;
                const displayIndex = sample.displayIndex;

                const input = sampleData.input || '';
                const target = sampleData.target || '';
                const questionId = sampleData.question_id || '';
                const categoryDisplay = category.replace('math_500_', '');

                // 提取题目前几行作为预览
                const preview = input.split('\\n').slice(0, 2).join(' ').substring(0, 150);

                // 检查模型评分
                const models = sampleData.models || {};
                let correctCount = 0;
                for (const modelData of Object.values(models)) {
                    if (modelData.acc === 1.0) {
                        correctCount++;
                    }
                }

                html += `
                    <div class="sample-item" data-category="${category}" data-index="${index}">
                        <div class="sample-title">
                            #${displayIndex}: ${questionId || '题目 ' + index}
                        </div>
                        <div class="sample-meta">
                            <span class="category">${categoryDisplay}</span>
                            <span class="index">ID: ${index}</span>
                            <span class="models">模型正确率: ${correctCount}/${Object.keys(models).length}</span>
                        </div>
                        <div class="sample-preview">${escapeHtml(preview)}...</div>
                    </div>
                `;
            });

            samplesListEl.innerHTML = html;

            // 绑定点击事件
            document.querySelectorAll('.sample-item').forEach(item => {
                item.addEventListener('click', function() {
                    const category = this.dataset.category;
                    const index = parseInt(this.dataset.index);
                    selectSample(category, index);
                });
            });
        }

        // 选择样本
        function selectSample(category, index) {
            currentCategory = category;
            currentSampleIndex = index;

            // 更新选中状态
            document.querySelectorAll('.sample-item').forEach(item => {
                item.classList.remove('selected');
                if (item.dataset.category === category && parseInt(item.dataset.index) === index) {
                    item.classList.add('selected');
                }
            });

            // 显示详情
            renderDetail();
        }

        // 渲染详情
        function renderDetail() {
            const sampleData = appData[currentCategory][currentSampleIndex];
            if (!sampleData) return;

            const {input, target, category, question_id, solution, models} = sampleData;
            const categoryDisplay = category.replace('math_500_', '');

            // 构建HTML
            let html = '';

            // 问题部分
            html += `
                <div class="question-section">
                    <div class="question-header">
                        <span>题目内容</span>
                        <span class="category-badge">${categoryDisplay}</span>
                    </div>
                    <div class="question-content">${escapeHtml(input)}</div>
                </div>
            `;

            // 正确答案部分
            if (target) {
                html += `
                    <div class="answer-section">
                        <div class="answer-label">正确答案</div>
                        <div class="answer-content">${escapeHtml(target)}</div>
                    </div>
                `;
            }

            // 模型比较部分
            if (models && Object.keys(models).length > 0) {
                html += `
                    <div class="models-section">
                        <div class="models-header">模型回答对比</div>
                        <div class="models-grid">
                `;

                // 按模型名称排序
                const sortedModelNames = Object.keys(models).sort();

                sortedModelNames.forEach(modelName => {
                    const modelData = models[modelName];
                    const {prediction, extracted_prediction, acc, explanation} = modelData;
                    const isCorrect = acc === 1.0;
                    const scoreClass = isCorrect ? 'correct' : 'incorrect';
                    const scoreText = isCorrect ? '✓ 正确' : '✗ 错误';
                    const modelColor = modelColors[modelName] || '#3498db';
                    const displayName = modelDisplayNames[modelName] || modelName;

                    html += `
                        <div class="model-card" style="--model-color: ${modelColor}; --model-color-dark: ${modelColor}88">
                            <div class="model-card-header">
                                <div class="model-name">${displayName}</div>
                                <div class="model-score ${scoreClass}">${scoreText}</div>
                            </div>
                            <div class="model-content">
                    `;

                    // 提取的答案
                    if (extracted_prediction) {
                        html += `
                            <div class="extracted-answer">
                                <div class="extracted-label">提取的答案</div>
                                <div class="extracted-content">${escapeHtml(extracted_prediction)}</div>
                            </div>
                        `;
                    }

                    // 完整回答
                    if (prediction) {
                        html += `
                            <div class="prediction-section">
                                <div class="prediction-label">完整回答</div>
                                <div class="prediction-content">${escapeHtml(prediction)}</div>
                            </div>
                        `;
                    }

                    html += `
                            </div>
                        </div>
                    `;
                });

                html += `
                        </div>
                    </div>
                `;
            }

            // 更新DOM
            detailContentEl.innerHTML = html;
            emptyStateEl.classList.add('hidden');
            detailContentEl.classList.remove('hidden');
        }

        // 设置事件监听器
        function setupEventListeners() {
            // 分类过滤器
            categoryFilterEl.addEventListener('change', function() {
                currentCategory = this.value;
                filterSamples();
            });

            // 搜索框
            searchBoxEl.addEventListener('input', function() {
                filterSamples();
            });
        }

        // 筛选样本
        function filterSamples() {
            const category = categoryFilterEl.value;
            const searchTerm = searchBoxEl.value.toLowerCase();

            let filtered = allSamples;

            // 按类别筛选
            if (category) {
                filtered = filtered.filter(sample => sample.category === category);
            }

            // 按搜索词筛选
            if (searchTerm) {
                filtered = filtered.filter(sample => {
                    const input = sample.sampleData.input || '';
                    const target = sample.sampleData.target || '';
                    const questionId = sample.sampleData.question_id || '';

                    return input.toLowerCase().includes(searchTerm) ||
                           target.toLowerCase().includes(searchTerm) ||
                           questionId.toLowerCase().includes(searchTerm);
                });
            }

            renderSampleList(filtered);
        }

        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', init);
    </script>
</body>
</html>'''

    return html_template

def main():
    """主函数"""
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "integrated_math_500.json"

    if not os.path.exists(input_file):
        print(f"错误：输入文件不存在 {input_file}", file=sys.stderr)
        sys.exit(1)

    print(f"加载数据文件: {input_file}")
    data = load_json_data(input_file)

    print("生成HTML...")
    html_content = generate_html(data)

    output_file = "math_500_comparison.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML生成完成，保存到 {output_file}")
    print(f"文件大小: {len(html_content) / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    main()