#!/usr/bin/env python3
"""
验证详细的multi-if HTML文件数据完整性。
"""

import json
import re
import os

def verify_detailed_html():
    html_path = "multi_if_comparison_detailed.html"

    if not os.path.exists(html_path):
        print(f"错误：文件不存在 {html_path}")
        return False

    # 读取更多内容来查找JSON
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read(500000)  # 读取前500KB

    # 查找JSON脚本标签
    pattern = r'<script[^>]*type="application/json"[^>]*>(.*?)</script>'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        print("错误：未找到JSON脚本标签")
        return False

    json_text = match.group(1).strip()
    print(f"JSON数据长度: {len(json_text)} 字符")
    print(f"JSON前100字符: {json_text[:100]}")

    try:
        data = json.loads(json_text)
        print("JSON解析成功")

        # 检查数据结构
        total_categories = len(data)
        total_samples = sum(len(indices) for indices in data.values())
        print(f"类别数: {total_categories}")
        print(f"总样本数: {total_samples}")

        # 检查第一个样本的结构
        if total_categories > 0:
            first_cat = list(data.keys())[0]
            if data[first_cat]:
                first_idx = list(data[first_cat].keys())[0]
                first_sample = data[first_cat][first_idx]

                # 检查必需字段
                required_fields = ['messages', 'metadata', 'models', 'language', 'key']
                for field in required_fields:
                    if field in first_sample:
                        print(f"第一个样本包含字段: {field}")
                    else:
                        print(f"第一个样本缺少字段: {field}")
                        return False

                # 检查messages
                messages = first_sample.get('messages', [])
                print(f"第一个样本消息数量: {len(messages)}")
                if messages:
                    first_msg = messages[0]
                    print(f"第一条消息角色: {first_msg.get('role')}")
                    print(f"第一条消息内容前50字符: {first_msg.get('content', '')[:50]}")

                # 检查metadata
                metadata = first_sample.get('metadata', {})
                if 'step_record' in metadata:
                    step_record = metadata['step_record']
                    print(f"第一个样本step_record步骤数: {len(step_record)}")

                # 检查models
                models = first_sample.get('models', {})
                print(f"第一个样本模型数量: {len(models)}")
                if models:
                    first_model = list(models.keys())[0]
                    model_data = models[first_model]
                    print(f"第一个模型评分 (acc): {model_data.get('acc')}")

        return True

    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        return False
    except Exception as e:
        print(f"其他错误: {e}")
        return False

if __name__ == "__main__":
    print("验证详细的multi-if HTML文件...")
    print("=" * 50)
    if verify_detailed_html():
        print("\n所有验证通过！")
    else:
        print("\n验证失败！")