#!/usr/bin/env python3
"""
整合所有模型的multi-if评测结果，生成一个统一的JSON文件。
从predictions文件提取完整的对话历史，从reviews文件提取评分信息。
处理两个文件：multi_if_Chinese.jsonl 和 multi_if_English.jsonl
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
    例如：multi_if_Chinese.jsonl -> multi_if_Chinese
         multi_if_English.jsonl -> multi_if_English
    """
    basename = os.path.basename(filename)
    if basename.endswith(".jsonl"):
        basename = basename[:-len(".jsonl")]
    return basename

def load_predictions_data(base_path="data_process/eval_result/predictions"):
    """
    从predictions目录加载所有模型的完整对话历史。
    返回数据结构：{
        category: {
            index: {
                "messages": list,  # 完整的对话历史
                "metadata": dict,   # 元数据（包含step_record等）
                "language": str,    # 语言
                "key": str          # 唯一标识
            }
        }
    }
    """
    predictions_data = defaultdict(lambda: defaultdict(dict))
    file_patterns = ["multi_if_Chinese.jsonl", "multi_if_English.jsonl"]

    for model in MODEL_DIRS:
        model_path = os.path.join(base_path, model)
        if not os.path.exists(model_path):
            print(f"警告：predictions模型目录不存在 {model_path}", file=sys.stderr)
            continue

        for filename in file_patterns:
            filepath = os.path.join(model_path, filename)
            if not os.path.exists(filepath):
                print(f"警告：模型 {model} 中没有找到predictions文件 {filename}", file=sys.stderr)
                continue

            category = extract_category(filepath)
            print(f"加载predictions数据 {model} - {category}")

            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError as e:
                        print(f"错误：predictions文件 {filepath} 第 {line_num} 行JSON解析失败: {e}", file=sys.stderr)
                        continue

                    index = data.get("index")
                    if index is None:
                        print(f"警告：predictions文件 {filepath} 第 {line_num} 行缺少index字段", file=sys.stderr)
                        continue

                    # 获取messages和metadata
                    messages = data.get("messages", [])
                    metadata = data.get("metadata", {})
                    language = metadata.get("language", "unknown")
                    key = metadata.get("key", f"unknown_{index}")

                    # 如果是第一个模型的数据，存储基础信息
                    if index not in predictions_data[category]:
                        predictions_data[category][index] = {
                            "messages": messages,
                            "metadata": metadata,
                            "language": language,
                            "key": key
                        }

    # 将defaultdict转换为普通dict
    result = {cat: dict(indices) for cat, indices in predictions_data.items()}
    return result

def load_reviews_data(base_path="data_process/eval_result/reviews"):
    """
    从reviews目录加载所有模型的评分信息。
    返回数据结构：{
        category: {
            index: {
                model_name: {
                    "prediction": str,
                    "acc": float,
                    "explanation": str,
                    "metadata": dict,
                    "all_scores": dict,
                    "language": str
                }
            }
        }
    }
    """
    reviews_data = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    file_patterns = ["multi_if_Chinese.jsonl", "multi_if_English.jsonl"]

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
                    prediction = score.get("extracted_prediction")
                    if prediction is None:
                        prediction = score.get("prediction", "")

                    value_dict = score.get("value", {})
                    main_score_name = score.get("main_score_name", "turn_3_prompt_level_strict")

                    # 使用main_score_name对应的评分
                    if main_score_name in value_dict:
                        acc = value_dict[main_score_name]
                    elif "turn_3_prompt_level_strict" in value_dict:
                        acc = value_dict["turn_3_prompt_level_strict"]
                    else:
                        acc = next(iter(value_dict.values())) if value_dict else 0.0

                    explanation = score.get("explanation", "")
                    metadata = score.get("metadata", {})
                    sample_metadata = sample_score.get("sample_metadata", {})
                    language = sample_metadata.get("language", "unknown")

                    reviews_data[category][index][model] = {
                        "prediction": prediction,
                        "acc": acc,
                        "explanation": explanation,
                        "metadata": metadata,
                        "all_scores": value_dict,
                        "language": language
                    }

    # 将defaultdict转换为普通dict
    result = {cat: dict(indices) for cat, indices in reviews_data.items()}
    return result

def integrate_data():
    """
    整合predictions和reviews数据。
    返回最终数据结构：{
        "multi_if_Chinese": {
            index: {
                "messages": list,      # 完整的对话历史
                "metadata": dict,      # 元数据（包含step_record等）
                "language": str,       # 语言
                "key": str,            # 唯一标识
                "models": {
                    model_name: {
                        "prediction": str,
                        "acc": float,
                        "explanation": str,
                        "metadata": dict,
                        "all_scores": dict,
                        "language": str
                    }
                }
            }
        },
        "multi_if_English": {...}
    }
    """
    print("开始加载predictions数据...")
    predictions_data = load_predictions_data()

    print("开始加载reviews数据...")
    reviews_data = load_reviews_data()

    print("开始整合数据...")
    integrated = defaultdict(lambda: defaultdict(dict))

    # 合并数据
    for category in set(list(predictions_data.keys()) + list(reviews_data.keys())):
        # 获取该类别在predictions和reviews中的所有索引
        pred_indices = set(predictions_data.get(category, {}).keys())
        rev_indices = set(reviews_data.get(category, {}).keys())
        all_indices = pred_indices.union(rev_indices)

        for index in all_indices:
            # 获取predictions数据
            pred_info = predictions_data.get(category, {}).get(index, {})
            # 获取reviews数据（模型评分）
            model_scores = reviews_data.get(category, {}).get(index, {})

            # 构建整合后的条目
            integrated[category][index] = {
                "messages": pred_info.get("messages", []),
                "metadata": pred_info.get("metadata", {}),
                "language": pred_info.get("language", "unknown"),
                "key": pred_info.get("key", f"unknown_{index}"),
                "models": dict(model_scores)
            }

    # 将defaultdict转换为普通dict
    result = {cat: dict(indices) for cat, indices in integrated.items()}
    return result

def main():
    # 检查目录是否存在
    predictions_path = "data_process/eval_result/predictions"
    reviews_path = "data_process/eval_result/reviews"

    if not os.path.exists(predictions_path):
        print(f"错误：predictions路径不存在 {predictions_path}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(reviews_path):
        print(f"错误：reviews路径不存在 {reviews_path}", file=sys.stderr)
        sys.exit(1)

    print("开始整合multi-if数据...")
    integrated_data = integrate_data()

    output_file = "integrated_multi_if_v2.json"
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
        print(f"  语言: {first_sample.get('language', 'unknown')}")
        print(f"  key: {first_sample.get('key', 'unknown')}")
        print(f"  消息数量: {len(first_sample.get('messages', []))}")

        if first_sample.get("models"):
            first_model = list(first_sample["models"].keys())[0]
            first_model_data = first_sample["models"][first_model]
            print(f"  第一个模型主要评分 (acc): {first_model_data['acc']}")
            print(f"  第一个模型语言: {first_model_data.get('language', 'unknown')}")

if __name__ == "__main__":
    main()