import os
import json

def count_question_types(directory):
    results = {}
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".jsonl"):
                file_path = os.path.join(root, file)
                question_types_to_count = {"Attribute Change": 0, "Temporal Reasoning": 0}
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                data = json.loads(line.strip())
                                for key, value in data.items():
                                    if isinstance(value, list):
                                        for item in value:
                                            question_type = item.get("question_type", "")
                                            if question_type in question_types_to_count:
                                                question_types_to_count[question_type] += 1
                            except json.JSONDecodeError:
                                print(f"Skipping invalid JSON line in file: {file_path}")
                    
                    results[file_path] = question_types_to_count
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
    
    return results

if __name__ == "__main__":
    directory = "/Users/dehua/code/image-video-bench/res/res_current_v2"
    result = count_question_types(directory)
    print("Question Type Counts Per File:")
    for file, counts in result.items():
        print(f"{file}:")
        for q_type, count in counts.items():
            print(f"  {q_type}: {count}")
