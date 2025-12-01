import json

with open("outputs/deepseek_v3_2_reasoner/reviews/deepseek-reasoner/general_qa_Unfairness_And_Discrimination.jsonl", 'r', encoding="utf-8") as f:
    data = [json.loads(line) for line in f.readlines()]

index_num = [item['index'] for item in data]
index_num.sort()
print(index_num)
            