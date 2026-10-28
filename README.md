# llm_eval_evalscope

人工智能导论期中项目的基准评测部分，包含全部评测脚本与原始数据。基于 [EvalScope](https://github.com/modelscope/evalscope) 框架对六个模型进行多数据集评测，每模型 1,373 条样本，合计 8,238 条。完整过程与逐题分析请见博文：

**[《小作业-3 LLMs Evaluation》](https://modenc.top/blog/wtn59a4/)**

受限于成本，整体评测规模不是很大，但仍然得到了一些有趣的结论。

## 概述

整个评测项目分三个阶段：Agent 编码试水、基准评测（本仓库）、防污染主观评测。基准成绩受训练集污染与数据集质量影响，部分模型的基准得分与主观使用体验并不相符。因此，我们将基准测评定位为主观评测的参照，结论需主观与客观两部分合并解读。

## 评测设置

| 维度 | 数据集 | 评测方式 |
|---|---|---|
| 指令遵循 | IFEval、Multi IF（中英文子集） | 模式匹配 |
| 事实问答 | Chinese Simple QA | LLM-as-judge |
| 代码 | SWE-bench Verified Mini | Docker 沙箱实测 |
| 数理推理 | MATH-500 | 模式匹配 |
| 价值观对齐 | Safety Prompts（典型安全场景七子集） | LLM-as-judge |

裁判模型为 deepseek-chat，16 并发。评测对象：

- `deepseek-reasoner` —— 三轮独立评测：V3.2-EXP 初测、Speciale 限时版、稳定版复测，占三个数据目录
- `doubao-seed-1-6-251015`
- `qwen3-max`、`qwen-plus`

Gemini 3 Pro 与 Kimi K2 系列因 API 成本过高未纳入基准，仅参与主观评测（见博文）。

## 结果与分析

| 模型 | 安全性 | 事实问答 | 数理推理 | Multi IF | IFEval | 代码 | 平均 |
|---|---|---|---|---|---|---|---|
| qwen-plus | 0.8284 | 0.8464 | 0.9766 | 0.8828 | 0.8906 | 0.1800 | 0.7675 |
| qwen3-max | 0.8352 | 0.8776 | 0.9799 | 0.8047 | 0.8594 | 0.2200 | 0.7628 |
| deepseek-reasoner V3.2 Exp | 0.8080 | 0.6589 | 0.9900 | 0.8984 | 0.9062 | 0.2600 | 0.7536 |
| deepseek-reasoner V3.2 | 0.7924 | 0.6953 | 0.9866 | 0.8203 | 0.9062 | 0.3000 | 0.7501 |
| doubao-seed-1-6-251015 | 0.7991 | 0.6901 | 0.9565 | 0.8125 | 0.8281 | 0.3200 | 0.7344 |
| deepseek-reasoner V3.2 Speciale | 0.7366 | 0.7109 | 0.9900 | 0.7266 | 0.9375 | 0.2800 | 0.7303 |

六个模型平均分集中于 0.73–0.77 区间，无综合领先者，各单项最优分属不同模型：

- **数理推理**：DeepSeek 系列三轮均不低于 0.987。MATH-500 对该批模型区分度不足（全员不低于 0.95），差异主要体现在 Level 3 及以上难度；doubao 自 Level 1 起即出现错误
- **事实问答**：qwen3-max 以 0.8776 领先，人文社科类子集差距最大（0.95 对 0.75）。该结果表明大模型提供的事实信息不足以直接信赖
- **指令遵循**：IFEval 最高分为 Speciale 的 0.9375，Multi IF 综合最高为 Exp 的 0.9010。多数模型英文指令遵循优于中文，doubao 相反
- **代码**：整体准确率偏低（0.18–0.32），doubao 居首，qwen-plus 垫底。各模型 patch 应用率仅 0.46–0.60，应用失败直接计零分，表明相当比例的失败源于补丁生成环节（复述既有代码）而非修复逻辑本身
- **价值观对齐**：Qwen 系列占据前二，Speciale 以 0.7366 垫底

综合主客观两部分（详见博文）：Gemini 3 Pro、Qwen3-Max、DeepSeek V3.2 Reasoner 构成第一梯队；qwen-plus 基准得分较高而主观体验不匹配。计入 API 成本后，多数场景下 DeepSeek V3.2 Reasoner 为质价比最优选择。

## 讨论

- **评测有效性**。裁判模型存在误判；Safety Prompts 部分题目以续写而非提问的形式给出，参考答案立场过度中立，致使符合主流价值观的回答被判错。人工复审表明各模型在价值观对齐上差异有限，该项分数差异主要来自数据集质量
- **Speciale 异常行为**。中文输入返回英文、将提示词识别为翻译任务、对安全场景仅输出单个字符 `D`。官方说明中提及，该模型仅在推理数据上训练并减小了 RL 长度惩罚。但在测评中，我们观察到其在非数学任务上平均输出长度反而更短，与预期相反
- **语料痕迹**。Doubao 与 Qwen 系列输出风格高度相似（主观感受，没有实际进行统计分析），提示两家训练数据重叠度可能较高，且均与 DeepSeek 差异明显；Qwen 在人文社科知识上的显著优势，或可归因于训练语料较好
- **裁判成本**。deepseek-chat 的输出 token 数恰好等于请求次数，即严格遵循了仅输出判定字母的评分指令；总消耗 600 万 token 仅花费 ¥6.33，主要得益于高缓存命中率
- MATH-500 中一道几何题可使 DeepSeek Reasoner 较稳定进入仅推理、无正文输出的状态，API 与网页端均可复现

## 成本

基准评测总成本约 ¥66，其中约 ¥18 源于一次配置错误导致的重测（deepseek-reasoner 被误设为所有题目都通过裁判模型打分）。连同主观评测，全程总成本 ¥72.73，详细成本列表见博文。

## 目录结构

- `eval_*.py` —— 每模型一份 TaskConfig 脚本，`uv run` 可直接运行；安全数据集单独一份（`*_safety_prompts.py`）
- `main.py` —— Safety Prompts 预处理，原 JSON 拆成各子集 jsonl
- `data_process/eval_result/` —— 全部原始数据：`predictions/` 模型输出、`reviews/` 逐样本打分、`reports/` 汇总指标，共 302 个文件
- `data_process/` —— 合并与出图管线：`merge_*.py` 将各模型报告合并为 Chart.js 格式的 `merged_evaluation_data.json`；`generate_*_report.py` 产出 `evaluation_report.md`（66 张图）；swebench 系列脚本抽取代码评测的检查点明细
- `data_visulization/` —— 分数据集的 HTML 对比页。用于嵌入 Blog

## License

MIT
