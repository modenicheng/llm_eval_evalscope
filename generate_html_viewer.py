#!/usr/bin/env python3
"""
生成一个独立的HTML文件，用于浏览和对比六个模型的general_qa评测结果。
JSON数据直接嵌入到HTML文件中。
"""

import json
import os
import sys
from pathlib import Path

def load_json_data(json_path):
    """加载JSON数据"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_html(data):
    """生成HTML内容"""
    # 将数据转换为JSON字符串，用于JavaScript
    json_str = json.dumps(data, ensure_ascii=False)

    # HTML模板
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>General QA 评测结果对比</title>
    <style>
        /* 基础重置 */
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
            padding: 10px;
            min-height: 100vh;
        }}

        .app-header {{
            text-align: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #dee2e6;
        }}

        .app-header h1 {{
            font-size: 1.8rem;
            color: #2c3e50;
            margin-bottom: 5px;
        }}

        .app-header .stats {{
            font-size: 0.9rem;
            color: #7f8c8d;
        }}

        /* 主容器 */
        .app-container {{
            display: flex;
            flex-direction: column;
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }}

        /* 样本列表 */
        .samples-panel {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            overflow: hidden;
        }}

        .samples-header {{
            padding: 15px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            font-weight: bold;
            color: #2c3e50;
        }}

        .samples-list {{
            max-height: 400px;
            overflow-y: auto;
        }}

        .sample-item {{
            padding: 12px 15px;
            border-bottom: 1px solid #f1f1f1;
            cursor: pointer;
            transition: background-color 0.2s;
        }}

        .sample-item:hover {{
            background-color: #f8f9fa;
        }}

        .sample-item.active {{
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
        }}

        .sample-category {{
            font-weight: bold;
            color: #2c3e50;
            font-size: 0.9rem;
        }}

        .sample-preview {{
            font-size: 0.85rem;
            color: #666;
            margin-top: 4px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        /* 详情面板 */
        .detail-panel {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            overflow: hidden;
        }}

        .detail-header {{
            padding: 15px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            font-weight: bold;
            color: #2c3e50;
        }}

        .detail-content {{
            padding: 20px;
        }}

        .section {{
            margin-bottom: 30px;
        }}

        .section-title {{
            font-size: 1.1rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 2px solid #e9ecef;
        }}

        .content-box {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #e9ecef;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 0.95rem;
            line-height: 1.6;
        }}

        .model-outputs {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
        }}

        .model-card {{
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}

        .model-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding-bottom: 8px;
            border-bottom: 1px solid #e9ecef;
        }}

        .model-name {{
            font-weight: bold;
            color: #2c3e50;
            font-size: 1rem;
        }}

        .model-acc {{
            background: #e8f5e9;
            color: #2e7d32;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: bold;
        }}

        .model-prediction {{
            margin-bottom: 10px;
            font-size: 0.95rem;
            line-height: 1.6;
        }}

        .model-explanation {{
            font-size: 0.85rem;
            color: #666;
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            border-left: 3px solid #ff9800;
        }}

        /* 移动端适配 */
        @media (min-width: 768px) {{
            .app-container {{
                flex-direction: row;
                height: calc(100vh - 100px);
            }}

            .samples-panel {{
                width: 300px;
                height: 100%;
                display: flex;
                flex-direction: column;
            }}

            .samples-list {{
                flex: 1;
                max-height: none;
            }}

            .detail-panel {{
                flex: 1;
                height: 100%;
                overflow-y: auto;
            }}

            .model-outputs {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}

        @media (min-width: 1200px) {{
            .model-outputs {{
                grid-template-columns: repeat(3, 1fr);
            }}
        }}

        /* 滚动条样式 */
        ::-webkit-scrollbar {{
            width: 8px;
        }}

        ::-webkit-scrollbar-track {{
            background: #f1f1f1;
        }}

        ::-webkit-scrollbar-thumb {{
            background: #c1c1c1;
            border-radius: 4px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: #a8a8a8;
        }}

        /* 工具提示 */
        .tooltip {{
            position: relative;
            display: inline-block;
        }}

        .tooltip .tooltiptext {{
            visibility: hidden;
            width: 200px;
            background-color: #555;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 0.8rem;
        }}

        .tooltip:hover .tooltiptext {{
            visibility: visible;
            opacity: 1;
        }}

        /* 空状态 */
        .empty-state {{
            text-align: center;
            padding: 40px 20px;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="app-header">
        <h1>General QA 评测结果对比</h1>
        <div class="stats">
            <span id="stats-categories">7</span> 个类别 •
            <span id="stats-samples">448</span> 个样本 •
            <span id="stats-models">6</span> 个模型
        </div>
    </div>

    <div class="app-container">
        <!-- 左侧：样本列表 -->
        <div class="samples-panel">
            <div class="samples-header">
                样本列表
                <span id="sample-count" style="float: right; font-weight: normal; font-size: 0.9rem;"></span>
            </div>
            <div class="samples-list" id="samples-list">
                <!-- 样本项将通过JavaScript动态生成 -->
                <div class="empty-state">正在加载样本...</div>
            </div>
        </div>

        <!-- 右侧：详情面板 -->
        <div class="detail-panel">
            <div class="detail-header">
                样本详情
                <span id="detail-title" style="float: right; font-weight: normal; font-size: 0.9rem;"></span>
            </div>
            <div class="detail-content" id="detail-content">
                <div class="empty-state">
                    请从左侧选择一个样本来查看详情
                </div>
            </div>
        </div>
    </div>

    <script>
        // 嵌入式JSON数据
        const evaluationData = {json_str};

        // 应用状态
        let currentSample = null;
        let currentCategory = null;
        let currentIndex = null;

        // DOM元素
        const samplesListEl = document.getElementById('samples-list');
        const detailContentEl = document.getElementById('detail-content');
        const detailTitleEl = document.getElementById('detail-title');
        const sampleCountEl = document.getElementById('sample-count');

        // 初始化
        function init() {{
            updateStats();
            renderSamplesList();
            // 默认选择第一个样本
            if (Object.keys(evaluationData).length > 0) {{
                const firstCategory = Object.keys(evaluationData)[0];
                const firstIndex = Object.keys(evaluationData[firstCategory])[0];
                selectSample(firstCategory, parseInt(firstIndex));
            }}
        }}

        // 更新统计信息
        function updateStats() {{
            let totalCategories = Object.keys(evaluationData).length;
            let totalSamples = 0;
            let modelCount = 0;

            for (const category in evaluationData) {{
                totalSamples += Object.keys(evaluationData[category]).length;
                // 获取第一个样本的模型数量
                if (modelCount === 0) {{
                    const firstIndex = Object.keys(evaluationData[category])[0];
                    if (firstIndex) {{
                        const sample = evaluationData[category][firstIndex];
                        modelCount = Object.keys(sample.models || {{}}).length;
                    }}
                }}
            }}

            document.getElementById('stats-categories').textContent = totalCategories;
            document.getElementById('stats-samples').textContent = totalSamples;
            document.getElementById('stats-models').textContent = modelCount;
        }}

        // 渲染样本列表
        function renderSamplesList() {{
            samplesListEl.innerHTML = '';

            let sampleCount = 0;

            // 按类别和索引排序
            const categories = Object.keys(evaluationData).sort();

            for (const category of categories) {{
                const indices = Object.keys(evaluationData[category]).sort((a, b) => parseInt(a) - parseInt(b));

                for (const index of indices) {{
                    const sample = evaluationData[category][index];
                    const inputText = sample.input || '';
                    // 移除**User**: 前缀
                    const previewText = inputText.replace(/^\\*\\*User\\*\\*:\\\\s*\\\\n/, '').substring(0, 80);

                    const itemEl = document.createElement('div');
                    itemEl.className = 'sample-item';
                    itemEl.dataset.category = category;
                    itemEl.dataset.index = index;
                    itemEl.innerHTML = `
                        <div class="sample-category">${{category}} #${{index}}</div>
                        <div class="sample-preview" title="${{inputText}}">${{previewText}}...</div>
                    `;

                    itemEl.addEventListener('click', () => {{
                        selectSample(category, parseInt(index));
                    }});

                    samplesListEl.appendChild(itemEl);
                    sampleCount++;
                }}
            }}

            sampleCountEl.textContent = `${{sampleCount}} 个样本`;

            if (sampleCount === 0) {{
                samplesListEl.innerHTML = '<div class="empty-state">没有找到样本数据</div>';
            }}
        }}

        // 选择样本
        function selectSample(category, index) {{
            // 更新当前选中状态
            currentCategory = category;
            currentIndex = index;
            currentSample = evaluationData[category][index];

            // 更新列表项选中状态
            document.querySelectorAll('.sample-item').forEach(item => {{
                item.classList.remove('active');
                if (item.dataset.category === category && item.dataset.index === index.toString()) {{
                    item.classList.add('active');
                }}
            }});

            // 渲染详情
            renderSampleDetail();
        }}

        // 渲染样本详情
        function renderSampleDetail() {{
            if (!currentSample) return;

            const inputText = currentSample.input || '';
            const targetText = currentSample.target || '';
            const models = currentSample.models || {{}};

            // 构建模型输出HTML
            let modelsHTML = '';
            const modelEntries = Object.entries(models);

            for (const [modelName, modelData] of modelEntries) {{
                const prediction = modelData.prediction || '';
                const acc = modelData.acc || 0.0;
                const explanation = modelData.explanation || '';

                modelsHTML += `
                    <div class="model-card">
                        <div class="model-header">
                            <div class="model-name">${{modelName}}</div>
                            <div class="model-acc">准确率: ${{acc.toFixed(2)}}</div>
                        </div>
                        <div class="model-prediction">${{prediction}}</div>
                        <div class="model-explanation">
                            <strong>评判结果:</strong> ${{explanation}}
                        </div>
                    </div>
                `;
            }}

            detailTitleEl.textContent = `${{currentCategory}} #${{currentIndex}}`;

            detailContentEl.innerHTML = `
                <div class="section">
                    <div class="section-title">用户输入</div>
                    <div class="content-box">${{inputText}}</div>
                </div>

                <div class="section">
                    <div class="section-title">参考答案</div>
                    <div class="content-box">${{targetText}}</div>
                </div>

                <div class="section">
                    <div class="section-title">模型输出 (${{modelEntries.length}} 个模型)</div>
                    <div class="model-outputs">
                        ${{modelsHTML}}
                    </div>
                </div>
            `;
        }}

        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', init);
    </script>
</body>
</html>'''
    return html

def main():
    json_path = "integrated_general_qa.json"
    output_path = "general_qa_comparison.html"

    if not os.path.exists(json_path):
        print(f"错误：JSON文件不存在 {json_path}", file=sys.stderr)
        print("请先运行 integrate_general_qa.py 生成整合数据", file=sys.stderr)
        sys.exit(1)

    print("正在加载JSON数据...")
    data = load_json_data(json_path)

    print("正在生成HTML文件...")
    html_content = generate_html(data)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML文件已生成: {output_path}")
    print(f"文件大小: {os.path.getsize(output_path) // 1024} KB")
    print("请在浏览器中打开此文件查看结果。")

if __name__ == "__main__":
    main()