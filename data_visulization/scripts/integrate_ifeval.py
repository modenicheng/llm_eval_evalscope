#!/usr/bin/env python3
"""
整合所有模型的ifeval评测结果，生成一个统一的JSON文件。
"""

import json
import glob
import os
from pathlib import Path
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

def integrate_data(base_path="data_process/eval_result/reviews"):
    """
    整合所有模型的数据。
    返回数据结构：{
        "ifeval": {  # 单一类别
            index: {
                "input": str,
                "target": str,
                "models": {
                    model_name: {
                        "prediction": str,
                        "acc": float,  # 使用main_score_name对应的评分
                        "explanation": str,  # 可能为空
                        "metadata": dict,
                        "all_scores": dict  # 所有评分
                    }
                }
            }
        }
    }
    """
    integrated = defaultdict(lambda: defaultdict(dict))
    # 存储每个index的input和target（从第一个模型读取）
    input_target_cache = {}
    category = "ifeval"  # 固定类别名称

    for model in MODEL_DIRS:
        model_path = os.path.join(base_path, model)
        if not os.path.exists(model_path):
            print(f"警告：模型目录不存在 {model_path}", file=sys.stderr)
            continue

        # 查找ifeval_default.jsonl文件
        filepath = os.path.join(model_path, "ifeval_default.jsonl")
        if not os.path.exists(filepath):
            print(f"警告：模型 {model} 中没有找到ifeval_default.jsonl文件", file=sys.stderr)
            continue

        print(f"处理 {model} - ifeval")

        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"错误：文件 {filepath} 第 {line_num} 行JSON解析失败: {e}", file=sys.stderr)
                    continue

                index = data.get("index")
                if index is None:
                    print(f"警告：文件 {filepath} 第 {line_num} 行缺少index字段", file=sys.stderr)
                    continue

                # 获取input和target（如果尚未缓存）
                key = (category, index)
                if key not in input_target_cache:
                    input_text = data.get("input", "")
                    target_text = data.get("target", "")
                    input_target_cache[key] = (input_text, target_text)

                # 获取模型输出
                sample_score = data.get("sample_score", {})
                score = sample_score.get("score", {})
                # 优先使用extracted_prediction，其次使用prediction
                prediction = score.get("extracted_prediction")
                if prediction is None:
                    prediction = score.get("prediction", "")

                # 获取评分
                value_dict = score.get("value", {})
                main_score_name = score.get("main_score_name", "prompt_level_strict")

                # 使用main_score_name对应的评分，如果没有则使用prompt_level_strict
                if main_score_name in value_dict:
                    acc = value_dict[main_score_name]
                elif "prompt_level_strict" in value_dict:
                    acc = value_dict["prompt_level_strict"]
                else:
                    # 取第一个可用的评分
                    acc = next(iter(value_dict.values())) if value_dict else 0.0

                explanation = score.get("explanation", "")
                metadata = score.get("metadata", {})

                # 确保该category和index的条目存在
                if index not in integrated[category]:
                    integrated[category][index] = {
                        "input": input_target_cache[key][0],
                        "target": input_target_cache[key][1],
                        "models": {}
                    }

                # 存储模型输出
                integrated[category][index]["models"][model] = {
                    "prediction": prediction,
                    "acc": acc,
                    "explanation": explanation,
                    "metadata": metadata,
                    "all_scores": value_dict  # 存储所有评分供参考
                }

    # 将defaultdict转换为普通dict
    result = {cat: dict(indices) for cat, indices in integrated.items()}
    return result

def main():
    base_path = "data_process/eval_result/reviews"
    if not os.path.exists(base_path):
        print(f"错误：基础路径不存在 {base_path}", file=sys.stderr)
        sys.exit(1)

    print("开始整合ifeval数据...")
    integrated_data = integrate_data(base_path)

    output_file = "integrated_ifeval.json"
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
            num_models = len(data["models"])
            model_counts[num_models] += 1

    print("\n模型覆盖统计:")
    for num_models, count in sorted(model_counts.items()):
        print(f"  有{num_models}个模型的样本: {count}个")

    # 打印评分信息示例
    if total_samples > 0:
        first_category = list(integrated_data.keys())[0]
        first_index = list(integrated_data[first_category].keys())[0]
        first_sample = integrated_data[first_category][first_index]
        if first_sample["models"]:
            first_model = list(first_sample["models"].keys())[0]
            first_model_data = first_sample["models"][first_model]
            print(f"\n第一个样本评分示例:")
            print(f"  主要评分 (acc): {first_model_data['acc']}")
            print(f"  所有评分: {first_model_data.get('all_scores', {})}")

if __name__ == "__main__":
    main()