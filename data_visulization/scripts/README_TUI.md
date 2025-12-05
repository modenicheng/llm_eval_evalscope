# General QA 评测结果对比工具

此工具用于整合六个模型的 `general_qa` 评测结果，并通过 TUI（文本用户界面）进行浏览和对比。

## 功能

- 整合所有六个模型的 `general_qa` 评测结果（包括七个类别：Crimes_And_Illegal_Activities、Ethics_And_Morality、Insult、Mental_Health、Physical_Harm、Privacy_And_Property、Unfairness_And_Discrimination）
- 提供交互式 TUI 界面，包含：
  - 左侧：样本列表（按类别和索引分组）
  - 右侧：样本详情（用户输入、参考答案、六个模型的输出）
  - 搜索功能：按用户输入文本过滤样本
  - 键盘导航：j/k 上下移动，Enter 选择，f 聚焦搜索框，q 退出

## 使用方法

### 1. 安装依赖

需要 Python 3.10+ 和 Textual 库：

```bash
pip install textual
```

### 2. 整合数据

运行整合脚本，生成统一的数据文件：

```bash
python integrate_general_qa.py
```

这将生成 `integrated_general_qa.json` 文件，包含所有样本和模型输出。

### 3. 启动 TUI

运行 TUI 程序：

```bash
python tui_app.py
```

### 4. 键盘快捷键

- `j` / `k`：在样本列表中上下移动
- `Enter`：选择当前样本（查看详情）
- `f`：聚焦搜索框
- `q`：退出程序

## 文件结构

- `integrate_general_qa.py`：数据整合脚本
- `tui_app.py`：TUI 主程序
- `integrated_general_qa.json`：生成的整合数据（第一次运行后产生）
- `data_process/eval_result/reviews/`：原始评测结果数据

## 数据格式

整合后的 JSON 文件结构：

```json
{
  "类别名称": {
    "索引号": {
      "input": "用户输入",
      "target": "参考答案",
      "models": {
        "模型名称": {
          "prediction": "模型输出",
          "acc": 准确率,
          "explanation": "LLM 评判结果",
          "metadata": { ... }
        },
        ...
      }
    }
  }
}
```

## 注意事项

- 某些样本可能缺少部分模型的输出（通常为 4-6 个模型）
- 搜索功能仅对用户输入文本进行简单子串匹配
- 模型输出文本可能较长，请使用滚动查看

## 扩展

如需整合其他数据集（如 `chinese_simpleqa`、`math_500` 等），可修改 `integrate_general_qa.py` 中的文件匹配模式。