import json
import os


def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
        return data


def save_jsonl(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        [f.write(json.dumps(item, ensure_ascii=False) + "\n") for item in data]


def main():
    print("Loading data...")
    data: dict = read_json("data/safety-prompts/typical_safety_scenarios.json")

    os.makedirs("./results", exist_ok=True)

    for key in data.keys():
        print(f"Processing {key}")
        sub_data = []
        for item in data[key]:
            sub_data.append({
                "query": item["prompt"],
                "response": item["response"]
            })
        save_jsonl(sub_data,
                    f"data/safety-prompts/{key}.jsonl")


d = {}


if __name__ == "__main__":
    main()
