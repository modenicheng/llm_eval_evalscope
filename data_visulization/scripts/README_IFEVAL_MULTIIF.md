# IFEval 和 Multi-IF 评测结果对比 - HTML 可视化文件

这是为 `ifeval` 和 `multi-if` 两个指令集生成的HTML可视化文件，用于浏览和对比六个模型的评测结果。功能与之前的 `general_qa` 可视化文件相同。

## 生成的文件

### IFEval
1. `integrated_ifeval.json` - 整合后的JSON数据（64个样本，6个模型）
2. `ifeval_comparison_safe.html` - HTML可视化文件（约921 KB）

### Multi-IF
1. `integrated_multi_if.json` - 整合后的JSON数据（2个类别：Chinese和English，共128个样本，6个模型）
2. `multi_if_comparison_safe.html` - HTML可视化文件（约1.9 MB）

## 功能特点

- **左侧面板**：样本列表（按类别和索引分组）
- **右侧面板**：样本详情（用户输入、模型输出）
- **响应式设计**：移动端单列，桌面端双栏布局
- **模型输出网格**：移动端单列，平板双列，桌面端三列
- **安全的数据嵌入**：使用 `<script type="application/json">` 标签，避免 XSS 风险
- **详细评分显示**：显示主要评分和所有详细评分

## 数据格式说明

### IFEval 数据特点
- 单一类别："ifeval"
- 64个样本
- 每个样本有6个模型的输出
- 评分包含：prompt_level_strict, inst_level_strict, prompt_level_loose, inst_level_loose
- 使用 `prompt_level_strict` 作为主要评分（acc字段）

### Multi-IF 数据特点
- 两个类别："multi_if_Chinese"（中文）, "multi_if_English"（英文）
- 每个类别64个样本，共128个样本
- 每个样本有6个模型的输出
- 评分按turn分组：turn_1, turn_2, turn_3，每个turn有prompt_level_strict, inst_level_strict, prompt_level_loose, inst_level_loose
- 使用 `turn_3_prompt_level_strict` 作为主要评分（acc字段）

## 使用方法

### 1. 生成数据文件（如果尚未生成）
```bash
# 生成ifeval整合数据
python integrate_ifeval.py

# 生成multi-if整合数据
python integrate_multi_if.py
```

### 2. 生成HTML文件（如果尚未生成）
```bash
# 生成ifeval HTML文件
python generate_ifeval_html.py

# 生成multi-if HTML文件
python generate_multi_if_html.py
```

### 3. 在浏览器中打开
```bash
# Windows
start ifeval_comparison_safe.html
start multi_if_comparison_safe.html

# macOS
open ifeval_comparison_safe.html
open multi_if_comparison_safe.html

# Linux
xdg-open ifeval_comparison_safe.html
xdg-open multi_if_comparison_safe.html
```

### 4. 使用界面
- **左侧面板**：点击任意样本选中
- **右侧面板**：显示选中样本的详细信息
- **自动选中**：加载后默认选中第一个样本
- **响应式布局**：
  - 屏幕宽度 < 768px：单列布局（样本列表在上，详情在下）
  - 屏幕宽度 ≥ 768px：双栏布局（左侧列表，右侧详情）
  - 屏幕宽度 ≥ 1200px：模型输出显示为三列网格

## 脚本说明

### 数据整合脚本
- `integrate_ifeval.py` - 整合ifeval评测结果
- `integrate_multi_if.py` - 整合multi-if评测结果

### HTML生成脚本
- `generate_ifeval_html.py` - 生成ifeval HTML文件
- `generate_multi_if_html.py` - 生成multi-if HTML文件

### 测试脚本
- `test_ifeval_multi_if_html.py` - 测试HTML文件结构

## 技术细节

- **数据嵌入**：JSON数据通过 `<script type="application/json">` 标签嵌入，使用 `JSON.parse()` 解析
- **安全性**：所有动态内容都经过HTML转义，防止XSS攻击
- **性能**：样本列表使用虚拟滚动（通过CSS `max-height` 和 `overflow-y` 实现）
- **兼容性**：使用现代CSS（Flexbox, Grid）和原生JavaScript，兼容主流浏览器

## 扩展

如需支持其他数据集，可参考现有脚本的结构：
1. 创建数据整合脚本（参考 `integrate_ifeval.py`）
2. 创建HTML生成脚本（参考 `generate_ifeval_html.py`）
3. 确保数据格式与现有结构兼容

## 注意事项

- HTML文件较大（ifeval约921KB，multi-if约1.9MB），加载可能需要几秒钟
- 模型输出文本可能较长，请使用滚动查看完整内容
- 某些样本的输入可能为空（特别是multi-if数据集）
- 评分显示包含所有详细评分，便于深入分析模型表现