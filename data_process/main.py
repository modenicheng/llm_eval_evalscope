import os
import json
from pathlib import Path
from chartjs_wrap import *


def load_reports():
    """自动检测并加载所有reports文件"""
    reports_dir = Path("./eval_result/reports")
    if not reports_dir.exists():
        raise FileNotFoundError(
            f"Reports directory not found at: {reports_dir}")

    all_reports = {}

    # 遍历所有模型目录 (deepseek-reasoner, doubao-seed-1-6-251015等)
    for model_dir in reports_dir.iterdir():
        if not model_dir.is_dir():
            continue

        model_name = model_dir.name
        all_reports[model_name] = {}

        # 遍历模型目录下的所有JSON报告文件
        for report_file in model_dir.glob("*.json"):
            task_name = report_file.stem  # 获取文件名(不含扩展名)

            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    # 尝试加载JSON内容
                    report_data = json.load(f)
                    all_reports[model_name][task_name] = report_data
            except json.JSONDecodeError as e:
                print(f"警告: 无法解析JSON文件 {report_file}: {str(e)}")
            except Exception as e:
                print(f"警告: 读取文件 {report_file} 时出错: {str(e)}")

    return all_reports


def get_overview(reports: dict[str, dict]) -> ChartJS:
    chart = ChartJS(ChartType.RADAR)
    labels = [
        "general_qa", "chinese_simpleqa", "math_500", "multi_if", "ifeval",
        "swe_bench_verified_mini"
    ]
    chart.set_labels(labels)
    for model_id in reports.keys():
        model_report: dict[str, dict] = reports[model_id]
        dataset = Dataset(
            label=model_id,
            data=[model_report[key]['score'] for key in labels],
        )
        chart.add_dataset(dataset)

    return chart


def main():
    """主函数：加载报告并展示结果"""
    try:
        reports_data = load_reports()

        # 打印加载结果摘要
        print(f"成功加载 {len(reports_data)} 个模型的评估报告:")
        for model_name, tasks in reports_data.items():
            print(f"\n模型: {model_name}")
            print(f"  包含 {len(tasks)} 个评测任务:")
            for task_name in tasks.keys():
                print(f"    - {task_name}")

        # 示例：访问特定报告数据
        # if reports_data:
        #     first_model = next(iter(reports_data))
        #     first_task = next(iter(reports_data[first_model]))
        #     print(f"\n示例数据 ({first_model} - {first_task}):")
        #     print(json.dumps(reports_data[first_model][first_task], indent=2, ensure_ascii=False)[:500] + "...")
        print(get_overview(reports_data).to_json())
    except Exception as e:
        print(f"错误: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
