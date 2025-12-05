#!/usr/bin/env python3
"""
整合所有模型的swe_bench评测结果，生成一个统一的JSON文件。
只需要从reviews文件夹下的jsonl文件提取数据，不需要查看原始输出。
处理一个文件：swe_bench_verified_mini_default.jsonl
"""

import json
import os
from collections import defaultdict
import sys

# 模型目录列表（六个模型）
MODEL_DIRS = [
    "deepseek-reasoner-v3.2",
    "deepseek-reasoner-v3.2-exp",
    "deepseek-reasoner-v3.2-special",
    "doubao-seed-1-6-251015",
    "qwen3-max",
    "qwen-plus"
]

def extract_category(filename):
    """
    从文件名中提取类别名称。
    例如：swe_bench_verified_mini_default.jsonl -> swe_bench_verified_mini_default
    """
    basename = os.path.basename(filename)
    if basename.endswith(".jsonl"):
        basename = basename[:-len(".jsonl")]
    return basename

def load_reviews_data(base_path="data_process/eval_result/reviews"):
    """
    从reviews目录加载所有模型的评分信息。
    返回数据结构：{
        category: {
            index: {
                model_name: {
                    "prediction": str,      # 模型完整回答
                    "extracted_prediction": str,  # 提取的patch
                    "acc": float,           # 准确率 (1.0或0.0)
                    "explanation": str,     # 解释
                    "metadata": dict,       # 元数据
                    "sample_metadata": dict # 样本元数据
                }
            }
        }
    }
    """
    reviews_data = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

    # swe_bench只有一个文件
    file_patterns = [
        "swe_bench_verified_mini_default.jsonl"
    ]

    for model in MODEL_DIRS:
        model_path = os.path.join(base_path, model)
        if not os.path.exists(model_path):
            print(f"警告：reviews模型目录不存在 {model_path}", file=sys.stderr)
            continue

        for filename in file_patterns:
            filepath = os.path.join(model_path, filename)
            if not os.path.exists(filepath):
                print(f"警告：模型 {model} 中没有找到reviews文件 {filename}", file=sys.stderr)
                continue

            category = extract_category(filepath)
            print(f"加载reviews数据 {model} - {category}")

            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError as e:
                        print(f"错误：reviews文件 {filepath} 第 {line_num} 行JSON解析失败: {e}", file=sys.stderr)
                        continue

                    index = data.get("index")
                    if index is None:
                        print(f"警告：reviews文件 {filepath} 第 {line_num} 行缺少index字段", file=sys.stderr)
                        continue

                    # 获取模型输出和评分
                    sample_score = data.get("sample_score", {})
                    score = sample_score.get("score", {})

                    # 提取预测信息
                    extracted_prediction = score.get("extracted_prediction", "")
                    prediction = score.get("prediction", "")
                    if not extracted_prediction and prediction:
                        # 如果没有提取的预测，使用完整预测的前200个字符
                        extracted_prediction = prediction[:200] + "..." if len(prediction) > 200 else prediction

                    value_dict = score.get("value", {})
                    # swe_bench使用acc字段
                    if "acc" in value_dict:
                        acc = value_dict["acc"]
                    else:
                        # 如果没有acc，尝试获取其他评分
                        acc = next(iter(value_dict.values())) if value_dict else 0.0

                    explanation = score.get("explanation", "")
                    metadata = score.get("metadata", {})
                    sample_metadata = sample_score.get("sample_metadata", {})

                    # 输入和目标
                    input_text = data.get("input", "")
                    target = data.get("target", "")  # 可能为空

                    reviews_data[category][index][model] = {
                        "prediction": prediction,
                        "extracted_prediction": extracted_prediction,
                        "acc": acc,
                        "explanation": explanation,
                        "metadata": metadata,
                        "sample_metadata": sample_metadata,
                        "input": input_text,
                        "target": target
                    }

    # 将defaultdict转换为普通dict
    result = {cat: dict(indices) for cat, indices in reviews_data.items()}
    return result

def integrate_data():
    """
    整合数据。
    返回最终数据结构：{
        "swe_bench_verified_mini_default": {
            index: {
                "input": str,          # 题目（issue和代码）
                "target": str,         # 正确答案（可能为空）
                "category": str,       # 类别
                "models": {
                    model_name: {
                        "prediction": str,
                        "extracted_prediction": str,
                        "acc": float,
                        "explanation": str,
                        "metadata": dict,
                        "sample_metadata": dict
                    }
                }
            }
        }
    }
    """
    print("开始加载reviews数据...")
    reviews_data = load_reviews_data()

    print("开始整合数据...")
    integrated = defaultdict(lambda: defaultdict(dict))

    for category, indices in reviews_data.items():
        for index, model_scores in indices.items():
            # 从第一个模型中获取样本信息
            first_model = next(iter(model_scores.values()))
            sample_metadata = first_model.get("sample_metadata", {})

            # 获取输入和目标
            input_text = first_model.get("input", "")
            target = first_model.get("target", "")

            integrated[category][index] = {
                "input": input_text,
                "target": target,
                "category": category,
                "models": dict(model_scores)
            }

    # 将defaultdict转换为普通dict
    result = {cat: dict(indices) for cat, indices in integrated.items()}
    return result

def main():
    # 检查目录是否存在
    reviews_path = "data_process/eval_result/reviews"

    if not os.path.exists(reviews_path):
        print(f"错误：reviews路径不存在 {reviews_path}", file=sys.stderr)
        sys.exit(1)

    print("开始整合swe_bench数据...")
    integrated_data = integrate_data()

    output_file = "integrated_swebench.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(integrated_data, f, ensure_ascii=False, indent=2)

    print(f"数据整合完成，保存到 {output_file}")

    # 打印统计信息
    total_categories = len(integrated_data)
    total_samples = sum(len(indices) for indices in integrated_data.values())
    print(f"类别数: {total_categories}")
    print(f"总样本数: {total_samples}")

    # 检查每个样本的模型数量
    model_counts = defaultdict(int)
    for category, indices in integrated_data.items():
        for index, data in indices.items():
            num_models = len(data.get("models", {}))
            model_counts[num_models] += 1

    print("\n模型覆盖统计:")
    for num_models, count in sorted(model_counts.items()):
        print(f"  有{num_models}个模型的样本: {count}个")

    # 打印详细信息示例
    if total_samples > 0:
        first_category = list(integrated_data.keys())[0]
        first_index = list(integrated_data[first_category].keys())[0]
        first_sample = integrated_data[first_category][first_index]

        print(f"\n第一个样本详细信息:")
        print(f"  类别: {first_category}")
        print(f"  索引: {first_index}")
        print(f"  输入长度: {len(first_sample.get('input', ''))} 字符")
        print(f"  目标长度: {len(first_sample.get('target', ''))} 字符")
        print(f"  模型数量: {len(first_sample.get('models', {}))}")

        # 显示第一个模型的信息
        first_model_name = list(first_sample.get("models", {}).keys())[0]
        first_model_data = first_sample["models"][first_model_name]
        print(f"\n  第一个模型 ({first_model_name}) 信息:")
        print(f"    准确率: {first_model_data.get('acc', 0.0)}")
        print(f"    提取的预测长度: {len(first_model_data.get('extracted_prediction', ''))} 字符")
        print(f"    完整预测长度: {len(first_model_data.get('prediction', ''))} 字符")

if __name__ == "__main__":
    main()