import os
import dotenv
from evalscope import TaskConfig, run_task
from evalscope.constants import EvalType, JudgeStrategy

import json

# 加载环境变量文件
dotenv.load_dotenv()

# with open("data/cvalues_responsibility_mc.jsonl", 'r', encoding='utf-8') as f:

task_cfg = TaskConfig(
    model='qwen3-max',
    api_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
    api_key=os.getenv('DASHSCOPE_API_KEY'),
    eval_type=EvalType.SERVICE,
    eval_batch_size=16,
    datasets=[
        'general_qa',
        # 'chinese_simpleqa',
        # 'math_500',
        # 'swe_bench_verified_mini',
        # 'multi_if'
    ],
    dataset_args={
        'general_qa': {
            "local_path":
            'data/safety-prompts',
            "subset_list": [
                'Unfairness_And_Discrimination',
                'Crimes_And_Illegal_Activities', 'Insult', 'Mental_Health',
                'Physical_Harm', 'Privacy_And_Property', 'Ethics_And_Morality'
            ]
        },
        'multi_if': {
            "subset_list": ['Chinese', 'English']
        }
    },
    limit=64,
    judge_strategy=JudgeStrategy.LLM,
    judge_worker_num=64,
    judge_model_args={
        'model_id': 'deepseek-chat',
        'api_url': 'https://api.deepseek.com/v1',
        'api_key': os.getenv('DEEPSEEK_API_KEY')
    },
    debug=True,
    work_dir='outputs/qwen_plus',
    use_cache='outputs/qwen_plus',
    ignore_errors=True,
)

# 运行评估任务
try:
    result = run_task(task_cfg=task_cfg)
    print("评估完成！")
    print("结果摘要:")
    print(result)

    # 保存详细结果到文件
    # import json
    # with open(os.path.join(task_cfg.work_dir, 'evaluation_results.json'), 'w', encoding='utf-8') as f:
    #     json.dump(result, f, ensure_ascii=False, indent=2)
    # print(f"详细结果已保存至: {os.path.join(task_cfg.work_dir, 'evaluation_results.json')}")

except Exception as e:
    print(f"评估过程中出错: {str(e)}")
    import traceback
    traceback.print_exc()
