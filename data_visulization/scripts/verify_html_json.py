#!/usr/bin/env python3
"""
验证HTML文件中的JSON数据是否能正常解析。
"""

import json
import re
import sys
import os

def extract_json_from_html(html_path):
    """从HTML文件中提取JSON数据"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 查找<script type="application/json">标签
    pattern = r'<script[^>]*type="application/json"[^>]*>(.*?)</script>'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        print(f"错误：在 {html_path} 中未找到JSON脚本标签")
        return None

    json_text = match.group(1).strip()
    return json_text

def verify_html_file(html_path):
    """验证HTML文件中的JSON数据"""
    print(f"\n验证文件: {html_path}")
    print("=" * 40)

    if not os.path.exists(html_path):
        print(f"错误：文件不存在 {html_path}")
        return False

    json_text = extract_json_from_html(html_path)
    if json_text is None:
        return False

    # 尝试解析JSON
    try:
        data = json.loads(json_text)
        print(f"[OK] JSON解析成功")

        # 统计信息
        if isinstance(data, dict):
            total_categories = len(data)
            total_samples = sum(len(indices) for indices in data.values())
            print(f"[INFO] 类别数: {total_categories}")
            print(f"[INFO] 总样本数: {total_samples}")

            # 检查第一个样本的模型数量
            if total_categories > 0:
                first_cat = list(data.keys())[0]
                if data[first_cat]:
                    first_idx = list(data[first_cat].keys())[0]
                    first_sample = data[first_cat][first_idx]
                    model_count = len(first_sample.get('models', {}))
                    print(f"[INFO] 第一个样本的模型数量: {model_count}")

                    # 检查评分信息
                    if model_count > 0:
                        first_model = list(first_sample['models'].keys())[0]
                        model_data = first_sample['models'][first_model]
                        acc = model_data.get('acc', 0.0)
                        print(f"[INFO] 第一个样本主要评分 (acc): {acc}")

        return True

    except json.JSONDecodeError as e:
        print(f"[FAIL] JSON解析失败: {e}")
        print(f"[DEBUG] JSON文本前100个字符: {json_text[:100]}")
        return False
    except Exception as e:
        print(f"[FAIL] 其他错误: {e}")
        return False

def main():
    html_files = [
        "ifeval_comparison_safe.html",
        "multi_if_comparison_safe.html",
        "general_qa_comparison_safe.html"
    ]

    all_passed = True
    for html_file in html_files:
        if os.path.exists(html_file):
            if not verify_html_file(html_file):
                all_passed = False
        else:
            print(f"\n文件不存在: {html_file}")

    if all_passed:
        print("\n所有HTML文件JSON验证通过！")
    else:
        print("\n部分HTML文件验证失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()