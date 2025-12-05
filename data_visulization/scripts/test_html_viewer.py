#!/usr/bin/env python3
"""
简单测试HTML文件是否包含必要元素。
"""

import json
import os
import sys
from html.parser import HTMLParser

class SimpleHTMLChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = set()
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        self.elements.add(tag)
        for attr, value in attrs:
            if attr == 'id':
                self.ids.add(value)
            if attr == 'type' and value == 'application/json':
                self.ids.add('has_json_script')

def test_html_file(filepath):
    """测试HTML文件"""
    if not os.path.exists(filepath):
        print(f"错误：文件不存在 {filepath}")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read(50000)  # 只读取前50KB进行快速检查

    # 检查基本结构
    checks = [
        ('DOCTYPE html' in content, '包含DOCTYPE声明'),
        ('<html lang="zh-CN">' in content, '包含HTML标签和中文语言'),
        ('<meta name="viewport"' in content, '包含移动端viewport'),
        ('<div class="app-container">' in content, '包含应用容器'),
        ('<div class="samples-panel">' in content, '包含样本列表面板'),
        ('<div class="detail-panel">' in content, '包含详情面板'),
        ('<script type="application/json"' in content, '包含JSON脚本标签'),
    ]

    all_ok = True
    for check, description in checks:
        if check:
            print(f"[OK] {description}")
        else:
            print(f"[FAIL] {description}")
            all_ok = False

    # 使用HTML解析器检查
    parser = SimpleHTMLChecker()
    parser.feed(content)

    required_ids = ['samples-list', 'detail-content', 'detail-title', 'sample-count', 'evaluation-data']
    for rid in required_ids:
        if rid in parser.ids:
            print(f"[OK] 找到ID: #{rid}")
        else:
            print(f"[FAIL] 缺少ID: #{rid}")
            all_ok = False

    # 检查JSON数据是否存在
    if 'has_json_script' in parser.ids:
        print("[OK] 找到JSON脚本标签")
    else:
        print("[FAIL] 未找到JSON脚本标签")
        all_ok = False

    return all_ok

def main():
    html_files = ['general_qa_comparison_safe.html', 'general_qa_comparison.html']

    for file in html_files:
        if os.path.exists(file):
            print(f"\n测试文件: {file}")
            print("=" * 40)
            if test_html_file(file):
                print(f"\n[PASS] {file} 通过基本测试")
            else:
                print(f"\n[FAIL] {file} 测试失败")
        else:
            print(f"\n文件不存在: {file}")

if __name__ == "__main__":
    main()