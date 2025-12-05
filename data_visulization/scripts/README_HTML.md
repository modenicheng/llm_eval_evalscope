# General QA 评测结果对比 - HTML 版本

这是一个纯 HTML 文件，用于浏览和对比六个模型的 `general_qa` 评测结果。JSON 数据直接嵌入到 HTML 文件中，无需网络连接。

## 功能

- 左侧：样本列表（按类别和索引分组）
- 右侧：样本详情（用户输入、参考答案、六个模型的输出）
- 响应式设计：移动端单列，桌面端双栏布局
- 模型输出网格：移动端单列，平板双列，桌面端三列
- 安全的数据嵌入：使用 `<script type="application/json">` 标签，避免 XSS 风险

## 使用方法

### 1. 生成 HTML 文件

确保已存在整合数据文件 `integrated_general_qa.json`（可通过运行 `integrate_general_qa.py` 生成）。

运行生成脚本：

```bash
python generate_html_viewer_v2.py
```

这将生成 `general_qa_comparison_safe.html` 文件（约 5.8 MB）。

### 2. 在浏览器中打开

双击 HTML 文件或在浏览器中打开：

```bash
# Windows
start general_qa_comparison_safe.html

# macOS
open general_qa_comparison_safe.html

# Linux
xdg-open general_qa_comparison_safe.html
```

### 3. 使用界面

- **左侧面板**：点击任意样本选中
- **右侧面板**：显示选中样本的详细信息
- **自动选中**：加载后默认选中第一个样本
- **响应式布局**：
  - 屏幕宽度 < 768px：单列布局（样本列表在上，详情在下）
  - 屏幕宽度 ≥ 768px：双栏布局（左侧列表，右侧详情）
  - 屏幕宽度 ≥ 1200px：模型输出显示为三列网格

## 文件说明

- `generate_html_viewer_v2.py`：HTML 文件生成脚本（推荐）
- `generate_html_viewer.py`：旧版生成脚本（不安全嵌入方式）
- `general_qa_comparison_safe.html`：生成的 HTML 文件（安全版本）
- `general_qa_comparison.html`：旧版 HTML 文件

## 数据统计

- 7 个类别
- 448 个样本
- 6 个模型（deepseek-reasoner-v3.2, deepseek-reasoner-v3.2-exp, deepseek-reasoner-v3.2-special, doubao-seed-1-6-251015, qwen3-max, qwen-plus）

## 技术细节

- **数据嵌入**：JSON 数据通过 `<script type="application/json">` 标签嵌入，使用 `JSON.parse()` 解析
- **安全性**：所有动态内容都经过 HTML 转义，防止 XSS 攻击
- **性能**：样本列表使用虚拟滚动（通过 CSS `max-height` 和 `overflow-y` 实现）
- **兼容性**：使用现代 CSS（Flexbox, Grid）和原生 JavaScript，兼容主流浏览器

## 扩展

如需支持其他数据集（如 `chinese_simpleqa`、`math_500` 等），可修改 `generate_html_viewer_v2.py` 中的 JSON 文件路径和数据加载逻辑。

## 注意事项

- HTML 文件较大（约 5.8 MB），加载可能需要几秒钟
- 某些样本可能缺少部分模型的输出（通常为 4-6 个模型）
- 模型输出文本可能较长，请使用滚动查看完整内容